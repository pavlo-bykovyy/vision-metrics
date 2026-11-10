"""Stress-test port: failure-mode invariants and a tiny end-to-end run (needs scipy + scikit-learn)."""
import numpy as np
import pandas as pd
import pytest

pytest.importorskip("scipy")
pytest.importorskip("sklearn")

from api_cv.services.stress_test import analysis, reviewer  # noqa: E402
from api_cv.services.stress_test.config import FAILURE_PATHS, PATH_LABELS, StressTestConfig  # noqa: E402
from api_cv.services.stress_test.simulation import (  # noqa: E402
    apply_failure_mode,
    calculate_metrics_platform_binary,
    generate_baseline_data,
    generate_non_gaussian_baseline,
    run_monte_carlo,
)

CFG = StressTestConfig()


@pytest.fixture(scope="module")
def baseline():
    rng = np.random.default_rng(np.random.SeedSequence([CFG.seed, 0, 0]))
    y, p, _ = generate_baseline_data(2000, 0.3, rng)
    return y, p


@pytest.fixture(scope="module")
def tiny_raw():
    cfg = StressTestConfig(n=300, replicates=2, severities=np.array([0.0, 0.5, 1.0]))
    return cfg, run_monte_carlo(cfg)


def test_zero_severity_is_identity(baseline):
    _, p = baseline
    for mode, direction in FAILURE_PATHS:
        np.testing.assert_allclose(apply_failure_mode(p, 0.0, mode, direction), p, atol=1e-9)


@pytest.mark.parametrize("direction", ["over", "under"])
def test_calibration_drift_keeps_decisions_and_ranking(baseline, direction):
    y, p = baseline
    base = calculate_metrics_platform_binary(y, p)
    drifted = calculate_metrics_platform_binary(y, apply_failure_mode(p, 1.0, "calibration_drift", direction))
    for key in ("tp", "fp", "tn", "fn"):
        assert drifted[key] == base[key]
    assert drifted["roc_auc"] == pytest.approx(base["roc_auc"], abs=1e-9)
    assert drifted["log_loss_value"] > base["log_loss_value"]


def test_score_bias_keeps_ranking_but_moves_decisions(baseline):
    y, p = baseline
    base = calculate_metrics_platform_binary(y, p)
    biased = calculate_metrics_platform_binary(y, apply_failure_mode(p, 1.0, "score_bias", "positive"))
    assert biased["roc_auc"] == pytest.approx(base["roc_auc"], abs=1e-9)
    assert biased["predicted_positive_rate"] > base["predicted_positive_rate"] + 0.2


def test_inversion_and_collapse_endpoints(baseline):
    y, p = baseline
    np.testing.assert_allclose(apply_failure_mode(p, 0.5, "score_inversion", "none"), 0.5)
    inverted = calculate_metrics_platform_binary(y, apply_failure_mode(p, 1.0, "score_inversion", "none"))
    assert inverted["roc_auc"] == pytest.approx(1 - calculate_metrics_platform_binary(y, p)["roc_auc"])
    collapsed = calculate_metrics_platform_binary(y, apply_failure_mode(p, 1.0, "collapse", "positive"))
    assert collapsed["predicted_positive_rate"] == 1.0
    assert collapsed["balanced_accuracy"] == 0.5


def test_custom_collapse_targets(baseline):
    _, p = baseline
    cfg = StressTestConfig(collapse_positive_target=0.8, collapse_negative_target=0.2)
    np.testing.assert_allclose(apply_failure_mode(p, 1.0, "collapse", "positive", cfg), 0.8)
    np.testing.assert_allclose(apply_failure_mode(p, 1.0, "collapse", "negative", cfg), 0.2)


def test_severity_band_labels():
    article = np.round(np.linspace(0.0, 1.0, 11), 2)
    labels = analysis.severity_band_labels(article)
    assert sorted(set(labels.values())) == ["mild_0.1_0.3", "moderate_0.4_0.7", "severe_0.8_1.0"]
    assert 0.0 not in labels

    custom = analysis.severity_band_labels(article, (0.2, 0.5))
    assert custom[0.2] == "mild_0.1_0.2" and custom[0.3] == "moderate_0.3_0.5" and custom[1.0] == "severe_0.6_1.0"

    coarse = analysis.severity_band_labels([0.0, 0.5, 1.0])
    assert coarse == {0.5: "moderate_0.5_0.5", 1.0: "severe_1.0_1.0"}


def test_non_gaussian_baselines_are_probabilities():
    rng = np.random.default_rng(1)
    for dist in reviewer.NON_GAUSSIAN_DISTRIBUTIONS:
        y, p = generate_non_gaussian_baseline(dist, 500, 0.3, rng)
        assert y.shape == p.shape == (500,)
        assert np.all((p > 0) & (p < 1))


def test_monte_carlo_shape_and_determinism(tiny_raw):
    cfg, raw = tiny_raw
    assert len(raw) == len(cfg.prevalences) * cfg.replicates * len(FAILURE_PATHS) * len(cfg.severities)
    assert set(raw["path_label"]) == set(PATH_LABELS)
    again = run_monte_carlo(cfg)
    pd.testing.assert_frame_equal(raw, again)


