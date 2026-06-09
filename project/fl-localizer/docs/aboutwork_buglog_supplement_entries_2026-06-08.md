### 2026-06-05 - Refreshed Firebase tokens are rejected because expiry checks use auth_time

Bug id:

- `aboutwork-20260605-001`

Area:

- `backend_auth`
- `firebase_authentication`

Dataset candidate:

- `yes; strong one-file backend authentication fix`

Observed behavior:

- API requests authenticated with a still-valid Firebase ID token could be rejected as expired.
- Users who had authenticated earlier in the session could unexpectedly lose backend access even though the token issue time was still within the accepted window.

Expected behavior:

- Backend token expiry checks should use the token issue time and accept refreshed Firebase ID tokens whose `iat` is still within the configured one-hour window.

Trigger:

```text
Send an authenticated backend API request with a Firebase ID token whose auth_time is older than one hour but whose iat is recent.
```

Failure evidence:

```text
Backend authentication raised:
AuthenticationFailed("Token is expired", code="token_expired")

The fix commit replaced the auth_time fallback check with an iat-based check.
```

Buggy commit or branch:

- backend parent commit `622d75a`

Fix commit:

- backend `8276702`

Ground truth files:

- `backend/user/authentication.py`

Root cause:

- `FirebaseAuthentication.authenticate` compared `auth_time` against the expiry threshold. `auth_time` can remain older than the current ID token refresh, so refreshed tokens were treated as stale.

Fix summary:

- Use `decoded_token["iat"]` for the one-hour minimum issue-time check.

Validation:

```bash
git -C backend show --name-status 8276702
```

Result:

```text
commit metadata verified on 2026-06-08; runtime regression not rerun
```

### 2026-06-02 - Fernet initialization fails when SECRET_KEY is not a valid Fernet key length

Bug id:

- `aboutwork-20260602-001`

Area:

- `backend_crypto`
- `public_invite`

Dataset candidate:

- `yes; strong one-file backend cryptography fix`

Observed behavior:

- Backend startup or public invite encryption/decryption paths could fail when `SECRET_KEY` was used directly as Fernet material.
- Longer or normal Django secret keys were not guaranteed to produce a valid 32-byte urlsafe Fernet key by simple base64 encoding.

Expected behavior:

- The backend should derive a valid Fernet key from `SECRET_KEY` regardless of the raw secret string length used by the Django deployment.

Trigger:

```text
Import backend.backend.cryptography or call encrypt/decrypt with a normal Django SECRET_KEY that is not already valid Fernet key material.
```

Failure evidence:

```text
The buggy code constructed Fernet(base64.b64encode(settings.SECRET_KEY.encode())).
The fix commit added PBKDF2HMAC key derivation and urlsafe base64 encoding before Fernet initialization.
```

Buggy commit or branch:

- backend parent commit `6101c47`

Fix commit:

- backend `c42eb3f`

Ground truth files:

- `backend/backend/cryptography.py`

Root cause:

- The code treated Django `SECRET_KEY` bytes as if they could be directly base64-encoded into Fernet key material, but Fernet requires a specific 32-byte urlsafe key.

Fix summary:

- Derive a 32-byte SHA256 PBKDF2 key from `SECRET_KEY`, encode it with `base64.urlsafe_b64encode`, and initialize Fernet with the derived key.

Validation:

```bash
git -C backend show --name-status c42eb3f
```

Result:

```text
commit metadata verified on 2026-06-08; runtime regression not rerun
```

### 2026-06-03 - Public invite and enrollment endpoints return server errors for invalid or incomplete request paths

Bug id:

- `aboutwork-20260603-003`

Area:

- `backend_api`
- `organization_invite`
- `path_enrollment`

Dataset candidate:

- `yes; clean two-file endpoint fix`

Observed behavior:

- Public organization invite lookups could return a server error when the invite token was malformed, expired, or decrypted to an invalid organization id.
- The user path enrollment endpoint had an incomplete viewset configuration and could fail schema/runtime handling because no serializer class was declared.

Expected behavior:

- Invalid or expired public invite tokens should return 404 rather than 500.
- Enrollment endpoints should have a serializer class and return normal serialized participation data.

Trigger:

```text
GET a public organization invite URL with a malformed or expired invite token.
Open or query the current user's path enrollment endpoint.
```

Failure evidence:

```text
The fix commit added handling for InvalidToken, ValueError, ValidationError, and Organization.DoesNotExist.
It also added serializer_class = PathParticipationSerializer to MyPathEnrollmentViewSet.
```

Buggy commit or branch:

- backend parent commit `5e68d1b`

Fix commit:

- backend `36d62c7`

Ground truth files:

- `backend/organization/views.py`
- `backend/path/views.py`

Root cause:

- The public invite view trusted decrypted token input and let malformed token or missing organization exceptions escape as server errors. The enrollment viewset was missing its serializer declaration.

Fix summary:

- Convert invalid invite/decryption lookup failures into `Http404`.
- Add the missing `PathParticipationSerializer` serializer class to the enrollment viewset.

Validation:

```bash
git -C backend show --name-status 36d62c7
```

Result:

```text
commit metadata verified on 2026-06-08; runtime regression not rerun
```

### 2026-06-05 - HR document chunks exceed Bedrock/Cohere input length and are dropped during indexing

Bug id:

- `aboutwork-20260605-002`

Area:

- `backend_documents`
- `hr_rag`
- `opensearch_indexing`

Dataset candidate:

- `yes; clean if ground truth is restricted to production indexing code`

Observed behavior:

- HR document indexing could partially fail or silently drop chunks when a generated passage exceeded the Bedrock Cohere embedding input length.
- Large PDF sections, table text, or long legal clauses could appear indexed only partially, reducing HR chatbot source recall.

Expected behavior:

- Chunking should keep both individual chunks and final embedded passages below the model input limit so every produced passage can be embedded safely.

Trigger:

```text
Index an HR document with long PDF text or long sentence/table content using the document-passages indexing pipeline.
```

Failure evidence:

```text
Bedrock Cohere embed-multilingual-v3 rejects single input texts over its request validation length.
The fix commit added MAX_PASSAGE_BYTES, CHUNK_MAX_CHARS, hard char splitting, and a final safe_truncate_utf8 guard.
```

Buggy commit or branch:

- backend parent commit `36d62c7`

Fix commit:

- backend `550cf88`

Ground truth files:

- `backend/documents/indexing.py`

Root cause:

- Chunking was limited by token count, but the embedding connector also enforced a character/request-size limit. Headers prepended to chunk text could push a passage over the limit.

Fix summary:

- Add character budgets for chunks and passages.
- Split oversized sentence-like units at word boundaries.
- Truncate final passage payloads to the safe byte limit before embedding.

Validation:

```bash
git -C backend show --name-status 550cf88
```

Result:

```text
commit metadata verified on 2026-06-08; runtime regression not rerun
```

### 2026-06-05 - Editing date-of-birth fields can show multiple update toasts for one change

Bug id:

- `aboutwork-20260605-003`

Area:

- `frontend_workforce`
- `people_profile`

Dataset candidate:

- `yes; clean frontend UI state fix`

Observed behavior:

- Updating or clearing an employee date-of-birth field could produce more than one success toast for a single visible edit.
- Clearing the field could also briefly continue to display the old date until the mutation settled.

Expected behavior:

- A single user edit should produce at most one update toast.
- Clearing the date-of-birth field should immediately show the empty/N/A state unless the save fails.

Trigger:

```text
Open an employee profile, edit the date-of-birth field through the custom date input, then blur or clear the field.
```

Failure evidence:

```text
The fix commit added onBlur propagation, silent save support, and local clearing state around date_of_birth updates.
```

Buggy commit or branch:

- frontend parent commit `375b1543`

Fix commit:

- frontend `ea15aaf2`

Ground truth files:

- `src/components/forms/modalForms/customDate.tsx`
- `src/components/workforce/people/peopleDetails/EditableField.tsx`
- `src/components/workforce/people/peopleDetails/sub/AboutComponent.tsx`

Root cause:

- The custom date input and editable field flow did not distinguish calendar changes, blur-driven confirmation, and clear actions. Each path could trigger visible save feedback.

Fix summary:

- Propagate blur handling through the date input/editable field.
- Add silent save options for date updates.
- Track DOB clearing locally so the UI reflects the cleared value immediately.

Validation:

```bash
git -C frontend show --name-status ea15aaf2
```

Result:

```text
commit metadata verified on 2026-06-08; runtime regression not rerun
```

### 2026-05-26 - Global search fails because search APIs and icons are not correctly imported

Bug id:

- `aboutwork-20260526-013`

Area:

- `frontend_global_search`

Dataset candidate:

- `yes; usable frontend import/API wiring fix`

Observed behavior:

- Global search could fail to compile or fail at runtime because required icons and search API functions were not imported in the search component.
- Office resource helper code also had a syntax issue at the boundary before `getOfficeTypes`.

Expected behavior:

- Global search should import all required icons and search API helpers and compile cleanly.
- Organization resource API helpers should expose `getOfficeTypes` without syntax errors.

Trigger:

```text
Build or open the frontend global search modal after the global search changes.
```

Failure evidence:

```text
The fix commit added the missing search icon imports, search API imports/types, and closed the getOfficesFiltered helper before getOfficeTypes.
```

Buggy commit or branch:

- frontend parent commit `eb3895c`

Fix commit:

- frontend `862f3890`

Ground truth files:

- `src/components/GlobalSearch.tsx`
- `src/api/org_resources/org_resources_requests.ts`
- `src/components/forms/modalForms/modalSelect.tsx`

Root cause:

- GlobalSearch referenced modules and symbols that were not imported, and a nearby API helper file had an incomplete function boundary.

Fix summary:

- Add the missing icon and search API imports.
- Close the office filtering helper correctly.
- Clean up the modal select avatar JSX formatting.

Validation:

```bash
git -C frontend show --name-status 862f3890
```

Result:

```text
commit metadata verified on 2026-06-08; runtime regression not rerun
```
