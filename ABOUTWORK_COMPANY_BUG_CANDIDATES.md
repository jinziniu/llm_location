# Aboutwork Company Bug Candidates

Source project:

- `/Users/jin/capi_project/aboutwork/backend`
- `/Users/jin/capi_project/aboutwork/frontend`

Selection date:

- 2026-05-26

Selection goal:

- Pick real Aboutwork commits that can become company fault-localization samples.
- Prefer clear fix commits with small production-code ground truth.
- Prefer `chatbot_v2` / `ai-chat-v2` because they match the LLM-agent research setting.

## Selection Criteria

A usable sample should have:

- clear bug symptom from commit message, worklog, or diff
- one to three main production files as ground truth
- reproducible trigger such as prompt, UI action, API call, failing test, or CI error
- limited unrelated refactoring
- no sensitive customer/personnel data in the report

Ranking:

- `A`: strong sample, use first
- `B`: usable with some cleanup or broader context
- `C`: weak or mixed; keep only if more samples are needed
- `Exclude`: not suitable for the first dataset

## A-Level Candidates

### 1. Backend `b6d40e0` - Fix user attendance follow-ups

Repo:

- `backend`

Date:

- 2026-05-20

Commit:

- `b6d40e0 Fix user attendance follow-ups`

Ground truth files:

- `backend/chatbot_v2/action_drafts.py`
- `backend/chatbot_v2/action_executors.py`

Why usable:

- Strong worklog evidence exists in `CHATBOT_V2_WORKLOG.md`.
- Clear pre-fix symptoms and prompts are recorded.
- The bug is about AI assistant follow-up routing, which fits the company case study.

Useful triggers:

```text
mark my attendance this week
do the same for 21st of May
same for tomorrow
make it remote instead
```

Pre-fix symptom:

- Attendance/presence follow-ups fell through to the LLM or created the wrong draft.
- Pending/executed/cancelled action cards were not consistently reusable as task context.

Notes:

- This is a larger fix, but still useful because documentation is unusually complete.

### 2. Backend `603c854` - Remove implicit workspace option follow-up booking

Repo:

- `backend`

Date:

- 2026-05-05

Commit:

- `603c854 fix(chatbot-v2): remove implicit workspace option follow-up booking`

Ground truth files:

- `backend/chatbot_v2/action_drafts.py`

Supporting test file changed:

- `backend/chatbot_v2/management/commands/run_prompt_regression.py`

Why usable:

- Small fix.
- Clear behavioral boundary: bare option selections after workspace availability should not silently create booking drafts.

Useful trigger:

```text
which desks are free tomorrow
first one
```

Pre-fix symptom:

- The assistant converted a bare selection like `first one` into a booking draft.

Expected behavior:

- Require explicit booking language such as `book the first one`.

### 3. Backend `5814f49` - Remove invalid `create_agent` import

Repo:

- `backend`

Date:

- 2026-04-08

Commit:

- `5814f49 fix(chatbot-v2): remove invalid create_agent import`

Ground truth files:

- `backend/chatbot_v2/orchestrator.py`
- `backend/chatbot_v2/planning.py`

Why usable:

- Clear dependency/API failure.
- The commit message states the failure: missing `langchain.agents.create_agent` usage caused CI/import failures.

Useful trigger:

```text
Run chatbot_v2 import/tests or start backend with the affected LangChain version.
```

Pre-fix symptom:

- Backend failed because `create_agent` could not be imported/used from the installed LangChain API.

Expected behavior:

- Chatbot v2 should run tool-calling without relying on the invalid helper import.

### 4. Frontend `724d6635` - Improve action card email draft handling

Repo:

- `frontend`

Date:

- 2026-05-14

Commit:

- `724d6635 fix(ai-chat): improve action card email draft handling`

Ground truth files:

- `src/components/ai-chat-v2/AIChatV2ActionCard.tsx`

Why usable:

- Single production file.
- Clear UI/action-card symptom.
- Good frontend complement to backend chatbot samples.

Useful trigger:

```text
Create an admin email draft action card, then inspect badge/state/Open draft behavior.
```

Pre-fix symptom:

- Action card local state did not refresh from incoming draft props.
- Admin email drafts were not labelled.
- `Open draft` could attempt invalid `mailto:` opens when recipient was missing.

Expected behavior:

