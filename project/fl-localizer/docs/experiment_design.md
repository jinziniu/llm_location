# LLM-Assisted Fault Localization Experiment Design

生成日期：2026-05-26  
更新日期：2026-06-02

## 1. 实验目标

本实验研究一个面向 benchmark 和真实项目的文件级缺陷定位方法。给定一个 bug 的失败测试、stack trace、bug report、运行上下文和源码文件集合，系统输出最可能包含缺陷的文件排序。

本项目不直接做自动修复，而是解决自动修复前更基础的一步：

```text
Where is the bug?
```

当前方法主线是：

```text
Selective Evidence-Aware LLM Fault Localization
```

也就是先用 BM25 / focused hybrid retrieval 生成候选文件，再构造可控 evidence，最后只在必要样例上调用 LLM reranker。controlled agentic inspection 和 verifier rerank 作为扩展实验与消融实验，而不是当前主方法。

实验核心目标是验证：

- BM25 和 focused hybrid retrieval 能否提供高召回、低成本的候选文件集合。
- LLM reranker 能否在候选池上提升 Top-k accuracy 和 MRR。
- evidence 质量、snippet 选择和 stack trace 去噪是否影响 LLM 排序效果。
- selective rerank 能否减少 API 调用，同时保持主要准确率收益。
- 该方法能否从 Defects4J benchmark 迁移到 AboutWork 和 Easy Finance 这类真实项目数据。
- controlled agentic inspection / verifier 是否真的优于 one-shot rerank，还是只增加成本。

## 2. 研究问题

RQ1：与 BM25 和 focused hybrid retrieval baseline 相比，LLM rerank 是否能提升 Defects4J 上的文件级 fault localization 效果？

RQ2：候选召回质量和源码 evidence 质量如何影响 LLM rerank？失败主要来自 retrieval miss、snippet miss、噪声 evidence，还是模型排序错误？

RQ3：selective rerank 能否减少 LLM 调用量、token 成本和运行时间，同时保留 Top-k accuracy 与 MRR 的主要收益？

RQ4：该方法能否从 Defects4J 迁移到真实项目数据，包括 AboutWork bug logs 和 Easy Finance git-history-derived bug records？

RQ5：controlled agentic inspection 和 verifier rerank 是否能在 one-shot LLM rerank 之上进一步提升定位效果？如果不能，额外成本和失败原因是什么？

## 3. 实验对象

实验对象分为三组。

### 3.1 Defects4J Benchmark

Defects4J 用于可复现 benchmark 验证。当前已完成 6 个项目，每个项目 20 个 active bugs：

```text
Lang-20
Math-20
Chart-20
Time-20
Closure-20
Mockito-20
```

每个 bug record 包含：

- `bug_id`
- `project`
- `bug_report.id`
- `bug_report.url`
- `test_failure`
- `triggering_tests`
- `stack_trace`
- `repo_path`
- `source_dir`
- `buggy_commit`
- `fixed_commit`
- `ground_truth.classes`
- `ground_truth.files`

其中 `ground_truth`、fixed commit diff 和 post-fix code 只用于评价，不能进入 prompt、agent tools 或 selector 规则。

### 3.2 AboutWork Bug Logs

AboutWork 是真实公司 bug log 数据，用于检验方法在人工记录 bug 描述、业务上下文和真实 repo 文件结构下的表现。

当前数据状态：

```text
records: 39
baseline: BM25 production
main method: BM25 production + selector_v3 + DeepSeek rerank
```

该数据集适合回答 RQ4：benchmark 中有效的方法是否能迁移到公司日常 bug log。

### 3.3 Easy Finance Git-History Cases

Easy Finance 是基于真实项目修复提交构造的 case study 数据，用于检验方法在 frontend/backend、UI bug、业务逻辑 bug 和真实 commit 历史中的表现。

当前主要数据版本：

```text
clean63
strict62
```

Easy Finance 当前也是 controlled agentic inspection 和 verifier rerank 的主要试验场。已有结果显示 agentic/verifier 技术上可运行，但暂时没有稳定超过 one-shot UI evidence rerank。

