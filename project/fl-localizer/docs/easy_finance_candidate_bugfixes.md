# Easy Finance Candidate Bug-Fix Commits

Source repos:

```text
/Users/jin/capi_project/easy_finance/easy_finance_backend
/Users/jin/capi_project/easy_finance/easy_finance_frontend
```

Selection criteria:

- Non-merge commit.
- Commit message describes a bug, error, crash, loading issue, route issue, or wrong behavior.
- Fix touches source files, not only dependencies, migrations, secrets, build metadata, or deployment config.
- Prefer 1-3 changed files and a clear ground-truth file set.
- The buggy version should be the parent of the listed commit; the fixed version is the listed commit.

## Priority Candidates

### Backend

| ID | Commit | Date | Bug Text Seed | Ground Truth Files | Size | Notes |
|---|---|---:|---|---|---:|---|
| easyfinance-backend-20260331-001 | `76f572417877a1fe0a02e59d97d55c99f394508a` | 2026-03-31 | User archive analysis crashes/fails when the Celery broker is unavailable; it should fall back to synchronous analysis. | `easy_finance_backend/user_archive/views.py` | 1 file, +9/-2 | Very usable. Clear infra fallback bug. |
| easyfinance-backend-20260305-001 | `5205f3d06c5cb256d3bc2e476cb5d2e6e8ddea24` | 2026-03-05 | OCR status bar returns 404 when there are no unreviewed records; it should return an empty list with HTTP 200. | `easy_finance_backend/ocr_email/views.py` | 1 file, +1/-4 | Very usable. Small API behavior fix. |
| easyfinance-backend-20251029-001 | `806575fe1aeecddb74758d344048b67d674a5b61` | 2025-10-29 | Deleting a manual journal leaves related journal vouchers/ledger entries instead of cascading cleanup. | `easy_finance_backend/manual_journal/apps.py`, `easy_finance_backend/manual_journal/signals.py` | 2 files, +26 | Very usable. Clear lifecycle/cascade bug. |
| easyfinance-backend-20250804-001 | `36be42ea9ca4c4987d1f126a3a2025fa74401588` | 2025-08-04 | GoCardless balance fetching misses balances whose `balanceType` is `expected`. | `easy_finance_backend/transfer/views.py` | 1 file, +5/-3 | Usable. Message directly explains missing field. |
| easyfinance-backend-20250705-001 | `858970dbb732bd45774f18ccd702b4b4e5a13fbd` | 2025-07-05 | Generated invoice PDFs show dollar symbols instead of euro symbols. | `easy_finance_backend/invoice/views.py` | 1 file, +5/-5 | Very usable. Simple presentation/data formatting bug. |
| easyfinance-backend-20250514-001 | `14377dcf64c39625f6b53e662f837e834e27b8e0` | 2025-05-14 | Deleting an expense does not update user totals/statistics or unlink the matched transfer. | `easy_finance_backend/expense/views.py` | 1 file, +19/-4 | Usable. Clear state cleanup bug. |
| easyfinance-backend-20241218-001 | `dba538c1aa8f492a854983aee4dd5a3a09585f75` | 2024-12-18 | Password reset email is sent to the default sender address instead of the user-provided email. | `easy_finance_backend/user/views.py` | 1 file, +1/-1 | Very usable. Minimal, clear fix. |
| easyfinance-backend-20250131-001 | `c19b4dc4bc76d880690984d6d1f943796af35d00` | 2025-01-31 | Invoice amount validation fails because calculated product totals are not rounded before comparison. | `easy_finance_backend/invoice/serializers.py` | 1 file, +3/-1 | Usable. Clear rounding bug. |

### Frontend

