# Mockito Fresh Validation Report: 21..30

日期：2026-05-31

## 1. Goal

Validate whether the Mockito tight selector and current focused hybrid retrieval generalize beyond the original `Mockito-1..20` pilot slice.

This run intentionally stopped before DeepSeek calls. The purpose was to check dataset availability, retrieval baseline quality, candidate recall, and selector behavior on fresh samples.

## 2. Dataset

Requested:

```text
Mockito-21..30
```

Built:

```text
9 records
```

Skipped:

```text
Mockito-21: defects4j compile failed
```

Output:

```text
data/defects4j/mockito_fresh_21_30.jsonl
```

## 3. Commands

Dataset build:

```bash
python3 scripts/build_defects4j_dataset.py \
  --project Mockito \
  --bugs 21-30 \
  --out data/defects4j/mockito_fresh_21_30.jsonl \
  --skip-failures
```

Focused hybrid retrieval:

```bash
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/mockito_fresh_21_30.jsonl \
  --out outputs/mockito_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints
```

Evaluation:

```bash
python3 scripts/evaluate_predictions.py \
  --bugs data/defects4j/mockito_fresh_21_30.jsonl \
  --pred outputs/mockito_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --per-bug \
  --out outputs/mockito_fresh_21_30_hybrid_focused_direct_top50_eval.json
```

Selector:

```bash
python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/mockito_fresh_21_30.jsonl \
  --pred outputs/mockito_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_21_30_tight_selector.json \
  --mockito-tight-patterns
```

## 4. Retrieval Baseline

Focused hybrid/direct top50 result:

```text
bugs: 9
Top-1: 0.4444
Top-3: 0.5556
Top-5: 0.5556
MRR:   0.5339
```

Per-bug rank:

| Bug | Correct rank | Top-5 |
|---|---:|---|
| Mockito-22 | 1 | yes |
| Mockito-23 | 2 | yes |
| Mockito-24 | 1 | yes |
| Mockito-25 | 1 | yes |
| Mockito-26 | 7 | no |
| Mockito-27 | 15 | no |
| Mockito-28 | 14 | no |
| Mockito-29 | 41 | no |
| Mockito-30 | 1 | yes |

Candidate recall:

```text
Recall@5:  5 / 9
Recall@10: 6 / 9
Recall@20: 8 / 9
Recall@50: 9 / 9
```

Interpretation:

- Candidate recall@50 is sufficient for reranking: every ground-truth file appears in top50.
- The ranking baseline is weak on the fresh slice, especially `Mockito-26`, `Mockito-27`, `Mockito-28`, and `Mockito-29`.
- This is a good validation slice because it exposes selector coverage problems.

## 5. Tight Selector Result

Selected:

```text
Mockito-23, Mockito-25, Mockito-27, Mockito-29
```

Summary:

```text
records: 9
selected: 4
selected_fraction: 0.4444
```

Reason counts:

```text
top1_without_direct_hint: 2
many_direct_hints>=7: 2
pattern:mockito_generic: 1
pattern:mockito_serialization: 1
```

Coverage:

| Failure type | Cases | Covered by selector |
|---|---:|---:|
| Top-1 misses | 5 | 3 |
| Top-3 misses | 4 | 2 |
| Top-5 misses | 4 | 2 |

Interpretation:

- The selected ratio is acceptable at 4/9.
- Coverage is not acceptable for a fresh validation run: the selector misses half of the Top-3/Top-5 failures.
- Because of this, the next step should not be an immediate DeepSeek run on selected cases. Running LLM now would leave `Mockito-26` and `Mockito-28` unaddressed.

## 6. Missed Failure Analysis

### Mockito-26

Ground truth:

```text
src/org/mockito/internal/util/Primitives.java
```

Focused hybrid rank:

```text
7
```

Bug signal:

```text
primitive default values
```

Top candidates are default answer classes such as `ReturnsEmptyValues.java`, `ReturnsMoreEmptyValues.java`, and `ReturnsSmartNulls.java`. The ground-truth utility file `Primitives.java` is present but ranked below several direct default-answer classes.

Selector miss reason:

- Top-1 has a direct hint.
- Score ratio is not low enough.
- Existing Mockito patterns do not include primitive/default-value utility cases.

Potential future rule:

```text
mockito_primitive_default_values
```

This should not be added directly from this validation result without testing on another held-out slice.

### Mockito-28

Ground truth:

```text
src/org/mockito/internal/configuration/DefaultInjectionEngine.java
```

Focused hybrid rank:

```text
14
```

Bug signal:

```text
InjectMocks exact type / ancestor matching
```

Top candidates are JUnit runner files, while `DefaultInjectionEngine.java` appears only at rank 14.

Selector miss reason:

- Top-1 has a direct hint.
- Score ratio is above the low-ratio threshold.
- Existing injection pattern requires terms such as field, property, setter, or candidate. This case uses exact type / ancestor wording, so the injection signal does not trigger.

Potential future rule:

```text
mockito_injection_exact_type_ancestor
```

This should also be validated on another slice before becoming a default selector rule.

## 7. Decision

Do not run DeepSeek on this fresh slice yet.

Reason:

- The selector is not covering enough fresh failures.
- Calling DeepSeek only on the selected 4 cases would be a partial experiment and would not test the current main question: whether the selector generalizes.

Next engineering step:

- Add diagnostic-only candidate rules for primitive default values and injection exact-type/ancestor cases.
- Test those rules on a separate Mockito validation slice, such as `Mockito-31..38`, before promoting them to production selector behavior.

Next reporting step:

- Record this as a useful fresh-validation result: tight selector9 partially generalizes but misses two important fresh hard-case families.

## 8. Diagnostic Selector Follow-up

Implemented a diagnostic-only selector switch:

```text
--mockito-diagnostic-patterns
```

This switch is disabled by default. It adds two candidate families:

```text
diagnostic:mockito_primitive_default_values
diagnostic:mockito_injection_exact_type_ancestor
```

Regression check without diagnostics:

```text
selected: 4 / 9
selected ids: Mockito-23, Mockito-25, Mockito-27, Mockito-29
```

With diagnostics:

```text
selected: 6 / 9
selected ids: Mockito-23, Mockito-25, Mockito-26, Mockito-27, Mockito-28, Mockito-29
Top-5 miss coverage: 4 / 4
```

Interpretation:

- The diagnostic switch correctly selects the two missed hard cases in this slice.
- This is not enough to promote the rules to production because they were derived from this fresh slice.
- The next check must use a separate slice, `Mockito-31..38`.