## 4. 系统流程

整体 pipeline：

```text
bug source collection
-> repository checkout / source snapshot
-> build bug JSONL dataset
-> index source files
-> BM25 retrieve top-k candidate files
-> focused hybrid retrieval / direct evidence expansion
-> evidence and snippet construction
-> selector decides whether to call LLM
-> one-shot LLM rerank selected cases
-> optional controlled agentic inspection
-> optional verifier rerank
-> validate model output
-> fill missing slots with retrieval fallback
-> evaluate against ground truth
-> summarize metrics, token usage, runtime
-> append worklog
```

主方法到 one-shot LLM rerank 为止。agentic 和 verifier 属于 RQ5 扩展，不应和主方法混在一起报告。

## 5. 方法设计

### 5.1 BM25 Baseline

BM25 是第一阶段候选生成器。查询由以下信息拼接：

```text
bug_report.id
bug_report.text
test_failure
triggering_tests
stack_trace runtime context
UI / business context when available
```

每个源码文件被索引为一个文档，文档内容包括文件路径、包名、类名、方法名和源码文本中的可检索信息。

主要输出：

```text
outputs/*_bm25.jsonl
outputs/*_bm25_top50.jsonl
```

BM25 结果有两个作用：

- 作为 baseline 直接评价。
- 作为 focused hybrid retrieval 和 LLM rerank 的候选输入。

### 5.2 Focused Hybrid Retrieval

Focused hybrid retrieval 在 BM25 上加入 deterministic signals，用于提高 candidate recall 和降低噪声：

- stack trace class matching
- triggering test matching
- exception type / method name / class name extraction
- identifier overlap
- direct file/path hint
- relevant failure-section filtering
- framework-specific evidence expansion when justified

对 Defects4J，hybrid retrieval 重点处理 `Math-12`、`Math-15`、`Closure-13`、`Closure-4`、Mockito ByteBuddy/MockMaker 这类 BM25 容易漏掉或被噪声误导的 case。

对真实项目，hybrid retrieval 还需要处理：

- UI component name 和 bug report wording 不一致。
- frontend route、page、store、API client 分布在多个文件。
- commit 修改文件不一定都是真正 root cause。

### 5.3 Evidence Construction

LLM 不直接读取整个仓库，而是接收固定大小的 evidence package：

- bug report / issue text
- failure message
- triggering tests or reproduction context
- stack trace after focused filtering
- candidate file path, class name, method names
- deterministic retrieval evidence
- source snippets
- UI or domain hints when available

snippet 选择需要避免两个问题：

- 真实相关方法没有被截取到，导致模型无法排序。
- 重复 stack frame 或大型工具类片段污染 prompt。

已有 Closure-4 结果说明，snippet scoring 对结果影响很大。加入 `handleTypeCycle` 和 `"Cycle detected in inheritance chain"` 后，`NamedType.java` 从候选 rank 49 被 DeepSeek 排到 rank 2。

### 5.4 Selective Rerank Gate

为了控制 API 成本，默认不对每个 bug 都调用 LLM。系统先运行 BM25 / focused hybrid retrieval，再由 selector 选择低置信或语义不匹配样例。

当前 selector 信号包括：

```text
top score gap / score ratio
top-1 candidate direct hint missing
too many direct class hints
stack trace or snippet evidence ambiguity
domain-specific pattern triggers
```

selector 必须是 non-oracle：不能使用 ground truth、fixed commit diff 或 post-fix code。

### 5.5 One-shot LLM Rerank

One-shot LLM rerank 是当前主方法。输入为 selected bug 的候选文件和 evidence package。默认 provider 是 DeepSeek API。

结构化输出格式：

```json
{
  "ranked_files": [
    {
      "file": "src/main/java/...",
      "confidence": 0.0,
      "reason": "..."
    }
  ]
}
```

系统会做输出规范化：

- 过滤不在候选池中的文件。
- 去重。
- 保留前 `top-output` 个有效文件。
- 如果模型返回不足，则按 retrieval 顺序 fallback 补齐。
- 记录 invalid files、duplicate files、fallback count。

当前默认参数：