- Card syncs with updated draft props, shows admin label, and disables opening email drafts without a recipient.

### 5. Frontend `d29dd3d1` - Support email drafts from payload

Repo:

- `frontend`

Date:

- 2026-05-14

Commit:

- `d29dd3d1 fix(ai-chat): support email drafts from payload`

Ground truth files:

- `src/api/ai-chat-v2/aiChatV2.ts`
- `src/components/ai-chat-v2/AIChatV2ActionCard.tsx`

Why usable:

- Small and clear.
- Directly connected to chatbot action draft serialization.

Useful trigger:

```text
Create an email draft action where fields are incomplete but payload contains recipient_email, subject, and body.
Click Open draft.
```

Pre-fix symptom:

- The frontend could not generate the correct `mailto:` draft when email values were stored in `payload` instead of rendered fields.

Expected behavior:

- Email draft card falls back to payload values.

### 6. Frontend `4d2404c6` - Hide option buttons in workspace availability mode

Repo:

- `frontend`

Date:

- 2026-05-05

Commit:

- `4d2404c6 fix(ai-chat): hide option buttons in workspace availability mode`

Ground truth files:

- `src/components/ai-chat-v2/AIChatV2Message.tsx`

Why usable:

- Very small one-file UI logic fix.
- Pairs naturally with backend workspace-option follow-up behavior.

Useful trigger:

```text
Ask which desks or rooms are available.
Inspect assistant message with meta.mode = workspace_availability.
```

Pre-fix symptom:

- Option buttons rendered for workspace availability messages when they should not.

Expected behavior:

- Do not render selectable option buttons for `workspace_availability` messages.

### 7. Frontend `654d3c07` - Fix chatbot mode effect gating

Repo:

- `frontend`

Date:

- 2026-04-21

Commit:

- `654d3c07 AB-350 fix v2 chatbot mode effect gating`

Ground truth files:

- `src/components/ai-chat-v2/AIChatV2Page.tsx`

Why usable:

- One production file.
- Clear mode/state bug from commit body.

Useful trigger:

```text
Load AI Chat V2 while current user context is still loading, then switch or resolve chatbot mode.
```

Pre-fix symptom:

- Mode-change invalidation could run before user context was available.

Expected behavior:

- Use current-self query loading/data state so invalidation runs only after user context is available.

### 8. Frontend `d8bcfd9f` - Extend sendMessage HTTP timeout

Repo:

- `frontend`

Date:

- 2026-04-03

Commit:

- `d8bcfd9f fix(chat-v2): extend sendMessage HTTP timeout for long replies`

Ground truth files:

- `src/api/ai-chat-v2/aiChatV2.ts`

Why usable:

- Minimal one-line fix.
- Good example of runtime/latency failure in LLM-backed UI.

Useful trigger:

```text
Send a chatbot-v2 message that takes longer than the default HTTP timeout.
```

Pre-fix symptom:

- Long chatbot replies could fail client-side before the backend completed.

Expected behavior:

- `sendMessage` should allow a longer request timeout.

## B-Level Candidates

### 9. Backend `736f925` - Align follow-up routing and slot extraction

Repo:

- `backend`

Date:

- 2026-05-06

Commit:

- `736f925 fix(chatbot-v2): align follow-up routing and slot extraction behavior`

Ground truth files:

- `backend/chatbot_v2/action_drafts.py`
- `backend/chatbot_v2/router.py`
- `backend/chatbot_v2/smart_slot_extractor.py`

Why B-level:

- Usable but mixed: profile queries, assets/profile disambiguation, leave cancel wording, and profile slot extraction are all touched.
- Better as a multi-symptom sample unless narrowed manually.

Possible trigger:

```text
Update my phone to +31 ...
What is my education level?
Drop my leave request
```

### 10. Frontend `962a62cc` - Dedupe optimistic user messages

Repo:

- `frontend`

Date:

- 2026-04-07

Commit:

- `962a62cc fix(chat): dedupe optimistic user messages and show header state`

Ground truth files:

- `src/api/ai-chat-v2/aiChatV2.ts`
- `src/components/ai-chat-v2/AIChatV2Page.tsx`

Why B-level:

- Clear UI symptom, but it also touches legacy `src/components/ai-chat/AIChatPage.tsx`.
- Usable if ground truth is limited to the v2 files.

