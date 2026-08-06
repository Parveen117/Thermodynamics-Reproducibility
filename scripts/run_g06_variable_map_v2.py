from __future__ import annotations

import importlib.util
import re
from pathlib import Path


def _load_base_module():
    script = Path(__file__).with_name("run_g06_variable_map.py")
    spec = importlib.util.spec_from_file_location("g06_base", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load variable-map engine from {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = _load_base_module()


REGEX_GROUPS: dict[str, tuple[str, ...]] = {
    "temperature_control": (
        r"^t$",
        r"\bt\s*[=(]",
        r"\btemperature\b",
        r"\belectron(?:ic)?\s+temperature\b",
        r"\bfermi\s+temperature\b",
        r"\b\d+(?:\.\d+)?\s*k\b",
    ),
    "density_control": (
        r"^n$",
        r"\bn\s*[=(]",
        r"\bn_?min\b",
        r"\bcarrier\s+density\b",
        r"\bcharge\s+density\b",
        r"\bdoping(?:\s+regime)?\b",
        r"\bvg\b",
        r"cm\s*[-^]?\s*2",
    ),
    "electrical_transport": (
        r"\belectrical\s+conductiv",
        r"\bconductance\b",
        r"\bresistance\b",
        r"\bsigma(?:_q)?\b",
        r"σ",
        r"^g(?:\s|\(|$)",
    ),
    "thermal_transport": (
        r"\bthermal\s+conductiv",
        r"\bkappa(?:_e)?\b",
        r"κ",
        r"\blorenz\b",
        r"\bwiedemann",
        r"\bl\s*/\s*l0\b",
    ),
    "derived_hydrodynamics": (
        r"\bviscosity\b",
        r"\bentropy\b",
        r"\benthalpy\b",
        r"\bmean\s+free\s+path\b",
        r"\bknudsen\b",
        r"\beta(?:_th)?\b",
    ),
    "uncertainty": (
        r"\berror\b",
        r"\buncertainty\b",
        r"\bstandard\s+deviation\b",
        r"\bconfidence\s+interval\b",
    ),
}


def matched_labels(
    labels: list[str],
    keyword_groups: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Combine frozen literal terms with physics-aware compact-header regexes."""
    result: dict[str, list[str]] = {}
    for group, keywords in keyword_groups.items():
        patterns = tuple(re.compile(pattern, flags=re.I) for pattern in REGEX_GROUPS.get(group, ()))
        matches: list[str] = []
        for label in labels:
            padded = f" {label.casefold()} "
            literal_match = any(keyword.casefold() in padded for keyword in keywords)
            regex_match = any(pattern.search(label) for pattern in patterns)
            if literal_match or regex_match:
                matches.append(label)
        result[group] = list(dict.fromkeys(matches))[:120]
    return result


BASE.matched_labels = matched_labels


if __name__ == "__main__":
    raise SystemExit(BASE.main())
