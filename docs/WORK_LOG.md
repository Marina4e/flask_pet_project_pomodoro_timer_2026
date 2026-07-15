# Журнал роботи

## 2026-07-14 — Аудит, SQLite bootstrap, test mode, and Google Calendar

### Мета

Довести проєкт до стану, коли його можна запустити локально однією простою
командою, перевірити базу окремим скриптом і не плутати користувача старою
Google Sheets документацією.

### Виконана робота

- Проведено повний аудит Markdown-документації, конфігурації, моделей, сервісів, маршрутів, шаблонів, JavaScript і тестів.
- Виявлено, що локальний перший запуск падав без таблиці `user_settings`.
- Додано автоматичне застосування міграцій для локального SQLite-старту.
- Переведено короткий режим на явний `POMODORO_TEST_MODE`.
- Обмежено значення тривалостей до списку, заданого в ТЗ.
- Замінено Google Sheets integration на простий Google Calendar sync останньої `work`-сесії.
- Додано `scripts/check_database.py`.
- Оновлено README, AGENTS і внутрішню документацію під фактичний стан проєкту.
- Запущено браузерний smoke через Playwright для головної сторінки та календаря.

### Змінені файли

- `app/__init__.py` — env overrides і локальний SQLite bootstrap
- `app/config.py` — нові env vars і test mode
- `app/models/work_session.py` — `google_calendar_event_id`
- `app/repositories/session_repository.py` — вибір останньої `work`-сесії
- `app/services/google_calendar_service.py` — новий integration layer
- `app/blueprints/integrations/routes.py` — нові Google Calendar endpoints
- `app/api/schemas/*` — оновлені інтеграційні та settings-схеми
- `app/templates/*`, `app/static/js/*` — оновлений UI і copy
- `tests/*` — нові Google Calendar перевірки
- `scripts/check_database.py` — читання SQLite
- `.env.example`, `render.yaml`, `README.md`, `docs/*`, `AGENTS.md`

### Перевірка

- `python -m compileall app scripts run.py` — PASSED
- `ruff check .` — PASSED
- `black --check .` — PASSED
- `pytest -v` — PASSED (`33 passed`)
- `flask --app run.py routes` — PASSED
- fresh SQLite startup smoke — PASSED
- `python scripts/check_database.py` — PASSED
- Playwright browser smoke — PASSED

### Як перевірити користувачу

1. Запустити `python run.py`.
2. Відкрити `/`.
3. За потреби увімкнути `POMODORO_TEST_MODE=true`.
4. Пройти `Start -> Pause -> Resume -> Reset`.
5. Завершити коротку `work`-сесію.
6. Запустити `python scripts/check_database.py`.
7. Перевірити `/calendar`.
8. За наявності credentials натиснути `Sync to Google Calendar`.

## 2026-07-11 — Підготовка структури та factory

### Мета

Почати проєкт із правильної Flask-архітектури, а не з одного великого файлу.

### Виконана робота

- Створено структуру директорій `app/`, `tests/`, `docs/`, `migrations/`.
- Додано `AGENTS.md`, `run.py`, `wsgi.py`, `requirements.txt`, `pyproject.toml`.
- Реалізовано `create_app()` і класи конфігурації.

### Змінені файли

- `app/__init__.py` — application factory
- `app/config.py` — класи конфігурації
- `app/extensions.py` — розширення Flask
- `AGENTS.md` — правила для майбутніх задач

### Використані Flask-концепції

- Application factory
- Flask configuration
- Extension initialization

### Перевірка

- створення структури — PASSED
- `flask --app run.py routes` — PASSED

### Як перевірити користувачу

1. Відкрити `app/__init__.py`.
2. Переконатися, що там є `create_app()`.
3. Запустити `flask --app run.py routes`.

### Наступний етап

Моделі, репозиторії, сервіси та міграції.

## 2026-07-11 — База даних і бізнес-логіка

### Мета

Додати збереження сесій, налаштування користувача та сервіси для статистики.

### Виконана робота

