# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

A-Profit: a web system that fills in vehicle technical-inspection protocols and generates DOCX/PDF documents from them. The UI, comments, templates and TODO are in Russian. Windows-only deployment (Word COM, LibreOffice paths, `venv\Scripts`).

## Правила работы

- Отвечай на русском. Комментарии в коде, тексты UI и TODO тоже на русском.
- Перед любыми изменениями в файлах опиши план (какие файлы и что меняешь) и жди моего подтверждения.
- После изменений запускай проверки из раздела «Validation expectations» и пиши, что прошло, а что не удалось запустить.

## Layout

- `main/` — Django 5.2 + DRF backend (project `main/main`, single app `main/cars`). MySQL only, no SQLite fallback.
- `car_front/` — React 19 + Vite + MUI frontend.
- `parser/` — standalone Selenium scraper for drom.ru that fills the car catalog tables (brands → models → generations → configurations → car data) directly through `mysql-connector`. Has its own `.env` keys (`DB_HOST`, `DB_USER`, ...), separate from Django's.
- `Бэкап/` — database backups. Do not modify unless explicitly asked.
- `lo_profile/`, `temp_preview/`, `_*.txt` — LibreOffice profile and scratch/reference files, not source.
- `TODO.md` — current task list, one block per task (why / where / done-when / how to verify). Finished tasks are removed; history lives in git.

## Commands

The Python virtualenv is `venv/` at the repo root. `.env` at the root (see `.env.example`) is required; `MYSQL_PASSWORD` has no default, so settings import fails without it.

```bash
# Backend (from main/)
../venv/Scripts/python.exe manage.py runserver 0.0.0.0:8000
../venv/Scripts/python.exe manage.py check
../venv/Scripts/python.exe manage.py test cars                                   # needs MySQL rights to create the test DB
../venv/Scripts/python.exe manage.py test cars.tests.ProtocolWorkflowTests.test_full_protocol_workflow_reaches_approved
../venv/Scripts/python.exe manage.py e2e_fixture prepare                        # seed data used by real E2E tests

# Frontend (from car_front/)
npm run dev            # port 3000
npm run lint
npm run build
npm run test:e2e       # Playwright smoke tests with mocked API (workflow.spec.js)
npm run test:e2e:real  # real backend + DB, starts Django itself (real-workflow.spec.js)
npx playwright test tests/e2e/workflow.spec.js -g "<test name>"

# Parser (from parser/)
../venv/Scripts/python.exe main.py --help
```

Playwright uses the installed Chrome channel. The frontend calls `http://<current hostname>:8000` unless `VITE_API_URL` is set (`src/shared/config.jsx`), so it works on localhost and on the office LAN.

## Backend architecture

- **Function-based views.** Nearly all endpoints live in `cars/views.py`, routed in `cars/urls.py` under `/cars/`. Every per-protocol route is wrapped in `protocol_access_required(...)`, which enforces role/ownership checks (IDOR protection). Keep new protocol endpoints wrapped the same way.
- **Data model.** `Protocol` is the root; one-to-one sections hang off it: `ProtocolMeasurement`, `ProtocolBrake`, `ProtocolLight`, `ProtocolTestCondition`, `ProtocolRoadCondition`, `ProtocolPowerSupply`, plus `ProtocolPhoto` rows. Each section has get/create/update endpoints. `DashFieldsMixin` adds "dash" (not applicable) flags to the sections. The catalog is `Brand → Model → Generation → Configuration → CarData`. A protocol's configuration must belong to its generation and match the manufacture month (covered by tests).
- **Workflow.** `Protocol.status`: `measurement → operator → review → approved | cancelled`, with `revision` as the return path from review. Roles are Django groups: `measurer`, `operator`, `manager`, `executive_director`; superusers bypass most restrictions. Operators only see `operator`/`revision` protocols. Status transitions go through dedicated endpoints (`submit-to-operator`, `submit-for-review`, `approve`, `cancel`, `return-to-draft`), not plain updates.
- **Editing locks.** `locked_by`/`locked_at` on `Protocol`. A client calls `start-editing`, then sends `heartbeat` every 30 s, and immediately when the tab becomes visible again. A lock without heartbeat expires after `LOCK_TIMEOUT_MINUTES` (2). Expired locks are cleared when the protocol list loads. A heartbeat takes the lock back if it was lost and nobody else holds it. A second user gets HTTP 423. Closing the tab sends `navigator.sendBeacon` to `release-lock/`; this is a plain Django view that reads the JWT from the body and releases only the caller's own lock. On touch devices the beacon is also sent when the page is hidden, because phones kill a backgrounded browser without `pagehide`; the next heartbeat takes the lock back. The protocol list reloads every minute and when the tab becomes visible again, so expired locks disappear without F5. The list lets a user open a protocol locked by themselves. Managers can force-release a lock.
- **Realtime.** Channels with `InMemoryChannelLayer` (single process). `ws/protocols/` (`consumers.py`) broadcasts status changes. JWT is passed as a WebSocket subprotocol (`["jwt", token]`) and read by `middleware.JwtAuthMiddleware`.
- **Auth/errors.** SimpleJWT for REST. API errors follow one shape, `{detail, code, errors}` (`api_errors.py`). The frontend parses it in `src/shared/errorHandler.jsx`. Server-side numeric range checks live in `numeric_validation.py`, mirrored by `numericRangeValidation.js` on the frontend.

