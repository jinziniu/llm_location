# LLM-Assisted Fault Localization 初步实验报告

日期：2026-05-30

## 1. 实验目标

本实验研究一个文件级缺陷定位方法：给定 bug report、失败测试、stack trace 和源码候选文件，系统输出最可能包含缺陷的文件排序。

当前实验的核心问题不是自动修复 bug，而是回答：

```text
Where is the bug?
```

实验方法采用两阶段设计：

```text
BM25 / hybrid retrieval
-> candidate source files
-> selective LLM rerank
-> optional controlled agentic inspection
-> optional verifier
-> file-level ranking
```

ground truth 来自 verified fixing commit touched files，但 ground truth、patch、fix commit 内容不进入 prompt，只用于最终评价。

## 2. 研究问题

本阶段实验主要对应以下问题：

| ID | Research Question |
|---|---|
| RQ1 | 与 BM25 / hybrid retrieval 相比，LLM rerank 是否能提升文件级 fault localization？ |
| RQ2 | 候选池召回和 snippet evidence 质量如何影响最终结果？ |
| RQ3 | selective rerank 是否能在保持效果的同时降低 token 成本？ |
| RQ4 | 方法能否从 Defects4J benchmark 迁移到真实公司项目？ |
| RQ5 | controlled agentic inspection 和 verifier 是否比 one-shot rerank 更有效？ |

## 3. 实验对象

### 3.1 Defects4J Benchmark

Defects4J 当前完成 6 个 pilot 项目，每个项目 20 个 bug，共 120 个 bug：

```text
Lang-20
Math-20
Chart-20
Time-20
Closure-20
Mockito-20
```

这些项目主要用于验证方法在公开 Java benchmark 上的可行性。

### 3.2 AboutWork 公司项目

AboutWork 是真实公司项目 bug log 数据集：

```text
records: 39 committed-history bug logs
backend: 17
frontend: 22
source: /Users/jin/capi_project/aboutwork/COMPANY_BUG_LOG.md
```

它覆盖 Python/Django、TypeScript/React、chatbot/admin-agent 等场景，用于验证方法在真实产品项目上的表现。

### 3.3 Easy Finance 公司项目

Easy Finance 来自 backend/frontend git history：

```text
clean committed records: 63
backend: 29
frontend: 34
strict sensitivity set: 62
source: /Users/jin/capi_project/easy_finance/
```

Easy Finance 的 bug report 多数由 commit metadata 推断，因此比 AboutWork 手写 bug log 噪声更高。实验中额外构建了 strict62 sensitivity analysis，排除一条 bug text 与实际 touched files 明显不一致的样本。

## 4. 方法设计

### 4.1 Baseline Retrieval

baseline 使用 BM25 或 focused hybrid retrieval 生成候选文件列表。query 主要由以下信息构成：

```text
bug_report.id
bug_report.text
test_failure
triggering_tests
stack_trace runtime context
```

BM25 的作用是提供候选池，而不是直接作为最终答案。后续 LLM rerank 只能在候选池内排序。

### 4.2 LLM Rerank

LLM rerank 接收：

- bug report
- failing test / stack trace
- BM25 或 hybrid top-k candidate files
- file path、class/method metadata
- relevant source snippets
- optional retrieval evidence

输出为 JSON ranking。系统会过滤 invalid files、去重，并在模型返回不足时用原始 BM25 顺序 fallback。

### 4.3 Selective Rerank

为了控制成本，实验不对所有 bug 调用 LLM。selector 会根据低置信度、domain mismatch、management command noise、frontend/backend 业务词错配等规则选出 hard cases。

核心思想：

```text
Only call the LLM when retrieval is uncertain or likely wrong.
```

### 4.4 Controlled Agentic Inspection

为了回答 RQ5，实验加入 controlled agentic inspection。agent 不允许自由操作 repo，只能使用固定工具：

```text
search_files(query)
inspect_candidate(file)
read_file_window(file, start_line, end_line)
```

约束：

```text
candidate pool: BM25 top-50 only
max_steps: 2
no fix commit
no patch
no ground truth
final output: same prediction JSONL schema
```

### 4.5 Verifier Pass

verifier 是独立验证器，不允许再调用工具，只能看：

- bug report
- agent top-10 ranking
- deterministic snippets
- prior agent observations

目标是测试 independent verification 是否能改进 agent ranking。

## 5. 评价指标

主要指标：

| Metric | Meaning |
|---|---|
| Top-1 Accuracy | 正确文件是否排第 1 |
| Top-3 Accuracy | 正确文件是否出现在前 3 |
| Top-5 Accuracy | 正确文件是否出现在前 5 |
| Top-10 Accuracy | 正确文件是否出现在前 10 |
| MRR | Mean Reciprocal Rank |
| Total Tokens | LLM 总 token 消耗 |
| Avg Tokens / Call | 平均每次调用 token 成本 |

