# Final RQ Answers

Date: 2026-06-08

This document gives the thesis-ready answers to RQ1--RQ5. It is a synthesis of
the current experiment reports, not a new experiment.

## RQ1: Does LLM reranking improve Defects4J file-level localization?

Answer: yes, when the candidate pool contains the faulty file and the evidence
package exposes useful signals.

The strongest benchmark evidence is the Closure `61..100` frozen held-out
aggregate:

| Setting | Bugs | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|---:|
| frozen retrieval baseline | 38 | 0 | 0.3947 | 0.5263 | 0.6053 | 0.7105 | 0.5080 |
| frozen cost-control v3 + DeepSeek | 38 | 11 | 0.5526 | 0.7105 | 0.7632 | 0.8421 | 0.6513 |

Pilot results across Lang, Math, Chart, Time, Closure, and Mockito also show
that LLM rerank can substantially improve file ranking, but those pilot results
include method evolution and targeted evidence add-ons. Therefore the Closure
`61..100` result should be treated as the main benchmark claim.

## RQ2: How do candidate recall and evidence quality affect reranking?

Answer: they are the main determinants of success and failure.

The current error analysis separates three major upstream limits:

| Failure Mode | Evidence | Interpretation |
|---|---|---|
| Candidate retrieval miss | `Closure-98` | Rerank cannot recover a true file absent from top50 candidates. |
| Selector false negative | `Closure-67`, `Closure-75`, `Closure-88`, `Closure-99` | Correct file may be present, but non-selected cases fall back to retrieval. |
| Evidence/snippet miss | `Closure-4` pilot | Candidate-present failures can be recovered when the prompt exposes the right evidence. |

The important point is that remaining failures are not mainly invalid JSON or
random LLM behavior. They usually come from missing candidates, missed selection,
or weak snippets.

## RQ3: Can selective reranking control cost while preserving gains?

Answer: yes, but selector recall is the main risk.

On Closure `61..100`, the method calls the LLM only 11/38 times:

```text
selected_fraction: 0.2895
total_tokens: 408568
avg_total_tokens_per_selected_case: 37142.55
total_duration_seconds: 178.838
avg_duration_seconds_per_selected_case: 16.258
```

This limited budget still improves Top-5 from 0.6053 to 0.7632 and MRR from
0.5080 to 0.6513. AboutWork committed-60 and Easy Finance clean63 also support
the same cost-control pattern in real-project case studies. AboutWork-60 selects
16 of 60 records for DeepSeek and improves Top-1 from 0.5667 to 0.7000 and MRR
from 0.7015 to 0.8117. However, skipped hard cases remain a central limitation,
so the selector should be reported as effective but not fully generalized.

## RQ4: Does the method transfer to real-project data?

Answer: initial case-study evidence says yes, but this is not broad industrial
generalization.

| Dataset | Method | Selected Records | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---|---:|---:|---:|---:|---:|---:|
| AboutWork committed-60 | BM25 production top50 | 0 / 60 | 0.5667 | 0.8333 | 0.9167 | 0.9333 | 0.7015 |
| AboutWork committed-60 | BM25 + selector_v3 + DeepSeek | 16 / 60 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 |
| Easy Finance clean63 | BM25 production top50 | 0 / 63 | 0.3968 | 0.7302 | 0.8730 | 0.8730 | 0.5684 |
| Easy Finance clean63 | BM25 + selector_v1 UI evidence v2 | 10 / 63 | 0.4921 | 0.8095 | 0.9841 | 1.0000 | 0.6729 |

The safe thesis wording is that the framework can be adapted to real bug logs
and git-history-derived records, but more projects or new time windows are
needed for stronger external-validity claims. The remaining AboutWork-60 Top-10
misses are both selector false negatives, so the main real-project limitation is
selector recall rather than selected-case reranking.

## RQ5: Do agentic inspection and verifier improve over one-shot reranking?

Answer: not in the current design.

Easy Finance strict62:

| Method | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| one-shot UI evidence v2 | 9 | 0.5000 | 0.8226 | 1.0000 | 1.0000 | 0.6817 | 226860 |
| controlled agentic s2 | 9 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6831 | 250481 |
| agentic s2 + verifier | 9 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6804 | 331050 |

Defects4J diagnostic mini-benchmark:

| Method | API Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| retrieval baseline top50 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.2000 | 0.0534 | 0 |
| one-shot DeepSeek | 10 | 0.4000 | 0.7000 | 0.8000 | 0.9000 | 0.5644 | 345937 |
| agentic DeepSeek | 32 | 0.3000 | 0.6000 | 0.6000 | 0.8000 | 0.4768 | 441952 |
| agentic + verifier DeepSeek | 42 | 0.3000 | 0.6000 | 0.6000 | 0.8000 | 0.4768 | 554133 |

The Defects4J mini-benchmark shows concrete regressions: agentic drops
`Math-12` from one-shot rank 9 to top10 miss, and worsens `Closure-4`,
`Closure-13`, and `Mockito-28`. The verifier then makes no correction.

AboutWork committed-60:

| Method | Selected Records | Model Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| one-shot DeepSeek | 16 / 60 | 16 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 519530 |
| agentic DeepSeek s2 | 16 / 60 | 40 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 440542 |
| agentic s2 + verifier | 16 / 60 | 56 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 589260 |

On AboutWork-60, one-shot, agentic, and agentic + verifier have identical
per-bug correct ranks. The verifier adds 148718 tokens and 196.194 seconds but
does not change any aggregate metric or per-bug correct rank.

Therefore RQ5 is a negative/conditional result: agentic inspection is feasible
and traceable, but current results do not justify replacing selective one-shot
rerank. Verifier should be reported as a negative ablation.

## One-Sentence Thesis Answer

Selective evidence-aware one-shot LLM reranking improves file-level fault
localization under sufficient candidate recall, and selective invocation can
control cost, but the current agentic and verifier extensions add cost without
clear accuracy gains.

## Do Not Overclaim

Do not write:

```text
The experiments completed full Defects4J.
The selector is fully generalized.
Agentic/verifier outperforms one-shot rerank.
The real-project case studies prove broad industrial generalization.
```

Use:

```text
The strongest benchmark result is Closure 61..100 frozen held-out.
The method improves file-level localization when candidate recall is sufficient.
Selector recall, candidate recall, and evidence quality remain the main limits.
Agentic/verifier are RQ5 ablations and do not replace the main method.
```