| ID | Commit | Date | Bug Text Seed | Ground Truth Files | Size | Notes |
|---|---|---:|---|---|---:|---|
| easyfinance-frontend-20260303-001 | `56640f3d4920a385a2983b52f68da1a4bb1060cf` | 2026-03-03 | Floating AI input bar appears on admin/bookkeeper routes where it should be hidden. | `easy_finance_frontend/src/components/wrapper/AuthRoute.tsx` | 1 file, +4/-2 | Very usable. Small route/UI visibility bug. |
| easyfinance-frontend-20250626-001 | `793ced2d0189769ddf9c817b413a87a578da64ad` | 2025-06-26 | Registration/login flow can remain stuck in loading after an error. | `easy_finance_frontend/src/hooks/useAuth.ts` | 1 file, +2/-1 | Very usable. Minimal state bug. |
| easyfinance-frontend-20250416-001 | `ffb8714c677297644a2ca6f4d7a9051d9b1f097b` | 2025-04-16 | Transaction table infinite pagination spinner/sentinel behaves incorrectly at the bottom of the table. | `easy_finance_frontend/src/components/Tables/TransactionTable.tsx` | 1 file, +5/-6 | Very usable. Small infinite-scroll UI bug. |
| easyfinance-frontend-20250311-001 | `26b38e8b6c51b860b3ddcc68af0707531c5047e5` | 2025-03-11 | The expenses page renders the wrong table for the unreviewed tab. | `easy_finance_frontend/src/pages/Expenses/AllExpensesPage.tsx` | 1 file, +6/-6 | Very usable. Clear conditional rendering bug. |
| easyfinance-frontend-20250701-001 | `afdb8e8f7069923eaa58eb02708f36ca81ad1d5f` | 2025-07-01 | Login redirects to the app before authentication is actually complete. | `easy_finance_frontend/src/AppMobile.tsx`, `easy_finance_frontend/src/components/wrapper/AuthRoute.tsx`, `easy_finance_frontend/src/components/wrapper/PublicRouteWrapper.tsx`, `easy_finance_frontend/src/pages/Auth/LoginPage.tsx` | 4 files, +14/-18 | Usable. Clear auth routing bug. |
| easyfinance-frontend-20250627-001 | `01f2e244f3ebc08e530ca9f8666fb0ec9100645c` | 2025-06-27 | Admin balance/P&L user search shows an empty state before the debounced search request catches up. | `easy_finance_frontend/src/pages/Admin/Balance/BalanceSheetPage.tsx`, `easy_finance_frontend/src/pages/Admin/Profit&Loss/ProfitLoss.tsx` | 2 files, +26/-44 | Usable. Clear loading/empty-state bug. |
| easyfinance-frontend-20250520-001 | `f17a74e67e864f97e770094aea774a6af9062cd8` | 2025-05-20 | Admin invoice/expense unreviewed counts show mocked or stale counts instead of API counts. | `easy_finance_frontend/src/pages/Admin/Expenses/ExpensesPage.tsx`, `easy_finance_frontend/src/pages/Admin/Invoices/InvoicePage.tsx` | 3 files, +8/-23 | Usable. Exclude removed style-only file if using production ground truth. |
| easyfinance-frontend-20250506-001 | `48a291fb075a8aa7473261b21630668300cf3510` | 2025-05-06 | Admin invoice table search/filter does not pass selected user filters into reviewed/unreviewed invoice queries. | `easy_finance_frontend/src/components/Admin/Invoices/InvoiceTableAdmin.tsx`, `easy_finance_frontend/src/components/Admin/Invoices/UnreviewedInvoiceTableAdmin.tsx`, `easy_finance_frontend/src/pages/Admin/Invoices/InvoicePage.tsx` | 3 files, +22/-19 | Usable. Clear filter propagation bug. |
| easyfinance-frontend-20260305-001 | `857a0b4ef3724d2a74a2f8a1e73992b54cd0efa4` | 2026-03-05 | Floating AI chat/input bar is covered or offset incorrectly by the iOS/Android keyboard. | `easy_finance_frontend/src/components/Layout/FloatingAIInputBar.tsx` | 1 file, +61/-22 | Usable but larger UI platform fix. |
| easyfinance-frontend-20260212-001 | `ebeb0259e730d54b6b4338d9841e25e06f25e367` | 2026-02-12 | AI chat needs to handle both old and new conversation id formats and merge conversation lists correctly. | `easy_finance_frontend/src/pages/AIChat/AIChatTable.tsx`, `easy_finance_frontend/src/pages/AIChat/UnifiedModal.tsx` | 2 files, +143/-37 | Usable but larger. |

## Expanded Usable Candidates

