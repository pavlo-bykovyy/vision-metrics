"""
CLI for the VisionMetrics statistical stress test.

    python -m api_cv.services.stress_test all --results-dir /app/extracted_datasets/stress_v3
    python -m api_cv.services.stress_test simulate --replicates 25     # quick smoke run
    python -m api_cv.services.stress_test reviewer                     # needs simulate output
    python -m api_cv.services.stress_test figures --formats png
    python -m api_cv.services.stress_test archive
"""
from __future__ import annotations

import argparse
from pathlib import Path

from api_cv.services.stress_test.config import DEFAULT_RESULTS_DIR, StressTestConfig

STEPS = ("simulate", "reviewer", "figures", "archive", "all")


def _parse() -> argparse.Namespace:
    defaults = StressTestConfig()
    p = argparse.ArgumentParser(prog="python -m api_cv.services.stress_test", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("step", choices=STEPS)
    p.add_argument("--results-dir", type=Path, default=Path(DEFAULT_RESULTS_DIR))
    p.add_argument("--seed", type=int, default=defaults.seed)
    p.add_argument("--n", type=int, default=defaults.n, help="samples per replicate")
    p.add_argument("--replicates", type=int, default=defaults.replicates,
                   help="Monte Carlo repetitions per prevalence (25 for a smoke test)")
    p.add_argument("--ood-replicates", type=int, default=defaults.ood_replicates)
    p.add_argument("--n-boot", type=int, default=defaults.n_boot)
    p.add_argument("--n-jobs", type=int, default=-1, help="parallel jobs for cross_val_predict")
    p.add_argument("--formats", nargs="+", default=["png", "pdf", "svg"])
    p.add_argument("--dpi", type=int, default=600)
    p.add_argument("--archive", action="store_true", help="with 'all': also zip the results")
    return p.parse_args()


def main() -> None:
    args = _parse()
    cfg = StressTestConfig(
        seed=args.seed, n=args.n, replicates=args.replicates,
        ood_replicates=args.ood_replicates, n_boot=args.n_boot,
    )
    from api_cv.services.stress_test import runner

    raw = None
    if args.step in ("simulate", "all"):
        raw = runner.run_simulation(cfg, args.results_dir)
    if args.step in ("reviewer", "all"):
        runner.run_reviewer(cfg, args.results_dir, raw=raw, n_jobs=args.n_jobs)
    if args.step in ("figures", "all"):
        runner.run_figures(args.results_dir, formats=tuple(args.formats), dpi=args.dpi)
    if args.step == "archive" or (args.step == "all" and args.archive):
        runner.archive_results(args.results_dir)


if __name__ == "__main__":
    main()