多文件 bug 使用 file-level hit：只要 ground truth files 中任意一个文件出现在 Top-k 内，即视为 Top-k 命中。

## 6. Defects4J 结果

当前 Defects4J best current row 汇总如下：

| Project | Baseline / Retrieval | Best Current Method | LLM Calls | Top-1 | Top-3 | Top-5 | MRR |
|---|---|---|---:|---:|---:|---:|---:|
| Lang-20 | BM25 | BM25 + DeepSeek full rerank | 20 | 0.95 | 1.00 | 1.00 | 0.9750 |
| Math-20 | BM25 / hybrid | Hybrid/direct + compact evidence DeepSeek | 20 | 0.90 | 0.95 | 1.00 | 0.9350 |
| Chart-20 | Focused hybrid/direct | Focused hybrid/direct | 0 | 0.85 | 0.95 | 1.00 | 0.9040 |
| Time-20 | Focused hybrid/direct + test-prefix hints | Focused hybrid/direct + DeepSeek hard4 | 4 | 0.90 | 1.00 | 1.00 | 0.9500 |
| Closure-20 | Focused hybrid/direct | DeepSeek hard8 + pass-chain C13 + type-cycle C4 | 10 | 0.40 | 0.80 | 1.00 | 0.6225 |
| Mockito-20 | Focused hybrid/direct | Diagnostic hard7 + ByteBuddy M20 add-on | 8 | 0.55 | 0.90 | 1.00 | 0.7200 |

Macro average:

```text
Top-1: 0.7583
Top-3: 0.9333
Top-5: 1.0000
MRR:   0.8511
```

初步解释：

- 6 个 Defects4J pilot 项目均达到 Top-5 1.00。
- Lang、Math、Time 的结果较强，说明 LLM rerank 在高召回候选池上效果明显。
- Closure 和 Mockito 的 best row 包含 diagnostic add-on，因此当前更适合作为方法潜力证明，还不能直接声称完全自动化。
- 结果支持一个核心判断：LLM 适合作为 second-stage reranker，而不是替代 retrieval。

## 7. AboutWork 结果

AboutWork production-only 结果：

| Method | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production | 0 / 39 | 0.5897 | 0.8462 | 0.9487 | 0.9487 | 0.7171 |
| BM25 + selector_v3 + DeepSeek | 11 / 39 | 0.7692 | 1.0000 | 1.0000 | 1.0000 | 0.8675 |

提升：

```text
Top-1: 0.5897 -> 0.7692
Top-3: 0.8462 -> 1.0000
Top-5: 0.9487 -> 1.0000
MRR:   0.7171 -> 0.8675
```

意义：

- AboutWork 证明 pipeline 可以迁移到真实公司项目。
- selective rerank 只调用 11/39 个样本，约 28.2%，但 Top-3、Top-5、Top-10 均达到 1.00。
- 这说明真实项目中 LLM 不需要全量调用，关键是识别 BM25 可能犯错的样本。

限制：

- selector_v3 是在当前 39 条 bug log 上调出来的。
- 后续需要用新增 bug logs 验证泛化能力。

## 8. Easy Finance 结果

### 8.1 Clean63 主结果

Easy Finance clean63 production-only 结果：

| Method | Selected LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production | 0 / 63 | 0.3968 | 0.6825 | 0.8571 | 0.8730 | 0.5727 |
| BM25 + hard9 oracle | 9 / 63 | 0.4444 | 0.7778 | 0.9524 | 1.0000 | 0.6344 |
| BM25 + selector_v1 | 10 / 63 | 0.4603 | 0.7778 | 0.9524 | 1.0000 | 0.6450 |
| BM25 + selector_v1 UI evidence v2 | 10 / 63 | 0.4921 | 0.8095 | 0.9841 | 1.0000 | 0.6729 |

当前 clean63 最好结果：

```text
BM25 production + selector_v1 UI evidence v2 + DeepSeek rerank
selected: 10 / 63
Top-1:  0.4921
Top-3:  0.8095
Top-5:  0.9841
Top-10: 1.0000
MRR:    0.6729
tokens: 250902 total
```

主要改进来自：

- selector_v1 捕捉 backend area mismatch、management command noise、frontend domain mismatch。
- UI evidence v2 强化 `useQuery`、button loading、currency display、unreviewed count 等代码证据。
- Top-10 从 0.8730 提升到 1.0000，说明候选召回和 selective rerank 对真实项目有效。

### 8.2 Strict62 Sensitivity Analysis

