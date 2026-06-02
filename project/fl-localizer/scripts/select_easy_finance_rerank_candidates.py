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


BACKEND_AREA_MISMATCH_AREAS = {"bookkeeping", "reports"}
COMMAND_CONTEXT_TERMS = ("command", "management command", "script", "cli")


def top_score_ratio(ranked_files: list[dict[str, Any]]) -> float | None:
    if len(ranked_files) < 2:
        return None
    top1_score = float(ranked_files[0].get("score", 0.0) or 0.0)
    top2_score = float(ranked_files[1].get("score", 0.0) or 0.0)
    if top2_score <= 0:
        return None
    return top1_score / top2_score


def bug_text(record: dict[str, Any]) -> str:
    bug_report = record.get("bug_report", {})
    if not isinstance(bug_report, dict):
        bug_report = {}
    extra_context = record.get("extra_context", {})
    if not isinstance(extra_context, dict):
        extra_context = {}
    return "\n".join(
        [
            str(bug_report.get("id", "")),
            str(bug_report.get("text", "")),
            str(record.get("test_failure", "")),
            str(record.get("stack_trace", "")),
            str(extra_context.get("area", "")),
        ]
    ).lower()


def area_for(record: dict[str, Any]) -> str:
    extra_context = record.get("extra_context", {})
    if not isinstance(extra_context, dict):
        return ""
    return str(extra_context.get("area", "")).strip().lower()


def backend_reasons(text: str, area: str, top1_file: str) -> list[str]:
    reasons: list[str] = []

    if area in BACKEND_AREA_MISMATCH_AREAS and f"/{area}/" not in top1_file:
        reasons.append(f"backend_area_mismatch:{area}")

    if "/management/commands/" in top1_file and not any(term in text for term in COMMAND_CONTEXT_TERMS):
        reasons.append("backend_management_command_noise")

    if "admin" in text and "invoice" in text:
        top1_is_admin_invoice = "/invoice/" in top1_file and (
            "admin" in top1_file or "views_admin" in top1_file
        )
        if not top1_is_admin_invoice:
            reasons.append("backend_admin_invoice_mismatch")

    return reasons


def frontend_reasons(text: str, top1_file: str) -> list[str]:
    reasons: list[str] = []

    if "admin" in text and "unreviewed" in text:
        if "/admin/" not in top1_file or "homedashboard" in top1_file:
            reasons.append("frontend_admin_unreviewed_mismatch")

    if "chat history" in text or ("skeleton" in text and "chat" in text):
        if "/pages/aichat/" not in top1_file or "table" not in top1_file:
            reasons.append("frontend_chat_history_mismatch")

    if "admin user" in text or "user filtering" in text or ("users" in text and "filter" in text):
        if "/users/" not in top1_file:
            reasons.append("frontend_admin_users_mismatch")

    if "invoice ui" in text and ("dollars" in text or "euros" in text):
        if "/invoices/" not in top1_file:
            reasons.append("frontend_invoice_currency_mismatch")

    if "expense form" in text:
        if "/expenses/" not in top1_file and "/admin/expenses/" not in top1_file:
            reasons.append("frontend_expense_form_mismatch")

    if "confirm" in text and "loading" in text and "expense" in text and "invoice" in text:
        if not ("expense" in top1_file and "invoice" in top1_file):
            reasons.append("frontend_confirm_multidomain_loading")

    return reasons


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
    lowered_top1 = top1_file.lower()
    text = bug_text(bug)
    area = area_for(bug)
    ratio = top_score_ratio(ranked_files)
    reasons: list[str] = []

    if score_ratio_threshold > 0 and ratio is not None and ratio <= score_ratio_threshold:
        reasons.append(f"low_score_ratio<={score_ratio_threshold:g}")

    project = str(bug.get("project", "")).lower()
    if "backend" in project:
        reasons.extend(backend_reasons(text, area, lowered_top1))
    else:
        reasons.extend(frontend_reasons(text, lowered_top1))

    if not reasons:
        return None

    return {
        "bug_id": prediction["bug_id"],
        "reasons": reasons,
        "area": area,
        "project": bug.get("project", ""),
        "top1_file": top1_file,
        "top2_file": ranked_files[1].get("file") if len(ranked_files) > 1 else None,
        "top5_files": [item.get("file") for item in ranked_files[:5]],
        "score_ratio": ratio,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Select Easy Finance rerank candidates.")
    parser.add_argument("--bugs", type=Path, required=True, help="Bug JSONL input")
    parser.add_argument("--pred", type=Path, required=True, help="BM25 prediction JSONL input")
    parser.add_argument("--out", type=Path, required=True, help="Selection report JSON output")
    parser.add_argument(
        "--score-ratio-threshold",
        type=float,
        default=0.0,
        help="Optional score-ratio ambiguity threshold. Use 0 to disable.",
    )
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
            "score_ratio_enabled": args.score_ratio_threshold > 0,
            "backend_area_mismatch_areas": sorted(BACKEND_AREA_MISMATCH_AREAS),
            "include_backend_management_command_noise": True,
            "include_backend_admin_invoice_mismatch": True,
            "include_frontend_admin_unreviewed_mismatch": True,
            "include_frontend_chat_history_mismatch": True,
            "include_frontend_admin_users_mismatch": True,
            "include_frontend_invoice_currency_mismatch": True,
            "include_frontend_expense_form_mismatch": True,
            "include_frontend_confirm_multidomain_loading": True,
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
