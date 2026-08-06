#!/usr/bin/env python3
"""Parametric bootstrap audit for the frozen T01D independent-bracket test."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

PAIR_ORDER = ("12", "13", "14", "23", "24", "34")


def run_bootstrap(result: dict, *, samples: int, seed: int) -> dict:
    if result.get("status") not in {"NOT_FALSIFIED", "FALSIFIED_MEASUREMENT_CONTRACT"}:
        return {
            "campaign": result.get("campaign"),
            "stage": "PARAMETRIC_BOOTSTRAP_AUDIT",
            "status": "INCONCLUSIVE_INPUT_RESULT",
            "input_status": result.get("status"),
            "samples": samples,
            "seed": seed,
        }

    rng = np.random.default_rng(seed)
    slot_draws: dict[str, np.ndarray] = {}
    for slot_name, fit in result["fits"].items():
        mean = np.asarray(fit["gradient_xy"], dtype=float)
        covariance = np.asarray(fit["gradient_covariance_xy"], dtype=float)
        slot_draws[slot_name] = rng.multivariate_normal(mean, covariance, size=samples)

    pair_draws: list[np.ndarray] = []
    for pair in PAIR_ORDER:
        left = slot_draws[f"{pair}.left"]
        right = slot_draws[f"{pair}.right"]
        pair_draws.append(left[:, 0] * right[:, 1] - left[:, 1] * right[:, 0])

    pairs = np.column_stack(pair_draws)
    residuals = (
        pairs[:, 0] * pairs[:, 5]
        - pairs[:, 1] * pairs[:, 4]
        + pairs[:, 2] * pairs[:, 3]
    )
    observed = float(result["plucker_test"]["residual"])
    delta_standard_error = float(result["plucker_test"]["standard_error"])
    bootstrap_mean = float(np.mean(residuals))
    bootstrap_standard_error = float(np.std(residuals, ddof=1))
    bootstrap_z = abs(observed) / bootstrap_standard_error
    threshold = float(result["plucker_test"]["z_threshold"])
    status = "FALSIFIED_MEASUREMENT_CONTRACT" if bootstrap_z > threshold else "NOT_FALSIFIED"

    quantile_levels = [0.0005, 0.005, 0.025, 0.5, 0.975, 0.995, 0.9995]
    quantiles = {
        f"{level:.4f}": float(np.quantile(residuals, level))
        for level in quantile_levels
    }
    return {
        "campaign": result["campaign"],
        "stage": "PARAMETRIC_BOOTSTRAP_AUDIT",
        "status": status,
        "samples": samples,
        "seed": seed,
        "pair_order": list(PAIR_ORDER),
        "observed_residual": observed,
        "bootstrap_mean": bootstrap_mean,
        "bootstrap_standard_error": bootstrap_standard_error,
        "delta_method_standard_error": delta_standard_error,
        "bootstrap_to_delta_standard_error_ratio": bootstrap_standard_error / delta_standard_error,
        "bootstrap_z_score": bootstrap_z,
        "z_threshold": threshold,
        "zero_inside_95_percent_interval": quantiles["0.0250"] <= 0.0 <= quantiles["0.9750"],
        "zero_inside_99_percent_interval": quantiles["0.0050"] <= 0.0 <= quantiles["0.9950"],
        "zero_inside_99_9_percent_interval": quantiles["0.0005"] <= 0.0 <= quantiles["0.9995"],
        "probability_residual_positive": float(np.mean(residuals >= 0.0)),
        "residual_quantiles": quantiles,
        "note": "Gradient draws are independent across the twelve distinct publication slots and use the fitted 2x2 covariance of each frozen source surface."
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("results/T01D_INDEPENDENT_PLUCKER.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/T01D_PARAMETRIC_BOOTSTRAP.json"),
    )
    parser.add_argument("--samples", type=int, default=200000)
    parser.add_argument("--seed", type=int, default=20260806)
    args = parser.parse_args()

    if args.samples < 1000:
        raise SystemExit("samples must be at least 1000")
    result = json.loads(args.input.read_text(encoding="utf-8"))
    audit = run_bootstrap(result, samples=args.samples, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
