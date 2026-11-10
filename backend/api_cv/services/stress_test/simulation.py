"""
Synthetic baselines, controlled failure modes, platform-aligned metrics and the
Monte Carlo loop of the stress test.

The deployed platform uses a fixed 0.5 threshold, so "threshold drift" is modelled
as a monotone logit offset (score bias) while the threshold stays exactly 0.5.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import norm
from scipy.stats import t as student_t
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)

from api_cv.services.stress_test.config import (
    EPS,
    FAILURE_PATHS,
    NON_GAUSSIAN_SPECS,
    PLATFORM_THRESHOLD,
    StressTestConfig,
)

ProgressFn = Callable[[int, int], None]


# ------------------------------------------------------------------
# Baselines
# ------------------------------------------------------------------

def generate_baseline_data(
    n: int, prevalence: float, rng: np.random.Generator, cfg: StressTestConfig = StressTestConfig()
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Y ~ Bernoulli(prevalence), S|Y ~ N(±mu, sigma^2); returns (y, p, s) where p is the
    exact posterior P(Y=1|S), so the baseline is calibrated by construction.
    """
    y = rng.binomial(1, prevalence, size=n).astype(int)
    means = np.where(y == 1, cfg.mu, -cfg.mu)
    s = rng.normal(loc=means, scale=cfg.sigma, size=n)

    log_prior_odds = math.log(prevalence / (1.0 - prevalence))
    mu1, mu0 = cfg.mu, -cfg.mu
    log_lr = ((mu1 - mu0) / cfg.sigma**2) * s - (mu1**2 - mu0**2) / (2.0 * cfg.sigma**2)
    return y, expit(log_prior_odds + log_lr), s


def generate_non_gaussian_baseline(
    dist_type: str, n: int, prevalence: float, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """
    Non-Gaussian latent scores with their exact Bayes posteriors (OOD transfer regimes).
    Parameters come from config.NON_GAUSSIAN_SPECS; the RNG call order matches the notebook.
    """
    spec = NON_GAUSSIAN_SPECS.get(dist_type)
    if spec is None:
        raise ValueError(f"Unknown distribution: {dist_type}")

    y = rng.binomial(1, prevalence, size=n).astype(int)
    s = np.zeros(n, dtype=float)
    mask1 = y == 1
    mask0 = ~mask1
    n1 = int(mask1.sum())
    n0 = n - n1
    kind = spec["kind"]

    if kind == "heteroscedastic_gaussian":
        (loc0, sd0), (loc1, sd1) = spec["neg"], spec["pos"]
        s[mask0] = rng.normal(loc0, sd0, size=n0)
        s[mask1] = rng.normal(loc1, sd1, size=n1)
        f1 = norm.pdf(s, loc=loc1, scale=sd1)
        f0 = norm.pdf(s, loc=loc0, scale=sd0)
    elif kind == "bimodal_mixture":
        loc0, sd0 = spec["neg"]
        (loc_a, sd_a), (loc_b, sd_b) = spec["pos_components"]
        w = spec["pos_weight"]
        s[mask0] = rng.normal(loc0, sd0, size=n0)
        mix = rng.random(n1) < w
        s[mask1] = np.where(mix, rng.normal(loc_a, sd_a, size=n1), rng.normal(loc_b, sd_b, size=n1))
        f1 = w * norm.pdf(s, loc=loc_a, scale=sd_a) + (1.0 - w) * norm.pdf(s, loc=loc_b, scale=sd_b)
        f0 = norm.pdf(s, loc=loc0, scale=sd0)
    elif kind == "student_t":
        df, scale = spec["df"], spec["scale"]
        s[mask0] = spec["loc0"] + student_t.rvs(df=df, scale=scale, size=n0, random_state=rng)
        s[mask1] = spec["loc1"] + student_t.rvs(df=df, scale=scale, size=n1, random_state=rng)
        f1 = student_t.pdf(s, df=df, loc=spec["loc1"], scale=scale)
        f0 = student_t.pdf(s, df=df, loc=spec["loc0"], scale=scale)
    else:
        raise ValueError(f"Unknown distribution kind: {kind}")

    p_post = (prevalence * f1) / (prevalence * f1 + (1.0 - prevalence) * f0 + 1e-15)
    return y, np.clip(p_post, EPS, 1.0 - EPS)


# ------------------------------------------------------------------
# Failure modes
# ------------------------------------------------------------------

def apply_failure_mode(
    p: np.ndarray,
    severity: float,
    failure_mode: str,
    direction: str,
    cfg: StressTestConfig = StressTestConfig(),
) -> np.ndarray:
    """Degrades probabilities with severity lambda in [0, 1]; the 0.5 threshold never moves."""
    lam = float(severity)

    if failure_mode == "collapse":
        target = cfg.collapse_positive_target if direction == "positive" else cfg.collapse_negative_target
        return (1.0 - lam) * p + lam * target

    if failure_mode == "score_bias":
        # Monotone logit shift: ranking preserved, fixed 0.5 boundary misaligned.
        sign = 1.0 if direction == "positive" else -1.0
        z = logit(np.clip(p, EPS, 1.0 - EPS))
        return expit(z + sign * cfg.max_logit_bias * lam)

    if failure_mode == "calibration_drift":
        # Temperature scaling: ranking and the 0.5 decision preserved, confidence changes.
        z = logit(np.clip(p, EPS, 1.0 - EPS))
        if direction == "over":
            temperature = 1.0 - (1.0 - cfg.min_temperature) * lam
        elif direction == "under":
            temperature = 1.0 + (cfg.max_temperature - 1.0) * lam
        else:
            raise ValueError("calibration_drift direction must be over/under")
        return expit(z / temperature)

    if failure_mode == "score_inversion":
        # lambda=0 -> p; lambda=0.5 -> all 0.5; lambda=1 -> 1-p
        return (1.0 - lam) * p + lam * (1.0 - p)

    raise ValueError(f"Unknown failure mode: {failure_mode}")


# ------------------------------------------------------------------
# Metrics (mirrors the binary branch of api_cv/services/metrics_calculator.py)
# ------------------------------------------------------------------

def calculate_metrics_platform_binary(y_true: np.ndarray, y_pred_probs: np.ndarray) -> dict:
    """
    Same sklearn metrics and `probs > 0.5` rule as the platform. Latency/model size are
    omitted (no real model). Specificity is derived from the same confusion matrix.
    """
    y_score = np.asarray(y_pred_probs).reshape(-1)
    y_pred = (y_score > PLATFORM_THRESHOLD).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    out = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average="binary", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="binary", zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, average="binary", zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "decision_threshold": PLATFORM_THRESHOLD,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "specificity_derived": float(tn / (tn + fp)) if (tn + fp) > 0 else np.nan,
    }

    try:
        out["roc_auc"] = float(roc_auc_score(y_true, y_score))
    except ValueError:
        out["roc_auc"] = np.nan
    try:
        out["pr_auc"] = float(average_precision_score(y_true, y_score))
    except Exception:
        out["pr_auc"] = np.nan
    try:
        out["log_loss_value"] = float(log_loss(y_true, y_score, labels=[0, 1]))
    except Exception:
        out["log_loss_value"] = np.nan
    try:
        out["brier_score"] = float(brier_score_loss(y_true, y_score))
    except Exception:
        out["brier_score"] = np.nan

    out["predicted_positive_rate"] = float(np.mean(y_pred))
    out["mean_probability"] = float(np.mean(y_score))
    return out