These extend the pool beyond the highest-confidence 18. They are still source-level fixes with usable commit messages, but many are more UI/product-specific or less precisely described.

### Backend Additions

| ID | Commit | Date | Bug Text Seed | Ground Truth Files | Size | Notes |
|---|---|---:|---|---|---:|---|
| easyfinance-backend-20260305-002 | `1ddc9f8` | 2026-03-05 | Support tickets and AI chats need to allow an empty subject while keeping Sendbird channel names non-empty. | `easy_finance_backend/notifications/serializers.py`, `easy_finance_backend/notifications/views.py` | 2 files, +27/-11 | Good API validation/name fallback case. |
| easyfinance-backend-20260304-001 | `5995fa9` | 2026-03-04 | Support notifications need correct customer/admin message source and should filter no-agent system messages. | `easy_finance_backend/notifications/views.py`, `easy_finance_backend/notifications/views_admin.py` | 2 files, +68/-8 | Usable messaging bug. |
| easyfinance-backend-20260217-001 | `a4175e7` | 2026-02-17 | Chatbot invoice edit tool cannot correctly edit client information on invoices and expenses. | `easy_finance_backend/chatbot/tools.py`, `easy_finance_backend/invoice/models.py` | 2 files, +56/-5 | Good LLM-tool/business data bug. |
| easyfinance-backend-20260217-002 | `ce9d9cc` | 2026-02-17 | Chatbot VAT data tool returns or handles VAT data incorrectly. | `easy_finance_backend/chatbot/tools.py` | 1 file, +37/-18 | Usable but message is terse. |
| easyfinance-backend-20260211-001 | `2670633` | 2026-02-11 | VAT declaration XML saving and quarterly report date handling need error handling/fixes. | `easy_finance_backend/vat_declaration/views.py` | 1 file, +58/-14 | Usable VAT workflow bug. |
| easyfinance-backend-20260204-001 | `8a6ee47` | 2026-02-04 | Google sign-in needs backend handling fixes. | `easy_finance_backend/user/views.py` | 1 file, +20/-9 | Usable auth bug. |
| easyfinance-backend-20260203-001 | `a2d8bb1` | 2026-02-03 | Balance sheet output is incorrect. | `easy_finance_backend/reports/services.py` | 1 file, +5/-5 | Good small report calculation fix. |
| easyfinance-backend-20251106-001 | `6044251` | 2025-11-06 | Non-admin or bookkeeper users hit an authorization/visibility edge case. | `easy_finance_backend/bookkeeping/views.py` | 1 file, +4/-8 | Usable permission bug. |
| easyfinance-backend-20251105-001 | `51b3675` | 2025-11-05 | Bookkeeping Calendly flow has incorrect behavior. | `easy_finance_backend/bookkeeping/callendly_views.py` | 1 file, +20/-19 | Usable but message is broad. |
| easyfinance-backend-20251017-001 | `b61b05a` | 2025-10-17 | OCR task can hit a null path bug. | `easy_finance_backend/ocr_email/tasks.py` | 1 file, +6/-6 | Good null-handling bug. |
| easyfinance-backend-20251015-001 | `e0aa069` | 2025-10-15 | Transfer logic causes incorrect balance sheet behavior. | `easy_finance_backend/transfer/services.py`, `easy_finance_backend/transfer/signals.py` | 2 files, +15/-0 | Usable accounting consistency bug. |
| easyfinance-backend-20250923-001 | `09e976c` | 2025-09-23 | Google login misses `user_type`. | `easy_finance_backend/easy_finance_backend/firebase_auth.py` | 1 file, +2/-1 | Very small, good auth metadata fix. |
| easyfinance-backend-20250922-001 | `33f32a3` | 2025-09-22 | Profit and loss report is incorrect. | `easy_finance_backend/reports/services.py` | 1 file, +9/-9 | Usable report calculation bug. |
| easyfinance-backend-20250826-001 | `c11dc6f` | 2025-08-26 | AI transaction categorization needs additional fixes. | `easy_finance_backend/transfer/views.py` | 1 file, +12/-8 | Usable but message is broad. |
| easyfinance-backend-20250825-001 | `effc259` | 2025-08-25 | Expense instalment handling is incorrect. | `easy_finance_backend/expense/serializers.py`, `easy_finance_backend/expense/views.py` | 2 files, +12/-6 | Good domain bug. |
| easyfinance-backend-20250814-001 | `94f360e` | 2025-08-14 | Matched expense transaction handling is incorrect. | `easy_finance_backend/expense/services.py` | 1 file, +2/-2 | Very small domain fix. |
| easyfinance-backend-20250807-001 | `fe97156` | 2025-08-07 | Creating an expense can fail or create incorrect state. | `easy_finance_backend/expense/views.py` | 1 file, +5/-1 | Good small create-flow bug. |
| easyfinance-backend-20250731-001 | `4edb070` | 2025-07-31 | Invoice creation has incorrect backend behavior. | `easy_finance_backend/user/serializers.py` | 1 file, +2/-2 | Very small, message is terse. |
| easyfinance-backend-20250513-001 | `b919bbf` | 2025-05-13 | GoCardless bank-account sync needs fixes. | `easy_finance_backend/bank_account/models.py`, `easy_finance_backend/bank_account/views.py` | 2 files, +13/-4 | Good integration bug. |
| easyfinance-backend-20250513-002 | `e02d3e8` | 2025-05-13 | Deleting an invoice does not update statistics. | `easy_finance_backend/invoice/views.py` | 1 file, +21/-0 | Good state cleanup bug. |
| easyfinance-backend-20250506-001 | `b7092bf` | 2025-05-06 | OCR/invoice search algorithm returns wrong results. | `easy_finance_backend/ocr_email/views.py` | 1 file, +43/-7 | Usable search bug. |
| easyfinance-backend-20250501-001 | `7f947cd` | 2025-05-01 | Admin invoice search has a small backend bug. | `easy_finance_backend/invoice/views_admin.py` | 1 file, +1/-1 | Minimal but usable. |

