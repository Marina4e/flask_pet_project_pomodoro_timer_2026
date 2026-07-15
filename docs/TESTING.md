# Тестування

## Автоматичні перевірки, які були виконані в цій сесії

```bash
python -m compileall app scripts run.py
ruff check .
black --check .
pytest -v
flask --app run.py routes
python scripts/check_database.py
```

## Фактичні результати

- `ruff check .` — PASSED
- `black --check .` — PASSED
- `pytest -v` — PASSED (`33 passed`)
- `flask --app run.py routes` — PASSED
- fresh SQLite startup smoke — PASSED
- `python scripts/check_database.py` на реальній SQLite-базі — PASSED

## Що покривають тести

- app factory
- сторінки
- sessions API
- statistics API
- calendar API
- settings API
- CSV export
- Google Calendar status
- Google Calendar sync failure without credentials
- mocked successful Google Calendar sync
- duplicate-sync prevention
- service-layer rules
