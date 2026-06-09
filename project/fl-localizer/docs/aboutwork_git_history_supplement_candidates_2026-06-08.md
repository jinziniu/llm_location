# AboutWork Git History Supplement Candidates

Date: 2026-06-08

Source repositories inspected:

```text
/Users/jin/capi_project/aboutwork/backend
/Users/jin/capi_project/aboutwork/frontend
```

Purpose: identify committed AboutWork fixes that are not already in
`COMPANY_BUG_LOG.md` and could be added as clean file-level fault-localization
records.

Implementation status: the recommended first batch of 6 records has been added
to `COMPANY_BUG_LOG.md` and rebuilt as:

```text
data/aboutwork/aboutwork_committed_60.jsonl
```

## Selection Criteria

Good candidates should have:

- a clear user-visible or operational failure;
- a committed fix with a stable parent buggy commit;
- a small or moderate source-code diff;
- ground-truth files that exist in the buggy parent commit;
- no merge-only, docs-only, local-config-only, broad feature, or pure refactor changes.

## Recommended First Batch

These are the cleanest additions. This batch has been implemented and moved
AboutWork from committed-54 to committed-60.

| Proposed Bug ID | Repo | Fixed Commit | Buggy Parent | Proposed Title | Ground Truth Files | Notes |
|---|---|---|---|---|---|---|
| `aboutwork-20260605-001` | backend | `8276702b15926d860f2ad96cce2a16f01945fafa` | `622d75a7cedcd4c805e62e3737972ad9e9b94913` | Refreshed Firebase tokens are rejected because expiry checks use auth_time | `backend/user/authentication.py` | Very clean one-file fix. |
| `aboutwork-20260602-001` | backend | `c42eb3fbfa4781697cc17c5e3241439990b347ca` | `6101c4754209e2c565b3f6b5704960231619d0a5` | Fernet initialization fails when SECRET_KEY is not a valid Fernet key length | `backend/backend/cryptography.py` | Very clean one-file fix. |
| `aboutwork-20260603-003` | backend | `36d62c7dc9fd9414341c59b70e0df1a277f70ca3` | `5e68d1b07a8fe400d1c1587ee6dde0141a2acf3c` | Public invite and enrollment endpoints return server errors for invalid or incomplete request paths | `backend/organization/views.py`, `backend/path/views.py` | Clean source fix, two related endpoint failures in one commit. |
| `aboutwork-20260605-002` | backend | `550cf887b10b941aa2e7cc90d2fecca44e79fc6f` | `36d62c7dc9fd9414341c59b70e0df1a277f70ca3` | HR document chunks exceed Bedrock/Cohere input length and are dropped during indexing | `backend/documents/indexing.py` | Keep ground truth focused on indexing; exclude `.gitignore` and experiment command changes. |
| `aboutwork-20260605-003` | frontend | `ea15aaf2e7ba0ea67e616acada2f8193825ac567` | `375b154370e0b303b5a059c9d09dbfd116b085b8` | Editing date-of-birth fields can show multiple update toasts for one change | `src/components/forms/modalForms/customDate.tsx`, `src/components/workforce/people/peopleDetails/EditableField.tsx`, `src/components/workforce/people/peopleDetails/sub/AboutComponent.tsx` | Clean UI state/blur handling bug. |
| `aboutwork-20260526-013` | frontend | `862f3890c0ceee57697805214d6384e4019979a8` | `eb3895c858d3c4b810674c66aec800f527706853` | Global search fails because search APIs/icons are not correctly imported | `src/components/GlobalSearch.tsx`, `src/api/org_resources/org_resources_requests.ts`, `src/components/forms/modalForms/modalSelect.tsx` | Good frontend candidate; includes one syntax/format cleanup file. |

## Optional Second Batch

These are usable, but either more environment-dependent, broader, or include
supporting non-root-cause files. Add them only if the dataset needs to be pushed
toward 62/63 records.

| Proposed Bug ID | Repo | Fixed Commit | Buggy Parent | Proposed Title | Ground Truth Files | Notes |
|---|---|---|---|---|---|---|
| `aboutwork-20260603-004` | backend | `9cdbc3e94f2db4353f1eca0001f868aa63c348b7` | `f248d5e9eb2002d069339f66f21933b544ff5a72` | OpenSearch Bedrock connector fails for application inference profile ARN paths | `backend/opensearch/connectors.py` | One source file, but partially environment/AWS-account dependent. |
| `aboutwork-20260605-004` | frontend | `01536c0a8aa56e1a0d1aa51cc37a2262d4349517` | `ea15aaf2e7ba0ea67e616acada2f8193825ac567` | Profile/feed uploads accept unsupported or oversized media without client-side validation | `src/components/PageHeader.tsx`, `src/components/TopBar.tsx`, `src/components/cards/PostCard.tsx` | Exclude locale JSON from root ground truth unless the thesis dataset wants UI-copy files counted. |
| `aboutwork-20260605-005` | backend | `973f38674ef084cd76e4619c9164494d05b8f64a` | `8276702b15926d860f2ad96cce2a16f01945fafa` | Content thumbnail and video upload flow blocks or stores media incorrectly | `backend/content/serializers.py`, `backend/content/views.py`, `backend/videofields/models.py` | Usable, but somewhat broader upload/performance fix. |

## Lower Priority / Not Recommended

| Commit | Repo | Reason |
|---|---|---|
| `147b463` | backend | Feature-like admin action support, not a bug-fix localization sample. |
| `622d75a` | backend | Large performance/architecture change around document upload and deletion; broad blast radius. |
| `661c85c` | backend | Feature/migration-heavy desk booking support. |
| `0de34500` | frontend | Mixed low-severity bundle; multiple unrelated UI/localization/prefetch fixes. |
| `7807834e` | frontend | Usable but combines document table caching and desk booking endpoint fixes in one commit. Prefer only if more samples are needed. |
| `cd6a26ea` | frontend | Very small modal-label/UI copy fix; valid but too trivial for a main sample. |

## Recommended Dataset Move

For consistency with Easy Finance:

- Conservative update: add the 6-record first batch and rebuild AboutWork as
  committed-60.
- Balanced update: add the first batch plus 2 optional records, producing roughly
  committed-62.
- Maximum clean-ish update: add the first batch plus all 3 optional records,
  producing roughly committed-63.

The balanced or maximum option would make AboutWork close to Easy Finance
`strict62` / `clean63` without forcing artificial equality.
