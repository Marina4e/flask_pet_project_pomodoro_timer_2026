# Розробка

## Локальне середовище

- Python 3.12+
- virtual environment
- SQLite для локальної БД

## Перший запуск

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python run.py
```

## Основні команди

```bash
python run.py
python scripts/check_database.py
python -m compileall app scripts run.py
ruff check .
black --check .
pytest -v
flask --app run.py routes
```

## Test mode

```powershell
$env:POMODORO_TEST_MODE="true"
python run.py
```

У цьому режимі в UI видно кнопку `Test mode 10с / 5с`.
