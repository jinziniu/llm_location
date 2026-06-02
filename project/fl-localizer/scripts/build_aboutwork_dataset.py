#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fl_localizer.io_utils import write_jsonl


HEADING_RE = re.compile(r"^### (?P<date>\d{4}-\d{2}-\d{2}) - (?P<title>.+)$", re.MULTILINE)
FIELD_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 /_-]*:\s*$")
COMMIT_RE = re.compile(r"\b[0-9a-f]{7,40}\b")


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def split_entries(markdown: str) -> list[dict[str, str]]:
    matches = list(HEADING_RE.finditer(markdown))
    entries: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        title = match.group("title").strip()
        if title == "Short Bug Title":
            continue
        entries.append(
            {
                "date": match.group("date"),
                "title": title,
                "body": markdown[start:end],
            }
        )
    return entries


def field_lines(body: str, label: str) -> list[str]:
    lines = body.splitlines()
    target = f"{label}:"
    for index, line in enumerate(lines):
        if line.strip() != target:
            continue
        collected: list[str] = []
        for next_line in lines[index + 1 :]:
            stripped = next_line.strip()
            if stripped.startswith("### "):
                break
            if FIELD_RE.match(stripped) and collected:
                break
            collected.append(next_line)
        return collected
    return []


def clean_markdown_lines(lines: list[str]) -> str:
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("```"):
            continue
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        stripped = stripped.strip("`")
        cleaned.append(stripped)
    return "\n".join(cleaned).strip()


def first_backtick_value(body: str, label: str) -> str:
    text = clean_markdown_lines(field_lines(body, label))
    match = re.search(r"`([^`]+)`", text)
    if match:
        return match.group(1).strip()
    return text.splitlines()[0].strip() if text else ""


def bullet_values(body: str, label: str) -> list[str]:
    values: list[str] = []
    for line in field_lines(body, label):
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        value = stripped[2:].strip().strip("`")
        if value:
            values.append(value)
    return values


def section_text(body: str, *labels: str) -> str:
    parts: list[str] = []
    for label in labels:
        text = clean_markdown_lines(field_lines(body, label))
        if text:
            parts.append(text)
    return "\n\n".join(parts).strip()


def infer_repo(fix_line: str, ground_truth_files: list[str], backend_repo: Path, frontend_repo: Path) -> str | None:
    lowered = fix_line.lower()
    if "frontend" in lowered:
        return "frontend"
    if "backend" in lowered:
        return "backend"

    if ground_truth_files and all(path.startswith(("src/", "frontend/src/")) for path in ground_truth_files):
        return "frontend"
    if ground_truth_files and all(path.startswith(("backend/", "backend/backend/")) for path in ground_truth_files):
        return "backend"

    commit_match = COMMIT_RE.search(fix_line)
    if commit_match:
        commit = commit_match.group(0)
        for repo_name, repo_path in (("backend", backend_repo), ("frontend", frontend_repo)):
            try:
                run_git(repo_path, "rev-parse", "--verify", f"{commit}^{{commit}}")
                return repo_name
            except subprocess.CalledProcessError:
                continue
    return None


def normalize_ground_truth_file(path: str, repo_name: str) -> str:
    normalized = path.strip().strip("`")
    if repo_name == "frontend" and normalized.startswith("frontend/"):
        return normalized.removeprefix("frontend/")
    return normalized


def make_worktree(repo: Path, workspace_root: Path, bug_id: str, repo_name: str, commit: str) -> Path:
    short = commit[:12]
    path = workspace_root / f"{bug_id}_{repo_name}_{short}"
    if path.exists():
        existing = run_git(path, "rev-parse", "HEAD")
        if existing != commit:
            raise RuntimeError(f"Existing worktree {path} is at {existing}, expected {commit}")
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    run_git(repo, "worktree", "add", "--detach", str(path), commit)
    return path


