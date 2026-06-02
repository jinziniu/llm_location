# 阶段性实验报告：LLM-Assisted Fault Localization

日期：2026-05-27

结果整合版：

```text
docs/results_integration_2026-05-27.md
```

## 1. 阶段目标

本阶段项目目标是构建一个可复现的文件级缺陷定位实验系统。给定一个 bug 的失败测试、stack trace、bug report 元信息和源码文件集合，系统输出最可能包含缺陷的文件排序。

当前工作不直接做自动修复，而是解决自动修复前的核心问题：

```text
Where is the bug?
```

阶段性研究问题：

- BM25 是否能作为第一阶段候选文件生成器？
- LLM rerank 是否能在候选池上提升 Top-k accuracy 和 MRR？
- 候选召回不足和 prompt 证据噪声分别会造成什么失败？
- DeepSeek API 是否适合当前成本和稳定性要求？
- 真实公司 bug log 是否能转换为同一套 benchmark/case-study 数据？

## 2. 当前系统

当前已经形成一条端到端 pipeline：

```text
Defects4J checkout
-> compile / test / export metadata
-> build bug JSONL
-> index source files
-> BM25 / hybrid retrieval
-> snippet extraction
-> DeepSeek rerank
-> evaluator
-> usage logging
-> worklog
```

主要实现：

- `scripts/build_defects4j_dataset.py`
- `scripts/run_bm25.py`
- `scripts/run_hybrid_retrieval.py`
- `scripts/run_llm_rerank.py`
- `scripts/select_rerank_candidates.py`
- `scripts/merge_selective_rerank.py`
- `scripts/evaluate_predictions.py`
- `scripts/build_aboutwork_dataset.py`

当前评测指标：

- Top-1 accuracy
- Top-3 accuracy
- Top-5 accuracy
- Top-10 / Top-20 / Top-50 candidate recall where applicable
- MRR
- LLM token usage
- LLM runtime
- invalid / duplicate / fallback output count

## 3. 方法进展

### 3.1 Baseline

第一版使用 BM25 直接对源码文件排序。查询由以下信息组成：

- bug report id/text
- failing test
- triggering tests
- stack trace runtime context

BM25 在简单项目上已经有一定效果，但在 Math、Closure、Mockito 等项目上 Top-5 不稳定，说明纯文本匹配不能充分处理复杂测试上下文、间接调用链和框架噪声。

### 3.2 Hybrid Retrieval

在 BM25 基础上加入：

- triggering test source context
- stack frame direct class hints
- test class name to source class hints
- identifier overlap boost
- focused stack trace section filtering

该方法显著改善 Chart、Time 等项目，尤其减少了无关 failing-test section 对 direct hints 的污染。

### 3.3 Evidence-Aware LLM Rerank

LLM rerank 输入 top candidates，每个候选包含：

- file path
- class names
- method names
- relevant snippet
- retrieval score components
- optional test source context

DeepSeek 输出排序后的文件列表，系统再做格式校验并用 fallback 补足输出。

### 3.4 Targeted Selector

为了避免全量调用 LLM，当前实现了 selector：

- low score ratio
- top1 without direct hint
- many direct hints
- pass-chain pattern
- type-cycle pattern
- state-reset pattern

其中新增三类 pattern 来自 Closure/Math 的失败分析：

- `pass-chain`：Closure compiler pass config 到具体 pass implementation。
- `type-cycle`：recursive type / inheritance / implements / StackOverflowError。
- `state-reset`：clone/copy/reset/state 与 random/seed/sample/distribution 相关状态一致性问题。

## 4. Defects4J 当前结果

当前已完成 6 个 Defects4J pilot 项目，共 120 个 bug：

```text
Lang-20
Math-20
Chart-20
Time-20
Closure-20
Mockito-20
```

核心结果表：