## DOCX/PDF generation pipeline

Entry point is `services/protocol_docx_generator.generate_protocol_docx(protocol)`:

1. `protocol_docx/context.py` builds a flat context dict from the protocol and its sections. It uses `calculations.py` (measurement uncertainty formulas, verified against the lab's Excel workbooks; numeric tests exist in `tests.py`), `applicability.py` (which requirement clauses apply), and `formatters.py`/`labels.py`.
2. `placeholder_aliases.py` adds alias keys. The mapping is documented in `protocol_placeholder_aliases.md` and `V5_PLACEHOLDER_RENAME_MAP.md`.
3. `renderer.py` renders `cars/templates/protocol_template.docx` with a custom python-docx renderer, not plain docxtpl. It replaces `{{ }}` placeholders across runs and handles row-level `{%tr if/else/endif %}` conditions by deleting table rows.
4. The render runs up to three times. `protocol_word.count_word_pages` opens the result in **Microsoft Word via COM (pywin32)** to get the real page count, which is fed back as `protocol_page_count` until it stabilizes. Word must be installed. Output overwrites `<protocol folder>/<number> Протокол.docx` (built in a temp file, then swapped in).

The «Сформировать» button (`generate-docx/` → `generate_protocol_documents`) builds all documents listed in `PROTOCOL_DOCUMENTS` from one shared context: `protocol_template.docx` → «<number> Протокол.docx», `application_template.docx` → «<number> Заявка.docx», `tech_record_template.docx` → «<number> Техзапись.docx». Page counting via Word runs only for the protocol. A document whose template is missing is skipped; a file open in Word is reported (409) while the others are still built. The same button also builds «<number> Лист оценки.xlsx» (uncertainty evaluation sheet) from `evaluation_sheet_template.xlsx`: rows and per-row X / uA / uB / uc / U = 1,65·uc are defined in `services/evaluation_sheet.py` (reusing `calculations.py`, placeholders `ev_<row>_x|_n|_ua|_ub|_uc|_u|_error`, row conditions `ev_*`), and `services/xlsx_renderer.py` (openpyxl) fills `{{ }}` with real numbers and handles `{%tr if/elif/else/endif %}` rows like the DOCX renderer. It also builds «<number> Таблица для техзаписи.xlsx», a paper form for handwriting, from `tech_record_table_template.xlsx` (a copy of «Таблица для техзаписи.xlsx»): values go into column D (`{{ tt_... }}`, `services/tech_record_table.py`), and the smoke rows are removed when А.21.8 does not apply. Both Excel documents are listed in `EXCEL_DOCUMENTS`.

Protocol files live in `services/protocol_storage.py`: `<root>/<number> <VIN> <created dd.mm.yyyy>/<number> <document>.docx` and `<folder>/photos/...`. There are two roots, «В работе» and «Завершённые» (`ProtocolStorageSettings` in the admin; defaults `media/protocols/in_progress|completed`). `Protocol.files_location` says which root holds the folder, `Protocol.files_folder` stores the folder name (read-only via API); `ProtocolPhoto.file_path` is relative to the protocol folder (`photos/...`). VIN is required when the measurer creates a protocol; when it changes, `sync_protocol_folder` renames the folder (on protocol update, «Сформировать» and approve) and returns a warning instead of failing if the rename is impossible. `approve` moves the folder to «Завершённые», `return-to-draft` moves it back. Photos are served via the protected `/cars/protocol-photos/<id>/file/`. The set of photos is fixed in `cars/photo_slots.py` (31 slots: code, title, hint, page group; served to the frontend by `/cars/protocol-photo-slots/`): one photo per slot, file named after the slot title, shown in «Фотофиксация» groups after page blocks 2, 6, 7 and 9, and rendered into the DOCX table «5. Фотоматериалы» (the `{{ photo_image }}`/`{{ photo_caption }}` row pair is repeated per 2 photos in `renderer.expand_photo_table`). Extra photos for the operator (`photo_type='extra'`, `ProtocolPhoto.title`, block «Дополнительные фото» at the end of the protocol page, `Features/ProtocolInspection/ProtocolExtraPhotos.jsx`) have no limit and a required title. They are stored as `photos/Дополнительные/<title>[ (n)].<ext>` and renamed via `protocol-photos/<id>/rename/`. They never go into the DOCX, because `build_photo_values` uses `slot_photos` only. `manage.py relocate_protocol_files [--dry-run] [--source DIR]` migrates old `media/protocol_photos` files and folders from previous roots.

`services/protocol_pdf.py` converts the DOCX to PDF with LibreOffice (`soffice`, searched in standard and `E:/Apps/LibreOffice` paths) in a temp directory for the inline `preview-pdf/` endpoint.

**Dates.**
- `Protocol.protocol_date` is the sampling date. It is set when the measurer creates the protocol, is read-only on the site, and can be changed only in the admin.
  - Placeholder `{{ sample_date }}`: used in the tech record and the application.
- `Protocol.first_generated_date` is the protocol date: the first «Сформировать», never changed afterwards.
  - Placeholder `{{ test_date }}`: used for all protocol dates (including «Дата получения образца») and in the evaluation sheet.
- `TIME_ZONE` is `Asia/Vladivostok`.

**Equipment verifications** (`services/equipment_verification.py`).
- `Equipment` holds the 45 СИ/ИО rows of the equipment tables. `EquipmentVerification` holds the history: number, start date, months. The end date is start + months − 1 day. The number is unique (case and spaces ignored). A record can be deleted on the page only after typing «УДАЛИТЬ»; the history is what old protocols are rebuilt from.
- Initial data comes from the template (migration `0027_load_equipment`).
- The protocol and the tech record show `{{ eq_<si|io><nnn>_verification }}`: the verification valid on the sampling date. On overlap, the one that started earlier wins while it is still valid. Exception: a verification with `supersedes_previous` («используется при пересечении») takes over from its own start date; the latest such active one wins. In the history on the page, the «Используется сейчас» switch is on for exactly one verification. Turning another one on (`use-now/` → `use_verification_now`) makes it the used one among those valid today; this is refused for ended and not-yet-started verifications. The flag in the edit form cannot be changed on an ended verification.
- Without a valid verification, «Сформировать» returns 400 `verification_missing`. Only a superuser can still generate; the nearest verification is used and a warning is returned.
- The page `/equipment-verifications` (API `equipment/…`) is for the executive director and superusers only.
- The first «Сформировать» pins the verifications used: `Protocol.pinned_verifications` = {equipment code: verification id}. Rebuilds use the pinned ones, and a pinned verification cannot be deleted.
- `protocols/<id>/verification-check/` lists the equipment without a valid verification on the sampling date. The protocol page shows it as a warning.
- Expiry reminder goes to Telegram (`services/verification_notifications.py`). Outgoing SMTP is blocked on the office network, so e-mail is not used.
  - It is sent when the server starts: `CarsConfig.ready`, `runserver` only, in a background thread.
  - It is one message listing every equipment whose latest verification ends within 14 days.
  - Each verification is included at most once a day (`expiry_notified_on`).
  - When nothing is expiring, the server instead sends «всё в порядке» once a day (`ReminderLog`, `send_daily_verification_status`).
  - `.env` holds `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` (comma-separated). Without them, a warning is logged and nothing is sent.
  - Commands: `manage.py check_verifications [--dry-run | --test]`. `manage.py telegram_chat_id` lists the chats that wrote to the bot.

When changing template placeholders, update the context builder, the aliases, and the template together.

## Frontend architecture

- Routes are defined in `src/main.jsx`. `Pages/` are route-level screens; `Features/` holds the larger components.
- `Features/ProtocolInspection/` is the main protocol form, split into one component per section. It has local calculation helpers (`brakeCalculations.js`, `speedCalculations.js`) and a local draft store (`protocolDraft.js`). `ProtocolInspection` with `measurementMode` is the measurer's view.
- All HTTP goes through `ApiClient` in `src/shared/api.jsx` (axios, JWT from `localStorage.accessToken`, CSRF client).
- Styling: use the shared `commonSx` and theme from `src/theme.js`, following `src/design-system.md`: black/white palette, square corners, 2px black borders, no shadows, `textTransform: none`. Avoid ad-hoc styles for standard elements.

## Validation expectations (from `.github/copilot-instructions.md`)

- For frontend changes, run `npm run lint` (currently clean, including `react-hooks/exhaustive-deps`) and the relevant build or E2E tests.
- For backend or parser changes, run `manage.py check` and the relevant tests in the venv.
- Say which checks could not be run (e.g. missing MySQL, Word or LibreOffice) and why.
- Don't commit `.env`, generated protocols or media.