def build_record(
    entry: dict[str, str],
    *,
    backend_repo: Path,
    frontend_repo: Path,
    workspace_root: Path,
    create_worktrees: bool,
) -> dict[str, Any] | None:
    body = entry["body"]
    bug_id = first_backtick_value(body, "Bug id")
    if not bug_id or "YYYY" in bug_id:
        return None

    fix_text = clean_markdown_lines(field_lines(body, "Fix commit"))
    if not fix_text or "pending" in fix_text.lower() or "not committed" in fix_text.lower():
        return None
    commit_match = COMMIT_RE.search(fix_text)
    if not commit_match:
        return None
    fixed_short = commit_match.group(0)

    ground_truth_raw = bullet_values(body, "Ground truth files")
    if not ground_truth_raw:
        return None

    repo_name = infer_repo(fix_text, ground_truth_raw, backend_repo, frontend_repo)
    if repo_name is None:
        return None

    source_repo = backend_repo if repo_name == "backend" else frontend_repo
    fixed_commit = run_git(source_repo, "rev-parse", f"{fixed_short}^{{commit}}")
    buggy_commit = run_git(source_repo, "rev-parse", f"{fixed_commit}^")
    repo_path = (
        make_worktree(source_repo, workspace_root, bug_id, repo_name, buggy_commit)
        if create_worktrees
        else source_repo
    )

    observed = section_text(body, "Observed behavior", "Pre-fix observed behavior", "User-visible symptom")
    expected = section_text(body, "Expected behavior")
    trigger = section_text(body, "Trigger")
    evidence = section_text(body, "Failure evidence", "Pre-fix evidence")
    area = clean_markdown_lines(field_lines(body, "Area"))
    ground_truth_files = [
        normalize_ground_truth_file(path, repo_name)
        for path in ground_truth_raw
    ]

    report_text_parts = [
        f"Title: {entry['title']}",
        f"Area: {area}" if area else "",
        "Observed behavior:\n" + observed if observed else "",
        "Expected behavior:\n" + expected if expected else "",
    ]
    bug_report_text = "\n\n".join(part for part in report_text_parts if part)

    return {
        "bug_id": bug_id,
        "project": f"AboutWork-{repo_name}",
        "bug_report": {
            "id": entry["title"],
            "url": str(Path("/Users/jin/capi_project/aboutwork/COMPANY_BUG_LOG.md")),
            "text": bug_report_text,
        },
        "test_failure": trigger,
        "triggering_tests": [line for line in trigger.splitlines() if line.strip()],
        "stack_trace": evidence,
        "repo_path": str(repo_path),
        "source_dir": "backend" if repo_name == "backend" else "src",
        "buggy_commit": buggy_commit,
        "fixed_commit": fixed_commit,
        "ground_truth": {
            "classes": [],
            "files": ground_truth_files,
            "methods": [],
        },
        "extra_context": {
            "area": area,
            "date": entry["date"],
            "repo": repo_name,
            "source": "AboutWork company bug log",
            "leakage_note": "Fix commit metadata and ground truth are for evaluation only.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build AboutWork company bug JSONL dataset.")
    parser.add_argument(
        "--log",
        type=Path,
        default=Path("/Users/jin/capi_project/aboutwork/COMPANY_BUG_LOG.md"),
        help="Company bug log markdown file",
    )
    parser.add_argument(
        "--aboutwork-root",
        type=Path,
        default=Path("/Users/jin/capi_project/aboutwork"),
        help="AboutWork project root containing backend and frontend git repos",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=ROOT.parent / "workspaces" / "aboutwork",
        help="Directory for detached buggy-commit worktrees",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "data" / "aboutwork" / "aboutwork_committed.jsonl",
        help="Output JSONL path",
    )
    parser.add_argument(
        "--create-worktrees",
        action="store_true",
        help="Create detached git worktrees at each buggy parent commit and use them as repo_path.",
    )
    args = parser.parse_args()

    backend_repo = args.aboutwork_root / "backend"
    frontend_repo = args.aboutwork_root / "frontend"
    markdown = args.log.read_text(encoding="utf-8")

    records: list[dict[str, Any]] = []
    skipped = 0
    for entry in split_entries(markdown):
        record = build_record(
            entry,
            backend_repo=backend_repo,
            frontend_repo=frontend_repo,
            workspace_root=args.workspace_root,
            create_worktrees=args.create_worktrees,
        )
        if record is None:
            skipped += 1
            continue
        records.append(record)

    write_jsonl(args.out, records)
    print(f"Wrote {len(records)} AboutWork committed bug record(s) to {args.out}")
    print(f"Skipped {skipped} non-committed/template/incomplete entrie(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
