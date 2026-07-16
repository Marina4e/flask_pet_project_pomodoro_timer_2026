# Pomodoro Work Tracker

## Головне відео проєкту

Стисла копія відео проєкту (8,2 МБ), оптимізована для перегляду в README.
Особистий Calendar ID у відео замаскований.

<video controls preload="metadata" width="760" src="docs/videos/timer-project.mp4"></video>

[Завантажити відео проєкту](docs/videos/timer-project.mp4)

## Відеозвіт про проєкт

Нижче — три відео з англійською озвучкою: огляд застосунку та відповідальності
класів, пояснення реальної SQLite-бази і демонстрація Google Sheets. У копії для
README ідентифікатори рядків Google Sheets замасковані.

<video controls preload="metadata" width="760" src="docs/videos/pomodoro-project-walkthrough.mp4"></video>

[Завантажити відео 1: project walkthrough](docs/videos/pomodoro-project-walkthrough.mp4)

<video controls preload="metadata" width="760" src="docs/videos/sqlite-database-report.mp4"></video>

[Завантажити відео 2: SQLite database report](docs/videos/sqlite-database-report.mp4)

<video controls preload="metadata" width="760" src="docs/videos/google-sheets-export-report.mp4"></video>

[Завантажити відео 3: Google Sheets export report](docs/videos/google-sheets-export-report.mp4)