Pre-fix symptom:

- Optimistic user messages could be duplicated after server messages arrived.

### 11. Frontend `8ab53c71` - Disable SSE stream and sync admin mode on login

Repo:

- `frontend`

Date:

- 2026-04-14

Commit:

- `8ab53c71 fix(chat-v2): disable SSE stream and sync admin mode on login`

Ground truth files:

- `src/components/ai-chat-v2/AIChatV2Page.tsx`
- `src/hooks/auth/useAuth.ts`

Why B-level:

- Real bug, but two concerns are mixed: SSE behavior and auth/mode sync.

### 12. Backend `df151ea` - Profile fallback on agent errors

Repo:

- `backend`

Date:

- 2026-04-22

Commit:

- `df151ea feat(chatbot-v2): add profile fallback on agent errors`

Ground truth files:

- `backend/chatbot_v2/orchestrator.py`

Why B-level:

- Strong one-file localization target.
- Commit is labeled `feat`, not `fix`, but behavior is error fallback.

Pre-fix symptom:

- Profile-related questions returned generic agent errors instead of falling back to `employee_profile_search`.

## C-Level Or Exclude For First Dataset

### Backend `c374dca`

Commit:

- `c374dca fix(chatbot-v2): JSON-safe SSE encoding; remove chatbot_v2 tests`

Decision:

- `C` / probably exclude from first batch.

Reason:

- Mixed changes: SSE encoding, tool behavior, `.gitignore`, and removal of several tests.
- Too broad for a clean file-level localization sample.

### Backend `1035d5a`

Commit:

- `1035d5a refactor(chatbot-v2): split action draft handlers by domain`

Decision:

- Exclude.

Reason:

- Refactor, not bug fix.
- Many files and movement-heavy diff.

### Backend `7f438c9`, `d1b2cd0`, `e4e7ee0`, `2a327ec`, `2d4a90f`

Decision:

- Exclude from first bug-fix dataset.

Reason:

- Mostly feature/hardening/regression-coverage commits.
- Useful background, but not clean fix samples.

## Recommended First Batch

Use these first:

```text
1. backend  b6d40e0  Fix user attendance follow-ups
2. backend  603c854  Remove implicit workspace option follow-up booking
3. backend  5814f49  Remove invalid create_agent import
4. frontend 724d6635  Improve action card email draft handling
5. frontend d29dd3d1  Support email drafts from payload
6. frontend 4d2404c6  Hide option buttons in workspace availability mode
7. frontend 654d3c07  Fix v2 chatbot mode effect gating
8. frontend d8bcfd9f  Extend sendMessage HTTP timeout
```

Then add B-level candidates only if more samples are needed:

```text
9.  backend  736f925
10. frontend 962a62cc
11. frontend 8ab53c71
12. backend  df151ea
```

## Additional General Aboutwork Candidates

These are earlier or non-chatbot Aboutwork bug fixes. They are useful if the company case study should cover the broader product, not only the AI assistant.

### General Backend A-Level

#### 13. Backend `ce788ca` - Feed media 500 error

Repo:

- `backend`

Date:

- 2026-02-26

Commit:

- `ce788ca AB-350 feed media 500 error fix`

Ground truth files:

- `backend/feed/views.py`

Why usable:

- Small one-file backend fix.
- Clear symptom from commit message: feed media triggered a 500 error.

Useful trigger:

```text
GET/list feed likes or media-related feed content through the feed API.
```

Pre-fix symptom:

- Like/feed media responses reused comment queryset behavior incorrectly and could produce server errors.

#### 14. Backend `ddb82b7` - Python 3.13 circular import from global FlexFieldsFilterBackend

Repo:

- `backend`

Date:

- 2026-02-26

Commit:

- `ddb82b7 fix: remove FlexFieldsFilterBackend from global filter backends to fix circular import on Python 3.13`

Ground truth files:

- `backend/backend/settings.py`

Why usable:

- One-line configuration fix.
- Very clear runtime/import failure.

Useful trigger:

```text
Start Django or run tests under Python 3.13.
```

Pre-fix symptom:

- Django startup/test initialization failed because global DRF filter backend configuration caused a circular import.

#### 15. Backend `937177b` - `/feed/` POST nested media bug

Repo:

- `backend`

Date:

- 2025-01-21

Commit:

- `937177b bugfix on /feed/ POST`

