#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fl_localizer.io_utils import write_jsonl


CANDIDATE_RE = re.compile(r"^\| (?P<bug_id>easyfinance-(?P<repo>backend|frontend)-\d{8}-\d{3}) \|")
BACKTICK_RE = re.compile(r"`([^`]+)`")


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def git_path_exists(repo: Path, commit: str, path: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{commit}:{path}"],
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def split_table_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def parse_candidates(path: Path) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    quality = ""
    repo_section = ""

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "## Priority Candidates":
            quality = "priority"
            continue
        if stripped == "## Expanded Usable Candidates":
            quality = "expanded"
            continue
        if stripped == "## Secondary Candidates":
            quality = "secondary"
            continue
        if stripped == "### Backend" or stripped == "### Backend Additions":
            repo_section = "backend"
            continue
        if stripped == "### Frontend" or stripped == "### Frontend Additions":
            repo_section = "frontend"
            continue

        match = CANDIDATE_RE.match(stripped)
        if not match:
            continue
        columns = split_table_row(stripped)
        if len(columns) < 7:
            raise ValueError(f"Unexpected candidate row: {line}")

        bug_id, commit_raw, date, seed, files_raw, size, notes = columns[:7]
        commit_values = BACKTICK_RE.findall(commit_raw)
        if not commit_values:
            raise ValueError(f"Missing commit in row: {line}")
        files = BACKTICK_RE.findall(files_raw)
        if not files:
            raise ValueError(f"Missing ground-truth files in row: {line}")
        repo = match.group("repo") or repo_section
        candidates.append(
            {
                "bug_id": bug_id,
                "repo": repo,
                "quality": quality,
                "date": date,
                "commit": commit_values[0],
                "bug_text_seed": seed,
                "ground_truth_files": files,
                "size": size,
                "notes": notes,
            }
        )
    return candidates


def make_worktree(repo: Path, workspace_root: Path, bug_id: str, repo_name: str, commit: str) -> Path:
    path = workspace_root / f"{bug_id}_{repo_name}_{commit[:12]}"
    if path.exists():
        existing = run_git(path, "rev-parse", "HEAD")
        if existing != commit:
            raise RuntimeError(f"Existing worktree {path} is at {existing}, expected {commit}")
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    run_git(repo, "worktree", "add", "--detach", str(path), commit)
    return path


def infer_area(repo_name: str, files: list[str]) -> str:
    if not files:
        return repo_name
    path = Path(files[0])
    parts = path.parts
    if repo_name == "backend" and len(parts) >= 2:
        return parts[1]
    if repo_name == "frontend":
        try:
            src_index = parts.index("src")
            if len(parts) > src_index + 1:
                return parts[src_index + 1]
        except ValueError:
            pass
    return repo_name


def source_dir_for(repo_name: str) -> str:
    if repo_name == "backend":
        return "easy_finance_backend"
    if repo_name == "frontend":
        return "easy_finance_frontend/src"
    raise ValueError(f"Unknown repo: {repo_name}")


def build_record(
    candidate: dict[str, Any],
    *,
    backend_repo: Path,
    frontend_repo: Path,
    workspace_root: Path,
    create_worktrees: bool,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    repo_name = str(candidate["repo"])
    source_repo = backend_repo if repo_name == "backend" else frontend_repo
    bug_id = str(candidate["bug_id"])

    try:
        fixed_commit = run_git(source_repo, "rev-parse", f"{candidate['commit']}^{{commit}}")
        buggy_commit = run_git(source_repo, "rev-parse", f"{fixed_commit}^")
    except subprocess.CalledProcessError as exc:
        return None, {
            "bug_id": bug_id,
            "reason": "commit_not_found_or_no_parent",
            "detail": str(exc),
        }

    existing_ground_truth: list[str] = []
    added_or_missing_ground_truth: list[str] = []
    for file_path in candidate["ground_truth_files"]:
        if git_path_exists(source_repo, buggy_commit, file_path):
            existing_ground_truth.append(file_path)
        else:
            added_or_missing_ground_truth.append(file_path)

    if not existing_ground_truth:
        return None, {
            "bug_id": bug_id,
            "reason": "no_ground_truth_file_exists_in_buggy_commit",
            "fixed_commit": fixed_commit,
            "buggy_commit": buggy_commit,
            "ground_truth_files": candidate["ground_truth_files"],
        }

    repo_path = (
        make_worktree(source_repo, workspace_root, bug_id, repo_name, buggy_commit)
        if create_worktrees
        else source_repo
    )

    if create_worktrees:
        missing_after_checkout = [
            file_path for file_path in existing_ground_truth if not (repo_path / file_path).exists()
        ]
        if missing_after_checkout:
            return None, {
                "bug_id": bug_id,
                "reason": "ground_truth_file_missing_after_worktree_checkout",
                "repo_path": str(repo_path),
                "ground_truth_files": missing_after_checkout,
            }

    area = infer_area(repo_name, existing_ground_truth)
    seed = str(candidate["bug_text_seed"])
    report_text = "\n\n".join(
        [
            f"Title: {seed}",
            f"Area: {area}",
            "Observed behavior:\n" + seed,
            "Expected behavior:\nThe affected Easy Finance workflow should complete with the intended data, navigation, loading, or display behavior.",
        ]
    )

    return {
        "bug_id": bug_id,
        "project": f"EasyFinance-{repo_name}",
        "bug_report": {
            "id": seed,
            "url": str(ROOT / "docs" / "easy_finance_candidate_bugfixes.md"),
            "text": report_text,
        },
        "test_failure": "",
        "triggering_tests": [],
        "stack_trace": "",
        "repo_path": str(repo_path),
        "source_dir": source_dir_for(repo_name),
        "buggy_commit": buggy_commit,
        "fixed_commit": fixed_commit,
        "ground_truth": {
            "classes": [],
            "files": existing_ground_truth,
            "methods": [],
        },
        "extra_context": {
            "area": area,
            "date": candidate["date"],
            "repo": repo_name,
            "quality": candidate["quality"],
            "size": candidate["size"],
            "notes": candidate["notes"],
            "source": "Easy Finance git-history candidate list",
            "fixed_commit_message_seed": seed,
            "excluded_ground_truth_files_not_in_buggy_commit": added_or_missing_ground_truth,
            "leakage_note": "Bug text was inferred from git commit metadata; fix commit and ground truth are for evaluation only.",
        },
    }, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Easy Finance git-history bug JSONL dataset.")
    parser.add_argument(
        "--candidates",
        type=Path,
        default=ROOT / "docs" / "easy_finance_candidate_bugfixes.md",
        help="Candidate bug-fix markdown file",
    )
    parser.add_argument(
        "--easy-finance-root",
        type=Path,
        default=Path("/Users/jin/capi_project/easy_finance"),
        help="Easy Finance project root containing backend and frontend git repos",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=ROOT.parent / "workspaces" / "easy_finance",
        help="Directory for detached buggy-commit worktrees",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "data" / "easy_finance" / "easy_finance_committed.jsonl",
        help="Output JSONL path",
    )
    parser.add_argument("--report", type=Path, help="Skip/build report JSON output")
    parser.add_argument(
        "--qualities",
        default="priority,expanded",
        help="Comma-separated candidate qualities to include, e.g. priority,expanded",
    )
    parser.add_argument("--limit", type=int, help="Maximum number of valid records to write")
    parser.add_argument(
        "--create-worktrees",
        action="store_true",
        help="Create detached git worktrees at each buggy parent commit and use them as repo_path.",
    )
    args = parser.parse_args()

    backend_repo = args.easy_finance_root / "easy_finance_backend"
    frontend_repo = args.easy_finance_root / "easy_finance_frontend"
    wanted_qualities = {part.strip() for part in args.qualities.split(",") if part.strip()}

    records: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for candidate in parse_candidates(args.candidates):
        if candidate["quality"] not in wanted_qualities:
            continue
        record, skip = build_record(
            candidate,
            backend_repo=backend_repo,
            frontend_repo=frontend_repo,
            workspace_root=args.workspace_root,
            create_worktrees=args.create_worktrees,
        )
        if skip is not None:
            skipped.append(skip)
            continue
        assert record is not None
        records.append(record)
        if args.limit is not None and len(records) >= args.limit:
            break

    write_jsonl(args.out, records)
    report_path = args.report or args.out.with_suffix(".report.json")
    report = {
        "input": str(args.candidates),
        "output": str(args.out),
        "qualities": sorted(wanted_qualities),
        "create_worktrees": args.create_worktrees,
        "records": len(records),
        "skipped": len(skipped),
        "skipped_records": skipped,
        "by_repo": {
            repo: sum(1 for record in records if record["extra_context"]["repo"] == repo)
            for repo in ("backend", "frontend")
        },
        "by_quality": {
            quality: sum(1 for record in records if record["extra_context"]["quality"] == quality)
            for quality in sorted(wanted_qualities)
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Wrote {len(records)} Easy Finance bug record(s) to {args.out}")
    print(f"Wrote report to {report_path}")
    print(f"Skipped {len(skipped)} candidate(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
