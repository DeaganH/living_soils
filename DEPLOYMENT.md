# Deploying to PythonAnywhere

1. **Clone code** to `/home/<user>/DocSense`.
2. **Create venv**: `python3.11 -m venv ~/.virtualenvs/docsense` then `pip install -r requirements.txt`.
3. **Env vars**: copy `.env.example` to `.env`; set `DJANGO_SETTINGS_MODULE=config.settings.production`.
4. **Migrations**: `python manage.py migrate --settings=config.settings.production`.
5. **Collect static**: `python manage.py collectstatic --noinput --settings=config.settings.production`.
6. **WSGI**: point the PythonAnywhere web app to `c:\Projects\Doc Sense\config\wsgi.py` path equivalent on PA (e.g., `/home/<user>/DocSense/config/wsgi.py`).
7. **Static/Media**: map `/static` to `~/DocSense/staticfiles`, `/media` to `~/DocSense/media`.
8. **Async worker**: configure an Always-on task: `workon docsense; python /home/<user>/DocSense/manage.py qcluster --settings=config.settings.production`.
9. **Restart** the web app.