Ground truth files:

- `backend/feed/serializers.py`

Why usable:

- Small exact `bugfix` commit.
- One production file.

Useful trigger:

```text
POST /feed/ with nested media payload.
```

Pre-fix symptom:

- `FeedPostSerializer` did not support writable nested media correctly.

#### 16. Backend `2fccc6b` - Workforce fetch field error

Repo:

- `backend`

Date:

- 2026-02-27

Commit:

- `2fccc6b AB-350 fix field error in workforce fetch`

Ground truth files:

- `backend/workforce/views.py`

Why usable:

- Tiny one-file backend fix.
- Clear API failure class: field error during workforce fetch.

Useful trigger:

```text
Fetch workforce employees with list/retrieve optimizations enabled.
```

Pre-fix symptom:

- Workforce fetch raised a field error from an invalid `select_related` path.

#### 17. Backend `07c2d66` - Scheduling user scope validation bug

Repo:

- `backend`

Date:

- 2026-02-01

Commit:

- `07c2d66 fix user scope`

Ground truth files:

- `backend/scheduling/serializers.py`

Why usable:

- Small one-file scheduling validation bug.
- The diff shows `user` was used in office scope checks before being read from request context.

Useful trigger:

```text
Create or validate presence/university leave request when organization offices exist.
```

Pre-fix symptom:

- Serializer validation could fail while checking organization-scoped offices for presence/university requests.

### General Frontend A-Level

#### 18. Frontend `6ce7b085` - Presence not showing in calendar

Repo:

- `frontend`

Date:

- 2026-01-06

Commit:

- `6ce7b085 AB-554 fix bug where presence was not showing up in calendar`

Ground truth files:

- `src/pages/user/Calender/UserCalendarPage.tsx`

Why usable:

- One-line UI data-normalization fix.
- Commit message gives the exact user-visible symptom.

Useful trigger:

```text
Open the user attendance calendar with presence entries returned by the backend.
```

Pre-fix symptom:

- Presence days did not render in the calendar because status normalization preferred `leave_type` over `status`.

#### 19. Frontend `5b4d54c5` - Reset password infinite loop

Repo:

- `frontend`

Date:

- 2026-03-27

Commit:

- `5b4d54c5 AB-685 fix infinite loop for reset password`

Ground truth files:

- `src/hooks/auth/useAuth.ts`

Why usable:

- Small one-file frontend auth fix.
- Explicit symptom: infinite loop in reset password/change password flow.

Useful trigger:

```text
Use the password change/reset flow from the authenticated UI.
```

Pre-fix symptom:

- Password update called the wrong client-side path and could loop/re-trigger unexpectedly.

#### 20. Frontend `8ea6b7fb` - UUID table selection corruption

Repo:

- `frontend`

Date:

- 2026-03-05

Commit:

- `8ea6b7fb fix: preserve UUID IDs in table row selection instead of parseInt conversion`

Ground truth files:

- `src/api/workforce/workforce.ts`
- `src/components/tables/PayrollTable.tsx`
- `src/components/tables/PeopleTable.tsx`
- `src/components/tables/SettingsTable.tsx`

Why usable:

- Commit body contains a full bug report and root cause.
- Good realistic frontend data handling bug.

Useful trigger:

```text
Select individual employee rows in People, Settings, or Payroll tables where row ids are UUID strings.
```

Pre-fix symptom:

- UUID IDs were converted with `parseInt`, causing failed checkbox selection and corrupted IDs sent to backend APIs.

Notes:

- More files than ideal, but the ground truth is coherent and well explained.

#### 21. Frontend `7c6ae224` - Recruitment board stale after adding candidate

Repo:

- `frontend`

Date:

- 2026-02-26

Commit:

- `7c6ae224 fix: invalidate applications query after adding candidate`

Ground truth files:

- `src/components/modals/Recruitment/AddCandidateModal.tsx`

Why usable:

- One-line query invalidation fix.
- Clear stale-data symptom.

Useful trigger:

```text
Add a candidate, then inspect the recruitment pipeline/applications board.
```

Pre-fix symptom:

- Backend auto-created an application, but the frontend only invalidated candidate data, so the board stayed stale.

#### 22. Frontend `64c49a93` - Exit management employee text overflow

Repo:

- `frontend`

Date:

- 2026-02-26