| Project | Method | Bugs | Top-1 | Top-3 | Top-5 | MRR |
|---|---|---:|---:|---:|---:|---:|
| Lang | BM25 | 20 | 0.60 | 0.85 | 0.85 | 0.7383 |
| Lang | BM25 + DeepSeek rerank | 20 | 0.95 | 1.00 | 1.00 | 0.9750 |
| Math | BM25 | 20 | 0.35 | 0.55 | 0.65 | 0.4794 |
| Math | BM25 + DeepSeek rerank | 20 | 0.75 | 0.90 | 0.90 | 0.8250 |
| Math | Hybrid/direct + compact evidence DeepSeek | 20 | 0.90 | 0.95 | 1.00 | 0.9350 |
| Math | Focused hybrid/direct + selective DeepSeek | 20 | 0.90 | 0.90 | 1.00 | 0.9200 |
| Chart | Focused hybrid/direct | 20 | 0.85 | 0.95 | 1.00 | 0.9040 |
| Chart | Hybrid/direct + DeepSeek hard4 | 20 | 0.55 | 0.90 | 1.00 | 0.7392 |
| Time | Focused hybrid/direct + test-prefix hints | 20 | 0.70 | 0.80 | 0.85 | 0.7800 |
| Time | Focused hybrid/direct + DeepSeek hard4 | 20 | 0.90 | 1.00 | 1.00 | 0.9500 |
| Closure | Focused hybrid/direct | 20 | 0.30 | 0.45 | 0.55 | 0.4323 |
| Closure | DeepSeek hard8 + pass-chain C13 + type-cycle C4 | 20 | 0.40 | 0.80 | 1.00 | 0.6225 |
| Mockito | Focused hybrid/direct | 20 | 0.35 | 0.55 | 0.65 | 0.4818 |
| Mockito | Diagnostic DeepSeek hard7 + ByteBuddy M20 | 20 | 0.55 | 0.90 | 1.00 | 0.7200 |
| Mockito | Focused hybrid/direct + tight selector9 DeepSeek | 20 | 0.65 | 1.00 | 1.00 | 0.8000 |

说明：

- Lang 和 Math 已有完整或接近完整 rerank 实验。
- Chart、Time、Closure 采用 targeted hard-case rerank。
- Mockito 当前完成数据集、focused hybrid baseline、hard7 diagnostic DeepSeek rerank、`Mockito-20` ByteBuddy evidence add-on 和 tight selector9。
- Mockito tight selector9 运行时不使用 ground truth，但仍是在当前 20 个 bug 上拟合出来的，需要新 bug 验证。

## 5. 关键实验发现

### 5.1 LLM rerank 有明显收益

在 Lang、Math、Chart、Time 上，DeepSeek rerank 能将很多 BM25 排名靠后的真实文件拉入 Top-1 或 Top-3。例如：

- Lang：Top-5 从 0.85 提升到 1.00。
- Math：BM25 Top-5 0.65，compact evidence DeepSeek 后 Top-5 1.00。
- Time：targeted hard4 后 Top-3/Top-5 达到 1.00。

这说明 LLM 适合做第二阶段排序，尤其适合在候选池中已经包含真实文件时利用语义证据重新排序。

### 5.2 候选召回是上限

当真实文件不在候选池中，LLM rerank 无法补救。Closure-13 是典型例子：

- focused hybrid top-200 仍然 miss。
- 加入 pass-chain retrieval 后，`PeepholeOptimizationsPass.java` 进入候选池 rank 39。
- DeepSeek rerank 后达到 rank 3。

这说明候选生成器不是可替代模块，而是 LLM rerank 的前提。

### 5.3 Prompt 证据质量影响很大

Closure-4 的真实文件 `NamedType.java` 原本在候选 rank 49，但 DeepSeek 未选中。原因不是候选缺失，而是 prompt 证据差：

- 原 snippet 只有 package/import。
- stack trace 被 1000+ 次重复的 `PrototypeObjectType.isSubtype` 污染。

修复后：

