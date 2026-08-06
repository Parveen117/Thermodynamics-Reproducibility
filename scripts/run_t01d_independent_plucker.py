#!/usr/bin/env python3
"""Fit the frozen independent ThermoML source slots and test Pluecker closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from thermo_recognition.plucker import PAIR_ORDER, independent_bracket_test


def canonical_sha256(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def standard_uncertainty(record: dict[str, Any], reference_scale: float) -> float | None:
    uncertainty = record["uncertainty"]
    standard = uncertainty.get("standard_uncertainty")
    if isinstance(standard, (int, float)) and standard > 0:
        return float(standard) / reference_scale
    expanded = uncertainty.get("expanded_uncertainty")
    if isinstance(expanded, (int, float)) and expanded > 0:
        return float(expanded) / (2.0 * reference_scale)
    return None


def design_matrix(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.column_stack(
        [
            np.ones_like(x),
            x,
            y,
            x * x,
            x * y,
            y * y,
        ]
    )


def effective_sample_size(weights: np.ndarray) -> float:
    total = float(np.sum(weights))
    square_total = float(np.sum(weights * weights))
    if square_total <= 0:
        return 0.0
    return total * total / square_total


def fit_slot(
    slot: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    coordinates = contract["state_coordinates"]
    fit_spec = contract["fit_model"]
    gates = contract["fit_gates"]
    target = contract["evaluation_point"]

    t0 = float(target["temperature_K"])
    p0 = float(target["pressure_kPa"])
    h_t = float(coordinates["temperature_bandwidth_K"])
    h_p = float(coordinates["pressure_bandwidth_kPa"])
    x_max = float(fit_spec["hard_window"]["absolute_x_max"])
    y_max = float(fit_spec["hard_window"]["absolute_y_max"])
    reference_scale = float(slot["reference_scale"])

    rows: list[dict[str, float]] = []
    missing_uncertainty = 0
    for record in slot["records"]:
        x = (float(record["temperature_K"]) - t0) / h_t
        y = (float(record["pressure_kPa"]) - p0) / h_p
        if abs(x) > x_max or abs(y) > y_max:
            continue
        sigma = standard_uncertainty(record, reference_scale)
        if sigma is None:
            missing_uncertainty += 1
            continue
        rows.append(
            {
                "x": x,
                "y": y,
                "z": float(record["property_value"]) / reference_scale,
                "sigma": sigma,
            }
        )

    minimum_points = int(gates["minimum_included_points"])
    if len(rows) < minimum_points:
        return {
            "status": "INCONCLUSIVE_FIT_GEOMETRY",
            "reason": "too_few_points_after_window_and_uncertainty_filter",
            "included_point_count": len(rows),
            "missing_uncertainty_count": missing_uncertainty,
        }

    x = np.asarray([row["x"] for row in rows], dtype=float)
    y = np.asarray([row["y"] for row in rows], dtype=float)
    z = np.asarray([row["z"] for row in rows], dtype=float)
    sigma = np.asarray([row["sigma"] for row in rows], dtype=float)
    kernel = np.exp(-0.5 * (x * x + y * y))
    precision_weights = kernel / (sigma * sigma)
    matrix = design_matrix(x, y)
    weighted_matrix = matrix * np.sqrt(precision_weights)[:, None]
    rank = int(np.linalg.matrix_rank(weighted_matrix))
    normal = matrix.T @ (precision_weights[:, None] * matrix)
    condition_number = float(np.linalg.cond(normal))
    ess = effective_sample_size(precision_weights)

    reasons: list[str] = []
    if rank < int(gates["required_design_rank"]):
        reasons.append("rank_deficient_design")
    if condition_number > float(gates["maximum_normal_matrix_condition_number"]):
        reasons.append("ill_conditioned_normal_matrix")
    if ess < float(gates["minimum_effective_sample_size"]):
        reasons.append("insufficient_effective_sample_size")
    if reasons:
        return {
            "status": "INCONCLUSIVE_FIT_GEOMETRY",
            "reason": reasons,
            "included_point_count": len(rows),
            "design_rank": rank,
            "normal_matrix_condition_number": condition_number,
            "effective_sample_size": ess,
            "missing_uncertainty_count": missing_uncertainty,
        }

    try:
        coefficient = np.linalg.solve(normal, matrix.T @ (precision_weights * z))
        inverse_normal = np.linalg.inv(normal)
    except np.linalg.LinAlgError:
        return {
            "status": "INCONCLUSIVE_FIT_GEOMETRY",
            "reason": "normal_matrix_inversion_failed",
            "included_point_count": len(rows),
            "design_rank": rank,
            "normal_matrix_condition_number": condition_number,
            "effective_sample_size": ess,
        }

    residual = z - matrix @ coefficient
    chi_square = float(np.sum(precision_weights * residual * residual))
    dof = max(len(rows) - rank, 1)
    reduced_chi_square = chi_square / dof
    variance_inflation = max(1.0, reduced_chi_square)
    coefficient_covariance = inverse_normal * variance_inflation
    gradient = coefficient[[1, 2]]
    gradient_covariance = coefficient_covariance[np.ix_([1, 2], [1, 2])]
    eigenvalues = np.linalg.eigvalsh(gradient_covariance)

    if float(np.min(eigenvalues)) < -1e-12:
        return {
            "status": "INCONCLUSIVE_UNCERTAINTY_MODEL",
            "reason": "gradient_covariance_not_positive_semidefinite",
            "minimum_covariance_eigenvalue": float(np.min(eigenvalues)),
        }

    weighted_rms = float(
        np.sqrt(np.sum(precision_weights * residual * residual) / np.sum(precision_weights))
    )
    return {
        "status": "PASS_FIT",
        "included_point_count": len(rows),
        "missing_uncertainty_count": missing_uncertainty,
        "design_rank": rank,
        "normal_matrix_condition_number": condition_number,
        "effective_sample_size": ess,
        "coefficient_order": ["1", "x", "y", "x^2", "x*y", "y^2"],
        "coefficients": coefficient.tolist(),
        "coefficient_covariance": coefficient_covariance.tolist(),
        "gradient_xy": gradient.tolist(),
        "gradient_covariance_xy": gradient_covariance.tolist(),
        "chi_square": chi_square,
        "degrees_of_freedom": dof,
        "reduced_chi_square": reduced_chi_square,
        "variance_inflation": variance_inflation,
        "weighted_rms_dimensionless": weighted_rms,
        "kernel_weight_range": [float(np.min(kernel)), float(np.max(kernel))],
        "dimensionless_value_range": [float(np.min(z)), float(np.max(z))],
    }


def bracket_from_fits(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_gradient = np.asarray(left["gradient_xy"], dtype=float)
    right_gradient = np.asarray(right["gradient_xy"], dtype=float)
    left_covariance = np.asarray(left["gradient_covariance_xy"], dtype=float)
    right_covariance = np.asarray(right["gradient_covariance_xy"], dtype=float)

    value = float(
        left_gradient[0] * right_gradient[1]
        - left_gradient[1] * right_gradient[0]
    )
    jacobian = np.array(
        [
            right_gradient[1],
            -right_gradient[0],
            -left_gradient[1],
            left_gradient[0],
        ],
        dtype=float,
    )
    covariance = np.zeros((4, 4), dtype=float)
    covariance[:2, :2] = left_covariance
    covariance[2:, 2:] = right_covariance
    variance = max(float(jacobian @ covariance @ jacobian), 0.0)
    return {
        "value": value,
        "variance": variance,
        "standard_error": float(np.sqrt(variance)),
        "left_gradient_xy": left_gradient.tolist(),
        "right_gradient_xy": right_gradient.tolist(),
        "jacobian": jacobian.tolist(),
    }


def run_test(
    raw_path: Path,
    manifest_path: Path,
    contract_path: Path,
) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    contract = json.loads(contract_path.read_text(encoding="utf-8"))

    fits: dict[str, Any] = {}
    for slot_name, slot in raw["slots"].items():
        fits[slot_name] = fit_slot(slot, contract)

    failed_fits = [name for name, fit in fits.items() if fit["status"] != "PASS_FIT"]
    result: dict[str, Any] = {
        "campaign": contract["campaign"],
        "stage": "FROZEN_INDEPENDENT_PLUCKER_TEST",
        "manifest_canonical_sha256": canonical_sha256(manifest_path),
        "fit_contract_canonical_sha256": canonical_sha256(contract_path),
        "raw_extraction_canonical_sha256": canonical_sha256(raw_path),
        "evaluation_point": contract["evaluation_point"],
        "state_coordinates": contract["state_coordinates"],
        "fit_model": contract["fit_model"],
        "source_independence": manifest["source_independence"],
        "fits": fits,
        "failed_fit_slots": failed_fits,
    }

    if failed_fits:
        result.update(
            {
                "status": "INCONCLUSIVE_FIT_GEOMETRY",
                "pair_order": list(PAIR_ORDER),
                "brackets": {},
                "pair_covariance": None,
                "plucker_test": None,
            }
        )
        return result

    brackets: dict[str, Any] = {}
    pair_values: list[float] = []
    pair_variances: list[float] = []
    for pair in PAIR_ORDER:
        left_name = f"{pair}.left"
        right_name = f"{pair}.right"
        bracket = bracket_from_fits(fits[left_name], fits[right_name])
        bracket["left_slot"] = left_name
        bracket["right_slot"] = right_name
        bracket["left_doi"] = raw["slots"][left_name]["citation"]["doi"]
        bracket["right_doi"] = raw["slots"][right_name]["citation"]["doi"]
        brackets[pair] = bracket
        pair_values.append(bracket["value"])
        pair_variances.append(bracket["variance"])

    pair_covariance = np.diag(pair_variances)
    test = independent_bracket_test(
        pair_values,
        pair_covariance,
        z_threshold=float(contract["decision"]["rejection_sigma"]),
    )
    result.update(
        {
            "status": test.status,
            "pair_order": list(PAIR_ORDER),
            "pair_values": pair_values,
            "pair_covariance": pair_covariance.tolist(),
            "brackets": brackets,
            "plucker_test": test.to_dict(),
            "residual_computed": True,
            "claim_boundary": contract["claim_boundary"],
        }
    )
    return result


def compact_summary(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "campaign": result["campaign"],
        "stage": result["stage"],
        "status": result["status"],
        "manifest_canonical_sha256": result["manifest_canonical_sha256"],
        "fit_contract_canonical_sha256": result["fit_contract_canonical_sha256"],
        "raw_extraction_canonical_sha256": result["raw_extraction_canonical_sha256"],
        "evaluation_point": result["evaluation_point"],
        "source_independence": result["source_independence"],
        "failed_fit_slots": result["failed_fit_slots"],
        "pair_order": result["pair_order"],
        "pair_values": result.get("pair_values"),
        "bracket_standard_errors": {
            pair: bracket["standard_error"]
            for pair, bracket in result.get("brackets", {}).items()
        },
        "fit_diagnostics": {
            name: {
                "status": fit["status"],
                "included_point_count": fit.get("included_point_count"),
                "effective_sample_size": fit.get("effective_sample_size"),
                "normal_matrix_condition_number": fit.get("normal_matrix_condition_number"),
                "reduced_chi_square": fit.get("reduced_chi_square"),
                "gradient_xy": fit.get("gradient_xy"),
            }
            for name, fit in result["fits"].items()
        },
        "plucker_test": result.get("plucker_test"),
        "claim_boundary": result.get("claim_boundary"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw",
        type=Path,
        default=Path("results/T01D_CANDIDATE_RAW.json"),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("protocols/T01D_CANDIDATE_MANIFEST.json"),
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path("protocols/T01D_FIT_CONTRACT.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/T01D_INDEPENDENT_PLUCKER.json"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/T01D_INDEPENDENT_PLUCKER_SUMMARY.json"),
    )
    args = parser.parse_args()

    result = run_test(args.raw, args.manifest, args.contract)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.summary.write_text(json.dumps(compact_summary(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(compact_summary(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
