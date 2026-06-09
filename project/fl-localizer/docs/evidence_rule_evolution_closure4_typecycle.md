# Evidence Rule Evolution: Closure-4 Type-Cycle Case

Date: 2026-06-03

This note records how the Closure-4 pilot failure was turned into a reusable evidence-rule hypothesis. It should be cited as method-evolution evidence, not as a frozen held-out result.

## Case Status

Closure-4 was not a candidate-recall miss. The faulty file `NamedType.java` was already present in the retrieval candidate pool at rank 49, but the initial DeepSeek rerank did not select it.

The failure was an evidence-quality problem:

- The prompt snippet for `NamedType.java` did not expose the strongest local signals, including `handleTypeCycle` and the `"Cycle detected in inheritance chain"` warning text.
- The stack trace was dominated by repeated `PrototypeObjectType.isSubtype` frames, which made downstream recursive symptoms more visible than the resolver/placeholder type code.
- The rerank prompt had no explicit rule telling the model to inspect lower-ranked type resolver files for inheritance-cycle failures.

## Changes Made

The diagnostic fix changed three parts of the evidence path:

- Snippet scoring now gives higher weight to cycle/type-system terms such as `cycle`, `detected`, `extends`, `implements`, `inheritance`, `resolve`, `recursive`, `stackoverflowerror`, `subtype`, and `unresolved`.
- Stack traces are compacted so repeated identical frames are shown only a few times, with an omission marker for the rest.
- The evidence-mode rerank prompt now tells the model that recursive type, inheritance, implements/extends, cycle-detected, or `StackOverflowError` failures may require inspecting lower-ranked resolver or placeholder type classes whose snippets mention `resolveInternal`, `handleTypeCycle`, unresolved/named types, or cycle warning text.

The same family of signals later became part of the experimental automatic selector path: pass-chain/type-cycle/state-reset pattern selection can be enabled or disabled as non-oracle selector logic, and Closure cost-control v1/v2/v3 apply additional gates around those signals.

## Result

Before the type-cycle add-on:

```text
Closure hard8 + pass-chain C13:
Top1 0.40 / Top3 0.75 / Top5 0.95 / MRR 0.5975
```

After adding the Closure-4 type-cycle evidence fix:

```text
Closure hard8 + pass-chain C13 + type-cycle C4:
Top1 0.40 / Top3 0.80 / Top5 1.00 / MRR 0.6225
```

For Closure-4 specifically:

```text
NamedType.java: retrieval candidate rank 49 -> DeepSeek rerank rank 2
```

## Thesis Interpretation

This case supports RQ2: when the faulty file is present but the evidence package is weak, improving snippet selection and prompt instructions can let one-shot rerank recover the correct file.

It should not be reported as held-out proof, because the rule came from diagnosing a pilot case. The conservative wording is:

> Closure-4 is a recovered pilot example showing that evidence construction matters: the faulty file was already in the candidate pool, and exposing type-cycle evidence moved it into the reranked Top-3. The frozen held-out claim should instead rely on Closure-61..100.

