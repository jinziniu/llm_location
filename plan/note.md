我建议你的实验设计成 “Benchmark Validation + Real-World Case Study”，不要把它设计成“benchmark vs real data 谁更好”。导师会议里已经明确认可这个方向：先在 benchmark 上验证你的方法，再把同一个方法应用到 Capstone/真实项目数据上，作为 case study chapter。

你的 thesis 实验可以围绕一句话展开：

This thesis evaluates whether a context-aware LLM agent can localize faults first on standard bug localization benchmarks, and then in a real-world repository case study where bug information comes from heterogeneous sources such as issue reports, logs, project structure, commits, and developer artifacts.

1. 总体实验结构

你的实验最好分成两个阶段。

阶段	目的	数据	结论类型
Experiment 1: Benchmark validation	证明你的方法在标准数据集上能工作，并且可以和已有方法比较	Defects4J / Bench4BL	controlled validation
Experiment 2: Real-world case study	证明你的方法在真实项目中如何使用，特别是多来源信息是否有帮助	Capstone / 真实项目仓库	practical evaluation

这个结构正好对应你 literature study 的 gap：现有 LLM-based fault localization 大多在 Defects4J 等 benchmark 上评估，缺少真实 repository-level validation；同时，不同 context level 和 independent verification 对 fault localization 的影响还没有被系统评估。

2. 推荐的 Research Questions

你可以把实验设计直接写成 4 个 RQ。

RQ1: Benchmark performance

RQ1: How accurately can the proposed LLM-based fault localization approach identify faulty files/methods on established benchmarks?

这个 RQ 用 benchmark 回答。目的是说明你的方法不是只在你自己的 Capstone case 上有效，而是在标准数据集上也能运行。

建议指标：

粒度	指标
File-level	Top-1, Top-3, Top-5 accuracy
Method-level	Top-1, Top-3, Top-5 accuracy
Ranking quality	MRR / MAP，可选
Cost	average tokens, average runtime, average number of LLM calls
RQ2: Context effect

RQ2: How does the amount and type of context affect fault localization accuracy?

这是你最重要的实验问题之一。你的核心创新不是“我用了 LLM”，而是：

我系统比较不同 bug context 对 fault localization 的影响。

你可以设计 4 个输入设置：

Setting	Input to LLM	目的
C0	Bug report only	最少信息 baseline
C1	Bug report + repository structure	看项目结构是否有帮助
C2	Bug report + retrieved code snippets	看代码检索是否有帮助
C3	Bug report + code snippets + stack trace/test failure/logs	看 runtime evidence 是否有帮助
C4	C3 + historical fix/context, if available	看历史信息是否有帮助

注意：不是每个数据源都有所有信息，所以 benchmark 和 case study 可以使用不同 context。关键是你要明确记录每个 bug 可用的信息。

RQ3: Agentic verification effect

RQ3: Does an independent verification agent improve the reliability of LLM-based fault localization?

这对应你 literature study 里提到的 Glasswing-style “agentic discovery + independent verification” gap。你的方法可以有两个版本：

Version	Description
Single-agent localization	一个 agent 直接输出 suspicious files/functions
Localization + verifier agent	第一个 agent 输出候选位置，第二个 agent 独立检查、重排、拒绝不合理结果

评估方式：

比较	看什么
Single-agent vs verifier-agent	Top-k accuracy 是否提升
Verifier 是否降低 false positives	Top-5 里不相关文件是否减少
Verifier 是否增加成本	token/runtime 是否明显增加
Verifier 是否过度保守	是否把正确答案排低或删掉
RQ4: Real-world applicability

RQ4: How does the proposed approach perform in a real-world repository case study with heterogeneous bug information?

这个 RQ 用 Capstone/真实项目回答。导师也说了：benchmark 后面可以加 case study，而且可以作为 thesis 的单独一章。

这里不要硬和 benchmark 做同等比较。真实 case study 的重点是：

在真实项目里，这个方法是否能帮助定位 bug？哪些信息源最有帮助？哪里失败？为什么失败？