Commit:

- `64c49a93 fix: use size="xs" for avatar in exit management table to prevent text overflow`

Ground truth files:

- `src/components/tables/OffboardingTable.tsx`

Why usable:

- One-line UI layout fix.
- Clear visible symptom.

Useful trigger:

```text
Open exit management/offboarding table with employee rows containing avatar and long names.
```

Pre-fix symptom:

- Avatar sizing caused employee text overflow in the table.

#### 23. Frontend `72dbf950` - Document sign button overflow

Repo:

- `frontend`

Date:

- 2026-05-21

Commit:

- `72dbf950 AB-350 fix sign button overflow`

Ground truth files:

- `src/components/tables/DocumentTable.tsx`

Why usable:

- Small one-file UI fix.
- Clear user-visible symptom.

Useful trigger:

```text
Open document table as a signatory with pending signing or pending digital signature documents.
```

Pre-fix symptom:

- Sign/sign-and-upload action button text overflowed.

### General B-Level

#### 24. Backend `86e85ab` - Anniversary week overlap edge case

Ground truth files:

- `backend/workforce/views.py`

Why B-level:

- Real edge-case bug, but the diff is larger than the A-level examples.

#### 25. Backend `a21065f` - Document name editing permission bug

Ground truth files:

- `backend/documents/permissions.py`
- `backend/documents/serializers.py`
- `backend/documents/views.py`

Why B-level:

- Good permission/editing bug, but touches three backend files.

#### 26. Backend `257f502` - Redis timeout handling on document upload/delete

Ground truth files:

- `backend/backend/settings.py`
- `backend/documents/models.py`

Why B-level:

- Useful runtime reliability bug, but includes a migration and infrastructure settings.

#### 27. Frontend `dcb19eba` - Date handling timezone shift

Ground truth files:

- `src/helpers/parseDateOnly.ts`
- several employee/profile components

Why B-level:

- Good real-world date bug, but touches many frontend files.

#### 28. Frontend `be27c27d` - Search bug on various tables

Ground truth files:

- several table components

Why B-level:

- Real product bug, but broad table sweep.

#### 29. Frontend `f7ce8b83` - Navbar permission bug

Ground truth files:

- `src/components/Navbar.tsx`

Why B-level:

- Likely usable, but needs a quick diff/worklog check before promotion.

## Expanded Recommended First Batch

If the dataset should include both AI-chat and broader Aboutwork product bugs, use this combined first batch:

```text
AI/chatbot:
1.  backend  b6d40e0   Fix user attendance follow-ups
2.  backend  603c854   Remove implicit workspace option follow-up booking
3.  backend  5814f49   Remove invalid create_agent import
4.  frontend 724d6635  Improve action card email draft handling
5.  frontend d29dd3d1  Support email drafts from payload
6.  frontend 4d2404c6  Hide option buttons in workspace availability mode
7.  frontend 654d3c07  Fix v2 chatbot mode effect gating
8.  frontend d8bcfd9f  Extend sendMessage HTTP timeout

General product:
9.  backend  ce788ca   Feed media 500 error
10. backend  ddb82b7   Python 3.13 circular import
11. backend  937177b   /feed/ POST nested media bug
12. backend  2fccc6b   Workforce fetch field error
13. backend  07c2d66   Scheduling user scope validation bug
14. frontend 6ce7b085  Presence not showing in calendar
15. frontend 5b4d54c5  Reset password infinite loop
16. frontend 8ea6b7fb  UUID table selection corruption
17. frontend 7c6ae224  Recruitment board stale after adding candidate
18. frontend 64c49a93  Exit management text overflow
19. frontend 72dbf950  Document sign button overflow
```

## Next Conversion Step

For each A-level commit:

1. Fill a `Full Bug Entry` using `COMPANY_BUG_LOG_STANDARD.md`.
2. Use the parent commit as `buggy_commit`.
3. Use the listed commit as `fixed_commit`.
4. Use the production files above as `ground_truth.files`.
5. Keep supporting test files out of `ground_truth.files` unless doing test-level localization.
6. Build a JSONL sample for the company dataset.

## Continued Git-History Scan - Batch 2

Scan date:

- 2026-05-27

Goal:

- Add enough clean Aboutwork history samples to push the company bug log toward a 50-sample first benchmark.
- Avoid repeats already listed above.