- Створено моделі `WorkSession` і `UserSettings`.
- Реалізовано репозиторії.
- Реалізовано сервіси таймера, сесій, статистики, календаря, налаштувань і CSV.
- Створено початкову міграцію.

### Змінені файли

- `app/models/*` — структура таблиць
- `app/repositories/*` — SQLAlchemy-запити
- `app/services/*` — бізнес-логіка
- `migrations/` — Alembic-середовище й версії

### Використані Flask-концепції

- Flask-SQLAlchemy
- Flask-Migrate
- Application context

### Перевірка

- `flask --app run.py db init` — PASSED
- `flask --app run.py db migrate -m "Initial migration"` — PASSED
- `flask --app run.py db upgrade` — PASSED

### Як перевірити користувачу

1. Подивитися `app/models/work_session.py`.
2. Запустити `flask --app run.py db upgrade`.
3. Переконатися, що з’явився файл БД.

### Наступний етап

API, Swagger і фронтенд.

## 2026-07-11 — API та інтерфейс

### Мета

Зв’язати Flask API з фронтендом через Jinja та Vanilla JS.

### Виконана робота

- Реалізовано Blueprints для sessions, statistics, calendar, settings, export, health.
- Додано Swagger UI й OpenAPI JSON.
- Створено сторінки `index`, `statistics`, `calendar`.
- Додано таймер, налаштування, графік, календар і теми.

### Змінені файли

- `app/blueprints/*/routes.py` — HTTP-рівень
- `app/api/schemas/*` — Marshmallow-схеми
- `app/templates/*` — сторінки та компоненти
- `app/static/js/*` — логіка браузера
- `app/static/css/*` — стилі та адаптивність

### Використані Flask-концепції

- Blueprint
- Request / JSON
- Jinja templates
- Flask-Smorest

### Перевірка

- `flask --app run.py routes` — PASSED
- `python -m compileall app run.py wsgi.py` — PASSED

### Як перевірити користувачу

1. Відкрити `/`.
2. Перевірити кнопки таймера.
3. Відкрити `/api/docs`.
4. Відкрити `/calendar`.

### Наступний етап

Тести, лінтинг, coverage і документація.

## 2026-07-11 — Тести та якість коду

### Мета

Переконатися, що MVP працює не лише вручну, а й через автоматичні перевірки.

### Виконана робота

- Написано 27 тестів.
- Виправлено серіалізацію ISO-рядків у схемах відповіді.
- Виправлено обробку 422 validation errors.
- Налаштовано Ruff і Black.

### Змінені файли

- `tests/*` — повний набір тестів
- `app/api/error_handlers.py` — JSON-помилки
- `app/api/schemas/*` — API-контракти

### Використані Flask-концепції

- Flask test client
- Testing config
- Error handling

### Перевірка

- `ruff check .` — PASSED
- `black --check .` — PASSED
- `pytest -v` — PASSED
- `pytest --cov=app --cov-report=term-missing` — PASSED

### Як перевірити користувачу

1. Запустити `pytest -v`.
2. Запустити `pytest --cov=app --cov-report=term-missing`.
3. Переглянути coverage summary.

### Наступний етап

Оформлення deployment-файлів і фінальної документації.

## 2026-07-11 — Інфраструктура та фінальна перевірка

### Мета

Підготувати проєкт до Docker/Render і зафіксувати реальні результати перевірок.

### Виконана робота

- Додано `Dockerfile`, `start.sh`, `render.yaml`.
- Перевірено локальний health endpoint через HTTP.
- Перевірено production import шляху через Python.
- Задокументовано Windows-обмеження Gunicorn.

### Змінені файли

- `Dockerfile` — контейнерний запуск
- `start.sh` — migrate + Gunicorn
- `render.yaml` — Render-конфігурація
- `README.md`, `docs/*` — фінальна документація

### Використані Flask-концепції

- WSGI entrypoint
- Production configuration
- Health endpoint

### Перевірка

