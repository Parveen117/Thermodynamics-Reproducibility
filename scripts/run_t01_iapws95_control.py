"""Run the IAPWS-95 water control grid and write a JSON certificate."""

from __future__ import annotations

import json
from pathlib import Path

import iapws

from thermo_recognition.iapws_control import iapws_point_control


CONTROL_POINTS = [
    (285.0, 0.1),
    (300.0, 0.1),
    (300.0, 1.0),
    (325.0, 5.0),
    (350.0, 10.0),
]


def main() -> int:
    point_results = [
        iapws_point_control(temperature_K, pressure_MPa).to_dict()
        for temperature_K, pressure_MPa in CONTROL_POINTS
    ]
    statuses = [result["status"] for result in point_results]
    overall_status = "PASS_CONTROL" if all(status == "PASS_CONTROL" for status in statuses) else "FAIL_CONTROL"

    certificate = {
        "campaign": "T01_PLUCKER_INDEPENDENT_BRACKETS",
        "stage": "T01C_IAPWS95_CONTROL",
        "overall_status": overall_status,
        "iapws_python_version": getattr(iapws, "__version__", "unknown"),
        "source": "IAPWS R6-95(2018) through the pinned iapws Python implementation",
        "control_points": point_results,
        "claim_boundary": (
            "One Helmholtz equation of state supplies every channel. This validates "
            "the numerical pipeline and thermodynamic identities but is not an "
            "independent experimental falsification test."
        ),
    }

    output = Path("results/T01C_IAPWS95_CONTROL.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print(json.dumps(certificate, indent=2, sort_keys=True))
    return 0 if overall_status == "PASS_CONTROL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
