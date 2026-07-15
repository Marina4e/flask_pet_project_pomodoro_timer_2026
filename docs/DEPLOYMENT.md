# Деплой

## Підготовлені deployment-файли

- `Dockerfile`
- `start.sh`
- `render.yaml`
- `.env.example`

## Production startup flow

`start.sh` виконує:

```sh
flask --app run.py db upgrade
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" "app:create_app()"
```

## Render env vars

- `APP_ENV=production`
- `POMODORO_TEST_MODE=false`
- `DEFAULT_TIMEZONE=Europe/Kyiv`
- `SECRET_KEY`
- `DATABASE_URL`

## Локальна база

Локально за замовчуванням використовується `sqlite:///pomodoro.db`, що
резольвиться в `instance/pomodoro.db`.

## Google Calendar

Google Calendar credentials залишаються опціональними й не потрібні для базового деплою.