- `python -c "from app import create_app; app = create_app('production'); print(app.config['ENV_NAME'])"` — PASSED
- `Invoke-RestMethod http://127.0.0.1:5010/api/health` — PASSED
- `gunicorn --check-config "app:create_app()"` — FAILED: Windows не має `fcntl`

### Як перевірити користувачу

1. Прочитати `README.md`.
2. Запустити локальний Flask-сервер.
3. Перевірити `/api/health`, `/api/docs`, `/calendar`.
4. За потреби виконати Docker build або Render deploy у Linux-сумісному середовищі.

### Наступний етап

Linux/Docker перевірка Gunicorn і реальний Render-деплой із PostgreSQL.

## 2026-07-11 — Виправлення експорту та календарної навігації

### Мета

Закрити функціональні дрібниці, які знайшлися під час повторної верифікації MVP: фільтрацію CSV-експорту та синхронізацію деталей дня на сторінці календаря.

### Виконана робота

- Виправлено `app/blueprints/export/routes.py`, щоб експорт підтримував `date_from` або `date_to` окремо.
- Додано валідацію діапазону дат для CSV-експорту з помилкою `400`, якщо `date_to < date_from`.
- Виправлено `app/static/js/calendar.js`, щоб під час переходу між місяцями панель деталей не поверталася до сьогоднішньої дати поза видимим місяцем.
- Додано 2 нові тести для CSV-експорту.
- Оновлено `docs/CURRENT_STATUS.md`, `docs/CHANGELOG.md` і `README.md` під фактичні результати перевірки.

### Змінені файли

- `app/blueprints/export/routes.py` — коректна обробка одно- та двосторонніх діапазонів дат для CSV
- `app/static/js/calendar.js` — синхронізація вибраної дати з видимим місяцем
- `tests/test_export_api.py` — перевірка фільтрації та невалідного діапазону експорту
- `docs/CURRENT_STATUS.md` — актуалізація перевірок і статусу
- `docs/CHANGELOG.md` — запис змін і перевірок
- `README.md` — оновлені фактичні результати та опис CSV-експорту

### Використані Flask-концепції

- Blueprint
- Query parameters
- Validation error handling
- Flask test client

### Перевірка

- `pytest -v tests/test_export_api.py` — PASSED
- `black tests/test_export_api.py` — PASSED
- `ruff check app/blueprints/export/routes.py tests/test_export_api.py` — PASSED
- `ruff check .` — PASSED
- `black --check .` — PASSED
- `pytest -v` — PASSED (`29 passed`)
- `pytest --cov=app --cov-report=term-missing` — PASSED (`90% coverage`)
- `Invoke-RestMethod http://127.0.0.1:5010/api/health` — PASSED

### Як перевірити користувачу

1. Відкрити `/calendar`.
2. Перейти на попередній або наступний місяць і переконатися, що панель деталей показує дату з видимого місяця.
3. Відкрити `/api/export/sessions.csv?date_from=YYYY-MM-DD&timezone=UTC`.
4. Спробувати невалідний діапазон `/api/export/sessions.csv?date_from=2026-07-11&date_to=2026-07-10&timezone=UTC` і перевірити `400`.

### Наступний етап

Додати браузерну автоматизацію для фронтенд-перевірок і Linux-перевірку Gunicorn/Docker.

## 2026-07-14 — Bootstrap-редизайн, автоцикли таймера та Google Sheets

### Мета

Перетворити MVP-дашборд на яскравіший Bootstrap-лендинг, зробити таймер логічнішим для щоденного використання та додати реальний Flask-шлях для Google Sheets sync.

### Виконана робота