3. Benchmark 选择

我建议你主 benchmark 用 Defects4J，可选再加 Bench4BL。

首选：Defects4J

Defects4J 适合你的第一阶段实验，因为它是 Java 真实 bug benchmark，带有可复现 bug 和实验基础设施。官方 README 现在显示 Defects4J 3.0.1 包含 854 个 active bugs，且每个 bug 通常有 issue tracker 信息、single fixing commit、buggy/fixed revision 和 triggering test。

你可以从 Defects4J 里抽样，例如：

Dataset subset	建议
项目	Chart, Lang, Math, Time, Mockito, Closure 中选 3–5 个
bug 数量	先做 30–50 个 pilot，最终做 100–200 个
粒度	file-level + method-level
ground truth	fixing commit 修改的 source file/method

为什么不一开始做全部 854 个？因为 LLM 成本、prompt 构建、代码检索、运行环境都会很耗时。你可以在 proposal 里说：先做 pilot subset，再根据时间扩展。

可选：Bench4BL

Bench4BL 更适合 bug report-based localization，因为它本身就是 bug reports 和对应 source-code files 的集合。官方 README 描述它包含 10,017 个 bug reports，来自 51 个开源项目，每个 bug report 都映射到对应版本的 source code files，用于支持 bug localization research。

Bench4BL 的优点是更贴近“从 bug report 定位代码文件”；缺点是项目多、环境旧、ground truth 和构建环境可能更难处理。

我的建议：

优先级	数据集	用法
Main benchmark	Defects4J	controlled validation，容易复现
Secondary benchmark, optional	Bench4BL	bug-report-driven file localization
Alternative, optional	BugsInPy	如果你想测试 Python；BugsInPy 官方目标是支持 real-world Python projects 的可复现实验研究。
4. Case study 数据怎么设计

你的第二阶段用 Capstone/真实项目。这里你需要自己构建一个 small but clean dataset。

Case study 的 bug 样本选择

建议选 10–20 个真实 bug，不要一开始选太多。

每个 bug 最好满足这些条件：

条件	原因
有明确 bug report / Jira issue / developer note	LLM 需要输入问题描述
有对应 fixing commit 或 PR	需要 ground truth
bug fix 修改了 source code，而不只是文档/配置	才能做 fault localization
bug 不是超大重构	否则 ground truth 不清楚
最好能复现失败或至少有错误日志	有助于 verifier/test agent
项目结构你能理解	方便 manual validation
每个 bug 记录成一条 dataset entry

你可以为每个真实 bug 建一个 JSON 文件，格式类似：

{
  "bug_id": "CAPSTONE-001",
  "project": "project-name",
  "bug_report": "User cannot submit the form when ...",
  "source": {
    "jira": "...",
    "bitbucket_issue": "...",
    "website_report": "...",
    "developer_note": "..."
  },
  "buggy_commit": "abc123",
  "fix_commit": "def456",
  "changed_files": [
    "backend/src/main/java/.../OrderService.java"
  ],
  "changed_methods": [
    "OrderService.validateOrder"
  ],
  "stack_trace": "...",
  "logs": "...",
  "test_failure": "...",
  "repository_structure": "...",
  "notes": "manual validation notes"
}

这样你的 case study 会非常清楚，导师也容易接受。

5. 你的方法应该怎么设计

你之前和导师说过想做多个 agents：一个收集 bug 信息，一个理解代码结构，一个定位代码，一个验证结果。这个方向是可以的，但 thesis 里最好不要搞得太复杂。建议设计成 4-stage pipeline。

Stage 1: Bug Context Collector

输入：

来源	Benchmark	Case study
bug report / issue title / description	Defects4J issue / Bench4BL report	Jira / Bitbucket / website / developer note
failing test / stack trace	Defects4J triggering test	CI logs / manual logs
repository metadata	project tree	frontend/backend/module structure
fixing commit	only for ground truth, not input	only for ground truth, not input

输出：

