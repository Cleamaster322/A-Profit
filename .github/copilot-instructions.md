# WebDZ project instructions

## Project structure

- `main/` contains the Django backend and API.
- `car_front/` contains the React/Vite frontend.
- `parser/` contains Python data parsers and database utilities.
- `Бэкап/` contains database backup files. Do not modify these files unless explicitly requested.

## Development rules

- Keep changes focused on the requested task.
- Preserve existing APIs and project conventions unless a change is required.
- Do not commit secrets, local environment files, or generated data.
- Prefer existing helpers and patterns over introducing new abstractions.
- Add or update focused tests when behavior changes.

## Validation

- For frontend changes, run the relevant checks from `car_front/`.
- For backend or parser changes, use the Python virtual environment and run the relevant Django checks or tests.
- Report any validation that could not be run and explain why.
