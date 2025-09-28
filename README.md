# SplitWise Clone (Flask)

A minimal SplitWise-like expense splitter built with Flask, Bootstrap, and JSON storage.

## Local Development

- Python 3.10+
- Create and activate a virtualenv (optional)
- Install deps: `pip install -r requirements.txt`
- Run: `flask --app app run --debug`

Data is stored in `data/store.json`. A default `SECRET_KEY` is used for dev; override with `SECRET_KEY` env var.

## Deploy (Render)

This repo includes `render.yaml` for one‑click deploy on Render.

1. Push this project to a GitHub repo.
2. Go to https://render.com and create a new Web Service from your GitHub repo.
3. Render will auto-detect from `render.yaml`:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
   - Environment: Python
4. Ensure `SECRET_KEY` is set (Render blueprint already generates one).
5. After deploy, your app will be available at `https://<your-service>.onrender.com`.

## Deploy (Heroku alternative)

This repo has a `Procfile` for Heroku-like platforms:

- Create app, set buildpack to Python
- `heroku config:set SECRET_KEY=<random>`
- `git push heroku main`

## Environment Variables

- `SECRET_KEY` – Flask secret (cookies/flash). Required in production.
- `STORAGE_DIR` – Optional path to data directory (defaults to `./data`).

## Notes

- JSON storage is simple and suitable for demos. For multi-user production, use a real DB.
- Remove `instance/splitwise.db` if not needed (not used by this app).
