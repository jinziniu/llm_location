# Company Bug Log Standard

Use this document to record real bugs encountered during day-to-day development.

The goal is not to add process overhead. The goal is to preserve the debugging context we already deal with during normal work, in a consistent format. These records can later support:

- team retrospectives
- test coverage analysis
- module risk analysis
- internal AI debugging / bug localization datasets

## 1. Core Principle

Please write the first part of each bug log from the **pre-fix perspective**.

That means:

- First record what you saw before the fix: symptom, trigger, logs, failing test, wrong response.
- Only later record what files were changed and what the root cause was.
- Do not mix the answer you discovered after the fix into the original symptom/evidence section.

This lets us preserve a realistic localization problem:

```text
Given only the bug symptom and evidence, can we identify the likely faulty files?
```

## 2. Do Not Include Sensitive Information

Do not paste:

- API keys
- tokens
- passwords
- sessions or cookies
- real customer names, phone numbers, or emails
- national identifiers, bank details, salary, or HR information
- contracts, commercial pricing, or private customer data
- anything that should not be shared in a team document

If logs contain sensitive values, replace them with placeholders:

```text
[USER_ID]
[EMAIL]
[PHONE]
[TOKEN]
[CUSTOMER_NAME]
[PRIVATE_VALUE]
```

## 3. Daily Template

Use this version for normal day-to-day bug logging. It should take about 3 minutes.

````md
### YYYY-MM-DD - Short Bug Title

Bug id:

- `aboutwork-YYYYMMDD-001`

Module:

- `backend` / `frontend` / `chatbot_v2` / `admin_agent` / `other`

Observed behavior:

- What did you see before the fix?

Expected behavior:

- What should have happened?

Trigger:

```text
User action / prompt / API request / command / test command
```

Failure evidence:

```text
Error message, stack trace, failing test, wrong response, relevant log, or screenshot note.
Do not include sensitive information.
```

Buggy branch or commit:

- `branch-or-commit`

Fix commit:

- `commit`

Files changed:

- `path/to/file1`
- `path/to/file2`

Root cause in one sentence:

- Write this after the fix. Do not put it in the observed behavior section.

Validation:

```bash
Test command or manual verification steps
```

Validation result:

```text
passed / failed / blocked, with short detail
```
````

## 4. Full Template

Use this version for bugs that are good candidates for future retrospectives or AI debugging datasets.

````md
### YYYY-MM-DD - Short Bug Title

Bug id:

- `aboutwork-YYYYMMDD-001`

Dataset candidate:

- `yes` / `no`

Dataset quality:

- `strong` / `medium` / `weak` / `exclude`

Reason for inclusion:

- Example: clear reproduction steps, failing test, clean root cause, important user flow.

Module:

- Product area:
- Backend module:
- Frontend module:

Pre-fix observed behavior:

- Describe only the user-visible or system-visible symptom before the fix. Do not mention the final answer.

Expected behavior:

- What should have happened?

Trigger:

```text
Exact prompt / API request / UI path / command / reproduction steps.
```

Pre-fix evidence:

```text
Stack trace, failing test, wrong response, relevant logs, or screenshot note.
Do not include sensitive information.
```

Buggy state:

- Branch:
- Buggy commit:
- Environment:
- Feature flag / mode:

Known localization context before the fix:

- Bug report / user report:
- Runtime logs:
- Failing test name:
- Suspected modules at the time:
- Files inspected before the fix:
- Wrong hypotheses:
- Most useful clue:

Do not include in the section above:

- fixed commit diff
- final changed files
- patch explanation
- root cause file, unless it was already known before the fix

Post-fix ground truth:

- Fixed commit:
- Changed production files:
- Root cause files:
- Changed test files:
- Non-code files changed:

Root cause:

- Write this after the fix. Explain the actual cause.

Fix summary:

- Briefly describe what changed.

Validation commands:

```bash
command 1
command 2
```

Validation result:

```text
passed / failed / blocked
```

Dataset notes:

- Is file-level localization appropriate?
- Is method-level localization possible?
- Is the ground truth clean?
- Were there refactors or unrelated edits?
- Should this bug be excluded?
````

## 5. What Bugs Are Good to Record?

Prioritize bugs that have:

- clear reproduction steps
- a failing test, stack trace, log, or wrong response
- a focused fix in one to three main production files
- a real product or system behavior issue
- validation through a command or manual steps
- useful evidence for understanding module risk