### Frontend Additions

| ID | Commit | Date | Bug Text Seed | Ground Truth Files | Size | Notes |
|---|---|---:|---|---|---:|---|
| easyfinance-frontend-20260331-001 | `f1da161` | 2026-03-31 | AI chat modal behavior needs fixes. | `easy_finance_frontend/src/pages/AIChat/UnifiedModal.tsx` | 1 file, +20/-20 | Usable but message is broad. |
| easyfinance-frontend-20260318-001 | `5b7573e` | 2026-03-18 | Floating AI input bar is too large or misaligned on the home screen. | `easy_finance_frontend/src/components/Layout/FloatingAIInputBar.tsx` | 1 file, +22/-19 | Good UI layout bug. |
| easyfinance-frontend-20260316-001 | `5fbd024` | 2026-03-16 | Home screen shows an unwanted company welcome header. | `easy_finance_frontend/src/pages/Home/HomeScreenPage.tsx` | 1 file, +0/-14 | Good UI visibility bug. |
| easyfinance-frontend-20260305-002 | `f7970ad` | 2026-03-05 | AI chat conversation names render incorrectly. | `easy_finance_frontend/src/pages/AIChat/AIChatTable.tsx` | 1 file, +4/-3 | Good small display bug. |
| easyfinance-frontend-20260225-001 | `0f5f114` | 2026-02-25 | Safe-area handling is wrong for the floating AI input bar. | `easy_finance_frontend/src/components/Layout/FloatingAIInputBar.tsx` | 1 file, +7/-5 | Good mobile layout bug. |
| easyfinance-frontend-20260220-001 | `72ed7ed` | 2026-02-20 | Chat history needs a skeleton loading state instead of poor/empty loading behavior. | `easy_finance_frontend/src/pages/AIChat/AIChatTable.tsx` | 1 file, +18/-5 | Usable loading-state bug. |
| easyfinance-frontend-20260220-002 | `97d804c` | 2026-02-20 | Chat display has a small rendering issue. | `easy_finance_frontend/src/components/Layout/FloatingAIInputBar.tsx` | 1 file, +1/-1 | Minimal but usable. |
| easyfinance-frontend-20260213-001 | `d7ddaa5` | 2026-02-13 | Transactions and VAT pages have incorrect back-button behavior. | `easy_finance_frontend/src/pages/Tax/VatTaxOverview.tsx`, `easy_finance_frontend/src/pages/Transactions/TransactionPage.tsx` | 2 files, +2/-2 | Good navigation bug. |
| easyfinance-frontend-20251104-001 | `c55e964` | 2025-11-04 | Manual journal page has missing Dutch translations. | `easy_finance_frontend/src/pages/Manual_journal/ManualJournalPage.tsx` | 1 file, +4/-4 | Usable i18n bug. |
| easyfinance-frontend-20251023-001 | `a1c80bb` | 2025-10-23 | Profit and loss page has incorrect translations. | `easy_finance_frontend/src/pages/Profit/ProfitAndLossPage.tsx` | 1 file, +2/-2 | Usable i18n bug. |
| easyfinance-frontend-20251022-001 | `b82a19f` | 2025-10-22 | Expense upload category selection behaves incorrectly. | `easy_finance_frontend/src/components/Common/HierarchicalCategorySelector.tsx`, `easy_finance_frontend/src/components/DataDisplay/TransactionItem.tsx`, `easy_finance_frontend/src/pages/Expenses/UploadExpensePage.tsx` | 3 files, +39/-32 | Good category-selection bug. |
| easyfinance-frontend-20251015-001 | `e521391` | 2025-10-15 | Asset change-client flow and back-button routes behave incorrectly. | `easy_finance_frontend/src/api/expense/expense.ts`, `easy_finance_frontend/src/pages/Assets/AssetsViewPage.tsx`, `easy_finance_frontend/src/pages/Expenses/ExpenseCustomerEditPage.tsx`, `easy_finance_frontend/src/pages/Expenses/ViewExpense.tsx` | 4 files, +30/-9 | Usable navigation/data-flow bug. |
| easyfinance-frontend-20251009-001 | `4d7ce5f` | 2025-10-09 | Quarter state does not show the expected profit-and-loss form. | `easy_finance_frontend/src/pages/Auth/FinanceDetailsForm.tsx` | 1 file, +3/-0 | Good conditional-state bug. |
| easyfinance-frontend-20251002-001 | `cc006ec` | 2025-10-02 | BackButton navigates to the wrong route in company details submission. | `easy_finance_frontend/src/pages/Tax/CompanyDetailsSubmission.tsx` | 1 file, +1/-1 | Very small route bug. |
| easyfinance-frontend-20251001-001 | `effcf21` | 2025-10-01 | Expense/invoice unit price and product total calculations are incorrect. | `easy_finance_frontend/src/pages/Expenses/ViewExpense.tsx`, `easy_finance_frontend/src/pages/Invoices/InvoiceSpecificPage.tsx` | 2 files, +5/-12 | Good calculation display bug. |
| easyfinance-frontend-20250930-001 | `16e3470` | 2025-09-30 | Confirm expense/invoice buttons lack correct loading states. | `easy_finance_frontend/src/pages/Expenses/UploadExpenseClientPage.tsx`, `easy_finance_frontend/src/pages/Invoices/CreateNewInvoicePage.tsx`, `easy_finance_frontend/src/pages/Invoices/InvoiceSpecificPage.tsx` | 3 files, +22/-4 | Usable loading-state bug. |
| easyfinance-frontend-20250926-001 | `b8f3ca3` | 2025-09-26 | VAT overview has a small functional/UI bug. | `easy_finance_frontend/src/pages/Tax/VatTaxOverview.tsx` | 1 file, +10/-5 | Usable but message is broad. |
| easyfinance-frontend-20250731-001 | `55e48e5` | 2025-07-31 | Bank connection flow behaves incorrectly. | `easy_finance_frontend/src/pages/Bank/LinkBankDetailsPage.tsx` | 1 file, +47/-26 | Good bank-flow bug. |
| easyfinance-frontend-20250705-001 | `87d74af` | 2025-07-05 | Invoice UI shows dollars instead of euros. | `easy_finance_frontend/src/pages/Invoices/InvoiceSpecificPage.tsx` | 1 file, +1/-1 | Very small formatting bug. |
| easyfinance-frontend-20250701-002 | `fdabe7f` | 2025-07-01 | Auth/admin login redirection still behaves incorrectly. | `easy_finance_frontend/src/hooks/useAuth.ts`, `easy_finance_frontend/src/pages/Admin/Auth/AdminLoginPage.tsx` | 2 files, +5/-1 | Good auth routing bug. |
| easyfinance-frontend-20250627-002 | `2e5c867` | 2025-06-27 | Expense form behavior/layout is incorrect. | `easy_finance_frontend/src/components/Admin/Expenses/NewExpense.tsx`, `easy_finance_frontend/src/components/Admin/Invoices/InvoiceSidebarPopup.tsx` | 2 files, +15/-7 | Usable form bug. |
| easyfinance-frontend-20250603-001 | `e2623ab` | 2025-06-03 | Login can remain stuck on the loading screen. | `easy_finance_frontend/src/components/Forms/PasswordInput.tsx`, `easy_finance_frontend/src/components/wrapper/AuthRoute.tsx`, `easy_finance_frontend/src/pages/Admin/Auth/AdminLoginPage.tsx` | 3 files, +14/-9 | Good auth loading bug. |
| easyfinance-frontend-20250523-001 | `951ce1f` | 2025-05-23 | Admin transaction filters/details have bugs. | `easy_finance_frontend/src/components/Layout/TransactionFilterModal.tsx`, `easy_finance_frontend/src/pages/Admin/Transactions/TransactionsPage.tsx` | 2 files, +12/-11 | Usable transaction filter bug. |
| easyfinance-frontend-20250522-001 | `33c49b2` | 2025-05-22 | Admin user filtering has bugs. | `easy_finance_frontend/src/components/Admin/Users/UserFilterModal.tsx`, `easy_finance_frontend/src/pages/Admin/Users/UsersPage.tsx` | 2 files, +7/-6 | Good filtering bug. |