```text
top_candidates: 50
top_output: 10
provider: deepseek
model: deepseek-v4-flash
```

### 5.6 Controlled Agentic Inspection

Controlled agentic inspection 是 RQ5 扩展实验。它不是让模型自由探索整个仓库，而是在固定预算下使用有限工具：

```text
search files
read selected file snippets
inspect candidate metadata
produce final JSON ranking
```

实验约束：

- 固定最大 step 数。
- 固定候选池。
- 固定工具输出格式。
- 记录每一步 tool trace。
- 不允许访问 ground truth、fixed commit diff 或 post-fix code。

当前 Easy Finance strict62 pilot 说明：agentic inspection 可以稳定运行并生成合法 JSON，但相对 one-shot UI evidence rerank 没有清晰提升，且 token 成本更高。因此现阶段应作为 RQ5 消融和讨论材料，而不是主方法。

### 5.7 Verifier Rerank

Verifier rerank 是 agentic 之后的独立检查步骤。它接收 bug report、agent top-10、固定 snippets 和 prior observations，再输出最终排序。

当前 Easy Finance strict62 结果显示 verifier 没有提升 agentic ranking，反而略降 MRR，并增加明显 token 成本。因此 verifier 暂时作为 negative ablation：

```text
Do not use verifier as the main method.
```

后续如果继续做 verifier，应只针对 one-shot 或 agentic 明确失败的 case，并改进 verifier 的输入质量。

## 6. 实验变量

自变量：

- 方法：BM25、focused hybrid retrieval、selective one-shot DeepSeek rerank、controlled agentic inspection、agentic + verifier。
- 数据集：Defects4J、AboutWork、Easy Finance。
- 候选池大小：top-20、top-50、top-80。
- snippet 策略：compact evidence、UI evidence、type-cycle evidence、pass-chain evidence、state-reset evidence。
- selector 策略：none、generic selector、project-specific selector、company-data selector。
- 模型后端：DeepSeek API；Codex backend 仅保留为未来工程对比，不再作为当前核心 RQ。

因变量：

- Top-1 accuracy
- Top-3 accuracy
- Top-5 accuracy
- Top-10 accuracy when available
- MRR
- Candidate Recall@k
- selected cases / total cases
- total tokens
- avg tokens per selected bug
- avg duration per selected bug
- invalid output count
- duplicate output count
- fallback added count

控制变量：

- 同一数据版本。
- 同一源码快照或 buggy checkout。
- 同一 evaluator。
- 同一 ground truth。
- rerank 和 agent 工具不暴露 ground truth、fixed commit diff 和 post-fix code。

## 7. 评价指标

### 7.1 Top-k Accuracy

如果 ground-truth 文件出现在模型输出的前 k 个文件中，则该 bug 在 Top-k 上为成功。

当前使用：

```text
Top-1
Top-3
Top-5
Top-10 for company datasets when reported
```

### 7.2 MRR

MRR 衡量第一个正确文件的排名：

```text
MRR = average(1 / rank_of_first_correct_file)
```

如果没有命中，记为 0。

### 7.3 Candidate Recall

在 rerank 前，先检查候选池是否包含 ground-truth 文件：

```text
Recall@k = bugs whose ground-truth file appears in candidate top-k / total bugs
```

这用于区分两种失败：

- Retrieval miss：真实文件不在候选池，rerank 无法成功。
- Rerank miss：真实文件在候选池，但模型没有排到前面。

### 7.4 成本和稳定性指标

成本指标：

- selected ratio
- total tokens
- avg tokens per selected case
- total duration
- avg duration per selected case

稳定性指标：

- JSON parse success rate
- invalid file count
- duplicate file count
- fallback count
- tool trace completeness for agentic runs

### 7.5 多文件 Bug 的处理

当前评价采用宽松 file-level hit：

```text
只要任一 ground-truth file 出现在 top-k 中，就算命中。
```

后续应补充严格指标：

```text
All-file recall: 所有 ground-truth files 都被召回或命中。
Partial recall: 命中的 ground-truth files / 全部 ground-truth files。
```

## 8. 实验步骤