- Перебудовано головну сторінку під Bootstrap 5.3 carousel-structure із яскравішими секціями та чітким порядком контенту.
- Додано анімованого помідорчика, який починає “бігти” під час активного таймера.
- Оновлено `timer.js`: додано demo-пресет `10с / 5с`, автоцикли `work -> break`, configurable long break interval і auto-start next session.
- Розширено `user_settings`, API-схеми та сервіс налаштувань для нових таймерних параметрів.
- Додано Flask API для `GET /api/integrations/google-sheets/status` і `POST /api/integrations/google-sheets/sync`.
- Додано `GoogleSheetsService` з env-driven service-account конфігурацією й snapshot-синхронізацією sessions + summary.
- Оновлено `.env.example`, `README.md`, `docs/CURRENT_STATUS.md`, `docs/CHANGELOG.md`, `docs/WORK_LOG.md` і `docs/FILE_MAP.md`.
- Додано 2 нові тести для інтеграції, загальна кількість тестів стала `31`.

### Змінені файли

- `app/templates/*` — новий landing layout, timer card, stats cards, settings card, tomato component
- `app/static/css/*` — яскравіші стилі, Bootstrap-сумісна адаптивність, анімація помідора
- `app/static/js/timer.js` — пресети, автоцикл, синхронізація стану анімації
- `app/static/js/settings.js`, `statistics.js`, `theme.js`, `integrations.js` — нові UI та integration flows
- `app/models/user_settings.py`, `app/services/settings_service.py`, `app/api/schemas/settings.py` — нові налаштування таймера
- `app/services/google_sheets_service.py`, `app/blueprints/integrations/routes.py`, `app/api/schemas/google_sheets.py` — Sheets integration layer
- `migrations/versions/8c4f1d2a9b31_add_timer_cycle_and_google_sheets_settings.py` — міграція нових полів
- `tests/test_integrations_api.py`, `tests/test_settings_api.py`, `tests/test_pages.py`, `tests/test_services.py` — оновлене покриття
- `.env.example`, `pyproject.toml`, `README.md`, `docs/*` — конфіг, команди та документація

### Використані Flask-концепції

- Blueprint
- Flask-Smorest request/response schemas
- Service layer
- Application config via environment variables
- Flask test client

### Перевірка

- `python -m compileall app run.py wsgi.py` — PASSED
- `ruff check .` — PASSED
- `black --check .` — PASSED
- `flask --app run.py routes` — PASSED
- `flask --app run.py db upgrade` — PASSED
- `pytest -v` — PASSED (`31 passed`)
- `pytest --cov=app --cov-report=term-missing` — PASSED (`86% coverage`)

### Як перевірити користувачу

1. Відкрити `/` і перевірити Bootstrap-carousel hero.
2. Натиснути `Start` і переконатися, що помідорчик почав бігти.
3. Обрати `Demo 10с / 5с` і перевірити автоматичне переключення на break.
4. Перевірити секції `Часы за день`, `Часы за неделю`, `Часы за месяц`.
5. За наявності `.env` credentials натиснути `Синхронизировать сейчас`.
6. Відкрити `/api/integrations/google-sheets/status`.

### Наступний етап

Додати браузерну візуальну перевірку нового лендингу та позитивний mocked-path test для реального Google Sheets sync.

## 2026-07-14 — Environment docs, cartoon tomato, and leaner buttons

### Мета

Уточнити інструкції з `.env` і Google Sheets, прибрати зайві кнопки з лендингу та зробити помідорчика більш мультяшним без зайвих архітектурних змін.

### Виконана робота

- Додано в `README.md` покрокове пояснення всіх `.env` змінних.
- Додано окремі покрокові інструкції, як знайти `GOOGLE_SHEETS_SPREADSHEET_ID`.
- Додано покрокові інструкції, як створити service account, увімкнути `Google Sheets API`, поділитися таблицею з `client_email` і перетворити JSON в один рядок.
- Додано розділ швидкої ручної перевірки фронтенду.
- Створено `spec.md` для економного file-by-file workflow.
- Створено `docs/STEP_BY_STEP_PLAN.md` з фазами роботи та reusable next-step prompt.
- Прибрано зайві hero CTA-кнопки.
- Переміщено `Export CSV` у картку таймера.
- Приховано кнопку Google Sheets sync, доки integration не налаштована.
- Замінено SVG помідора на більш мультяшний варіант із чіткішим idle/running відчуттям.

### Змінені файли

