# AboutWork Committed-60 Dataset Update

Date: 2026-06-08

This note records the implemented first-batch git-history supplement for:

```text
/Users/jin/capi_project/aboutwork/COMPANY_BUG_LOG.md
```

The current AboutWork committed dataset now contains 60 file-level records.

## Version Change

| Dataset | Records | Status |
|---|---:|---|
| `data/aboutwork/aboutwork_committed_39.jsonl` | 39 | Original thesis AboutWork dataset |
| `data/aboutwork/aboutwork_committed_54.jsonl` | 54 | Superseded updated buglog rebuild |
| `data/aboutwork/aboutwork_committed_60.jsonl` | 60 | Current updated AboutWork dataset |

Relative to committed-54, committed-60 adds 6 clean git-history records. Relative
to the original committed-39 thesis dataset, it adds 21 records.

## Added Records Since Committed-54

| Bug ID | Title | Repo | Ground Truth Files | Correct BM25 Rank |
|---|---|---|---|---:|
| `aboutwork-20260605-001` | Refreshed Firebase tokens are rejected because expiry checks use auth_time | backend | `backend/user/authentication.py` | 2 |
| `aboutwork-20260602-001` | Fernet initialization fails when SECRET_KEY is not a valid Fernet key length | backend | `backend/backend/cryptography.py` | 1 |
| `aboutwork-20260603-003` | Public invite and enrollment endpoints return server errors for invalid or incomplete request paths | backend | `backend/organization/views.py`, `backend/path/views.py` | 3 |
| `aboutwork-20260605-002` | HR document chunks exceed Bedrock/Cohere input length and are dropped during indexing | backend | `backend/documents/indexing.py` | 1 |
| `aboutwork-20260605-003` | Editing date-of-birth fields can show multiple update toasts for one change | frontend | `src/components/forms/modalForms/customDate.tsx`, `src/components/workforce/people/peopleDetails/EditableField.tsx`, `src/components/workforce/people/peopleDetails/sub/AboutComponent.tsx` | 2 |
| `aboutwork-20260526-013` | Global search fails because search APIs and icons are not correctly imported | frontend | `src/components/GlobalSearch.tsx`, `src/api/org_resources/org_resources_requests.ts`, `src/components/forms/modalForms/modalSelect.tsx` | 1 |

## Generated Files

```text
data/aboutwork/aboutwork_committed_60.jsonl
outputs/aboutwork_committed_60_bm25_top50.jsonl
outputs/aboutwork_committed_60_bm25_top50_eval.json
outputs/aboutwork60_selector_v3.json
outputs/aboutwork_committed_60_rerank_deepseek_selector_v3.jsonl
outputs/aboutwork_committed_60_bm25_plus_deepseek_selector_v3.jsonl
outputs/aboutwork_committed_60_bm25_plus_deepseek_selector_v3_eval.json
outputs/aboutwork_committed_60_rerank_deepseek_selector_v3_usage.json
outputs/aboutwork_committed_60_agentic_deepseek_selector_v3_s2.jsonl
outputs/aboutwork_committed_60_agentic_deepseek_selector_v3_s2_trace.jsonl
outputs/aboutwork_committed_60_agentic_deepseek_selector_v3_s2_usage.json
outputs/aboutwork_committed_60_bm25_plus_agentic_deepseek_selector_v3_s2_eval.json
outputs/aboutwork_committed_60_agentic_plus_verifier_deepseek_selector_v3_s2.jsonl
outputs/aboutwork_committed_60_agentic_plus_verifier_deepseek_selector_v3_s2_usage.json
outputs/aboutwork_committed_60_bm25_plus_agentic_verifier_deepseek_selector_v3_s2_eval.json
docs/aboutwork_buglog_supplement_entries_2026-06-08.md
docs/aboutwork_committed_60_rerank_results_2026-06-08.md
docs/aboutwork_committed_60_agentic_verifier_results_2026-06-08.md
```

The source candidate scan is documented in:

```text
docs/aboutwork_git_history_supplement_candidates_2026-06-08.md
```

## BM25 and Selective Rerank Validation

DeepSeek/selective rerank has now been rerun on committed-60 using the same
AboutWork `selector_v3` family as the earlier committed-39 experiment:

```text
score_ratio_threshold = 1.02
selected = 16 / 60
provider = deepseek
model = deepseek-v4-flash
top_candidates = 50
top_output = 10
```

| Dataset | Bugs | Top-1 | Top-3 | Top-5 | Top-10 | Top-50 | MRR |
|---|---:|---:|---:|---:|---:|---:|---:|
| AboutWork committed-54 BM25 top50 | 54 | 0.5741 | 0.8148 | 0.9074 | 0.9259 | 1.0000 | 0.6991 |
| AboutWork committed-60 BM25 top50 | 60 | 0.5667 | 0.8333 | 0.9167 | 0.9333 | 1.0000 | 0.7015 |
| AboutWork committed-60 BM25 + selector_v3 + DeepSeek | 60 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | n/a | 0.8117 |
| AboutWork committed-60 BM25 + selector_v3 + agentic DeepSeek s2 | 60 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | n/a | 0.8117 |
| AboutWork committed-60 BM25 + selector_v3 + agentic s2 + verifier | 60 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | n/a | 0.8117 |

Selected-case behavior on committed-60:

| Subset | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|
| BM25 selected subset | 7 / 16 | 9 / 16 | 13 / 16 | 14 / 16 | 0.5486 |
| DeepSeek selected subset | 15 / 16 | 16 / 16 | 16 / 16 | 16 / 16 | 0.9688 |

Remaining Top-10 misses:

| Bug ID | Ground Truth | BM25 Rank | Final Rank | Note |
|---|---|---:|---:|---|
| `aboutwork-20260528-002` | `backend/chatbot_v2/planning.py` | 14 | n/a | selector false negative |
| `aboutwork-20260603-001` | `backend/opensearch/connectors.py` | 26 | n/a | selector false negative |

Per-record BM25 ranks for the 6 added records:

| Bug ID | Correct Rank | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---|---|---|---|---:|
| `aboutwork-20260605-001` | 2 | false | true | true | true | 0.5000 |
| `aboutwork-20260602-001` | 1 | true | true | true | true | 1.0000 |
| `aboutwork-20260603-003` | 3 | false | true | true | true | 0.3333 |
| `aboutwork-20260605-002` | 1 | true | true | true | true | 1.0000 |
| `aboutwork-20260605-003` | 2 | false | true | true | true | 0.5000 |
| `aboutwork-20260526-013` | 1 | true | true | true | true | 1.0000 |

## Interpretation

The added records are clean and not unusually hard for lexical retrieval: all 6
are within BM25 Top-3. The committed-60 selective rerank result is now the
current AboutWork RQ4 result. It improves over BM25 on every reported metric
while calling DeepSeek on 16/60 records. The main remaining AboutWork weakness is
selector recall: both final Top-10 misses were unselected records rather than
selected-case DeepSeek ranking failures.
