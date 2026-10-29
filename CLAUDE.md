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
- **Editing locks.** `locked_by`/`locked_at` on `Protocol`. A client calls `start-editing`, then sends `heartbeat`. A second user gets HTTP 423. Managers can force-release a lock.
- **Realtime.** Channels with `InMemoryChannelLayer` (single process). `ws/protocols/` (`consumers.py`) broadcasts status changes. JWT is passed as a WebSocket subprotocol (`["jwt", token]`) and read by `middleware.JwtAuthMiddleware`.
- **Auth/errors.** SimpleJWT for REST. API errors follow one shape, `{detail, code, errors}` (`api_errors.py`). The frontend parses it in `src/shared/errorHandler.jsx`. Server-side numeric range checks live in `numeric_validation.py`, mirrored by `numericRangeValidation.js` on the frontend.

## DOCX/PDF generation pipeline

Entry point is `services/protocol_docx_generator.generate_protocol_docx(protocol)`:

1. `protocol_docx/context.py` builds a flat context dict from the protocol and its sections. It uses `calculations.py` (measurement uncertainty formulas, verified against the lab's Excel workbooks; numeric tests exist in `tests.py`), `applicability.py` (which requirement clauses apply), and `formatters.py`/`labels.py`.
2. `placeholder_aliases.py` adds alias keys. The mapping is documented in `protocol_placeholder_aliases.md` and `V5_PLACEHOLDER_RENAME_MAP.md`.
3. `renderer.py` renders `cars/templates/protocol_template.docx` with a custom python-docx renderer, not plain docxtpl. It replaces `{{ }}` placeholders across runs and handles row-level `{%tr if/else/endif %}` conditions by deleting table rows.
4. The render runs up to three times. `protocol_word.count_word_pages` opens the result in **Microsoft Word via COM (pywin32)** to get the real page count, which is fed back as `protocol_page_count` until it stabilizes. Word must be installed. Output overwrites `<protocol folder>/<number> Протокол.docx` (built in a temp file, then swapped in).

The «Сформировать» button (`generate-docx/` → `generate_protocol_documents`) builds all documents listed in `PROTOCOL_DOCUMENTS` from one shared context: `protocol_template.docx` → «<number> Протокол.docx», `application_template.docx` → «<number> Заявка.docx», `tech_record_template.docx` → «<number> Техзапись.docx». Page counting via Word runs only for the protocol. A document whose template is missing is skipped; a file open in Word is reported (409) while the others are still built. The same button also builds «<number> Лист оценки.xlsx» (uncertainty evaluation sheet) from `evaluation_sheet_template.xlsx`: rows and per-row X / uA / uB / uc / U = 1,65·uc are defined in `services/evaluation_sheet.py` (reusing `calculations.py`, placeholders `ev_<row>_x|_n|_ua|_ub|_uc|_u|_error`, row conditions `ev_*`), and `services/xlsx_renderer.py` (openpyxl) fills `{{ }}` with real numbers and handles `{%tr if/elif/else/endif %}` rows like the DOCX renderer.

Protocol files live in `services/protocol_storage.py`: `<root>/<number> <VIN> <created dd.mm.yyyy>/<number> <document>.docx` and `<folder>/photos/...`. There are two roots, «В работе» and «Завершённые» (`ProtocolStorageSettings` in the admin; defaults `media/protocols/in_progress|completed`). `Protocol.files_location` says which root holds the folder, `Protocol.files_folder` stores the folder name (read-only via API); `ProtocolPhoto.file_path` is relative to the protocol folder (`photos/...`). VIN is required when the measurer creates a protocol; when it changes, `sync_protocol_folder` renames the folder (on protocol update, «Сформировать» and approve) and returns a warning instead of failing if the rename is impossible. `approve` moves the folder to «Завершённые», `return-to-draft` moves it back. Photos are served via the protected `/cars/protocol-photos/<id>/file/`. The set of photos is fixed in `cars/photo_slots.py` (31 slots: code, title, hint, page group; served to the frontend by `/cars/protocol-photo-slots/`): one photo per slot, file named after the slot title, shown in «Фотофиксация» groups after page blocks 2, 6, 7 and 9, and rendered into the DOCX table «5. Фотоматериалы» (the `{{ photo_image }}`/`{{ photo_caption }}` row pair is repeated per 2 photos in `renderer.expand_photo_table`). `manage.py relocate_protocol_files [--dry-run] [--source DIR]` migrates old `media/protocol_photos` files and folders from previous roots.

`services/protocol_pdf.py` converts the DOCX to PDF with LibreOffice (`soffice`, searched in standard and `E:/Apps/LibreOffice` paths) in a temp directory for the inline `preview-pdf/` endpoint.

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
