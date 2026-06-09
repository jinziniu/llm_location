# AboutWork Committed-40 Dataset Update

Date: 2026-06-08

Superseded note: this was a provisional one-record update. The current updated
dataset is now documented in:

```text
docs/aboutwork_committed_60_update_2026-06-08.md
```

This note records a dataset-only update from:

```text
/Users/jin/capi_project/aboutwork/COMPANY_BUG_LOG.md
```

## Added Record

Added one clean file-level committed record:

| Bug ID | Title | Buggy Commit | Fixed Commit | Ground Truth File |
|---|---|---|---|---|
| `aboutwork-20260603-001` | Local/staging chatbot LLM calls fail with Bedrock InvokeModel access denied | `4954da19ab9a89dff1a72bff4112e4d1735d633f` | `cee869746be89900fae1a48dc9d566b2dee5200b` | `backend/opensearch/connectors.py` |

The buggy source is checked out at:

```text
/Users/jin/llm_location/project/workspaces/aboutwork/aboutwork-20260603-001_backend_4954da19ab9a
```

## New Files

```text
data/aboutwork/aboutwork_committed_40.jsonl
outputs/aboutwork_committed_40_bm25_top50.jsonl
outputs/aboutwork_committed_40_bm25_top50_eval.json
```

The original thesis dataset remains unchanged:

```text
data/aboutwork/aboutwork_committed_39.jsonl
```

## Excluded New Log Entries

The current log has 19 entries that are not included by the committed-dataset
builder because they are pending, incomplete, documentation/test-infrastructure
samples, or not clean file-level localization samples.

Most new product entries still say:

```text
Fix commit:
- pending ...
```

`aboutwork-20260603-002` is also excluded for now because the entry is an
OpenSearch FGAC/environment configuration fix and currently lacks the complete
standard localization fields (`Expected behavior`, `Trigger`, `Failure
evidence`, `Fix commit`, and clean source-file-only ground truth).

## Baseline Validation

Simple BM25 top50 was run on the new 40-record dataset:

| Dataset | Bugs | Top-1 | Top-3 | Top-5 | Top-10 | Top-50 | MRR |
|---|---:|---:|---:|---:|---:|---:|---:|
| AboutWork committed-39 BM25 top50 | 39 | 0.5897 | 0.8462 | 0.9487 | 0.9487 | 1.0000 | 0.7171 |
| AboutWork committed-40 BM25 top50 | 40 | 0.5750 | 0.8500 | 0.9500 | 0.9500 | 1.0000 | 0.7075 |

For the added case:

| Bug ID | Correct Rank | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---|---|---|---:|
| `aboutwork-20260603-001` | 3 | true | true | true | 0.3333 |

## Interpretation

This is a dataset update, not a replacement for the thesis AboutWork-39 result.
Use AboutWork-40 for future validation runs after explicitly stating the updated
dataset version. Keep the already reported thesis tables on AboutWork-39 unless
the downstream BM25/selective rerank/DeepSeek experiments are rerun on the new
40-record dataset.
