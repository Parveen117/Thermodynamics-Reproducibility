"""T02_RAMAN_THERMAL_HYSTERESIS — graphene Raman thermal-cycle re-analysis.

Raw data: data/raman_graphene_cense_20260219/*.txt (Horiba LabSpec exports,
CeNSE IISc Bangalore, 19 Feb 2026; Spot 1 & 2; 300->500 K heating and reverse).

For every spectrum: Lorentzian + linear baseline fit of the G band (1500–1700)
and 2D band (2550–2850 cm⁻¹). Per spot/band: heating and cooling branches,
loop area A = ∫|ω_cool − ω_heat| dT (trapezoid), uncertainty from fit covariance,
closure gap at 300 K, and a per-temperature branch-separation table.

Verdicts (predeclared, v1):
  HYSTERESIS_OBSERVED      — loop area > 5 sigma on the same spot/band
  NONCLOSURE_AT_300K       — |gap| > 3 sigma (irreversible component present)
  CURVATURE_NOT_ESTABLISHED — single cycle cannot separate reversible curvature
                             from irreversible drift; follow-up rule below.

Predeclared cycle-2 decision rule (for the follow-up session):
  reopen ratio r = A_cycle2 / A_cycle1 on the same spot and band.
  r >= 0.6 on both G and 2D  -> CURVATURE_SUPPORTED_PENDING_SUBSTRATE_CONTROL
  r <= 0.2 on both           -> IRREVERSIBLE_DRIFT_DOMINANT
  otherwise                  -> INDETERMINATE (more cycles / ramp-rate sweep)
Thresholds are fixed here, before any second-cycle data exist.

Deterministic; certificate SHA-256 over canonical JSON.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

import numpy as np
from scipy.optimize import curve_fit

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raman_graphene_cense_20260219"
OUT = ROOT / "results" / "T02_RAMAN_HYSTERESIS.json"
PROTOCOL = "T02_RAMAN_THERMAL_HYSTERESIS_V1"
BANDS = {"G": (1500.0, 1700.0, 1585.0), "2D": (2550.0, 2850.0, 2690.0)}
CYCLE2_RULE = {"reopen_ratio_curvature": 0.6, "reopen_ratio_drift": 0.2,
               "applies_to": "same spot, both G and 2D"}


def lor(x, A, x0, G, m, b):
    return A * (G / 2) ** 2 / ((x - x0) ** 2 + (G / 2) ** 2) + m * x + b


def fit_band(x, y, lo, hi, guess):
    m = (x > lo) & (x < hi)
    xx, yy = x[m], y[m]
    p0 = [float(yy.max() - yy.min()), guess, 20.0, 0.0, float(yy.min())]
    p, c = curve_fit(lor, xx, yy, p0=p0, maxfev=20000)
    e = np.sqrt(np.diag(c))
    return {"center": float(p[1]), "center_err": float(e[1]),
            "fwhm": float(abs(p[2])), "fwhm_err": float(e[2])}


def load_spectrum(path):
    a = np.loadtxt(path, encoding="latin-1")
    return a[:, 0], a[:, 1]


def parse_name(name):
    spot = int(re.search(r"Spot (\d)", name).group(1))
    t = re.search(r"(RT|\d{3}K)", name).group(1)
    T = 300 if t == "RT" else int(t[:-1])
    return spot, T, "reverse" in name.lower(), t == "RT"


def canonical(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def build():
    fits = []
    for f in sorted(DATA.glob("Spot [12]*.txt")):
        spot, T, rev, is_rt = parse_name(f.name)
        x, y = load_spectrum(f)
        rec = {"file": f.name, "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
               "spot": spot, "T_K": T, "branch": "cooling" if rev else "heating", "rt_file": is_rt}
        for band, (lo, hi, g) in BANDS.items():
            rec[band] = fit_band(x, y, lo, hi, g)
        fits.append(rec)

    def branch(spot, cooling, band):
        """Prefer the '300K' file at 300 K; if absent for this branch (Spot 1 cooling has only
        an 'RT reverse' export), fall back to the 'RT' file and record it."""
        d, used = {}, {}
        for r in fits:
            if r["spot"] != spot or (r["branch"] == "cooling") != cooling:
                continue
            T = r["T_K"]
            if T == 300 and T in d and not r["rt_file"]:
                pass  # '300K' file wins over 'RT'
            elif T == 300 and T in d and r["rt_file"]:
                continue
            d[T] = (r[band]["center"], r[band]["center_err"]); used[T] = r["file"]
        Ts = sorted(d)
        return (np.array(Ts, float), np.array([d[t][0] for t in Ts]), np.array([d[t][1] for t in Ts]), used)

    loops = []
    for spot in (1, 2):
        for band in BANDS:
            T, h, eh, used_h = branch(spot, False, band)
            T2, c, ec, used_c = branch(spot, True, band)
            assert np.array_equal(T, T2)
            diff = np.abs(c - h)
            A = float(np.trapezoid(diff, T))
            w = np.array([(T[1] - T[0]) / 2] + list((T[2:] - T[:-2]) / 2) + [(T[-1] - T[-2]) / 2])
            sA = float(np.sqrt(np.sum(w ** 2 * (eh ** 2 + ec ** 2))))
            gap = float(c[0] - h[0]); sgap = float(np.hypot(eh[0], ec[0]))
            loops.append({
                "spot": spot, "band": band, "T_K": [int(t) for t in T],
                "file_300K_heating": used_h[300], "file_300K_cooling": used_c[300],
                "heating": [round(v, 3) for v in h], "cooling": [round(v, 3) for v in c],
                "loop_area_cm1K": round(A, 2), "loop_area_err": round(sA, 2),
                "loop_area_sigma": round(A / sA, 1),
                "closure_gap_300K_cm1": round(gap, 3), "closure_gap_err": round(sgap, 3),
                "closure_gap_sigma": round(abs(gap) / sgap, 1),
                "branch_separation_per_T": [round(v, 2) for v in diff],
                "fraction_of_area_from_300K_endpoint": round(float(diff[0] * (T[1] - T[0]) / 2 / A), 3) if A else None,
                "verdicts": [
                    *(["HYSTERESIS_OBSERVED"] if A / sA > 5 else ["HYSTERESIS_NOT_SIGNIFICANT"]),
                    *(["NONCLOSURE_AT_300K"] if abs(gap) / sgap > 3 else ["CLOSED_AT_300K"]),
                    "CURVATURE_NOT_ESTABLISHED",
                ],
            })
    paper = {"S1_G": (749.7, 24.9), "S1_2D": (711.1, 34.2), "S2_G": (189.0, 31.5), "S2_2D": (295.1, 55.7)}
    comparison = {}
    for L in loops:
        k = f"S{L['spot']}_{L['band']}"
        pa, pe = paper[k]
        comparison[k] = {"refit": L["loop_area_cm1K"], "paper_tableV": pa,
                         "agree_within_combined_1sigma": bool(abs(L["loop_area_cm1K"] - pa) <= float(np.hypot(pe, L["loop_area_err"])))}
    body = {
        "protocol": PROTOCOL,
        "data_manifest_sha256": hashlib.sha256((DATA / "MANIFEST.json").read_bytes()).hexdigest(),
        "fits": fits, "loops": loops, "paper_comparison": comparison,
        "predeclared_cycle2_rule": CYCLE2_RULE,
        "classification": "FIRST_CYCLE_HYSTERESIS_WITH_NONCLOSURE" if all("NONCLOSURE_AT_300K" in L["verdicts"] for L in loops) else "FIRST_CYCLE_HYSTERESIS",
        "claim_boundary": ("Single thermal cycle per spot on SiO2-supported CVD graphene in ambient. Reproducible "
                           "first-cycle hysteresis is observed; the loop does not close at 300 K, consistent with an "
                           "irreversible component (doping/adsorbate/strain). Reversible thermodynamic curvature is NOT "
                           "established by this dataset; the predeclared cycle-2 rule is the test."),
    }
    body["certificate_sha256"] = hashlib.sha256(canonical(body).encode()).hexdigest()
    return body


if __name__ == "__main__":
    cert = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    (ROOT / "results" / "T02_RAMAN_HYSTERESIS.sha256").write_text(cert["certificate_sha256"] + "\n")
    for L in cert["loops"]:
        print(f"S{L['spot']} {L['band']:2s} area {L['loop_area_cm1K']:7.1f} ± {L['loop_area_err']:5.1f} ({L['loop_area_sigma']}σ) "
              f"gap300K {L['closure_gap_300K_cm1']:+.2f} ({L['closure_gap_sigma']}σ) {L['verdicts']}")
    print(cert["classification"], cert["certificate_sha256"])
