# AboutWork Committed-54 Dataset Update

Date: 2026-06-08

Superseded note: this update was superseded by the current committed-60 dataset
after adding 6 clean git-history records. Current note:

```text
docs/aboutwork_committed_60_update_2026-06-08.md
```

This note records a second read of the updated company bug log:

```text
/Users/jin/capi_project/aboutwork/COMPANY_BUG_LOG.md
```

The previous `AboutWork committed-40` file was a provisional one-record update.
After re-reading the updated log with the dataset builder, the committed
file-level dataset now contains 54 records.

## Version Change

| Dataset | Records | Status |
|---|---:|---|
| `data/aboutwork/aboutwork_committed_39.jsonl` | 39 | Original thesis AboutWork dataset |
| `data/aboutwork/aboutwork_committed_40.jsonl` | 40 | Provisional update; superseded by committed-54 |
| `data/aboutwork/aboutwork_committed_54.jsonl` | 54 | Current updated AboutWork dataset |

Relative to committed-40, committed-54 adds 14 records. Relative to the original
committed-39 thesis dataset, it adds 15 records: the 14 records below plus the
previously added `aboutwork-20260603-001`.

## Added Records Since Committed-40

| Bug ID | Title | Repo | Ground Truth Files | Buggy Commit | Fixed Commit |
|---|---|---|---|---|---|
| `aboutwork-20260526-001` | Admin to-do attendance typo and generic task words miss matching reminders | backend | backend/chatbot_v2/admin_tools.py, backend/chatbot_v2/admin_continuation.py | `9d89e8ed4824` | `6257615ba78f` |
| `aboutwork-20260526-002` | Admin write action cards display weak result and refresh too little data | frontend | src/components/ai-chat-v2/AIChatV2ActionCard.tsx, src/api/ai-chat-v2/aiChatV2.ts | `464fe514e334` | `cb0d53d73faf` |
| `aboutwork-20260526-003` | Admin evaluation reminder misses lowercase non-possessive employee phrasing | backend | backend/chatbot_v2/admin_action_drafts.py | `20ad0a67eeae` | `d7408498e708` |
| `aboutwork-20260526-006` | User HR policy question is misrouted as schedule setup | backend | backend/chatbot_v2/action_drafts.py, backend/chatbot_v2/schedule_action_drafts.py, backend/chatbot_v2/leave_action_drafts.py, backend/chatbot_v2/router.py, backend/chatbot_v2/orchestrator.py, backend/chatbot_v2/continuation.py | `6257615ba78f` | `f6660ed99827` |
| `aboutwork-20260526-007` | Q&A prompts are misrouted to unrelated data summaries | backend | backend/chatbot_v2/router.py, backend/chatbot_v2/action_drafts.py, backend/chatbot_v2/smart_slot_extractor.py, backend/chatbot_v2/admin_router.py, backend/chatbot_v2/admin_smart_slot_extractor.py, backend/chatbot_v2/orchestrator.py | `6257615ba78f` | `f6660ed99827` |
| `aboutwork-20260526-008` | Q&A classifier blocks admin workforce and asset lookups | backend | backend/chatbot_v2/admin_router.py | `6257615ba78f` | `f6660ed99827` |
| `aboutwork-20260526-010` | HR knowledge Q&A can retrieve employee personal documents as sources | backend | backend/chatbot_v2/retriever.py, backend/chatbot_v2/orchestrator.py | `601cacde6ae0` | `459d58737d3f` |
| `aboutwork-20260526-011` | Personal signing document questions route as HR knowledge Q&A | backend | backend/chatbot_v2/user_hr_knowledge.py | `601cacde6ae0` | `459d58737d3f` |
| `aboutwork-20260526-012` | Date-specific remote/leave questions route as HR policy Q&A | backend | backend/chatbot_v2/user_hr_knowledge.py | `601cacde6ae0` | `459d58737d3f` |
| `aboutwork-20260527-001` | Personal profile value questions route to handbook Q&A | backend | backend/chatbot_v2/user_hr_knowledge.py, backend/chatbot_v2/orchestrator.py, backend/chatbot_v2/action_drafts.py | `459d58737d3f` | `b27324cb9632` |
| `aboutwork-20260527-002` | Handbook QA retrieves weak excerpts or routes statutory leave as profile data | backend | backend/chatbot_v2/retriever.py, backend/chatbot_v2/user_hr_knowledge.py | `332682eea059` | `3654c6212e0a` |
| `aboutwork-20260528-001` | HR QA fallback exposes specific HR contact details | backend | backend/chatbot_v2/orchestrator.py, backend/chatbot_v2/user_hr_knowledge.py | `6101c4754209` | `2628007d9025` |
| `aboutwork-20260528-002` | User pending planning requests are missing from chatbot planning answers | backend | backend/chatbot_v2/planning.py | `6101c4754209` | `2628007d9025` |
| `aboutwork-20260601-001` | Admin asset return confirmation crashes on missing updated_at field | backend | backend/chatbot_v2/admin_action_executors.py, backend/chatbot_v2/regression_tests/test_admin_followups.py | `a10c3558f529` | `530b5be0c5c0` |