### Additional A-Level Candidates

#### 30. Backend `eb1c3a0` - Asset filtering by role

Ground truth files:

- `backend/assets/views.py`

Changed test files:

- `backend/assets/tests.py`

Why usable:

- Clear role/permission filtering bug.
- One production file with focused tests.

Useful trigger:

```text
List company assets as country_admin, team_leader, or regular user.
```

Pre-fix symptom:

- Non-org-admin roles could see an asset set that did not match their role scope.

#### 31. Backend `3286eb4` - Redis/Celery broker timeout can break employee save

Ground truth files:

- `backend/workforce/signals.py`

Why usable:

- One production file.
- Clear runtime failure class: Redis broker problems should not block HTTP writes.

Useful trigger:

```text
Create or update an employee while Redis/Celery broker is unavailable or timing out.
```

Pre-fix symptom:

- Employee save could be affected by synchronous Stripe seat sync queueing.

#### 32. Backend `5dca13f` - Workforce roster deferred field error

Ground truth files:

- `backend/workforce/views.py`

Why usable:

- One-line backend query fix.
- Clear Django field-error symptom.

Useful trigger:

```text
Fetch organization roster with flex-fields/deferred fields enabled.
```

Pre-fix symptom:

- Roster query tried to `select_related` a field that could be deferred, causing a field error.

#### 33. Backend `0b161bc` - Workforce query selects deferred organization relation

Ground truth files:

- `backend/workforce/views.py`

Why usable:

- One production file.
- Another clean Django query/deferred-field localization sample.

Useful trigger:

```text
Fetch workforce list/retrieve with a `fields` query that excludes organization-related fields.
```

Pre-fix symptom:

- Query optimization selected relations that were not requested and could conflict with deferred fields.

#### 34. Backend `9f4fb7c` - Meeting room list requires admin permission

Ground truth files:

- `backend/org_resources/views.py`

Why usable:

- One production file.
- Clear permission boundary: read should be broader than create.

Useful trigger:

```text
Open meeting room list as a non-admin employee.
```

Pre-fix symptom:

- Regular employees could be blocked from listing meeting rooms.

#### 35. Backend `52588f6` - Users cannot view their own published evaluations

Ground truth files:

- `backend/evaluations/views.py`

Why usable:

- One-line access-control fix.
- Clear user-visible symptom and clean file-level ground truth.

Useful trigger:

```text
Open evaluations as a normal user with a published evaluation.
```

Pre-fix symptom:

- Non-admin users without managed teams got no evaluations, including their own published evaluations.

#### 36. Backend `702af5a` - Full-time employees get empty-attendance to-dos

Ground truth files:

- `backend/notifications/providers.py`
- `backend/notifications/signals.py`

Why usable:

- Small notification logic fix.
- Clear business-rule boundary around contracted hours.

Useful trigger:

```text
View attendance-empty-next-week to-dos for employees with hours_per_week >= 40.
```

Pre-fix symptom:

- Full-time employees could receive attendance-empty dynamic to-dos intended only for part-time/flexible schedules.

#### 37. Backend `e293aa6` - Employee context serializer rejects UUID IDs

Ground truth files:

- `backend/workforce/serializers.py`

Why usable:

- One production file.
- Direct type mismatch bug.

Useful trigger:

```text
Serialize/validate employee context payload containing UUID employee_id and organization_id.
```

Pre-fix symptom:

- Serializer expected integer IDs even though employee and organization IDs are UUIDs.

#### 38. Frontend `9e257e32` - Content statistics pending filter prefetch sends boolean

Ground truth files:

- `src/components/tables/ContentStatisticsTable.tsx`

Why usable:

- One-line frontend data/query bug.

Useful trigger:

```text
Toggle pending filter on Content Statistics, then rely on prefetched next page.
```

Pre-fix symptom:

- Prefetch request sent `has_pending` as `pendingFilter.length > 0` instead of the actual pending filter value.

#### 39. Frontend `c8dae726` - Public holiday country filter payload mismatch

Ground truth files:

- `src/api/scheduling/publicHolidays.ts`

Why usable:

- One API helper file.
- Clear frontend-backend query parameter mismatch.

Useful trigger:

```text
Filter public holidays by one or more countries.
```

Pre-fix symptom:

- Frontend appended repeated `countries` params and could include `all`, while the backend expected a normalized `country` payload.

