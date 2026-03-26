# Doc Sense – AI Presentation Feedback

Django 4.x monolith to upload PDF decks, process them asynchronously via an LLM API, and deliver feedback in a shared library. Target platform: PythonAnywhere.

## Getting Started

1. **Python**: 3.11 (PythonAnywhere system image that supports Django 4.x).
2. **Install deps**: `pip install -r requirements.txt`
3. **Env vars**: copy `.env.example` to `.env` and fill values.
4. **Migrate**: `python manage.py migrate`
5. **Run dev server**: `python manage.py runserver`
6. **Start worker (Django-Q)**: `python manage.py qcluster`

## Key Apps

- `presentations`: upload handling, async processing, LLM API calls, feedback views.

## Deployment (PythonAnywhere summary)

- Add a **Virtualenv** with project deps.
- Set `DJANGO_SETTINGS_MODULE=config.settings.production`.
- Point WSGI file to `config/wsgi.py`.
- Collect static: `python manage.py collectstatic --noinput`.
- Run DB migrations.
- Start `qcluster` as a PythonAnywhere **always-on task**.

## Directories

- `config/`: project settings, URLs, ASGI/WSGI.
- `presentations/`: domain app with models, tasks, views, templates.
- `templates/`, `static/`, `media/`: user-facing assets and uploads.

## Tests

Add tests under `presentations/tests/` (not scaffolded yet).