## Skipped Log Entries

The formal `--create-worktrees` build skipped 4 entries:

| Bug ID | Title | Reason |
|---|---|---|
| `aboutwork-20260526-004` | Stage 5 acceptance references missing frontend component test | Pending documentation-only local note, not a clean committed backend/frontend source-fix record |
| `aboutwork-20260526-005` | Stage 6 acceptance describes team removal as blocked after backend support exists | Pending documentation-only local note, not a clean committed backend/frontend source-fix record |
| `aboutwork-20260601-002` | Admin follow-up regression tests depended on Bedrock and an expired fixed deadline | Pending local changes, not committed yet |
| `aboutwork-20260603-002` | HR RAG returns no sources because OpenSearch FGAC has no master user | Environment/OpenSearch FGAC configuration entry, not a clean source-file-only localization sample |

## Data Cleaning Rules Added

The builder now applies stricter file-level dataset hygiene:

- Only source-like ground-truth paths are kept.
- Non-file ground-truth notes are excluded, for example local regression coverage notes and AWS/IAM configuration notes.
- `backend/backend/...` paths are remapped to `backend/...` only when the original path is absent and the remapped path exists in the buggy worktree.
- Ground-truth files added only by the fixed commit are excluded from evaluation because file-level localization cannot rank a file that is absent in the buggy version.
- Records with no remaining existing buggy-version ground-truth file are skipped.

The cleaning metadata is stored per record in `extra_context`:

```text
excluded_ground_truth_entries
excluded_ground_truth_files_not_in_buggy_commit
ground_truth_path_remaps
```

## Generated Files

```text
data/aboutwork/aboutwork_committed_54.jsonl
outputs/aboutwork_committed_54_bm25_top50.jsonl
outputs/aboutwork_committed_54_bm25_top50_eval.json
```

The buggy worktrees are under:

```text
/Users/jin/llm_location/project/workspaces/aboutwork
```

## BM25 Validation

This is a BM25-only validation run. DeepSeek/selective rerank has not yet been
rerun on committed-54.

| Dataset | Bugs | Top-1 | Top-3 | Top-5 | Top-10 | Top-50 | MRR |
|---|---:|---:|---:|---:|---:|---:|---:|
| AboutWork committed-39 BM25 top50 | 39 | 0.5897 | 0.8462 | 0.9487 | 0.9487 | 1.0000 | 0.7171 |
| AboutWork committed-40 BM25 top50 | 40 | 0.5750 | 0.8500 | 0.9500 | 0.9500 | 1.0000 | 0.7075 |
| AboutWork committed-54 BM25 top50 | 54 | 0.5741 | 0.8148 | 0.9074 | 0.9259 | 1.0000 | 0.6991 |

Per-record BM25 ranks for the 14 records added after committed-40:

| Bug ID | Correct Rank | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---|---|---|---|---:|
| `aboutwork-20260526-001` | 5 | false | false | true | true | 0.2000 |
| `aboutwork-20260526-002` | 1 | true | true | true | true | 1.0000 |
| `aboutwork-20260526-003` | 3 | false | true | true | true | 0.3333 |
| `aboutwork-20260526-006` | 1 | true | true | true | true | 1.0000 |
| `aboutwork-20260526-007` | 1 | true | true | true | true | 1.0000 |
| `aboutwork-20260526-008` | 7 | false | false | false | true | 0.1429 |
| `aboutwork-20260526-010` | 2 | false | true | true | true | 0.5000 |
| `aboutwork-20260526-011` | 1 | true | true | true | true | 1.0000 |
| `aboutwork-20260526-012` | 2 | false | true | true | true | 0.5000 |
| `aboutwork-20260527-001` | 1 | true | true | true | true | 1.0000 |
| `aboutwork-20260527-002` | 1 | true | true | true | true | 1.0000 |
| `aboutwork-20260528-001` | 1 | true | true | true | true | 1.0000 |
| `aboutwork-20260528-002` | 14 | false | false | false | false | 0.0714 |
| `aboutwork-20260601-001` | 1 | true | true | true | true | 1.0000 |

The earlier `aboutwork-20260603-001` record remains included in committed-54.
Its BM25 rank in the committed-54 rebuild is 26. This differs from the earlier
manual committed-40 note because the automatic builder uses the standardized
bug-report fields from the log rather than the manually drafted report text.

## Interpretation

Committed-54 is the current updated AboutWork dataset, but it is not yet a new
thesis result table. The already reported AboutWork-39 DeepSeek/selective-rerank
numbers remain the thesis numbers until downstream rerank experiments are
explicitly rerun on committed-54.