Mark as `weak` or `exclude` when the bug is:

- formatting only
- copy/text only
- broad refactoring
- dependency upgrade without a clear fault
- fixed only by changing tests
- mixed with many unrelated file changes
- missing reproduction steps
- missing evidence
- too sensitive to safely sanitize

## 6. Dataset Quality Guide

Use this quick guide:

```text
strong:
Clear trigger, failure evidence, buggy commit, fixed commit, ground truth files, and validation command.

medium:
Symptom and changed files are clear, but logs or test evidence are incomplete.

weak:
The issue and fix are roughly known, but reproduction steps or evidence are missing.

exclude:
Not suitable for a dataset, such as refactoring, formatting-only changes, sensitive data, or unclear ground truth.
```

## 7. Recommended Worklog Locations

Append entries to the relevant project worklog:

- `CHATBOT_V2_WORKLOG.md`
- `ADMIN_AI_AGENT_WORKLOG.md`
- `FRONTEND_AI_CHAT_V2_WORKLOG.md`
- another project-specific worklog

If you are not sure where to put the entry, temporarily use:

```text
COMPANY_BUG_LOG.md
```

The entries can be reorganized later.

## 8. Short Message to Send to Teammates

You can send this message directly:

```text
When you run into a real bug during development, please add a short bug log using this template.

It does not need to be long. The daily version should take about 3 minutes. The most important fields are:

1. What you observed before the fix
2. How to trigger it
3. Error evidence
4. Which files were changed
5. One-sentence root cause
6. How the fix was validated

Please do not paste tokens, passwords, customer private data, real phone numbers, or real emails.

These logs will help with team retrospectives, test coverage analysis, and an internal AI debugging / bug localization dataset.
```

## 9. Example

````md
### 2026-05-21 - Chat confirm text executes latest pending action

Bug id:

- `aboutwork-20260521-001`

Module:

- `chatbot_v2`

Observed behavior:

- After the assistant created a pending attendance action card, typing `confirm that` did not reliably execute the latest pending draft.

Expected behavior:

- Text confirmation should execute the latest pending action draft before generic continuation parsing.

Trigger:

```text
mark me in office tomorrow
confirm that
```

Failure evidence:

```text
The second message was handled as a generic continuation instead of confirming the pending ChatbotActionDraft.
```

Buggy branch or commit:

- `staging before 2026-05-21 action cancel follow-up hardening`

Fix commit:

- `fill-in-commit`

Files changed:

- `backend/chatbot_v2/action_drafts.py`
- `backend/chatbot_v2/regression_tests/test_action_followups.py`

Root cause in one sentence:

- Chat text confirmation was not checked early enough against the latest pending action draft.

Validation:

```bash
DJANGO_SETTINGS_MODULE=backend.settings_test .venv/bin/python backend/manage.py test chatbot_v2.regression_tests.test_action_followups -v 2
```

Validation result:

```text
passed: 6 tests
```
````

## 10. Later Conversion to Experiment Data

This section is mainly for whoever converts logs into a fault-localization dataset. Teammates do not need to fill this manually during daily logging.

When converting to JSONL, map a bug entry like this:

```json
{
  "bug_id": "aboutwork-YYYYMMDD-001",
  "project": "aboutwork",
  "bug_report": {
    "id": "aboutwork-YYYYMMDD-001",
    "url": "",
    "text": "Observed behavior + expected behavior + trigger"
  },
  "test_failure": "failing test name or empty string",
  "triggering_tests": [],
  "stack_trace": "pre-fix evidence",
  "repo_path": "/path/to/aboutwork",
  "source_dir": "backend",
  "buggy_commit": "commit",
  "fixed_commit": "commit",
  "ground_truth": {
    "classes": [],
    "files": [
      "backend/chatbot_v2/action_drafts.py"
    ],
    "methods": []
  },
  "extra_context": {
    "source": "aboutwork company bug log",
    "area": "chatbot_v2",
    "dataset_quality": "strong",
    "leakage_note": "ground_truth and fixed_commit are evaluation-only"
  }
}
```

Important:

- `bug_report.text`, `test_failure`, and `stack_trace` are allowed model inputs.
- `fixed_commit`, `ground_truth.files`, and root cause files are for evaluation only.
- Do not leak ground truth into the prompt/context used for localization experiments.