[![CI](https://github.com/Marina4e/flask_pet_project_pomodoro_timer_2026/actions/workflows/ci.yml/badge.svg)](https://github.com/Marina4e/flask_pet_project_pomodoro_timer_2026/actions/workflows/ci.yml)
![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![Flask 3.1](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)

[English README](README.en.md) ·
[Інструкція Google Cloud: Pomodoro, Calendar і Sheets](docs/GOOGLE_INTEGRATIONS_GUIDE.md) ·
[Інструкція для захисту](docs/PROJECT_DEFENSE_GUIDE.md) ·
[API docs після запуску](http://127.0.0.1:5000/api/docs)

`Pomodoro Work Tracker` — однокористувацький навчальний Flask-застосунок для
focus-таймера, обліку завершених сесій, статистики, календаря активності,
CSV-експорту та опціональних інтеграцій Google Calendar і Google Sheets.

> Google-сервіси не є обов'язковими. Таймер, SQLite, статистика, календар
> активності та CSV працюють без Google credentials.

## Українська версія

### 1. Призначення проєкту

`Pomodoro Work Tracker` допомагає чергувати focus та break-інтервали, зберігає
нормально завершені сесії у локальній SQLite-базі й перетворює ці записи на
статистику, календар активності та CSV. За бажанням користувач може вручну:

- створити Google Calendar event для останньої завершеної `work`-сесії;
- експортувати завершені `work`-сесії як рядки Google Sheets.

Це навчальний portfolio-проєкт: він демонструє повний шлях від браузерного
таймера до Flask API, SQLAlchemy, migrations, зовнішніх Google API, тестів і
Docker. Він не позиціонується як enterprise або multi-user SaaS.

### 2. Реалізовані можливості

- `Start`, `Pause`, `Resume`, `Reset` і `Skip` для `work`, `short_break` та
  `long_break`;
- стандартні тривалості: `work` — 25 хвилин, `short_break` — 5 хвилин,
  `long_break` — 25 хвилин;
- автоматичний перехід між focus і break, а також опціональний auto-start;
- відновлення активного countdown після reload через `localStorage`;
- збереження нормально завершених focus і break-сесій у SQLite;
- окремий облік `focus_minutes`, `break_minutes` і `total_tracked_minutes`;
- статистика за день, тиждень і місяць та 7-денний Chart.js-графік;
- activity calendar з деталями за вибраний день;
- налаштування тривалості, циклів, теми, звуку та IANA timezone;
- CSV export;
- швидкий `POMODORO_TEST_MODE` з інтервалами `10 / 5 / 5` секунд;
- ручна optional-синхронізація з Google Calendar і Google Sheets;
- OpenAPI/Swagger, pytest, Ruff, Black, Docker і Gunicorn.

### 3. Технології

| Шар | Технології |
| --- | --- |
| Backend | Python 3.12+, Flask, Flask-Smorest, Marshmallow |
| Data | Flask-SQLAlchemy, SQLite, Flask-Migrate/Alembic |
| Frontend | Jinja2, Bootstrap 5.3, Vanilla JavaScript, Chart.js |
| Google | Google Calendar API, Google Sheets API, service account |
| Quality | pytest, Ruff, Black, compileall |
| Deployment | Docker, Gunicorn, `start.sh` |

### 4. Швидкий запуск на Windows

```powershell
git clone <PROJECT_URL>
cd flask_pet_project_pomodoro_timer_2026

py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

Copy-Item .env.example .env
python run.py
```

Відкрийте `http://127.0.0.1:5000`. Для зупинки натисніть `Ctrl+C`.

`create_app()` завантажує `.env`, реєструє extensions і blueprints, застосовує
migrations для локальної SQLite та створює default settings. Змінна, уже задана
в PowerShell, має пріоритет над однойменним значенням із `.env`; після зміни
`.env` сервер потрібно перезапустити.

### 5. Основні environment variables

```dotenv
APP_ENV=development
SECRET_KEY=replace-with-a-secure-secret
DEBUG=true
DATABASE_URL=sqlite:///pomodoro.db
DEFAULT_TIMEZONE=Europe/Kyiv
DEFAULT_CYCLES_BEFORE_LONG_BREAK=4
POMODORO_TEST_MODE=false

# Google Calendar: optional; leave required values blank to keep it unconfigured.
GOOGLE_CALENDAR_ID=
GOOGLE_CALENDAR_CREDENTIALS_JSON=
GOOGLE_CALENDAR_EVENT_PREFIX=Pomodoro
GOOGLE_CALENDAR_EVENT_COLOR_ID=

# Google Sheets: independent and optional.
GOOGLE_SHEETS_ENABLED=false
GOOGLE_SHEETS_SPREADSHEET_ID=
GOOGLE_SHEETS_CREDENTIALS_JSON=
```

У поточній реалізації Calendar не має окремого
`GOOGLE_CALENDAR_ENABLED`: інтеграція вважається не налаштованою, доки
`GOOGLE_CALENDAR_ID` або `GOOGLE_CALENDAR_CREDENTIALS_JSON` порожні. Sheets має
окремий прапорець `GOOGLE_SHEETS_ENABLED` і безпечні browser settings у SQLite.

Ніколи не додавайте реальний `.env`, service-account JSON або private key до
Git, README, screenshot чи чату.

### 6. Test mode, Reset і Skip

```powershell
$env:POMODORO_TEST_MODE="true"
python run.py
```

У test mode `work` триває 10 секунд, а обидва break-режими — 5 секунд. Щоб
вимкнути тимчасову змінну:

```powershell
Remove-Item Env:POMODORO_TEST_MODE
python run.py
```

Правила збереження:

- нормальне завершення countdown створює SQLite-запис;
- `Pause` не завершує і не зберігає сесію;
- `Reset` відкидає поточний інтервал і не створює запис;
- `Skip` відкидає поточний інтервал, не створює запис і запускає наступний mode;
- завершені 10-секундні test-mode `work`-сесії є повноцінними записами та
  придатні для Calendar sync;
- Calendar не синхронізує break-сесії, хоча нормально завершені breaks
  зберігаються й враховуються у статистиці.

### 7. SQLite, статистика, activity calendar і CSV

Локальна база за замовчуванням: `instance/pomodoro.db`. Основні таблиці:

- `work_sessions` — тип, планова/фактична тривалість, UTC timestamps,
  `client_session_id` і optional `google_calendar_event_id`;
- `user_settings` — timer settings, timezone, theme, sound, auto-start і
  безпечні Sheets settings;
- `alembic_version` — поточна migration revision.

Безпечна read-only перевірка:

```powershell
python scripts/check_database.py
```

Сторінки та export:

- `/` — timer, settings та optional integration cards;
- `/statistics` — today/week/month totals і 7-day chart;
- `/calendar` — month activity view та day details;
- `/api/export/sessions.csv?timezone=Europe/Kyiv` — CSV download;
- `/api/docs` — Swagger UI.

Timestamps зберігаються в UTC, а statistics, calendar, CSV і Google payloads
перетворюються до обраної IANA timezone, наприклад `Europe/Kyiv`.

### 8. Google Calendar: що означає блок і чому кнопка не працювала

Текст `Save the latest focus session as an event` означає: взяти **останню
завершену SQLite-сесію з `mode="work"`** і вручну створити для неї одну подію.
Це не running/paused session, не reset/skip, не break і не вже синхронізована
сесія.

Скриншот показував точну причину неактивної кнопки: credentials і completed
work `#63` були готові, але `GOOGLE_CALENDAR_ID` містив embed URL. Раніше backend
повертав `calendar_id_valid=false`, тому `canSync()` залишав кнопку disabled.

Тепер backend безпечно розпізнає офіційний Google Calendar embed URL, декодує
його `src` як Calendar ID і передає до API саме нормалізований ID. Реальна
перевірка створила Google event для work `#63` і зберегла event marker у SQLite.
Після success кнопка знову disabled навмисно: `#63` уже synchronized. Завершіть
нову focus-сесію — і кнопка автоматично стане активною для нового запису.

Кнопка видима завжди, але активна лише за трьох одночасних умов:

```text
status.configured
AND status.latest_work_session_id exists
AND status.latest_work_session_synced is false
```

| Фактична умова | Стан кнопки | Результат backend |
| --- | --- | --- |
| ID або credentials порожні | Disabled, `Setup required` | `400`, not configured |
| Офіційний embed URL має `src` | Enabled за наявності unsynced work | ID автоматично декодується |
| Інший URL, share link або HTML | Disabled, `Fix Calendar ID` | `400`, invalid Calendar ID |
| Немає завершеної `work`-сесії | Disabled | `400`, no completed work session |
| Остання загальна сесія — break, але раніше є work | Залежить від work | Backend вибирає останню саме `work` |
| Є завершена unsynced work | Enabled | Спроба `events.insert()` |
| Остання work уже має event ID | Disabled, `already synced` | `409 Conflict` при прямому API call |
| JSON неповний/пошкоджений | Може бути enabled, бо status перевіряє наявність | Безпечний `400` під час sync |
| API/permission/network error | Enabled до click | Безпечний `400`, secret details не повертаються |

`configured=true` означає, що required values присутні й Calendar ID має
допустиму форму. Повний JSON, Google access і sharing перевіряються лише під час
ручного sync; застосунок не звертається до Google під час startup.

### 9. Google Calendar setup — короткий маршрут

1. У Google Cloud створіть або виберіть project.
2. У `APIs & Services` увімкніть **Google Calendar API**.
3. У `IAM & Admin → Service Accounts` створіть service account.
4. У `Keys → Add key → Create new key` завантажте JSON key.
5. Скопіюйте `client_email` з JSON.
6. У Google Calendar краще створіть окремий календар для Pomodoro.
7. Відкрийте `Settings and sharing → Share with specific people or groups`,
   додайте `client_email` і надайте **Make changes to events**.
8. У `Integrate calendar` бажано скопіювати саме **Calendar ID**. Також можна
   вставити повний офіційний embed URL із параметром `src`; Public URL, share
   link і `<iframe>` не підходять.
9. Перетворіть JSON у один рядок:

```powershell
(Get-Content .\service-account.json -Raw |
    ConvertFrom-Json |
    ConvertTo-Json -Compress)
```

Альтернатива:

```powershell
python -c "import json; print(json.dumps(json.load(open('service-account.json', encoding='utf-8')), separators=(',', ':')))"
```

10. Вставте значення тільки у локальний `.env`:

```dotenv
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
GOOGLE_CALENDAR_CREDENTIALS_JSON='{"type":"service_account","...":"..."}'
```

11. Перезапустіть Flask, завершіть work-сесію та натисніть
    `Sync to Google Calendar`.

Google Cloud IAM role сам по собі **не** відкриває особистий Calendar. Окреме
sharing конкретного календаря з `client_email` є обов’язковим. Для work/school
акаунтів адміністратор домену може заборонити зовнішнє sharing.

Повна двомовна інструкція, troubleshooting і API flow:
[docs/GOOGLE_INTEGRATIONS_GUIDE.md](docs/GOOGLE_INTEGRATIONS_GUIDE.md).

### 10. Швидка Calendar-перевірка через test mode

1. Налаштуйте Google Calendar і перезапустіть Flask.
2. Увімкніть `POMODORO_TEST_MODE=true`.
3. Запустіть `work` та дочекайтеся повних 10 секунд.
4. Перевірте, що Calendar card показує `ready to sync`.
5. Натисніть `Sync to Google Calendar`.
6. Знайдіть коротку event у shared calendar за часом цієї сесії.
7. Повторна синхронізація тієї ж work-сесії буде заблокована.

Test mode створює реальні локальні записи; він лише скорочує duration.

### 11. Штучна завершена work-сесія без очікування

Новий dev endpoint не потрібен: існуючий `POST /api/sessions` безпечно створює
один завершений запис і **не** викликає Google автоматично. Запустіть Flask, а в
іншому PowerShell:

```powershell
$completed = [DateTimeOffset]::UtcNow
$started = $completed.AddSeconds(-10)
$body = @{
  client_session_id = "calendar-test-$([guid]::NewGuid().ToString('N'))"
  mode = "work"
  planned_duration_seconds = 10
  actual_duration_seconds = 10
  started_at_utc = $started.ToString("o")
  completed_at_utc = $completed.ToString("o")
} | ConvertTo-Json

$created = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/sessions" `
  -ContentType "application/json" `
  -Body $body

$created
```

Якщо далі хочете натиснути саме browser button, оновіть сторінку `/`: POST з
окремого PowerShell не генерує browser event `pomodoro:sessions-changed`.
Прямий API sync нижче не потребує reload.

Після цього перевірте status і синхронізуйте:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:5000/api/integrations/google-calendar/status"

$syncBody = @{ timezone = "Europe/Kyiv" } | ConvertTo-Json
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/integrations/google-calendar/sync" `
  -ContentType "application/json" `
  -Body $syncBody
```

Щоб видалити **лише локальний** тестовий запис:

```powershell
Invoke-RestMethod `
  -Method Delete `
  -Uri "http://127.0.0.1:5000/api/sessions/$($created.id)"
```

Якщо event уже створена, DELETE локального запису не видаляє її з Google
Calendar — видаліть event у Calendar вручну. Не видаляйте всю SQLite-базу заради
одного тестового запису.

### 12. Google Sheets — незалежна optional-інтеграція

Calendar і Sheets не викликають одне одного.

| Властивість | Google Calendar | Google Sheets |
| --- | --- | --- |
| Результат | Одна Calendar event | Нові rows A:I |
| Джерело | Остання completed work | Усі completed work |
| Trigger | Manual button | Manual button |
| External resource | Shared Calendar | Shared Spreadsheet |
| Enable rule | ID + credentials | Enable + ID + credentials |
| Duplicate protection | Event ID у SQLite | `client_session_id` у колонці A |
| Break export | Ні | Ні |
| Незалежність | Працює без Sheets | Працює без Calendar |

Sheets setup:

1. Увімкніть **Google Sheets API** у тому самому або окремому Cloud project.
2. Створіть Google Sheet вручну.
3. Натисніть `Share`, додайте service-account `client_email` як **Editor** і
   вимкніть `Notify people`, бо service account не має inbox.
4. Скопіюйте ID між `/d/` і `/edit` у URL.
5. Додайте one-line JSON у `GOOGLE_SHEETS_CREDENTIALS_JSON` і перезапустіть Flask.
6. У `Google Sheets Settings` увімкніть checkbox, вставте Spreadsheet ID та
   натисніть `Save Settings`.
7. Натисніть `Sync Completed Sessions`.

`Save Settings` зберігає лише enable flag та Spreadsheet ID у SQLite, перевіряє
server credentials, але не додає rows. `Sync Completed Sessions` створює header
у порожньому sheet, додає лише відсутні work-сесії й пропускає duplicates.

### 13. Google notifications: точне формулювання

Flask-застосунок створює event, але не реалізує push, email або browser
notifications. Service account також не «надсилає повідомлення» користувачу.
Після створення event саме Google Calendar застосовує особисті default/event
notification settings: email, desktop notification або Calendar alert.

Налаштуйте їх у Google Calendar:
`Settings → Settings for my calendars → <calendar> → Event notifications`, або
відкрийте конкретну event і додайте reminder. Browser/OS має дозволяти
notifications для `calendar.google.com`.

### 14. API для ручної перевірки

| Method | URL | Body | Призначення |
| --- | --- | --- | --- |
| `GET` | `/api/integrations/google-calendar/status` | немає | Безпечний Calendar status |
| `POST` | `/api/integrations/google-calendar/sync` | optional `timezone` | Sync останньої work |
| `GET` | `/api/integrations/google-sheets/settings` | немає | Безпечні Sheets settings |
| `PUT` | `/api/integrations/google-sheets/settings` | `enabled`, `spreadsheet_id` | Save non-secret settings |
| `POST` | `/api/integrations/google-sheets/sync` | немає | Export completed work |
| `POST` | `/api/sessions` | completed session payload | Створити локальну сесію |
| `DELETE` | `/api/sessions/<id>` | немає | Видалити один локальний запис |

### 15. Архітектура, файли й відповідальність

| Файл | Роль |
| --- | --- |
| `run.py` | Створює app і запускає Flask dev server |
| `app/__init__.py` | `create_app`, config, extensions, blueprints, SQLite bootstrap |
| `app/config.py` | Читає env і визначає development/testing/production config |
| `app/models/work_session.py` | SQLAlchemy-модель завершеної сесії |
| `app/repositories/session_repository.py` | Queries, включно з latest work |
| `app/services/session_service.py` | Validation, create/list/get/delete sessions |
| `app/services/google_calendar_service.py` | Calendar status, payload, client, sync, duplicate guard |
| `app/services/google_sheets_service.py` | Settings, rows, header і duplicate guard |
| `app/blueprints/integrations/routes.py` | Calendar status/sync endpoints |
| `app/blueprints/google_sheets/routes.py` | Sheets settings/sync endpoints |
| `app/static/js/integrations.js` | Status, button readiness і API calls у browser |
| `scripts/check_database.py` | Read-only SQLite inspection |
| `tests/test_integrations_api.py` | Mocked Calendar scenarios |
| `tests/test_google_sheets_api.py` | Mocked Sheets scenarios |
| `.env` | Локальні secrets; не комітиться |
| `.env.example` | Безпечний шаблон без secrets |

### 16. Docker

```powershell
docker build -t pomodoro-work-tracker .
docker run --rm `
  -p 5000:5000 `
  --env-file .env `
  -v "${PWD}/instance:/app/instance" `
  pomodoro-work-tracker
```

Volume зберігає SQLite між контейнерами. Production command у `start.sh`
застосовує migrations і запускає Gunicorn. Не комітьте `.env` в image.

### 17. Перевірки

```powershell
python -m compileall app scripts run.py
ruff check .
black --check .
pytest tests/test_integrations_api.py -v
pytest -v
flask --app run.py routes
python scripts/check_database.py
```

Automated Google tests використовують mocks і не створюють зовнішні events або
rows. Реальну зовнішню інтеграцію можна підтвердити лише з коректними user-owned
resources, API access, service-account key і sharing permissions.

`.github/workflows/ci.yml` автоматично запускає compileall, Ruff, Black,
`pip check` і повний pytest на Python 3.12 для кожного push, pull request та
ручного запуску. Бейдж `CI` угорі README показує останній GitHub Actions status.

### 18. Зручність, обмеження та переваги для захисту

Базовим timer flow користуватися просто: Google setup не потрібен, записи
переживають restart, а test mode дає швидку демонстрацію. Google setup є
технічнішим одноразовим кроком; найчастіша помилка — переплутати resource ID з
URL або не поділитися resource з `client_email`.

Відомі обмеження:

- single-user застосунок без authentication;
- countdown живе у browser, а server зберігає тільки завершення;
- Calendar sync ручний, односторонній і лише для latest work;
- локальне видалення не видаляє вже створену Google event;
- Sheets export ручний і не є real-time stream;
- Flask не реалізує Google push notifications;
- SQLite і JSON key у `.env` придатні для local/portfolio demo, але production
  потребує managed database, secret manager і продуманого OAuth/WIF flow.

Сильна сторона проєкту — поєднання Flask architecture з реальною моделлю
optional Google Cloud integration. Під час роботи опрацьовано application
factory, blueprints, schemas, SQLAlchemy, migrations, repositories/services,
UTC/timezone conversion, API errors, secure env configuration, service
accounts, Calendar/Spreadsheet sharing, external API mocks і duplicate
protection. Це практичне знайомство не лише з Flask, а й з Google Cloud та
Google Workspace API.

### 19. Документація

- [Інструкція Google Cloud для Calendar і Sheets](docs/GOOGLE_INTEGRATIONS_GUIDE.md)
  — Calendar, Sheets, test session, API, errors, secrets і notifications;
- [Project Defense Guide](docs/PROJECT_DEFENSE_GUIDE.md) — архітектура та
  сценарій захисту;
- [API Reference](docs/API_REFERENCE.md);
- [Deployment](docs/DEPLOYMENT.md);
- [Current Status](docs/CURRENT_STATUS.md).