# ------------------------------------------------------------------
# Monte Carlo
# ------------------------------------------------------------------

def run_monte_carlo(
    cfg: StressTestConfig = StressTestConfig(),
    progress: Optional[ProgressFn] = None,
) -> pd.DataFrame:
    """
    One row per (prevalence, replicate, failure path, severity):
    len(prevalences) * replicates * 7 * len(severities) rows.
    Every replicate has its own SeedSequence([seed, prevalence_idx, replicate]).
    """
    rows: list[dict] = []
    total = len(cfg.prevalences) * cfg.replicates
    step = max(1, total // 20)
    done = 0

    for p_idx, prevalence in enumerate(cfg.prevalences):
        for replicate in range(cfg.replicates):
            done += 1
            rng = np.random.default_rng(np.random.SeedSequence([cfg.seed, p_idx, replicate]))
            y, p_base, _ = generate_baseline_data(cfg.n, prevalence, rng, cfg)
            prevalence_observed = float(np.mean(y))

            for failure_mode, direction in FAILURE_PATHS:
                path_label = f"{failure_mode}:{direction}"
                for severity in cfg.severities:
                    p_stressed = apply_failure_mode(p_base, severity, failure_mode, direction, cfg)
                    rows.append({
                        "replicate": replicate,
                        "group_id": f"p{p_idx}_r{replicate}",
                        "n": cfg.n,
                        "prevalence_target": prevalence,
                        "prevalence_observed": prevalence_observed,
                        "failure_mode": failure_mode,
                        "direction": direction,
                        "path_label": path_label,
                        "severity": float(severity),
                        **calculate_metrics_platform_binary(y, p_stressed),
                    })

            if progress is not None and (done % step == 0 or done == total):
                progress(done, total)

    return pd.DataFrame(rows)
