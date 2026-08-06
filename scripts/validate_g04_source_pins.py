from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PIN_FIELDS = (
    "byte_size",
    "sha256",
    "page_count",
    "topology_status",
)


def validate_pins(
    pinned: dict[str, Any],
    observed: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []

    if pinned.get("campaign") != "G04_GRAPHENE_SOURCE_PINNING":
        errors.append("unexpected pinned-certificate campaign")
    if observed.get("campaign") != "G04_GRAPHENE_SOURCE_PINNING":
        errors.append("unexpected observed-audit campaign")
    if observed.get("experimental_plucker_significance_computed") is not False:
        errors.append("G04 must not compute an experimental Pluecker significance")
    if observed.get("source_files_committed") is not False:
        errors.append("source PDFs must not be committed")
    if observed.get("source_files_uploaded_as_artifacts") is not False:
        errors.append("source PDFs must not be uploaded as workflow artifacts")

    pinned_sources = {
        item["source_id"]: item
        for item in pinned.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("source_id"), str)
    }
    observed_sources = {
        item["source_id"]: item
        for item in observed.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("source_id"), str)
    }

    if pinned_sources.keys() != observed_sources.keys():
        errors.append(
            "source identifier set changed: "
            f"pinned={sorted(pinned_sources)} observed={sorted(observed_sources)}"
        )

    for source_id in sorted(pinned_sources.keys() & observed_sources.keys()):
        expected = pinned_sources[source_id]
        actual = observed_sources[source_id]
        if actual.get("status") != "PINNED":
            errors.append(f"{source_id}: observed status is not PINNED")
        for field in PIN_FIELDS:
            if expected.get(field) != actual.get(field):
                errors.append(
                    f"{source_id}: {field} changed: "
                    f"{expected.get(field)!r} != {actual.get(field)!r}"
                )
        if actual.get("machine_readable_attachment_names"):
            errors.append(
                f"{source_id}: embedded machine-readable attachments appeared; "
                "promote through a new reviewed contract rather than silently changing G04"
            )

    status = "PASS_PIN_VALIDATION" if not errors else "FAIL_PIN_VALIDATION"
    return {
        "campaign": "G04_GRAPHENE_SOURCE_PINNING",
        "status": status,
        "errors": errors,
        "validated_source_count": len(pinned_sources),
        "experimental_plucker_significance_computed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pinned",
        type=Path,
        default=Path("results/G04_SOURCE_PINNING_CERTIFICATE.json"),
    )
    parser.add_argument(
        "--observed",
        type=Path,
        default=Path("results/G04_SOURCE_ACQUISITION_AUDIT.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/G04_PIN_VALIDATION.json"),
    )
    args = parser.parse_args()

    pinned = json.loads(args.pinned.read_text(encoding="utf-8"))
    observed = json.loads(args.observed.read_text(encoding="utf-8"))
    result = validate_pins(pinned, observed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS_PIN_VALIDATION" else 1


if __name__ == "__main__":
    raise SystemExit(main())
