# Pomodoro Work Tracker

Single-user educational Flask portfolio project for Pomodoro timing, session
tracking, statistics, calendar views, CSV export, simple Google Calendar sync,
and deployment practice.

## Stack

- Python 3.12+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Smorest
- Marshmallow
- Jinja2
- Vanilla JavaScript
- Chart.js
- Gunicorn

## Main Commands

- `python run.py`
- `python scripts/check_database.py`
- `python -m compileall app scripts run.py`
- `ruff check .`
- `black --check .`
- `pytest -v`
- `flask --app run.py routes`
- `flask --app run.py db upgrade`
- `gunicorn "app:create_app()"`

## Architecture Layers

- `app/__init__.py`: application factory and local SQLite bootstrap
- `app/extensions.py`: Flask extension objects
- `app/models/`: SQLAlchemy models
- `app/repositories/`: database query layer
- `app/services/`: business logic layer
- `app/blueprints/`: page and API routes
- `app/api/schemas/`: Marshmallow validation and serialization
- `app/templates/` and `app/static/`: Jinja frontend and browser assets
- `scripts/check_database.py`: read-only SQLite inspection helper

## Future Task Rules

- Read `docs/PROJECT_CONTEXT.md`, `docs/CURRENT_STATUS.md`, and `docs/FILE_MAP.md` first.
- Read only files directly related to the current task.
- Do not reread the entire repository unless necessary.
- Do not modify unrelated functionality.
- Change the minimum necessary number of files.
- Run relevant tests for the task.
- Run the full `pytest` suite when possible.
- Report only commands and checks that were actually executed.
- Update documentation after every task.
- Explain changes step by step for the user.

For every future task:

1. Read `docs/PROJECT_CONTEXT.md`.
2. Read `docs/CURRENT_STATUS.md`.
3. Read `docs/FILE_MAP.md`.
4. Identify only the files related to the task.
5. Do not reread the entire repository unless necessary.
6. Explain the planned changes step by step.
7. Change the minimum necessary number of files.
8. Do not modify unrelated functionality.
9. Run relevant tests.
10. Run the full test suite when possible.
11. Update `docs/CURRENT_STATUS.md`.
12. Update `docs/CHANGELOG.md`.
13. Update `docs/WORK_LOG.md`.
14. Update `docs/FILE_MAP.md` only when important files change.
15. Update `README.md` only when user-facing behavior or commands change.
16. Explain what was changed, why it was changed, and how to verify it.
17. Report only commands and checks that were actually executed.

## Правила последующих изменений

1. Перед работой прочитать `AGENTS.md` и связанные документы.
2. Найти точную причину проблемы.
3. Перечислить файлы, которые нужно изменить.
4. Не изменять архитектуру без необходимости.
5. Не изменять несвязанные файлы.
6. Не добавлять новые функции без отдельного задания.
7. Не удалять работающие функции.
8. Делать минимальное исправление.
9. Запускать связанные тесты.
10. Давать ручной сценарий проверки.
11. Честно сообщать, если проблема не воспроизводится.
12. Не менять Flask на другой фреймворк.
13. Не удалять SQLite-базу пользователя.
14. Не коммитить Google credentials.
15. Не переписывать целый шаблон ради одной кнопки.

## Шаблон дальнейшего задания для Codex

```text
Проверь проблему: [описание проблемы].

Перед внесением изменений:

1. Прочитай AGENTS.md и связанные Markdown-документы.
2. Найди точную причину проблемы.
3. Перечисли файлы, которые планируешь изменить.
4. Не меняй архитектуру проекта.
5. Не изменяй несвязанные части.
6. Не добавляй новые функции.
7. Не удаляй работающие функции.
8. Сделай минимальное исправление.
9. Запусти связанные тесты.
10. Дай пошаговую инструкцию ручной проверки.
11. Перечисли измененные файлы.
12. Объясни, что выполняет измененный Flask-маршрут или функция.
13. Если проблема не подтверждена, не изменяй код и опиши результат проверки.
```