- snippet scoring 能显示 `handleTypeCycle` 和 `"Cycle detected in inheritance chain"`。
- prompt 压缩重复栈帧。
- DeepSeek 将 `NamedType.java` 排到 rank 2。

这说明需要同时优化 retrieval、snippet 和 prompt，而不是只换模型。

### 5.4 Selective Rerank 是成本控制关键

Math selective rerank 将 DeepSeek 调用从 20/20 降到 6/20，仍保持：

```text
Top-1: 0.90
Top-5: 1.00
MRR:   0.9200
```

AboutWork selector_v3 用 11/39 的调用达到：

```text
Top-1: 0.7692
Top-3: 1.0000
Top-5: 1.0000
MRR:   0.8675
```

这说明全量 LLM 并不是必要策略，更合理的研究方向是“高召回候选池 + 可解释 selector + targeted LLM rerank”。

### 5.5 Mockito 证明 hard cases 可被 rerank，但 selector 仍需收紧

Mockito-20 focused hybrid/direct：

```text
Top-1:  0.35
Top-3:  0.55
Top-5:  0.65
Top-10: 0.75
Top-20: 0.95
Top-50: 1.00
MRR:    0.4818
```

Top-50 召回 1.00，说明 LLM 有发挥空间。新增 Mockito-specific selector 后，pattern-only selector 选择 12/20，并覆盖全部 7 个 baseline Top-5 failures：

```text
Mockito-1, Mockito-7, Mockito-9, Mockito-12, Mockito-15, Mockito-17, Mockito-20
```

随后对这 7 个 hard cases 做 DeepSeek diagnostic rerank。第一轮合并回 Mockito-20 后：

```text
Top-1:  0.35 -> 0.55
Top-3:  0.55 -> 0.85
Top-5:  0.65 -> 0.95
Top-10: 0.75 -> 0.95
MRR:    0.4818 -> 0.7033
```

其中 6/7 个 hard cases 被 DeepSeek 拉入 Top-3；剩余失败是 `Mockito-20`。进一步加入 Mockito constructor/spy evidence rule 后，`ByteBuddyMockMaker.java` 从 baseline rank 23 被 DeepSeek 提到 rank 3。

最终合并结果：

```text
Top-1:  0.35 -> 0.55
Top-3:  0.55 -> 0.90
Top-5:  0.65 -> 1.00
Top-10: 0.75 -> 1.00
MRR:    0.4818 -> 0.7200
```

进一步收紧 Mockito selector 后，`tight selector9` 选择 9/20，覆盖 baseline 全部 9 个 Top-3 misses。补跑 `Mockito-3` 和 `Mockito-19` 后：

```text
Top-1:  0.35 -> 0.65
Top-3:  0.55 -> 1.00
Top-5:  0.65 -> 1.00
Top-10: 0.75 -> 1.00
MRR:    0.4818 -> 0.8000
```

因此 Mockito 的结论是：hard cases 可被 LLM rerank 明显改善，且 tight selector 已经比原先 12/20 pattern selector 更接近可部署策略；但它仍是当前 pilot 上的 in-sample 规则，下一步要用 fresh bugs 验证泛化。

## 6. AboutWork 公司项目 Case Study

公司 bug log 已转换为同一套实验格式：

```text
source: /Users/jin/capi_project/aboutwork/COMPANY_BUG_LOG.md
records: 39 committed-history bug logs
backend: 17
frontend: 22
```

当前最好结果：

| Method | Selected LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production | 0 / 39 | 0.5897 | 0.8462 | 0.9487 | 0.9487 | 0.7171 |
| BM25 + selector_v3 | 11 / 39 | 0.7692 | 1.0000 | 1.0000 | 1.0000 | 0.8675 |

AboutWork 的意义：

- 它不是公开 benchmark，而是真实产品开发 bug。
- 它覆盖 Python/Django、TypeScript/React 和 chatbot/admin-agent 场景。
- 它能作为工业 case study，补充 Defects4J 的 Java benchmark 局限。

