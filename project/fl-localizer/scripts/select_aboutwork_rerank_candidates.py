#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fl_localizer.io_utils import read_jsonl


DOMAIN_RULES: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
    (("asset", "assets"), ("assets",)),
    (("employee context", "employee_id", "organization_id", "uuid ids", "uuid"), ("workforce",)),
]
FOLLOWUP_TERMS = ("follow-up", "followup", "follow up", "previous", "reusable")
ACTION_CONTEXT_TERMS = ("action", "draft", "context")
MANAGEMENT_COMMAND_DOMAIN_TERMS = ("attendance",)


def top_score_ratio(ranked_files: list[dict[str, Any]]) -> float | None:
    if len(ranked_files) < 2:
        return None
    top1_score = float(ranked_files[0].get("score", 0.0) or 0.0)
    top2_score = float(ranked_files[1].get("score", 0.0) or 0.0)
    if top2_score <= 0:
        return None
    return top1_score / top2_score


def domain_mismatch_reason(text: str, top1_file: str) -> str | None:
    lowered_text = text.lower()
    lowered_file = top1_file.lower()
    for terms, expected_paths in DOMAIN_RULES:
        if not any(term in lowered_text for term in terms):
            continue
        if any(expected in lowered_file for expected in expected_paths):
            continue
        return "domain_mismatch:" + "|".join(terms) + "->" + "|".join(expected_paths)
    return None


def management_command_reason(text: str, top1_file: str) -> str | None:
    if "/management/commands/" not in top1_file:
        return None
    lowered_text = text.lower()
    if not any(term in lowered_text for term in FOLLOWUP_TERMS):
        return None
    if not any(term in lowered_text for term in ACTION_CONTEXT_TERMS):
        return None
    if not any(term in lowered_text for term in MANAGEMENT_COMMAND_DOMAIN_TERMS):
        return None
    return "management_command_noise:attendance_followup_action_context"


def select_record(
    bug: dict[str, Any],
    prediction: dict[str, Any],
    *,
    score_ratio_threshold: float,
) -> dict[str, Any] | None:
    ranked_files = prediction.get("ranked_files", [])
    if not isinstance(ranked_files, list) or not ranked_files:
        return {"bug_id": prediction["bug_id"], "reasons": ["empty_ranking"]}

    top1_file = str(ranked_files[0].get("file", ""))
    ratio = top_score_ratio(ranked_files)
    reasons: list[str] = []

    if ratio is not None and ratio <= score_ratio_threshold:
        reasons.append(f"low_score_ratio<={score_ratio_threshold:g}")

    bug_report = bug.get("bug_report", {})
    if not isinstance(bug_report, dict):
        bug_report = {}
    text = "\n".join(
        [
            str(bug_report.get("id", "")),
            str(bug_report.get("text", "")),
            str(bug.get("test_failure", "")),
            str(bug.get("stack_trace", "")),
        ]
    )
    mismatch = domain_mismatch_reason(text, top1_file)
    if mismatch:
        reasons.append(mismatch)

    management_reason = management_command_reason(text, top1_file)
    if management_reason:
        reasons.append(management_reason)

    if not reasons:
        return None

    return {
        "bug_id": prediction["bug_id"],
        "reasons": reasons,
        "top1_file": top1_file,
        "top2_file": ranked_files[1].get("file") if len(ranked_files) > 1 else None,
        "score_ratio": ratio,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Select AboutWork rerank candidates.")
    parser.add_argument("--bugs", type=Path, required=True)
    parser.add_argument("--pred", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--score-ratio-threshold", type=float, default=1.02)
    parser.add_argument("--ids-only", action="store_true")
    args = parser.parse_args()

    bugs = {record["bug_id"]: record for record in read_jsonl(args.bugs)}
    predictions = read_jsonl(args.pred)
    selected = [
        item
        for prediction in predictions
        if (
            item := select_record(
                bugs[str(prediction["bug_id"])],
                prediction,
                score_ratio_threshold=args.score_ratio_threshold,
            )
        )
    ]
    payload = {
        "input": str(args.pred),
        "criteria": {
            "score_ratio_threshold": args.score_ratio_threshold,
            "include_management_command_followup_context": True,
            "include_domain_mismatch": True,
        },
        "summary": {
            "records": len(predictions),
            "selected": len(selected),
            "selected_fraction": len(selected) / len(predictions) if predictions else 0.0,
        },
        "selected_bug_ids": [item["bug_id"] for item in selected],
        "selected": selected,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.ids_only:
        print(",".join(payload["selected_bug_ids"]))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