def test_analysis_pipeline_runs_on_tiny_data(tiny_raw):
    cfg, raw = tiny_raw
    summary = analysis.summarize_results(raw)
    _, sig = analysis.build_signature_matrix(summary)
    assert sig["mean_normalized_response"].abs().max() <= 1.0 + 1e-12

    ablation = analysis.run_metric_family_ablation(raw, n_splits=cfg.cv_splits)
    assert set(ablation["folds"]["metric_family"]) == set(analysis.METRIC_FAMILIES)
    assert ablation["confusion_matrix"].shape == (7, 7)

    loo, _ = analysis.leave_one_prevalence_out_validation(raw, list(cfg.prevalences))
    assert set(loo["heldout_prevalence"]) == set(cfg.prevalences)

    tables = analysis.build_publication_tables(
        raw, ablation["folds"], ablation["performance"], loo,
        analysis.theoretical_invariance_checks(summary),
    )
    assert len(tables["publication_table_baseline_prevalence.csv"]) == len(cfg.prevalences)


def test_reviewer_ablation_runs_on_tiny_data(tiny_raw):
    _, raw = tiny_raw
    df_diag = reviewer.prepare_diagnostic_dataset(raw)
    ablation, wilcoxon = reviewer.run_ablation_study(df_diag, n_boot=50, n_jobs=1)
    assert ablation.loc[0, "Wilcoxon p vs 11D"] == "Reference"
    assert len(ablation) == len(wilcoxon) == 9
    assert ablation["Wilcoxon p vs 11D"].str.len().gt(0).all()


def test_simulation_design_matches_notebook_rows():
    design = analysis.simulation_design_table(CFG)
    notebook = {
        "Sample size per replicate": "1000",
        "Monte Carlo repetitions": "1000",
        "Positive-class prevalence": "0.5, 0.3, 0.1, 0.05",
        "Severity": "0.0 to 1.0; step 0.1",
        "VisionMetrics binary threshold": "0.5",
        "Binary threshold rule": "y_pred_probs > 0.5",
        "PR AUC implementation": "sklearn.average_precision_score",
        "Number of failure paths": "7",
        "Primary cross-validation": "5-fold GroupKFold by baseline replicate",
        "Out-of-prevalence validation": "Leave-one-prevalence-out",
        "Metric-family ablation": "full_panel, threshold_confusion, ranking_only, probability_only",
    }
    assert list(design["factor"][: len(notebook)]) == list(notebook)
    assert dict(zip(design["factor"], design["value"])) | notebook == dict(zip(design["factor"], design["value"]))
    assert analysis._severity_grid_text(np.round(np.linspace(0, 1, 7), 2)) == "0.0 to 1.0; 7 levels"


def test_reviewer_tables_use_notebook_metric_names(tiny_raw):
    _, raw = tiny_raw
    df_diag = reviewer.prepare_diagnostic_dataset(raw)
    _, loadings = reviewer.run_pca(df_diag)
    corr, cos, _ = reviewer.run_redundancy(df_diag)
    for table in (loadings, corr, cos):
        assert "specificity" in table.index and "specificity_derived" not in table.index
    assert list(corr.columns) == list(cos.columns) == reviewer.NOTEBOOK_11D


def test_ood_crosscheck_reproduces_table_11(tiny_raw):
    import dataclasses

    cfg, raw = tiny_raw
    cfg = dataclasses.replace(
        cfg, ood_prevalences=(0.3,), ood_replicates=2,
        ood_distributions=(reviewer.NON_GAUSSIAN_DISTRIBUTIONS[0],),
    )
    df_diag = reviewer.prepare_diagnostic_dataset(raw)
    probes = reviewer.fit_ood_probes(df_diag, cfg)
    pd.testing.assert_frame_equal(
        reviewer.run_ood_transfer(df_diag, cfg, probes=probes),
        reviewer.run_ood_crosscheck(df_diag, cfg, probes=probes),
    )


def test_reproducibility_row_uses_configured_links():
    row = reviewer._reproducibility_row(CFG)
    assert row[1].startswith("GitHub + Kaggle; fixed random seed")
    assert row[2] == " | ".join(link.split(": ", 1)[1] for link in CFG.public_links)

    none = reviewer._reproducibility_row(StressTestConfig(public_links=()))
    assert none[1] == f"Fixed random seed {CFG.seed}"
    assert none[2] == "no public links configured"

    bare = reviewer._reproducibility_row(StressTestConfig(public_links=("https://example.org/repo",)))
    assert bare[2] == "https://example.org/repo"


def test_profile_vector_matches_full_11d(baseline):
    y, p = baseline
    m = calculate_metrics_platform_binary(y, p)
    vec = reviewer.profile_vector(m)
    assert len(vec) == len(reviewer.FULL_11D)
    assert vec[reviewer.FULL_11D.index("f1")] == m["f1_score"]
    assert vec[reviewer.FULL_11D.index("log_loss")] == m["log_loss_value"]
