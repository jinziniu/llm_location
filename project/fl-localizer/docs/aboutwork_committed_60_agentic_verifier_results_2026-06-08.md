# AboutWork Committed-60 Agentic and Verifier Results

Date: 2026-06-08

This note records the RQ5-style extension run on the updated AboutWork
committed-60 dataset.

## Protocol

Dataset:

```text
data/aboutwork/aboutwork_committed_60.jsonl
```

Baseline:

```text
outputs/aboutwork_committed_60_bm25_top50.jsonl
```

Selection:

```text
outputs/aboutwork60_selector_v3.json
selected = 16 / 60
score_ratio_threshold = 1.02
```

Methods:

- One-shot DeepSeek rerank on selected cases.
- Controlled agentic DeepSeek rerank on the same selected cases.
- Verifier DeepSeek rerank over the agentic output and trace.

Agentic configuration:

```text
provider: deepseek
model: deepseek-v4-flash
top_candidates: 50
top_output: 10
max_steps: 2
```

## Aggregate Results

| Method | Selected Records | Model Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|---:|
| BM25 production top50 | 0 / 60 | 0 | 0.5667 | 0.8333 | 0.9167 | 0.9333 | 0.7015 |
| BM25 + selector_v3 + one-shot DeepSeek | 16 / 60 | 16 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 |
| BM25 + selector_v3 + agentic DeepSeek s2 | 16 / 60 | 40 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 |
| BM25 + selector_v3 + agentic s2 + verifier | 16 / 60 | 56 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 |

The correct rank is identical for one-shot, agentic, and agentic + verifier on
all 60 records.

## Usage

| Method | Records | Total Tokens | Avg Tokens | Total Seconds | Avg Seconds |
|---|---:|---:|---:|---:|---:|
| One-shot DeepSeek | 16 | 519530 | 32470.62 | 336.034 | 21.002 |
| Agentic DeepSeek s2 | 16 | 440542 | 27533.88 | 339.600 | 21.225 |
| Verifier extra pass | 16 | 148718 | 9294.88 | 196.194 | 12.262 |
| Agentic s2 + verifier total | 16 | 589260 | 36828.75 | 535.794 | 33.487 |

## Generated Files

```text
outputs/aboutwork_committed_60_agentic_deepseek_selector_v3_s2.jsonl
outputs/aboutwork_committed_60_agentic_deepseek_selector_v3_s2_trace.jsonl
outputs/aboutwork_committed_60_agentic_deepseek_selector_v3_s2_usage.json
outputs/aboutwork_committed_60_bm25_plus_agentic_deepseek_selector_v3_s2.jsonl
outputs/aboutwork_committed_60_bm25_plus_agentic_deepseek_selector_v3_s2_eval.json
outputs/aboutwork_committed_60_agentic_plus_verifier_deepseek_selector_v3_s2.jsonl
outputs/aboutwork_committed_60_agentic_plus_verifier_deepseek_selector_v3_s2_usage.json
outputs/aboutwork_committed_60_bm25_plus_agentic_verifier_deepseek_selector_v3_s2.jsonl
outputs/aboutwork_committed_60_bm25_plus_agentic_verifier_deepseek_selector_v3_s2_eval.json
```

## Interpretation

AboutWork-60 confirms the RQ5 pattern already seen on Easy Finance strict62 and
the Defects4J RQ5 diagnostic mini-benchmark: agentic inspection is technically
workable, but it does not improve aggregate localization quality over one-shot
evidence-aware rerank. The verifier also does not improve ranking, and only adds
extra token/runtime cost.

For the thesis, AboutWork-60 should still report one-shot selective rerank as the
main RQ4 method. Agentic and verifier should be discussed as RQ5 negative or
neutral ablations.