## Secondary Candidates

These are probably usable, but should be inspected again before inclusion.

| Repo | Commit | Date | Reason To Keep | Caution |
|---|---|---:|---|---|
| backend | `b192bebbed58ab8f4ceec5abe8f0e5757174358e` | 2026-03-31 | PDF bytes handling and user archive crash handling are real bugs. | 2 files, +103/-85; multiple fixes in one commit. |
| backend | `4be8ec0660bd1827ca3861cf75efc065ff83e66b` | 2026-03-06 | Invoice creation assigns the wrong/missing user through chatbot flow. | 2 files, +60/-142; large deletion/refactor noise. |
| backend | `0b9e9ed691c099fa74989d51adcb16b3193ba592` | 2025-05-12 | Type mismatch when summing invoice values. | 2 files, +80/-13; may involve broader serializer/view changes. |
| backend | `1fed2c4f9520a4ffa9dac9bcd0a34342013ec982` | 2025-10-27 | Orphan vouchers and depreciation tracking break balance sheet/cascade behavior. | 4 files, +125/-34; includes management command. |
| frontend | `e5f2cd04c471d4b52040ca891e5b27a2db550c8e` | 2025-07-30 | Infinite scrolling issue in transactions. | 1 file but +123/-40; larger local rewrite. |
| frontend | `2228be72da532e1aa351bec87021b9354d37c0c8` | 2025-04-07 | Invoice edit product white-screen fix. | 4 files, +68/-23; includes toast utility changes. |
| frontend | `50ccbfc4598145b3f9e059a1860bb65161c05f20` | 2025-02-24 | Route bug. | Touches `.env`; avoid if building clean source-only dataset. |
| frontend | `fd93f2ba13084b5fe509171273e8eef3f0f40d69` | 2025-03-10 | Bank accounts display fix. | 2 files, +153/-8; larger icon/UI addition. |

## Initial Dataset Recommendation

Start with the 18 highest-confidence priority candidates if you want a small clean pilot.

For the requested larger Easy Finance run, use the priority and expanded usable candidates together:

```text
priority: 18
expanded usable: 46
total primary pool: 64
```

This is enough to select at least 50 samples while keeping a reserve. Use the secondary candidates only if the 64-item primary pool loses too many records during worktree validation or source-file existence checks.