### 8.1 Defects4J 数据生成

示例：

```bash
python3 scripts/build_defects4j_dataset.py \
  --project Math \
  --first-active 20 \
  --out data/defects4j/math_pilot_20.jsonl
```

### 8.2 运行 BM25 / Retrieval Baseline

```bash
python3 scripts/run_bm25.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --out outputs/math_pilot_20_bm25.jsonl \
  --top-k 10

python3 scripts/run_bm25.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --out outputs/math_pilot_20_bm25_top50.jsonl \
  --top-k 50
```

### 8.3 运行 One-shot DeepSeek Rerank

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --bm25 outputs/math_pilot_20_bm25_top50.jsonl \
  --out outputs/math_pilot_20_rerank_deepseek.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 12
```

### 8.4 运行 Agentic / Verifier 扩展

Agentic 和 verifier 只用于 RQ5，不替代主方法。

```bash
python3 scripts/run_agentic_rerank.py \
  --bugs data/easy_finance/easy_finance_committed_strict62.jsonl \
  --bm25 outputs/easy_finance_committed_strict62_bm25_prod_top50.jsonl \
  --out outputs/easy_finance_committed_strict62_agentic_deepseek_selector_v1_s2.jsonl \
  --provider deepseek

python3 scripts/run_verifier_rerank.py \
  --bugs data/easy_finance/easy_finance_committed_strict62.jsonl \
  --agentic outputs/easy_finance_committed_strict62_agentic_deepseek_selector_v1_s2.jsonl \
  --out outputs/easy_finance_committed_strict62_agentic_plus_verifier_deepseek_selector_v1_s2.jsonl \
  --provider deepseek
```

### 8.5 评价和 Usage 汇总

```bash
python3 scripts/evaluate_predictions.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --pred outputs/math_pilot_20_rerank_deepseek.jsonl \
  --per-bug \
  > outputs/math_pilot_20_rerank_deepseek_eval.json

python3 scripts/summarize_llm_usage.py \
  --pred outputs/math_pilot_20_rerank_deepseek.jsonl \
  --out outputs/math_pilot_20_rerank_deepseek_usage.json
