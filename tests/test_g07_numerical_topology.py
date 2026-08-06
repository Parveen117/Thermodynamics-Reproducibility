from __future__ import annotations

import importlib.util
from pathlib import Path

from openpyxl import Workbook


def load_module():
    script = Path(__file__).parents[1] / "scripts" / "run_g07_numerical_topology.py"
    spec = importlib.util.spec_from_file_location("g07_topology", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_connected_numeric_block_bounds() -> None:
    module = load_module()
    values = {
        (2, 2): 1.0,
        (2, 3): 2.0,
        (3, 2): 3.0,
        (3, 3): 4.0,
        (8, 8): 9.0,
    }
    blocks, small = module.connected_numeric_blocks(values, minimum_block_size=3)
    assert len(blocks) == 1
    assert blocks[0]["numeric_cell_count"] == 4
    assert blocks[0]["distinct_row_count"] == 2
    assert blocks[0]["distinct_column_count"] == 2
    assert small == 1


def test_labeled_vertical_numeric_run() -> None:
    module = load_module()
    workbook = Workbook()
    sheet = workbook.active
    sheet["A1"] = "T(K)"
    sheet["A2"] = 100.0
    sheet["A3"] = 150.0
    sheet["A4"] = 200.0
    run = module.numeric_run(sheet, 1, 1, direction="vertical")
    workbook.close()
    assert run is not None
    assert run["count"] == 3
    assert run["distinct_count"] == 3
    assert run["minimum"] == 100.0
    assert run["maximum"] == 200.0


def test_surface_precheck_requires_both_controls_observable_and_units() -> None:
    module = load_module()
    labeled_runs = [
        {
            "categories": ["temperature"],
            "run": {"distinct_count": 3},
        },
        {
            "categories": ["density"],
            "run": {"distinct_count": 7},
        },
    ]
    headers = [
        {"categories": ["electrical"]},
        {"categories": ["units_or_scaling"]},
    ]
    gate = {
        "minimum_distinct_temperature_support": 3,
        "minimum_distinct_density_support": 5,
        "minimum_numeric_observations": 15,
    }
    result = module.surface_precheck(labeled_runs, headers, 30, gate)
    assert result["structural_surface_gate_pass"] is True
    assert result["fit_allowed"] is False
    assert result["fit_blocker"] == "UNCERTAINTY_OR_REPLICATE_CONTRACT_NOT_YET_FROZEN"


def test_compact_graphene_labels_are_categorized() -> None:
    module = load_module()
    assert "temperature" in module.label_categories("T(K)")
    assert "density" in module.label_categories("n (1e12 cm^-2)")
    assert "electrical" in module.label_categories("Sigma_Q")
    assert "thermal" in module.label_categories("L/L0")