Structured bug context:
- Symptom
- Expected behavior
- Actual behavior
- Error messages
- Affected feature/module
- Mentioned files/classes/functions
- Candidate keywords

注意：fixing commit 不能作为 localization input，否则数据泄漏。fixing commit 只能用于 evaluation ground truth。

Stage 2: Repository Retrieval Agent

这个 agent 不要直接把整个 repo 塞给 LLM。你应该先做检索。

输入：

Structured bug context + repository index

检索候选代码：

方法	简单实现
keyword search	bug report keywords match file names, class names, function names
embedding retrieval	用 code/text embedding 找 top-k files
structure rule	如果 bug report 提到 frontend/API/service，就优先对应模块
stack trace extraction	如果 stack trace 提到 class/method，直接加入候选
dependency expansion	对 top files 加上 caller/callee 或 import files

输出：

Top-20 candidate files
Top-50 candidate methods/snippets
Stage 3: Localization Agent

输入：

bug context + repository structure + retrieved code snippets

输出一个 ranked list：

[
  {
    "rank": 1,
    "file": "src/main/java/.../OrderService.java",
    "method": "validateOrder",
    "reason": "The bug report describes incorrect validation when ... This method checks ..."
  },
  {
    "rank": 2,
    "file": "src/main/java/.../OrderController.java",
    "method": "submitOrder",
    "reason": "..."
  }
]

你需要要求 LLM 输出固定格式，方便自动计算 Top-k。

Stage 4: Verification Agent

Verifier 不应该看到 fixing commit。它只能基于 bug report、候选代码、logs/tests 来判断候选位置是否合理。

Verifier 的任务：

动作	输出
检查候选位置是否和 bug symptom 一致	accept/reject
解释为什么该位置可能导致 bug	reasoning summary
根据 evidence 重新排序	re-ranked top-k
如果有测试/日志，检查是否能解释失败	verification note

输出：

{
  "verified_ranking": [
    {
      "rank": 1,
      "file": "...",
      "method": "...",
      "verdict": "likely",
      "evidence": "..."
    }
  ],
  "rejected_candidates": [
    {
      "file": "...",
      "reason": "The file is related to UI rendering but the failure happens in backend validation."
    }
  ]
}
6. Baselines 怎么设置

你至少需要 3 类 baseline。

Baseline A: Information Retrieval baseline

这是最容易实现、也最重要的 baseline。

Baseline	Description
BM25 / keyword search	bug report 和 source files 做文本匹配
Embedding retrieval	bug report embedding 和 code snippet embedding 相似度
File-name/class-name matching	简单关键词规则

这类 baseline 证明你的 agent 不是只比 random 好。

Baseline B: Traditional fault localization baseline

如果你使用 Defects4J，并且能运行 tests/coverage，可以加：

Baseline	Description
Tarantula	SBFL suspiciousness formula
Ochiai	常用 SBFL baseline
DStar	可选

但注意：你的方法可能是 bug-report/code-context based，不一定依赖 coverage。传统 SBFL 需要 failing/passing tests 和 coverage，所以它适合 Defects4J，不一定适合 Capstone。

Baseline C: Simple LLM baseline

这是你必须有的。

Baseline	Input
LLM-simple	bug report only
LLM-code	bug report + retrieved code
Your method	bug report + structured context + retrieval + verifier

这样你能证明：提升来自你的 pipeline，而不是“随便问 LLM”。

7. 实验条件设计：最关键的 ablation

你的实验核心应该是 ablation study。也就是逐步加信息，看性能变化。

推荐设计：

Variant	Bug report	Repo structure	Retrieved code	Logs/tests/stack trace	Verifier
V0 IR baseline	✓	✗	index only	✗	✗
V1 LLM-basic	✓	✗	✗	✗	✗
V2 LLM+structure	✓	✓	✗	✗	✗
V3 LLM+retrieved code	✓	✓	✓	✗	✗
V4 LLM+runtime evidence	✓	✓	✓	✓	✗
V5 Full agentic pipeline	✓	✓	✓	✓	✓

你的 thesis 亮点就来自这张表。