- `README.md` — детальні `.env` та Google Sheets інструкції
- `spec.md` — внутрішня робоча специфікація
- `docs/STEP_BY_STEP_PLAN.md` — поетапний план і reusable prompt
- `app/templates/index.html` — менше зайвих кнопок
- `app/templates/components/timer.html` — `Export CSV` у блоці таймера
- `app/templates/components/tomato_runner.html` — новий мультяшний SVG
- `app/static/css/styles.css` — стилі нового помідора та idle/running станів
- `app/static/js/integrations.js` — sync button ховається до готової конфігурації
- `docs/CURRENT_STATUS.md`, `docs/CHANGELOG.md`, `docs/WORK_LOG.md`, `docs/FILE_MAP.md` — актуалізація документації

### Використані Flask-концепції

- Jinja templates
- static asset updates
- environment-driven integration UX

### Перевірка

- `ruff check .` — PASSED
- `black --check .` — PASSED
- `pytest -v` — PASSED (`31 passed`)

### Як перевірити користувачу

1. Відкрити README і звірити `.env` з власним файлом.
2. Відкрити `/` і перевірити, що зверху немає зайвих hero CTA-кнопок.
3. Перевірити, що `Export CSV` тепер знаходиться в блоці таймера.
4. Перевірити, що без Google Sheets env кнопка sync не показується.
5. Натиснути `Start` і перевірити мультяшного помідорчика у стані бігу.

### Наступний етап

При потребі зробити окремий повний English-only pass для всього фронтенд-контенту та прив’язати точніший образ помідора після отримання прямого зображення або прикріпленого скриншота.

## 2026-07-14 — Bootstrap Carousel і перевірка timezone `Europe/Kyiv`

### Мета

Точково довести головну Bootstrap-карусель до більш офіційної структури з
переходами між секціями і перевірити, чи справді статистичні endpoint-и
ламаються на `timezone=Europe/Kyiv`.

### Виконана робота

- Перевірено поточний HTML, CSS, JS і тести лише в межах carousel/statistics scope.
- Підтягнуто структуру головної каруселі ближче до офіційного Bootstrap 5.3 carousel example:
  п’ять слайдів, індикатори, `Previous` / `Next`, кнопки переходу до реальних сторінок і секцій.
- Додано `id="settings-panel"` для прямого переходу із слайду налаштувань.
- Оновлено стилі каруселі для desktop і mobile, щоб стрілки не зникали на `390x844`
  і не з’являвся горизонтальний overflow.
- Додано regression tests для `Europe/Kyiv`, `UTC`, missing timezone і invalid timezone.
- Перевірено реальний HTTP-запуск локального Flask-сервера:
  `Europe/Kyiv` на `/api/statistics/month`, `/week`, `/chart` повернув `200`.
- Backend timezone-логіку не змінювали, бо `400` на `Europe/Kyiv` не відтворився
  на поточному дереві.
- Додано inline favicon, щоб браузерний smoke більше не давав `404` у консолі.

### Змінені файли

- `app/templates/index.html` — нова структура Bootstrap-carousel з deeplink-кнопками
- `app/templates/components/settings_panel.html` — `id="settings-panel"` для якірного переходу
- `app/templates/base.html` — inline favicon без окремого статичного файлу
- `app/static/css/styles.css` — новий visual layer для carousel slides і controls
- `app/static/css/responsive.css` — mobile-поведінка carousel без прихованих стрілок
- `tests/test_pages.py` — перевірки carousel markup і Bootstrap assets
- `tests/test_statistics_api.py` — timezone regression coverage
- `docs/CURRENT_STATUS.md`, `docs/CHANGELOG.md`, `docs/WORK_LOG.md`, `README.md` — актуалізація під результат цього точкового завдання

### Використані Flask-концепції

- Jinja templates
- static asset integration
- Flask test client
- query-parameter validation through existing statistics routes

### Перевірка

