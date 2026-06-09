# Thesis Consistency Review

Date: 2026-06-08

This document records the canonical experiment wording and numbers to use when moving the current draft into the thesis. It is a consistency checklist, not a new experiment result.

## Canonical Main Claim

Use:

```text
Selective evidence-aware LLM rerank improves file-level fault localization when candidate retrieval contains the faulty file and the evidence package exposes useful signals.
```

Do not use:

```text
The experiments completed full Defects4J.
The selector is fully generalized.
Agentic/verifier outperforms one-shot rerank.
```

## Canonical Dataset Scope

| Dataset | Role | Size | Thesis Status |
|---|---|---:|---|
| Defects4J pilot | method development and pilot validation | 120 bugs | report as pilot |
| Closure-21..60 | fresh validation | 40 bugs | report as fresh validation |
| Closure-61..100 | frozen held-out aggregate | 38 bugs | strongest benchmark result |
| Mockito-21..30 | fresh attempt | 9 usable bugs | report as fresh validation / diagnostics |
| Mockito-31..38 | fresh validation | 8 bugs | report as fresh validation |
| AboutWork committed-60 | real bug-log case study | 60 records | RQ4 case study; RQ5 ablation |
| Easy Finance clean63 | real git-history case study | 63 records | RQ4 case study |
| Easy Finance strict62 | filtered real git-history case study | 62 records | RQ5 ablation |
| Defects4J RQ5 mini | diagnostic extension benchmark | 10 bugs | RQ5 ablation |

Current approximate Defects4J usable records: 215.

Mockito active bugs in this checkout end at `38`, so Mockito cannot provide another held-out slice.

## Canonical Main Result

Closure frozen held-out aggregate, `Closure-61..100`:

| Setting | Bugs | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|---:|
| frozen retrieval baseline | 38 | 0 | 0.3947 | 0.5263 | 0.6053 | 0.7105 | 0.5080 |
| frozen cost-control v3 + DeepSeek | 38 | 11 | 0.5526 | 0.7105 | 0.7632 | 0.8421 | 0.6513 |

Improvement:

```text
Top-1:  +0.1579
Top-3:  +0.1842
Top-5:  +0.1579
Top-10: +0.1316
MRR:    +0.1434
```

Cost:

```text
selected: 11 / 38
selected_fraction: 0.2895
total_tokens: 408568
avg_total_tokens_per_selected_case: 37142.55
total_duration_seconds: 178.838
avg_duration_seconds_per_selected_case: 16.258
```

## RQ Mapping

| RQ | Evidence To Cite | Answer |
|---|---|---|
| RQ1 Defects4J improvement | pilot table plus Closure `61..100` held-out | yes, when candidate recall is sufficient |
| RQ2 candidate/evidence quality | `Closure-98`, selector false negatives, `Closure-4` recovered evidence miss | retrieval, selector, and evidence quality dominate remaining failures |
| RQ3 cost control | Closure `61..100`, AboutWork committed-60, Easy Finance clean63 | selective rerank preserves gains with limited calls |
| RQ4 real-project transfer | AboutWork committed-60, Easy Finance clean63 | initial case-study support only |
| RQ5 agentic/verifier | Easy Finance strict62, Defects4J RQ5 mini, AboutWork committed-60 | feasible but not better than one-shot; verifier is negative ablation |

## Error Analysis Anchors

| Category | Cases | Use |
|---|---|---|
| Recovered evidence/snippet miss | `Closure-4` | pilot example showing evidence construction matters |
| Selector false negative | `Closure-67`, `Closure-75`, `Closure-88`, `Closure-99` | main remaining selector-recall risk |
| Candidate retrieval miss | `Closure-98` | rerank cannot fix absent candidates |
| Utility-file ambiguity | `Closure-61`, `Closure-75`, `Closure-94` | shared helper files need better non-oracle diagnostics |
| Code-output evidence gap | `Closure-65` | code-output selector is too narrow |
| Agentic/verifier cost | Easy Finance strict62; Defects4J RQ5 mini; AboutWork committed-60 | RQ5 ablation, not main method |

## Writing Rules

- Keep pilot, fresh validation, frozen held-out, and real-project case studies separate.
- Keep one-shot selective rerank as the main method.
- Keep agentic and verifier under RQ5 only.
- Report candidate Recall@20/50 from retrieval outputs, not merged Top-10 outputs.
- State that file-level Top-k uses any-hit ground truth for multi-file bugs.
- State that AboutWork and Easy Finance need new logs or new time windows for stronger generalization claims.
- Use AboutWork committed-60 as the current AboutWork result: BM25 Top-1/MRR 0.5667/0.7015, selector_v3 + one-shot DeepSeek Top-1/MRR 0.7000/0.8117.
- State that AboutWork-60 agentic and verifier match one-shot per-bug correct ranks; verifier adds 148718 tokens without improvement.
- State that full Defects4J has not been completed.

## Files Checked In This Pass

```text
docs/thesis_experiment_sections_2026-06-03.md
docs/thesis_experiment_chapter_draft_2026-06-03.md
docs/experiment_design.md
docs/current_results_report.md
docs/error_analysis_table_2026-06-03.md
docs/evidence_rule_evolution_closure4_typecycle.md
docs/rq5_defects4j_mini_benchmark_protocol_2026-06-03.md
docs/rq5_defects4j_mini_benchmark_results_2026-06-03.md
docs/aboutwork_committed_60_rerank_results_2026-06-08.md
docs/aboutwork_committed_60_agentic_verifier_results_2026-06-08.md
docs/rq_answers_final_2026-06-03.md
```