8. Metrics 怎么定义
Benchmark metrics

用标准 Top-k。

Metric	Definition
Top-1 file accuracy	ranked first file 是否包含 ground-truth changed file
Top-3 file accuracy	top 3 files 是否包含 ground-truth changed file
Top-5 file accuracy	top 5 files 是否包含 ground-truth changed file
Method-level Top-k	top k methods 是否包含 ground-truth changed method
MRR	正确位置排名越靠前分数越高
Recall@k	如果一个 bug 有多个 changed files，top-k 覆盖多少
Cost	每个 bug 平均 tokens / LLM calls / runtime

Method-level 会比 file-level 难。如果时间紧，file-level 必做，method-level 可选。

Case study metrics

真实项目不一定有完美 ground truth，所以用混合指标。

Metric	用法
File-level hit	Top-k 是否包含 fixing commit 修改文件
Method-level hit	Top-k 是否包含修改方法
Manual relevance	你人工判断候选位置是否与 bug 相关
Explanation usefulness	候选解释是否能帮助 developer 理解 bug
Context usefulness	哪些信息源帮助最大
Failure analysis	agent 为什么失败

Case study 里最重要的是 qualitative analysis。比如：

Bug	Top-1?	Top-5?	Which context helped?	Failure reason
CAP-001	yes	yes	stack trace + service name	-
CAP-002	no	yes	repository structure	similar class confused model
CAP-003	no	no	none	bug report too vague
9. Ground truth 怎么定义

这是实验里最容易被导师问的问题。

Benchmark ground truth

Defects4J 的 bug 通常有 buggy/fixed revision 和 fixing commit，你可以把 fixing commit 修改的 source files/methods 作为 ground truth。Defects4J 官方说明每个 bug 是 single fixing commit，且修复是修改 source code，而不是配置、文档或测试文件。

你的定义可以写成：

A prediction is considered correct at file level if at least one of the files in the top-k ranked list matches a source file modified by the official fixing commit.

如果一个 bug 修改多个文件：

情况	处理方式
LLM 命中任意一个 modified source file	Top-k hit
LLM 命中所有 modified source files	strict hit，可选
只修改 test 文件 / config 文件	从 dataset 排除
Case study ground truth

真实项目用 fixing commit / PR diff 定义。

排除规则：

排除情况	原因
fix 是大规模重构	难以判断 fault location
fix 只改配置/文档	不属于 source-code FL
bug report 过于模糊且无 commit	无法评估
fix commit 混合多个 bug	ground truth 不干净
10. 具体实验流程

你可以按这个流程做。

Step 1: Pilot experiment

先选：

数据	数量
Defects4J bugs	20–30
Capstone bugs	3–5

目标不是追求大规模，而是验证 pipeline 能跑通。

你要检查：

检查点	是否成功
能自动 checkout buggy version	yes/no
能提取 bug report / issue text	yes/no
能建立 repository index	yes/no
能检索 candidate files	yes/no
LLM 能输出 JSON ranking	yes/no
能自动计算 Top-k	yes/no
verifier 是否能稳定输出	yes/no
Step 2: Full benchmark experiment

扩大到：

数据	建议数量
Defects4J	100–200 bugs
Bench4BL optional	200–500 bug reports

对每个 bug 跑：

IR baseline
LLM-basic
LLM+structure
LLM+retrieved code
Full pipeline with verifier

输出表格：

Method	Top-1	Top-3	Top-5	MRR	Avg cost
BM25					
Embedding retrieval					
LLM-basic					
LLM+retrieved code					
Full agentic method					
Step 3: Case study experiment

选 10–20 个 Capstone/真实项目 bugs。

每个 bug 做一页 case analysis：

Field	内容
Bug symptom	用户看到什么问题
Available artifacts	Jira, Bitbucket, logs, website report, source files
Ground truth	fix commit changed files/methods
Agent result	Top-k ranking
Correctness	是否命中
Context analysis	哪个信息最有帮助
Failure mode	如果失败，为什么