strict62 排除 `easyfinance-frontend-20250930-001`。该样本的 bug text 提到 confirm expense/invoice buttons，但实际 fix touches 涉及 Continue/Create Invoice/View PDF loading 状态，bug text 与 touched-file ground truth 存在明显不一致。

Strict62 结果：

| Method | Selected LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production | 0 / 62 | 0.4032 | 0.6935 | 0.8710 | 0.8871 | 0.5810 |
| BM25 + selector_v1 UI evidence v2 | 9 / 62 | 0.5000 | 0.8226 | 1.0000 | 1.0000 | 0.6817 |
| BM25 + selector_v1 controlled agentic s2 | 9 / 62 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6831 |
| BM25 + selector_v1 agentic s2 + verifier | 9 / 62 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6804 |

解释：

- strict62 上 one-shot UI evidence v2 已达到 Top-5 和 Top-10 1.00。
- controlled agentic s2 的 MRR 略高于 one-shot，但 Top-3 略低，且 token 成本更高。
- verifier pass 没有提升结果，反而略降 MRR。

## 9. Agentic Inspection 与 Verifier 分析

### 9.1 Agentic Inspection

Easy Finance strict62 selector_v1 的 9 个样本上，agentic s2 单独结果：

```text
Top-1:  0.6667
Top-3:  0.8889
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.8056
tokens: 250481
```

合并回 62 条后：

```text
Top-1:  0.5000
Top-3:  0.8065
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.6831
```

初步结论：

- controlled agent protocol 技术上可运行。
- 工具 trace 可记录，输出 JSON 可评价，能接入现有 merge/evaluation pipeline。
- 但当前 Easy Finance strict62 上，agentic inspection 没有明显超过 one-shot UI evidence rerank。

### 9.2 Verifier Pass

verifier 额外结果：

```text
selected 9-case verifier:
Top-1:  0.6667
Top-3:  0.8889
Top-5:  1.0000
MRR:    0.7870
tokens: 80569

merged strict62:
Top-1:  0.5000
Top-3:  0.8065
Top-5:  1.0000
MRR:    0.6804
```

与 agent-only 对比：

| Method | Full Strict62 MRR | Total Tokens |
|---|---:|---:|
| Agentic s2 only | 0.6831 | 250481 |
| Agentic s2 + verifier | 0.6804 | 331050 |

初步结论：

- 当前 verifier-loop 是负向 ablation。
- independent verifier 没有提升 Top-k，反而因为 noisy top-10 evidence 把一个正确文件从 rank 2 降到 rank 4。
- 这说明更多 LLM 步骤不一定更好；证据选择质量比 agent step 数量更关键。

## 10. 成本分析

当前主要 LLM usage 汇总：

| Experiment | LLM Calls | Total Tokens | Avg Tokens / Call | Total Seconds | Avg Seconds / Call |
|---|---:|---:|---:|---:|---:|
| Math-20 full compact evidence | 20 | 536625 | 26831.3 | - | - |
| Math-20 selective rerank | 6 | about 188355 | about 31392.5 | - | - |
| Time-20 hard4 | 4 | about 117138 | 29284.5 | about 73.2 | 18.312 |
| Closure hard8 + C13 + C4 | 10 | 325602 | 32560.2 | about 193.5 | 19.351 |
| Mockito hard7 + M20 successful add-on | 8 | 177588 | 22198.5 | 167.729 | 20.966 |
| AboutWork selector_v3 | 11 | 303537 | 27594.3 | - | - |
| Easy Finance clean63 selector_v1 UI evidence v2 | 10 | 250902 | 25090.2 | 215.589 | 21.559 |
| Easy Finance strict62 selector_v1 UI evidence v2 | 9 | 226860 | 25206.7 | 188.506 | 20.945 |
| Easy Finance strict62 agentic s2 | 9 | 250481 | 27831.2 | 154.399 | 17.155 |
| Easy Finance strict62 verifier pass | 9 | 80569 | 8952.1 | 121.980 | 13.553 |

成本结论：

- selective rerank 是必要的。全量 rerank 在中大型项目上 token 成本较高。
- agentic s2 比 one-shot strict62 多约 10.4% tokens，但没有带来稳定收益。
- verifier 单次较便宜，但叠加在 agent 后总成本达到 331050 tokens，效果反而下降。

## 11. 初步结论

### 11.1 支持的结论

当前结果支持以下判断：

1. LLM-assisted fault localization 作为 second-stage reranker 是有效的。
2. 高召回、低噪声候选池是效果上限。
3. Prompt snippet / evidence 质量对 rerank 影响很大。
4. Selective rerank 是成本控制的关键。
5. 真实公司项目中，domain mismatch 和 retrieval noise 是主要错误来源之一。
6. Agentic inspection 可以运行，但当前还没有证明比精心设计的 one-shot rerank 更好。
7. Verifier-loop 当前是负向结果，说明 independent verification 需要更干净的 evidence selection。

