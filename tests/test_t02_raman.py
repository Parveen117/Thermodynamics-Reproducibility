import hashlib, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_t02_raman_hysteresis as t02

def test_certificate_reproduces_pin():
    cert = t02.build()
    pinned = (ROOT / "results" / "T02_RAMAN_HYSTERESIS.sha256").read_text().strip()
    assert cert["certificate_sha256"] == pinned

def test_paper_table_v_reproduced():
    cert = t02.build()
    assert all(v["agree_within_combined_1sigma"] for v in cert["paper_comparison"].values())

def test_nonclosure_is_recorded_not_hidden():
    cert = t02.build()
    assert all("NONCLOSURE_AT_300K" in L["verdicts"] for L in cert["loops"])
    assert cert["classification"] == "FIRST_CYCLE_HYSTERESIS_WITH_NONCLOSURE"
    assert all("CURVATURE_NOT_ESTABLISHED" in L["verdicts"] for L in cert["loops"])

def test_cycle2_rule_is_predeclared():
    r = t02.build()["predeclared_cycle2_rule"]
    assert r["reopen_ratio_curvature"] == 0.6 and r["reopen_ratio_drift"] == 0.2

def test_data_manifest_matches_files():
    man = json.loads((t02.DATA / "MANIFEST.json").read_text())["files"]
    for name, h in man.items():
        assert hashlib.sha256((t02.DATA / name).read_bytes()).hexdigest() == h

def test_tamper_detected():
    cert = t02.build()
    body = {k: v for k, v in cert.items() if k != "certificate_sha256"}
    body["loops"][0]["loop_area_cm1K"] += 1
    assert hashlib.sha256(t02.canonical(body).encode()).hexdigest() != cert["certificate_sha256"]
