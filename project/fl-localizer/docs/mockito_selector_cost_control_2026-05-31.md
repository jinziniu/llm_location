# Mockito Selector Cost-Control Analysis

日期：2026-05-31

## 1. Goal

After the fresh Mockito validation runs, the next question is cost control:

```text
Can we reduce selected LLM calls while preserving coverage of retrieval Top-5 failures?
```

This analysis compares selector variants across:

- `Mockito-1..20` pilot.
- `Mockito-21..30` fresh slice, 9 usable records.
- `Mockito-31..38` fresh slice, 8 usable records.

No DeepSeek calls were made in this analysis.

## 2. Selector Variants

### Pattern-only tight selector

The original tight selector used for `Mockito-1..20`:

```bash
--mockito-tight-patterns \
--score-ratio-threshold 0 \
--direct-hint-count-threshold 0 \
--no-top1-without-direct
```

### Pattern-only + diagnostics

Same as pattern-only tight selector, but with:

```bash
--mockito-diagnostic-patterns
```

Diagnostic-only patterns:

```text
diagnostic:mockito_primitive_default_values
diagnostic:mockito_injection_exact_type_ancestor
```

### Cost-control v2

Experimental selector:

```bash
--mockito-tight-patterns \
--mockito-diagnostic-patterns \
--mockito-cost-control-v2 \
--score-ratio-threshold 0 \
--direct-hint-count-threshold 0 \
--no-top1-without-direct
```

Additional v2 behavior:

- Keep `pattern:mockito_invocation_varargs` when there are many direct hints.
- Add `pattern:mockito_real_method_interface` for real-method-on-interface failures.
- Keep the diagnostic-only primitive/default-value and exact-type/ancestor injection signals.
- Do not use generic `top1_without_direct_hint`.
- Do not use broad low-score-ratio or many-direct-hints as standalone reasons.

### Full no-top1 diagnostic selector

Broader selector used as a comparison:

```bash
--mockito-tight-patterns \
--mockito-diagnostic-patterns \
--no-top1-without-direct
```

This keeps score-ratio and many-direct-hints standalone rules.

## 3. Results

### Mockito-1..20

| Selector | Selected | Top-1 miss cov | Top-3 miss cov | Top-5 miss cov |
|---|---:|---:|---:|---:|
| Pattern-only tight | 9/20 | 9/13 | 9/9 | 7/7 |
| Pattern-only + diagnostics | 10/20 | 9/13 | 9/9 | 7/7 |
| Cost-control v2 | 11/20 | 10/13 | 9/9 | 7/7 |
| Full no-top1 diagnostics | 14/20 | 11/13 | 9/9 | 7/7 |

### Mockito-21..30

| Selector | Selected | Top-1 miss cov | Top-3 miss cov | Top-5 miss cov |
|---|---:|---:|---:|---:|
| Pattern-only tight | 2/9 | 1/5 | 0/4 | 0/4 |
| Pattern-only + diagnostics | 4/9 | 3/5 | 2/4 | 2/4 |
| Cost-control v2 | 6/9 | 5/5 | 4/4 | 4/4 |
| Full no-top1 diagnostics | 6/9 | 5/5 | 4/4 | 4/4 |

### Mockito-31..38

| Selector | Selected | Top-1 miss cov | Top-3 miss cov | Top-5 miss cov |
|---|---:|---:|---:|---:|
| Pattern-only tight | 1/8 | 1/7 | 1/4 | 0/2 |
| Pattern-only + diagnostics | 1/8 | 1/7 | 1/4 | 0/2 |
| Cost-control v2 | 4/8 | 4/7 | 4/4 | 2/2 |
| Full no-top1 diagnostics | 3/8 | 3/7 | 3/4 | 2/2 |

## 4. Aggregate View

Across all three slices:

```text
total records: 37
total retrieval Top-5 failures: 13
```

| Selector | Selected | Top-5 miss coverage |
|---|---:|---:|
| Pattern-only tight | 12/37 | 7/13 |
| Pattern-only + diagnostics | 15/37 | 9/13 |
| Cost-control v2 | 21/37 | 13/13 |
| Full no-top1 diagnostics | 23/37 | 13/13 |

## 5. Interpretation

Pattern-only tight selector was good on the original `Mockito-1..20` pilot, but it does not generalize to fresh Mockito slices.

The diagnostic patterns recover two important `Mockito-21..30` failures:

- `Mockito-26`: primitive default values, `Primitives.java`.
- `Mockito-28`: InjectMocks exact type / ancestor matching, `DefaultInjectionEngine.java`.

Cost-control v2 is the best current compromise:

- It preserves 13/13 Top-5 failure coverage across the three slices.
- It selects 21/37 cases, compared with 23/37 for the broader full no-top1 diagnostic selector.
- It avoids generic `top1_without_direct_hint`, which selected several Top-5-success cases in `Mockito-31..38`.

However, v2 is not final:

- It is still derived after inspecting fresh validation behavior.
- It should be called an experimental selector, not the main production selector.
- More held-out bugs or another project-specific validation is needed before claiming generalization.

## 6. Decision

Do not run DeepSeek on all v2-selected cases yet.

Recommended next options:

1. If the goal is to test final rerank accuracy, run DeepSeek only on the `Mockito-31..38` v2 selected set:

```text
Mockito-32, Mockito-33, Mockito-36, Mockito-37
```

2. If the goal is method development, continue selector analysis and try to reduce v2 selection from 21/37 while keeping Top-5 miss coverage.

3. Keep diagnostic and v2 flags explicit in commands. Do not make them default.