当前注意点：

- selector_v3 是在这 39 条日志上调出来的，需要后续新增 bug log 验证泛化。
- 公司数据必须继续保持 allowed localization context 和 ground truth 分离，避免评测泄漏。

## 7. 当前贡献

本阶段已经形成以下阶段性成果：

1. 建成可运行的文件级 fault localization pipeline。
2. 支持 Defects4J 数据集构建、检索、rerank、评测和 usage logging。
3. 接入 DeepSeek API，并完成多项目 pilot。
4. 设计并验证 focused hybrid retrieval。
5. 通过 Closure-13 证明 pass-chain retrieval 对 compiler integration case 有价值。
6. 通过 Closure-4 证明 snippet scoring 和 stack compaction 能修复 rerank miss。
7. 通过 Math-12 证明 state-reset 类 evidence 可以被 selector/snippet 规则捕捉。
8. 建成 AboutWork 公司 bug log case-study 数据集。
9. 完成 Mockito-20 数据集接入、baseline、hard7 diagnostic rerank、M20 ByteBuddy add-on 和 tight selector9。
10. 增加 Mockito-specific selector patterns，并从 12/20 收紧到 9/20。
11. 通过 Mockito-20 证明 constructor/spy 失败需要检查 MockMaker/bytecode creation 层。
12. 建立 worklog 机制，保证每轮实验可追溯。

## 8. 当前限制

内部有效性：

- ground truth 来自 modified classes/files，可能包含非 bug root cause 的伴随修改。
- 多文件 bug 当前使用任一文件命中，可能高估效果。
- selector 在部分数据上有调参痕迹，需要新数据验证。

外部有效性：

- Defects4J 主要是 Java 项目，不能完全代表工业多语言系统。
- AboutWork 是单公司项目，样本还不够大。
- Mockito tight selector9 仍是在当前 pilot 上调出来的，需要新 bug 验证泛化。

构造有效性：

- 文件级定位比 method/line-level 定位更粗。
- Top-k accuracy 不能完全等价于真实调试成本。
- token 成本和 prompt 长度会影响方法可用性。

复现风险：

- DeepSeek 模型版本可能变化。
- Mockito Gradle 4.9 构建需要允许本地 file-lock 通信，沙箱环境会阻塞。
- Defects4J checkout/compile/test 对本地 JDK 和缓存状态敏感。

## 9. 下一步计划

为了形成更扎实的阶段性报告，下一步优先级如下：

1. 验证 Mockito tight selector9。
   - 当前 selector 选择 9/20，覆盖当前 pilot 全部 baseline Top-3 misses。
   - 下一步要在 fresh Mockito bugs 或相似 mocking-framework bugs 上验证。
   - 重点观察是否仍能少选且覆盖 hard cases。

2. 泛化 Mockito constructor/spy evidence rule。
   - M20 已验证 `ByteBuddyMockMaker.java` 可以通过 MockMaker/instance-creation evidence 进入 Top-3。
   - 下一步要把这条规则变成非 oracle selector/snippet 策略。

3. 整理最终阶段结果表。
   - Defects4J 6 个项目。
   - AboutWork case study。
   - token cost / selected calls / runtime。

4. 准备阶段性论文/汇报结构。
   - Introduction。
   - Method。
   - Experimental Design。
   - Results。
   - Error Analysis。
   - Threats to Validity。
   - Next Work。

## 10. 阶段性结论

当前结果支持以下结论：

```text
LLM-assisted fault localization is effective when used as a second-stage reranker over a high-recall candidate pool.
```

但是，当前项目最重要的问题已经不是“是否调用 LLM”，而是：

```text
How can we build a high-recall, low-noise candidate pool and select only the bugs that need LLM reranking?
```

因此，后续阶段应围绕候选召回、证据选择、selector 泛化和 token 成本控制继续推进。