#### 40. Frontend `172e7710` - Old auth session error state lingers

Ground truth files:

- `src/hooks/auth/useAuth.ts`

Why usable:

- One auth hook file.
- Clear stale state symptom.

Useful trigger:

```text
Trigger an auth user fetch error, navigate/remount, then recover auth state.
```

Pre-fix symptom:

- Auth session error dedupe state could persist incorrectly and hide or repeat future real errors.

#### 41. Frontend `bece3690` - Admin MFA reset session hijack risk

Ground truth files:

- `src/components/workforce/people/peopleDetails/sub/AdminAccountSettings.tsx`

Why usable:

- One production file.
- Security-sensitive state-management bug with clear symptom.

Useful trigger:

```text
Admin resets another employee's MFA while React Query background refetches are active.
```

Pre-fix symptom:

- Background requests could run during the temporary sign-in-as-target window.

#### 42. Frontend `42291ba3` - Forgot password reveals account existence

Ground truth files:

- `src/pages/auth/ForgotPage.tsx`

Why usable:

- One production file.
- Strong security/privacy bug sample.

Useful trigger:

```text
Submit forgot-password form with existing and non-existing emails.
```

Pre-fix symptom:

- UI could show different failure behavior depending on whether the email existed.

#### 43. Frontend `6d7f26ed` - Reset password errors are swallowed

Ground truth files:

- `src/api/auth/auth.ts`

Why usable:

- One API/auth file.
- Clear error propagation bug.

Useful trigger:

```text
Call resetPassword with an email/error condition that Firebase rejects.
```

Pre-fix symptom:

- The API helper caught and logged reset-password errors instead of surfacing them to callers.

#### 44. Frontend `26d65616` - Evaluation editor uses obsolete published boolean

Ground truth files:

- `src/components/workforce/people/peopleDetails/sub/EditEvaluation.tsx`

Why usable:

- One production file.
- Clear model-state mismatch after evaluation status changes.

Useful trigger:

```text
Open EditEvaluation for draft, published, and approved evaluations.
```

Pre-fix symptom:

- Publish/unpublish buttons and disabled scoring state were derived from `published` instead of `status`.

#### 45. Frontend `f721ed1d` - Empty editable select does not save first selected option

Ground truth files:

- `src/components/workforce/people/peopleDetails/EditableField.tsx`

Why usable:

- One shared component file.
- Clear UI state/update symptom.

Useful trigger:

```text
Edit an empty select field and choose the first option, then blur.
```

Pre-fix symptom:

- The field did not update because blur/save read stale `newValue`.

#### 46. Frontend `4ba489ec` - Admin to-do document navigation opens wrong mode

Ground truth files:

- `src/components/cards/TodoCard.tsx`

Why usable:

- One production file.
- Clear cross-mode navigation bug.

Useful trigger:

```text
Click a document-related to-do while currently in admin mode.
```

Pre-fix symptom:

- The todo card navigated to user documents without first switching out of admin mode.

#### 47. Frontend `9ca44a16` - Reload navigation redirects through login

Ground truth files:

- `src/hooks/auth/useAuth.ts`

Why usable:

- One auth hook file.
- Clear route/loading-state bug.

Useful trigger:

```text
Reload a protected user page such as /user/settings.
```

Pre-fix symptom:

- Auth loading state could briefly resolve as not loading, causing protected-route redirect churn.

#### 48. Frontend `383714fa` - Comment edit/delete menu appears behind modal

Ground truth files:

- `src/components/utils/commentLine.tsx`

Why usable:

- One small UI layering fix.
- Clear user-visible symptom.

Useful trigger:

```text
Open a modal containing comments, then open the comment edit/delete menu.
```

Pre-fix symptom:

- The popover menu appeared behind the modal.

### Excluded From Batch 2

```text
backend  f4b31a7   Schedule request notifications lingering: useful symptom, but commit includes several temporary root-level test files.
backend  138ff31   Legacy attendance status normalization: useful symptom, but mixed with outflow initial migration.
frontend 1494a17e  Optimistic messages/loading/query retry fixes: too broad for clean localization.
frontend 22284c2c  Assets/outflow/todo/booking/date fixes: too broad.
frontend a5794966  Timezone date issue: useful but too many files for first-pass ground truth.
```