### 11.2 对各 RQ 的初步回答

| RQ | 初步回答 |
|---|---|
| RQ1 | LLM rerank 在 Defects4J 多个项目上显著提升 Top-k，尤其当候选池召回足够时。 |
| RQ2 | 候选池召回和 snippet evidence 是主要瓶颈；真实文件不在候选池中时 LLM 无法补救。 |
| RQ3 | selective rerank 有效；AboutWork 只调用 11/39，Easy Finance 只调用 10/63 或 9/62，也能显著提升 Top-k。 |
| RQ4 | 方法可以迁移到 AboutWork 和 Easy Finance，但公司数据质量、commit-derived reports 和 selector overfitting 需要单独讨论。 |
| RQ5 | controlled agent 可运行，但当前不优于 one-shot；verifier pass 没有提升，属于负向 ablation。 |

## 12. 威胁与限制

### 12.1 Internal Validity

- ground truth 使用 fix commit touched files，可能包含伴随修改，而不一定都是 root cause。
- 多文件 bug 使用任一文件命中，可能高估实际定位能力。
- 一些 selector 和 evidence rule 是在当前样本上诊断后形成的，存在 fitted rule 风险。
- Closure 和 Mockito 的 best row 包含 diagnostic add-on，不能直接当作完全自动 selector 结果。

### 12.2 External Validity

- Defects4J 主要是 Java benchmark，不能完全代表真实多语言系统。
- AboutWork 和 Easy Finance 都是公司项目 case study，样本量仍有限。
- Easy Finance 的 bug reports 来自 git commit metadata，文本质量弱于人工 bug log。

### 12.3 Construct Validity

- 文件级定位比 method-level 或 line-level 更粗。
- Top-k accuracy 不能完全代表真实 debugging effort。
- token 成本、prompt 长度和模型版本变化会影响实际可用性。

### 12.4 Reproducibility Risk

- DeepSeek 模型版本可能变化。
- Defects4J checkout、compile、test 对本地 JDK、缓存和环境有依赖。
- 公司项目 worktree 和历史 commit 数据需要固定记录。

## 13. 下一步工作

短期优先级：

1. 把 Defects4J、AboutWork、Easy Finance 结果统一成最终论文表格。
2. 把 Closure / Mockito diagnostic add-on 改写为非 oracle selector 规则。
3. 为 Easy Finance 和 AboutWork 增加新 bug logs，验证 selector 泛化能力。
4. 对 agentic inspection 做更精准的 case selection，只在 one-shot snippet 明显不足的样本上测试。
5. 暂时不把 verifier-loop 作为主方法，而是作为 negative ablation 写入 RQ5。

论文写作建议：

- 主结果应强调 BM25/hybrid + selective LLM rerank。
- Agent/verifier 不要写成主要贡献，而应写成 exploratory extension。
- 公司项目结果要单独标注数据来源差异：AboutWork 是手写 bug log，Easy Finance 是 git-history-derived reports。
- Threats to Validity 中必须说明 touched-file ground truth 的局限。

## 14. 主要结果文件

主整理文档：

```text
project/fl-localizer/docs/results_integration_2026-05-27.md
project/fl-localizer/docs/stage_report_2026-05-27.md
project/fl-localizer/docs/current_results_report.md
project/fl-localizer/docs/worklog.md
```

Easy Finance agent/verifier 相关输出：

```text
project/fl-localizer/outputs/easy_finance_committed_strict62_agentic_deepseek_selector_v1_s2.jsonl
project/fl-localizer/outputs/easy_finance_committed_strict62_agentic_deepseek_selector_v1_s2_trace.jsonl
project/fl-localizer/outputs/easy_finance_committed_strict62_bm25_prod_plus_agentic_deepseek_selector_v1_s2_eval.json
project/fl-localizer/outputs/easy_finance_committed_strict62_agentic_plus_verifier_deepseek_selector_v1_s2.jsonl
project/fl-localizer/outputs/easy_finance_committed_strict62_bm25_prod_plus_agentic_verifier_deepseek_selector_v1_s2_eval.json
project/fl-localizer/outputs/easy_finance_committed_strict62_agentic_plus_verifier_deepseek_selector_v1_s2_usage.json
```

## 15. 一句话总结

当前实验已经证明：在高召回候选池基础上，selective LLM rerank 能显著提升文件级 fault localization，并且能迁移到真实公司项目；但 agentic inspection 和 verifier-loop 目前还只是探索性扩展，尚未超过精心设计的 one-shot selective rerank。
