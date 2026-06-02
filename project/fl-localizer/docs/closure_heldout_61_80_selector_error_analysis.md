# Closure Held-Out 61..80 Selector Error Analysis

Date: 2026-06-02

This analysis explains the selector behavior observed in the frozen `Closure-61..80` held-out run. It is error analysis only. It must not change the reported held-out result.

## Summary

Frozen protocol:

```text
docs/frozen_protocol_2026-06-01.md
```

Held-out result:

```text
records: 19
selected: 6
selected fraction: 0.3158
selected-case rerank Top-3: 1.0000
merged Top-5: 0.7895
merged Top-10: 0.8947
merged MRR: 0.7018
```

The selected cases were not the problem: every selected case reached Top-3 after rerank. The main remaining problem is selector recall.

## Selector Coverage

Baseline retrieval had 8 Top-5 failures:

```text
Closure-61, Closure-65, Closure-67, Closure-70,
Closure-72, Closure-75, Closure-76, Closure-77
```

The frozen selector selected 4 of those 8:

```text
Closure-70, Closure-72, Closure-76, Closure-77
```

The frozen selector missed 4 of those 8:

```text
Closure-61, Closure-65, Closure-67, Closure-75
```

The two most important missed cases are `Closure-67` and `Closure-75`, because their baseline ranks were outside Top-20.

## Selected Cases

| Bug | Ground Truth File | Selector Reason | Baseline Rank | Merged Rank |
|---|---|---|---:|---:|
| Closure-64 | `Compiler.java` | `low_score_ratio<=1.02` | 4 | 2 |
| Closure-69 | `TypeCheck.java` | `pattern:type_system` | 1 | 1 |
| Closure-70 | `TypedScopeCreator.java` | `pattern:type_system` | 14 | 3 |
| Closure-72 | `FunctionToBlockMutator.java` | `pattern:closure_deep_specific_direct_hint` | 12 | 1 |
| Closure-76 | `DeadAssignmentsElimination.java` | `pattern:closure_deep_specific_direct_hint` | 18 | 1 |
| Closure-77 | `CodeGenerator.java` | `pattern:closure_code_output` | 8 | 1 |

## False Negatives

| Bug | Ground Truth File | Baseline Rank | Merged Rank | Top-1 File | Selector-Relevant Signals |
|---|---|---:|---:|---|---|
| Closure-61 | `NodeUtil.java` | 8 | 8 | `PeepholeRemoveDeadCode.java` | top1 has direct hint; score ratio 1.0274; direct hints point to `Compiler` / `PeepholeRemoveDeadCode`; ground truth has only identifier overlap |
| Closure-65 | `CodeGenerator.java` | 8 | 8 | `CodePrinter.java` | top1 has direct hint; score ratio 1.0640; no numeric/key code-generator pattern trigger |
| Closure-67 | `AnalyzePrototypeProperties.java` | 48 | miss in Top-10 | `Compiler.java` | top1 has direct hint; score ratio 1.1673; direct hint names `RemoveUnusedPrototypeProperties`, not the actual changed file |
| Closure-75 | `NodeUtil.java` | 21 | miss in Top-10 | `Compiler.java` | top1 has direct hint; score ratio 1.0174; direct hints point to `Compiler` / `PeepholeFoldConstants`; ground truth has only identifier overlap |

## Failure Modes

1. `NodeUtil` utility-file failures are under-selected.

`Closure-61` and `Closure-75` both modify `NodeUtil.java`, but the failing tests point strongly at compiler passes (`PeepholeRemoveDeadCode` / `PeepholeFoldConstants`) and generic compiler infrastructure. The current selector treats a direct-hint top1 as relatively safe and therefore does not trigger rerank unless an additional Closure-specific pattern fires.

2. Output-generation failures are partly covered but not complete.

`Closure-77` was selected by `pattern:closure_code_output` and improved from rank 8 to rank 1. `Closure-65` is another `CodeGenerator.java` case, but it did not satisfy the current score-ratio / term conditions. This suggests the code-output pattern is useful but too narrow for all output-generation failures.

3. Semantic pass-name mismatch is not covered.

`Closure-67` has a direct hint for `RemoveUnusedPrototypeProperties`, while the ground truth is `AnalyzePrototypeProperties.java`. The current pass-chain and direct-hint logic does not connect these semantically related pass names strongly enough, leaving the true file at rank 48.

## Next Frozen Protocol Hypotheses

These are hypotheses for a later protocol, not changes to the current reported run.

- Add a non-oracle selector diagnostic for utility-file candidates such as `NodeUtil.java` when the true candidate is within Top-25/Top-50 and the top results are generic compiler/pass files.
- Broaden the Closure code-output pattern cautiously: include `CodePrinter` top1 with `CodeGenerator` in Top-20 even when the score ratio is between 1.05 and 1.15, but validate on a new held-out slice.
- Add pass-family evidence for related optimization passes, for example connecting `RemoveUnusedPrototypeProperties` to `AnalyzePrototypeProperties`, again only in a later frozen protocol.
- Measure selector recall over baseline Top-5 and Top-10 failures as a first-class metric, alongside selected fraction and Top-k accuracy.

## Do Not Change

Do not revise the `Closure-61..80` main result after this analysis. The correct use of this document is to design the next frozen validation, likely another Closure slice or a cross-project held-out slice.