- `pytest tests/test_pages.py tests/test_statistics_api.py -v` — PASSED
- `python -m compileall app` — PASSED
- `ruff check .` — PASSED
- `black --check .` — PASSED
- `pytest -v` — PASSED (`41 passed`)
- `pytest tests/test_pages.py -v` — PASSED
- live HTTP smoke for `/` and statistics timezone endpoints — PASSED
- Playwright + Edge headless smoke for carousel desktop/mobile flow — PASSED

### Як перевірити користувачу

1. Відкрити `/`.
2. Переконатися, що перший слайд каруселі активний.
3. Натиснути `Next`, потім `Previous`.
4. Натиснути індикатор `Calendar` і кнопку `Open Calendar`.
5. Повернутися на `/`, натиснути індикатор `Settings` і кнопку `Open Settings`.
6. Відкрити `/api/statistics/month?timezone=Europe/Kyiv`.
7. Відкрити `/api/statistics/week?timezone=Europe/Kyiv`.
8. Відкрити `/api/statistics/chart?timezone=Europe/Kyiv`.

### Наступний етап

Якщо `400` на `Europe/Kyiv` з’являється лише в іншому середовищі, тоді вже
потрібно збирати точний reproducer: OS image, Python build і встановлені
timezone-data пакети.

## 2026-07-15 — Frontend cleanup and valid timezone settings

### Мета

Зробити існуючий frontend компактним і повністю англомовним, повернути
Pomodoro image у carousel та зробити timezone settings зрозумілими й
перевірюваними.

### Виконана робота

- Перекладено видимі рядки в `base`, home, statistics, calendar, settings,
  timer та error templates, а також у browser messages.
- У carousel повторно використано наявний `tomato-idle.png`; додано однакову
  image-and-text структуру для п’яти слайдів без нового asset або dependency.
- Видалено redundant feature teaser row, зменшено carousel/card/calendar
  spacing і залишено responsive Bootstrap layout.
- Statistics cards зроблено компактними: Today, This Week, This Month,
  Completed Pomodoros.
- Основні settings залишено в одному compact row; theme, sound, auto-start і
  cycle interval перенесено в Bootstrap Advanced Settings accordion.
- У settings додано активне значення timezone, IANA example `Europe/Kyiv`,
  helper text про daily/weekly/monthly statistics та field-level error message.
- Shared `get_timezone()` тепер trim-ить input; settings зберігають normalized
  timezone, а invalid save повертає форму до попереднього valid state.
- Reproducer знайдено в project `.venv`: Python 3.12 на Windows не мав
  `tzdata` і повертав `ZoneInfoNotFoundError` для `Europe/Kyiv`, тоді як system
  Python 3.13 приховував проблему. Додано `tzdata>=2024.1` у `requirements.txt`.

### Змінені файли

- Frontend templates: `app/templates/`
- Frontend styles: `app/static/css/styles.css`, `app/static/css/responsive.css`
- Frontend scripts: `app/static/js/timer.js`, `settings.js`, `statistics.js`, `calendar.js`
- Timezone logic: `app/time_utils.py`, `app/services/settings_service.py`
- Dependency: `requirements.txt`
- Regression tests: `tests/test_pages.py`, `tests/test_statistics_api.py`, `tests/test_settings_api.py`
- Documentation: `README.md`, `docs/CURRENT_STATUS.md`, `docs/CHANGELOG.md`, `docs/WORK_LOG.md`

### Перевірка

- `pytest tests/test_statistics_api.py tests/test_settings_api.py tests/test_pages.py -v` — `21 passed`
- `python -m compileall app scripts run.py` — PASSED
- `ruff check .` — PASSED
- `black --check .` — PASSED
- `node --check` for all frontend JavaScript files — PASSED
- `pytest -v` — `45 passed`
- live HTTP smoke — valid `Europe/Kyiv` / `UTC` returned `200`; invalid
  timezone returned `400` on month, week, and chart endpoints
- project `.venv` `ZoneInfo('Europe/Kyiv')` after installing `tzdata` — PASSED
- Windows browser-control smoke was attempted but stopped because the tool
  could not safely determine the current Chrome URL; no visual result is
  claimed from that attempt.