Case study 不需要像 benchmark 一样追求统计显著性。它的价值是解释真实环境中发生了什么。

11. 你可以使用的实验假设

你可以在 proposal 里写成 hypotheses。

Hypothesis	Meaning
H1	Adding repository structure improves file-level localization compared with bug report only.
H2	Adding retrieved source-code context improves Top-k accuracy compared with no code context.
H3	Runtime evidence such as stack traces, logs, or failing tests improves localization when available.
H4	An independent verifier agent improves ranking quality but increases cost.
H5	Real-world case study performance is lower or less stable than benchmark performance because inputs are noisier and less standardized.

H5 要小心表达：不是说 benchmark 没用，而是说 benchmark 和 real-world case study 测的是不同层面的 evidence。

12. 最小可行版本

如果时间不够，你就做这个最小版本。

Minimum viable experiment
Component	做什么
Dataset	Defects4J 50 bugs + Capstone 5 bugs
Baselines	BM25 + LLM bug-report-only
Your method	bug report + repo structure + retrieved code + verifier
Metrics	File-level Top-1/3/5 + cost
Case study	每个真实 bug 做 qualitative analysis

这个版本已经足够成为 thesis 实验，因为它回答了：

方法在 benchmark 上是否有效；
context 是否有帮助；
verifier 是否有帮助；
真实项目里是否可用；
benchmark 和真实项目有什么不同。
13. Thesis 章节结构建议

你的实验章节可以这样安排：

Chapter 3: Methodology

3.1 Problem definition
3.2 Dataset construction
3.3 Proposed agentic fault localization pipeline
3.4 Retrieval strategy
3.5 Localization prompt
3.6 Verification agent
3.7 Evaluation metrics

Chapter 4: Benchmark Experiment

4.1 Dataset: Defects4J / Bench4BL
4.2 Baselines
4.3 Experimental settings
4.4 Results
4.5 Ablation study
4.6 Cost analysis
4.7 Threats to validity

Chapter 5: Real-World Case Study

5.1 Capstone project context
5.2 Bug selection criteria
5.3 Case study protocol
5.4 Results per bug
5.5 Cross-case analysis
5.6 Lessons learned

这样非常符合导师说的：benchmark 是 validation，case study 是 evaluation。

14. 可以直接发给导师的 proposal 版本

你可以这样写：

The experiment will be organized into two parts. First, I will validate the proposed LLM-based fault localization approach on an established benchmark such as Defects4J. This benchmark experiment will provide controlled and comparable results using file-level and method-level Top-k accuracy. Second, I will apply the same approach to a real-world Capstone case study, where bug information may come from multiple sources such as Jira issues, Bitbucket commits, logs, website reports, and repository structure.

The proposed method will follow an agentic pipeline: a bug context collector extracts structured information from the bug report and available artifacts; a repository retrieval component selects candidate files and methods; a localization agent ranks suspicious locations; and an independent verifier agent re-checks and re-ranks the candidates.

The main experimental variable is the amount of context provided to the model. I will compare bug-report-only localization, localization with repository structure, localization with retrieved source code, localization with runtime evidence, and the full pipeline with independent verification. The benchmark experiment will measure Top-1, Top-3, Top-5 accuracy and cost, while the case study will combine Top-k hit rate with qualitative analysis of how different information sources affect the result.

15. 我的最终建议

你现在不要把实验设计做成：

benchmark 不真实，所以我只做真实数据。

应该做成：

benchmark 用来证明方法有基本有效性和可比性；真实数据用来证明方法在复杂开发环境中的适用性。

最推荐的最终设计是：

Main experiment: Defects4J file-level fault localization, 100–200 bugs, Top-1/3/5。
Ablation: bug report only vs +repo structure vs +retrieved code vs +logs/tests vs +verifier。
Case study: Capstone/真实项目 10–20 bugs，使用 Jira/Bitbucket/logs/website/source code，做 qualitative + Top-k hit analysis。

这样设计最稳，也最符合你导师的反馈和你 literature study 的 research gap。