```

### 8.6 写入 Worklog

每次实验必须记录：

- 日期。
- 实验目标。
- 输入数据。
- 命令。
- 输出文件。
- 主要指标。
- 异常和失败样本。
- 结论和下一步。

## 9. 当前结果摘要

### 9.1 Defects4J 当前最佳结果

当前 Defects4J 六项目 120 bugs 的阶段性最佳 macro 结果：

```text
Top-1: 0.7750
Top-3: 0.9500
Top-5: 1.0000
MRR:   0.8644
```

| Project | Bugs | Current best method | LLM calls | Top-1 | Top-3 | Top-5 | MRR |
|---|---:|---|---:|---:|---:|---:|---:|
| Lang | 20 | BM25 + DeepSeek full rerank | 20 | 0.95 | 1.00 | 1.00 | 0.9750 |
| Math | 20 | Hybrid/direct + compact evidence DeepSeek | 20 | 0.90 | 0.95 | 1.00 | 0.9350 |
| Chart | 20 | Focused hybrid/direct | 0 | 0.85 | 0.95 | 1.00 | 0.9040 |
| Time | 20 | Focused hybrid/direct + DeepSeek hard4 | 4 | 0.90 | 1.00 | 1.00 | 0.9500 |
| Closure | 20 | DeepSeek hard8 + pass-chain C13 + type-cycle C4 | 10 | 0.40 | 0.80 | 1.00 | 0.6225 |
| Mockito | 20 | Tight selector9 + DeepSeek | 9 | 0.65 | 1.00 | 1.00 | 0.8000 |

注意：Closure 和 Mockito 仍包含 targeted/diagnostic add-ons。论文报告时需要把这些标为 targeted selector 或 diagnostic evidence，而不是完整全量 rerank。

### 9.1.1 Fresh / Held-Out Validation

为区分探索性调参和可报告的泛化证据，后续结果分为 fresh validation 和 frozen held-out validation。

| Dataset | Setting | Bugs | LLM calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Closure-21..60 | focused retrieval baseline | 40 | 0 | 0.3000 | 0.4250 | 0.5750 | 0.7250 | 0.4211 |
| Closure-21..60 | cost-control v3 + DeepSeek | 40 | 20 | 0.6000 | 0.8000 | 0.9750 | 1.0000 | 0.7348 |
| Closure-61..80 held-out | frozen retrieval baseline | 19 | 0 | 0.4737 | 0.4737 | 0.5789 | 0.7368 | 0.5344 |
| Closure-61..80 held-out | frozen cost-control v3 + DeepSeek | 19 | 6 | 0.6316 | 0.7368 | 0.7895 | 0.8947 | 0.7018 |
| Mockito-31..38 fresh | focused retrieval baseline | 8 | 0 | 0.1250 | 0.5000 | 0.7500 | 0.8750 | 0.3382 |
| Mockito-31..38 fresh | cost-control v2 + DeepSeek | 8 | 4 | 0.6250 | 1.0000 | 1.0000 | 1.0000 | 0.7500 |

解释：

- `Closure-61..80` 是当前第一组明确 frozen protocol held-out run，协议见 `docs/frozen_protocol_2026-06-01.md`。
- `Closure-61..80` 在 selector 只调用 6/19 的情况下提升 Top-1、Top-3、Top-5、Top-10 和 MRR，但 selector 漏选 `Closure-61`、`Closure-65`、`Closure-67`、`Closure-75`。
- `Closure-21..60` 和 `Mockito-31..38` 支持 selector/rerank 方向，但仍应标注为 fresh / experimental validation，而不是最终冻结协议。
- 后续新协议可以使用这些 false negatives 做 error analysis，但不能反向修改已经报告的 frozen held-out 结果。

### 9.2 AboutWork 当前结果

AboutWork 数据集：

```text
records: 39
```

| Method | LLM calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production | 0 | 0.5897 | 0.8462 | 0.9487 | 0.9487 | 0.7171 |
| BM25 + selector_v3 + DeepSeek | 11 | 0.7692 | 1.0000 | 1.0000 | 1.0000 | 0.8675 |

该结果支持 RQ4：在真实 bug log 上，selective LLM rerank 可以用较少调用提升排序质量。

### 9.3 Easy Finance 当前结果

Easy Finance clean63：

| Method | LLM calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production top50 | 0 | 0.3968 | 0.7302 | 0.8730 | 0.8730 | 0.5684 |
| BM25 + selector_v1 | 10 | 0.4603 | 0.7778 | 0.9524 | 1.0000 | 0.6450 |
| BM25 + selector_v1 UI evidence v2 | 10 | 0.4921 | 0.8095 | 0.9841 | 1.0000 | 0.6729 |

Easy Finance strict62：

| Method | LLM calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 + selector_v1 UI evidence v2 | 9 | 0.5000 | 0.8226 | 1.0000 | 1.0000 | 0.6817 |
| BM25 + selector_v1 controlled agentic s2 | 9 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6831 |
| BM25 + selector_v1 agentic s2 + verifier | 9 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6804 |

解释：

- UI evidence v2 是当前 Easy Finance 主结果。
- controlled agentic s2 技术上跑通，但没有清晰超过 one-shot。
- verifier 增加 token 成本但没有提升结果，应作为 negative ablation。

## 10. 结果分析计划

每个数据集输出四类表：

1. 方法整体指标表。
2. 候选召回表。
3. selected-case 成本表。
4. per-bug rank change / error type 表。

主结果表应分组报告：

- Retrieval baseline：BM25、focused hybrid。
- Main method：selective one-shot DeepSeek rerank。
- Extension：controlled agentic inspection。
- Ablation：verifier、snippet strategy、selector strategy。

错误分析分类：

- Retrieval miss。
- Candidate present but rerank miss。
- Weak snippet / missing method evidence。
- Noisy stack trace。
- Ambiguous bug report。
- Multi-file partial hit。
- Large utility class。
- Selector false negative。
- Model output invalid。
- Agent tool-use not helpful。
- Verifier over-correction。

## 11. 有效性威胁

内部有效性：

- ground truth 来自 modified files/classes，可能包含非 root cause 改动。
- 多文件 bug 目前使用任一文件命中，可能高估效果。
- prompt、snippet 和 selector 是方法的一部分，会显著影响 LLM 表现。
- Closure、Mockito 的部分结果包含 targeted evidence add-ons，需要和全量自动方法区分。
- Easy Finance 的 commit-derived ground truth 可能受重构、格式化或顺手修改影响。

外部有效性：

- Defects4J 是 Java benchmark，不能直接代表所有语言和工业项目。
- AboutWork 和 Easy Finance 是公司/项目 case study，样本量仍有限。
- API 模型版本可能变化，影响复现实验。
- 公司 bug log 的记录风格会影响可迁移性。

构造有效性：

- 文件级定位比方法级或行级定位更粗。
- Top-k accuracy 不能完全代表开发者真实调试成本。
- 候选池大小会影响 rerank 上限。
- selector selected ratio 影响成本和准确率，需要和完整 rerank 分开解释。

结论有效性：

- 当前 Defects4J 主 pilot 样本量为 120 个 bugs，另有 Closure/Mockito fresh 与 held-out validation；仍不足以支持全库强统计结论。
- company datasets 还需要更多 bug logs 或更多项目交叉验证。
- agentic/verifier 当前只有 pilot 结论，不能过度推广。

## 12. 阶段安排

第一阶段：原型和 Defects4J pilot，已完成。

- Defects4J 环境。
- 数据生成脚本。
- BM25 baseline。
- DeepSeek rerank。
- evaluator。
- worklog。
- Lang-20、Math-20、Chart-20、Time-20、Closure-20、Mockito-20。
- Focused hybrid retrieval。
- Selective rerank gate。
- Closure pass-chain / type-cycle diagnostics。
- Mockito tight selector9 diagnostics。

第二阶段：真实项目 case study，已完成初版。

- AboutWork bug log dataset。
- AboutWork selector_v3 + DeepSeek。
- Easy Finance clean63 / strict62。
- Easy Finance UI evidence v2。
- Easy Finance controlled agentic s2 pilot。
- Easy Finance verifier negative ablation。

第三阶段：整理最终实验设计和结果报告，当前进行中。

- 2026-06-01 已完成第一轮 frozen held-out validation：`Closure-61..80`，19 records，selector 6/19，merged Top-5 0.7895、Top-10 0.8947、MRR 0.7018。
- 当前需要把 frozen held-out 和 fresh validation 分开写入论文结果章节。
- 2026-06-02 已新增论文结果草稿与 held-out selector error analysis：
  - `docs/results_chapter_draft_2026-06-02.md`
  - `docs/closure_heldout_61_80_selector_error_analysis.md`

- 将 proposal、experiment design、current results report 对齐。
- 把主方法、extension 和 ablation 分开报告。
- 更新结果表和 RQ 对应关系。
- 明确 no-leakage 规则。

第四阶段：补强实验。

- 对 selector 做 non-oracle validation。
- 对 Closure / Mockito 的 targeted evidence 做自动化规则验证。
- 在 Easy Finance 上只针对 one-shot 失败样例重新设计 agentic run。
- 选择是否补跑更多 AboutWork bug logs。

第五阶段：论文写作。

- 方法章节。
- 实验设计章节。
- 结果章节。
- 错误分析。
- 有效性威胁。
- 工程复现说明。

## 13. 预期贡献

本项目最终可以形成以下贡献：

- 一个从 Defects4J benchmark 到真实项目 case study 的文件级 fault localization 实验框架。
- 一个 selective evidence-aware LLM rerank 方法，结合 retrieval、evidence construction 和 selective invocation。
- 关于候选召回、snippet 质量、stack trace 噪声和 selector 成本控制的系统性分析。
- 对 AboutWork 和 Easy Finance 真实项目数据的迁移验证。
- 对 controlled agentic inspection 和 verifier rerank 的实证分析，包括 negative findings。
- 一套可复现的脚本、输出、worklog 和阶段性结果报告。
