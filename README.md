# Pomodoro Work Tracker

`Pomodoro Work Tracker` — це невеликий навчальний Flask-проєкт для локального
запуску Pomodoro-таймера, збереження завершених сесій у SQLite, перегляду
статистики, календаря активності, експорту в CSV і простої синхронізації
останньої робочої сесії в Google Calendar.

## Реально реалізовані можливості

- `Start`, `Pause`, `Resume`, `Reset`, `Skip` для браузерного таймера
- збереження завершених `work`, `short_break`, `long_break` сесій у SQLite
- відновлення активного таймера після перезавантаження сторінки через `localStorage`
- статистика за день, тиждень і місяць
- 7-денний графік продуктивності
- календар активності з деталями по вибраній даті
- збереження налаштувань таймера, теми, звуку й часової зони
- CSV-експорт сесій
- Bootstrap Carousel на головній сторінці з `Previous` / `Next` і кнопками переходу до реальних сторінок та секцій
- світла / темна / системна тема
- звукове повідомлення після завершення сесії
- проста синхронізація останньої завершеної `work`-сесії в Google Calendar

## Технології

- Python 3.12+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Smorest
- Marshmallow
- Jinja2
- SQLite
- Vanilla JavaScript
- Bootstrap 5.3
- Chart.js
- Gunicorn
- pytest

## Швидкий локальний запуск

### Варіант 1: через ZIP

1. Завантажте ZIP з GitHub.
2. Розпакуйте архів.
3. Відкрийте папку проєкту в терміналі.

### Варіант 2: через `git clone`

```powershell
git clone <PROJECT_URL>
cd flask_pet_project_pomodoro_timer_2026
```

### Запуск на Windows

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

python run.py
```

Після запуску відкрийте:

```text
http://127.0.0.1:5000
```

## Конфігурація середовища

Скопіюйте `.env.example` у локальний `.env` і не додавайте `.env` або JSON-ключі
Google до Git. Застосунок викликає `load_dotenv()` один раз у `create_app()`;
змінна, уже задана в PowerShell, має пріоритет над значенням із `.env`.

Підтримувані змінні:

- Flask: `FLASK_APP`, `APP_ENV`, `SECRET_KEY`, `DEBUG`; `PORT` використовується
  контейнерним `start.sh`, а локальний `python run.py` відкриває стандартний `5000`
- SQLite: `DATABASE_URL`
- таймер: `DEFAULT_TIMEZONE`, `DEFAULT_CYCLES_BEFORE_LONG_BREAK`, `POMODORO_TEST_MODE`
- Google Calendar: `GOOGLE_CALENDAR_ID`, `GOOGLE_CALENDAR_CREDENTIALS_JSON`,
  `GOOGLE_CALENDAR_EVENT_PREFIX`, `GOOGLE_CALENDAR_EVENT_COLOR_ID`
- Google Sheets: `GOOGLE_SHEETS_ENABLED`, `GOOGLE_SHEETS_SPREADSHEET_ID`,
  `GOOGLE_SHEETS_CREDENTIALS_JSON`

`sqlite:///pomodoro.db` перетворюється на абсолютний шлях до
`instance/pomodoro.db`. Google credentials передаються як JSON в один рядок;
значення з неекранованими переносами або лапками не буде прочитане `python-dotenv`.

Безпечна перевірка конфігурації без виведення секретів:

```powershell
python -c "from app import create_app; app=create_app(); keys=['GOOGLE_CALENDAR_ID','GOOGLE_CALENDAR_CREDENTIALS_JSON','POMODORO_TEST_MODE']; print({key: bool(app.config.get(key)) for key in keys})"
```

## Що важливо про перший запуск

- локальна SQLite-база створюється автоматично
- папка `instance/` використовується для локальної БД
- схеми застосовуються автоматично під час локального старту
- HR не потрібно вручну створювати БД або запускати окремий SQLite-клієнт

## Test mode

Щоб не чекати 25 хвилин, увімкніть короткий локальний режим:

```powershell
$env:POMODORO_TEST_MODE="true"
python run.py
```

У цьому режимі:

- `work` триває `10` секунд
- `short_break` і `long_break` тривають `5` секунд
- на головній сторінці видно кнопку `Test mode 10с / 5с`
- біля таймера видно позначку `Test mode active`

Щоб вимкнути test mode:

```powershell
Remove-Item Env:POMODORO_TEST_MODE
python run.py
```

Його також можна ввімкнути через `.env`:

```dotenv
POMODORO_TEST_MODE=true
```

Якщо значення задане і в PowerShell, і в `.env`, перемагає PowerShell. Кнопка
короткого preset доступна лише при активному test mode. Завершені test-mode
сесії зберігаються у `work_sessions` так само, як звичайні; `Reset` і `Skip` не
створюють запис для поточного інтервалу, бо API викликається тільки після
нормального завершення countdown.

### Пропуск focus або break

Кнопка `Skip` знаходиться поруч із `Reset` і працює для `work`, `short_break`
та `long_break`. Вона відкидає поточний незавершений інтервал і негайно запускає
наступний режим незалежно від `auto_start_next_session`.

- `work` -> `short_break`; пропущений focus не збільшує число completed work cycles
- `short_break` -> `work`
- `long_break` -> `work` і початок нового циклу

Пропущена сесія не зберігається. Нормально завершені focus і break сесії
зберігаються окремо; статистика рахує `focus_minutes`, `break_minutes` і
`total_tracked_minutes`.

## Налаштування таймера

Форма налаштувань приймає тільки дозволені значення:

- `work`: `15`, `25`, `30`, `45`, `60` хвилин
- `short break`: `5`, `10`, `15` хвилин
- `long break`: `5`, `10`, `15` хвилин

Додатково зберігаються:

- `cycles_before_long_break`
- `auto_start_next_session`
- `theme`
- `sound_enabled`
- `timezone`

Налаштування зберігаються в SQLite і відновлюються після перезапуску.
У формі timezone відображається як IANA-значення, наприклад `Europe/Kyiv`,
і пояснюється, що воно використовується для daily, weekly та monthly statistics.
Для Windows у virtualenv встановлюється `tzdata`, щоб Python `zoneinfo`
стабільно знаходив IANA timezones.

## Перевірка SQLite

### Де лежить база

За замовчуванням локальна база створюється тут:

```text
instance/pomodoro.db
```

### Коли вона створюється

- при першому локальному запуску застосунку
- під час старту `python run.py`, якщо SQLite-файл або таблиці ще відсутні

### Які таблиці містить

- `work_sessions`
- `user_settings`
- `alembic_version`

`work_sessions` містить ID сесії, browser-generated `client_session_id`, тип,
планову й фактичну тривалість, UTC-час початку/завершення, час створення та
опціональний `google_calendar_event_id`. `user_settings` містить тривалості,
цикл довгої перерви, звук, auto-start, тему й timezone. Статистика читає
завершені сесії з `work_sessions` і групує їх за локальною датою обраної timezone.

### Як швидко перевірити БД

1. Запустіть застосунок через `python run.py`.
2. За потреби увімкніть `POMODORO_TEST_MODE=true`.
3. На головній сторінці виберіть `Test mode 10с / 5с`.
4. Завершіть коротку `work`-сесію.
5. Запустіть:

```powershell
python scripts/check_database.py
```

6. Переконайтеся, що скрипт показує:
   - кількість сесій
   - час початку
   - час завершення
   - тривалість
   - тип сесії
   - статус синхронізації з Google Calendar
7. Перезапустіть застосунок.
8. Повторно запустіть `python scripts/check_database.py`.
9. Переконайтеся, що запис не зник.

Перевірка через Flask model:

```powershell
python -c "from app import create_app; from app.models import WorkSession; app=create_app(); app.app_context().push(); print(WorkSession.query.order_by(WorkSession.id.desc()).limit(10).all())"
```

Якщо окремий `sqlite3` CLI встановлено, можна також використати:

```text
sqlite3 instance/pomodoro.db
.tables
SELECT * FROM work_sessions ORDER BY id DESC LIMIT 10;
.quit
```

На Windows цей CLI необов'язковий; `scripts/check_database.py` достатньо.

### Як безпечно видалити тестову локальну базу

Спочатку зупиніть сервер, потім:

```powershell
Remove-Item .\instance\pomodoro.db
```

Після наступного `python run.py` буде створена чиста база.

## Google Calendar

Проєкт не робить складну двосторонню синхронізацію. Реалізовано простий сценарій:

- застосунок бере **останню завершену `work`-сесію**
- створює для неї **одну подію** в Google Calendar
- зберігає `google_calendar_event_id` у SQLite
- повторна синхронізація тієї самої останньої сесії блокується

### Змінні `.env` для Google Calendar

```env
GOOGLE_CALENDAR_ID=
GOOGLE_CALENDAR_CREDENTIALS_JSON=
GOOGLE_CALENDAR_EVENT_PREFIX=Pomodoro
GOOGLE_CALENDAR_EVENT_COLOR_ID=
```

### Як налаштувати

1. Увімкніть `Google Calendar API` у Google Cloud.
2. Створіть `Service account`.
3. Завантажте JSON-ключ.
4. Поділіться потрібним Google Calendar з `client_email` цього service account.
5. У Google Calendar відкрийте `Settings and sharing` → `Integrate calendar` і
   скопіюйте саме `Calendar ID`. Не вставляйте embed/share URL.
6. Перетворіть JSON у один рядок і вставте в `GOOGLE_CALENDAR_CREDENTIALS_JSON`.
7. Вставте ID календаря в `GOOGLE_CALENDAR_ID`.

Кнопка `Sync to Google Calendar` стає активною лише після коректної серверної
конфігурації та появи завершеної `work`-сесії. Вона створює одну event для
останнього focus, не експортує breaks і не запускається автоматично. Результат
потрібно шукати у shared Google Calendar у час завершеної сесії. Після success
`google_calendar_event_id` записується в SQLite, тому повторна event для тієї
самої сесії блокується.

Для цього шляху потрібні `google-api-python-client` і `google-auth`, уже вказані
в `requirements.txt`. Якщо `import googleapiclient` не працює, достатньо
точково виконати `pip install google-api-python-client==2.181.0`; `gspread` для
поточної Calendar integration не використовується.

### Що реально перевірено

- відсутність credentials повертає зрозумілу помилку
- успішний шлях покрито mocked-тестом
- повторна синхронізація тієї самої останньої сесії блокується тестом

### Що не перевірялося з реальним Google акаунтом у цій сесії

- створення реальної події у зовнішньому календарі

## Google Sheets

Google Sheets є окремою опціональною інтеграцією і не замінює Google
Calendar. Кнопка `Sync Completed Sessions` викликає
`POST /api/integrations/google-sheets/sync` та експортує тільки завершені
`work`-сесії.

Таблиця отримує дев'ять колонок:

1. `Session ID`
2. `Date`
3. `Start Time`
4. `End Time`
5. `Planned Duration`
6. `Actual Duration`
7. `Mode`
8. `Timezone`
9. `Created At`

`Planned Duration` і `Actual Duration` зберігаються в секундах. Стабільний
`client_session_id` використовується як `Session ID`: перед записом сервіс
читає першу колонку й пропускає вже наявні ID. Якщо таблиця порожня, перша
синхронізація створює заголовки. Якщо наявний заголовок не відповідає цьому
формату, API повертає контрольовану помилку й нічого не дописує.

У браузері зберігаються лише безпечні налаштування `Enable` і `Spreadsheet
ID`. JSON service account залишається тільки на Flask-сервері.

### Змінні `.env` для Google Sheets

```env
GOOGLE_SHEETS_ENABLED=false
GOOGLE_SHEETS_SPREADSHEET_ID=
GOOGLE_SHEETS_CREDENTIALS_JSON=
```

Підтримується один формат credentials: повний JSON service account в один
рядок у `GOOGLE_SHEETS_CREDENTIALS_JSON`. Альтернативні назви змінних або
шлях до JSON-файлу застосунок не читає.

На PowerShell JSON можна стиснути однією командою:

```powershell
(Get-Content .\service-account.json -Raw | ConvertFrom-Json | ConvertTo-Json -Compress)
```

Альтернатива через Python:

```powershell
python -c "import json; print(json.dumps(json.load(open('service-account.json', encoding='utf-8')), separators=(',', ':')))"
```

Вставте результат в одинарних лапках, щоб `python-dotenv` коректно прочитав
внутрішні подвійні лапки JSON:

```env
GOOGLE_SHEETS_CREDENTIALS_JSON='{"type":"service_account","...":"..."}'
```

Не вставляйте отриманий рядок у README, GitHub, чат, screenshot або browser
form. У поточному проєкті credentials читаються тільки Flask-сервером. Після
зміни `.env` обов’язково перезапустіть застосунок.

### Налаштування Google Cloud і таблиці

1. Створіть або виберіть Google Cloud project.
2. Увімкніть `Google Sheets API` у Google Cloud Console.
3. Створіть service account і JSON key.
4. Відкрийте потрібну Google Sheet, натисніть `Share` і додайте `client_email`
   із JSON-ключа з роллю `Editor`. Domain-wide delegation для однієї
   конкретної таблиці не потрібен.
5. Скопіюйте ID між `/d/` і `/edit` у URL таблиці.
6. Перетворіть JSON key в один рядок, вставте його в
   `GOOGLE_SHEETS_CREDENTIALS_JSON`, додайте ID і встановіть
   `GOOGLE_SHEETS_ENABLED=true`.
7. Запустіть `flask --app run.py db upgrade`, потім `python run.py`.
8. На головній сторінці відкрийте `Google Sheets Settings`, збережіть ID і
   натисніть `Sync Completed Sessions`.

### Що роблять дві кнопки Sheets

- `Save Settings` перевіряє enabled-конфігурацію та зберігає в SQLite тільки
  checkbox і Spreadsheet ID. Ця кнопка не звертається до Google і не додає rows.
- `Sync Completed Sessions` стає активною лише після успішного Save і готових
  server credentials. Вона читає завершені `work`-сесії, перевіряє header A:I та
  додає тільки відсутні `client_session_id`.

Зелений badge у UI позначає повністю опціональну частину. Помаранчевий badge
означає «обов’язково лише тоді, коли інтеграцію ввімкнено». При disabled Sheets
відсутні ID/credentials не є помилкою й не перевіряються.

### Ручна перевірка трьох станів Sheets

1. **Disabled:** залиште три default values, запустіть Flask, завершіть Pomodoro
   і перевірте SQLite/статистику. UI показує `Optional · Off`, Sync disabled.
2. **Enabled, але incomplete:** встановіть `GOOGLE_SHEETS_ENABLED=true` із blank
   ID/credentials. Flask стартує, а Save/Sync повертає контрольоване пояснення;
   інші функції продовжують працювати.
3. **Fully configured:** share Sheet із service-account `client_email`, збережіть
   ID, виконайте Sync і перевірте A:I. Повторний Sync має показати skipped
   duplicates без нових rows.

Офіційні інструкції Google: [увімкнення Sheets API та Python
клієнт](https://developers.google.com/workspace/sheets/api/quickstart/python),
[створення service account, JSON key і прямий доступ до конкретного
файлу](https://developers.google.com/workspace/guides/create-credentials).

Не комітьте `.env`, JSON key або його `private_key`. Для коду достатньо вже
наявних `google-api-python-client` і `google-auth`; `gspread` та
`oauth2client` не використовуються.

### Чи підходить безкоштовний доступ для portfolio demo

Станом на 15 липня 2026 року стандартне використання Google Sheets API не має
додаткової оплати в межах квот. Google вказує 300 read і 300 write requests за
хвилину на project та 60 за хвилину на користувача в project; ручний експорт
portfolio demo суттєво нижчий за ці межі. Водночас Google уже попереджає, що
перевищення квот планують зробити платним пізніше у 2026 році, тому перед
публічним production-запуском варто повторно перевірити [актуальні квоти й
pricing](https://developers.google.com/workspace/sheets/api/limits).

### Що перевірено без реального Google акаунта

- disabled integration, відсутні ID/credentials та некоректний JSON
- mocked successful export із правильними колонками
- пропуск повторних `Session ID`
- експорт лише завершених `work`-сесій
- безпечна зовнішня помилка без сирого тексту Google API
- збереження `Enable` і `Spreadsheet ID` через frontend settings

Реальний запис у зовнішню Google Sheet потребує власного service account і не
виконувався в цій сесії.

## CSV export

Кнопка `Export CSV` викликає `GET /api/export/sessions.csv`. Endpoint читає
завершені rows із SQLite, за потреби фільтрує date range, конвертує timestamps у
вибрану timezone й повертає `pomodoro-sessions.csv`. База при цьому не змінюється.

## Документація для захисту

Детальний зв’язок між файлами, класами, методами, routes, кнопками, моделями,
Google integrations і тестами описано в
[`docs/PROJECT_DEFENSE_GUIDE.md`](docs/PROJECT_DEFENSE_GUIDE.md). Там також є
5–7-хвилинний виступ, live-demo checklist і відповіді на типові питання викладача.

## Команди для перевірки

```powershell
python -m compileall app scripts run.py
ruff check .
black --check .
flask --app run.py routes
pytest -v
python scripts/check_database.py
```

## Docker

Docker необов'язковий для локальної перевірки: найпростіший запуск —
`python run.py`. Він корисний для повторюваного Linux-оточення й перевірки
Gunicorn. Усі команди запускаються з кореня проєкту:

```powershell
docker build -t pomodoro-work-tracker .
docker run --rm -p 5000:5000 --env-file .env -e APP_ENV=production pomodoro-work-tracker
```

Щоб SQLite не зникла разом із контейнером, змонтуйте `instance/` у `/app/instance`:

```powershell
docker run --rm `
  -p 5000:5000 `
  --env-file .env `
  -e APP_ENV=production `
  -v "${PWD}\instance:/app/instance" `
  pomodoro-work-tracker
```

`WORKDIR` у Dockerfile — `/app`, порт — `5000`, а `start.sh` застосовує міграції
й запускає Gunicorn. Без volume файл `/app/instance/pomodoro.db` живе лише у
filesystem контейнера.

## Як працює Flask-проєкт

1. `run.py` створює Flask-застосунок через `create_app()`.
2. `app/__init__.py` підключає конфігурацію, розширення, маршрути й error handlers.
3. `app/static/js/timer.js` керує активним countdown у браузері.
4. Після завершення таймер надсилає `POST /api/sessions`.
5. Flask зберігає завершену сесію в SQLite.
6. `statistics.js` і `calendar.js` запитують API для оновлення статистики й календаря.
7. `integrations.js` окремо перевіряє Calendar і Sheets readiness: Calendar
   sync-ить latest `work`, Sheets Save зберігає safe settings, а Sheets Sync
   експортує нові completed `work` rows.

## Використані Flask-компоненти

- `Flask` — створення застосунку
- `Blueprint` — групування сторінок і API
- `render_template` — серверний HTML через Jinja
- `request` — обробка HTTP-запитів усередині Flask-Smorest/Flask
- `jsonify` — JSON-помилки й службові відповіді
- `current_app` — доступ до конфігурації
- `send_file` не використовується
- `session` не використовується
- `flash` не використовується

## Структура проєкту

```text
flask_pet_project_pomodoro_timer_2026/
├── app/
│   ├── __init__.py
│   ├── api/
│   ├── blueprints/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── static/
│   └── templates/
├── docs/
├── instance/
├── migrations/
├── scripts/
│   └── check_database.py
├── tests/
├── .env.example
├── AGENTS.md
├── IMPLEMENTATION_PLAN.md
├── README.md
├── requirements.txt
└── run.py
```

## Сторінки проєкту

### Головна сторінка — `/`

Шаблон: `app/templates/index.html`

Призначення:

- показує таймер
- дає кнопки `Start`, `Pause`, `Resume`, `Reset`, `Skip`
- показує кількість completed `work`-сесій через денну статистику
- містить Bootstrap Carousel
- дозволяє експортувати CSV
- містить блок Google Calendar sync
- містить незалежний опціональний Google Sheets settings/sync блок

Ручна перевірка:

1. Відкрийте `/`.
2. Переконайтеся, що видно Carousel і перший слайд активний.
3. Натисніть `Next`, потім `Previous`.
4. Натисніть один з індикаторів слайда.
5. Натисніть `Start`.
6. Натисніть `Pause`.
7. Натисніть `Resume`.
8. Натисніть `Skip` і переконайтеся, що наступний режим одразу має статус `Running`.
9. Натисніть `Reset`.
10. Перевірте `Export CSV`.

### Сторінка статистики — `/statistics`

Шаблон: `app/templates/statistics.html`

Призначення:

- показує картки дня, тижня й місяця
- показує 7-денний графік

Ручна перевірка:

1. Відкрийте `/statistics`.
2. Переконайтеся, що картки не порожні після завершення сесії.
3. Перевірте графік.

### Сторінка календаря — `/calendar`

Шаблон: `app/templates/calendar.html`

Призначення:

- показує активність за місяць
- дозволяє перейти на попередній або наступний місяць
- показує список сесій для вибраної дати

Ручна перевірка:

1. Відкрийте `/calendar`.
2. Натисніть `Next`.
3. Натисніть `Previous`.
4. Оберіть дату.
5. Перевірте список сесій або повідомлення про їх відсутність.

## Ручна перевірка інтерфейсу

| Кнопка або елемент | Де знаходиться | Дія | Очікуваний результат | Зміна в SQLite |
| --- | --- | --- | --- | --- |
| `Start` | `/` | натиснути | таймер починає зменшуватися, статус `Running` | без запису до завершення |
| `Pause` | `/` | натиснути під час роботи | таймер зупиняється, `Resume` стає активною | без запису |
| `Resume` | `/` | натиснути після паузи | countdown продовжується | без запису |
| `Reset` | `/` | натиснути до завершення | таймер повертається у `Ready`, сесія не зберігається | без нового запису |
| `Skip` | `/` | натиснути під час focus або break | поточний інтервал відкидається, наступний режим одразу запускається | без нового запису |
| `Test mode 10с / 5с` | `/` | натиснути | короткий пресет стає активним | без запису |
| `Зберегти налаштування` | `/` | змінити значення і зберегти | форма повертає повідомлення про успіх | оновлюється `user_settings` |
| `Export CSV` | `/` | натиснути | завантажується CSV-файл | без зміни |
| `Next` / `Previous` у календарі | `/calendar` | натиснути | змінюється місяць | без зміни |
| вибір дати | `/calendar` | натиснути день | оновлюються деталі дня | без зміни |
| перемикач теми | `/` | вибрати `light` або `dark` | змінюється тема інтерфейсу | оновлюється `user_settings.theme` |
| `sound_enabled` | `/` | увімкнути / вимкнути | змінюється поведінка звуку після завершення сесії | оновлюється `user_settings.sound_enabled` |
| Bootstrap Carousel | `/` | натиснути індикатори або `Previous` / `Next` | змінюється активний слайд | без зміни |
| `Sync to Google Calendar` | `/` | натиснути після завершення `work`-сесії | створюється одна подія або повертається зрозуміла помилка | записується `google_calendar_event_id` |
| Sheets `Save Settings` | `/` | disabled або повна enabled-конфігурація | зберігаються лише checkbox та Spreadsheet ID; Google request не виконується | оновлюються nullable Sheets fields у `user_settings` |
| `Sync Completed Sessions` | `/` | натиснути після ready status | нові completed `work` rows з’являються в A:I, duplicate IDs пропускаються | SQLite не змінюється |

## Що реально перевірено в цій сесії

- focused integrations/pages/frontend suite — `32 passed`
- повний `pytest -v` — `79 passed`
- `python -m compileall app scripts run.py`
- `ruff check .`
- `black --check .`
- `flask --app run.py routes`
- `python scripts/check_database.py` — read-only перевірка знайшла `34` локальні сесії
- `googleapiclient` і `google.auth` імпортуються, `pip check` не знаходить конфліктів
- live HTTP smoke:
  - `/` і `/api/health` повертають `200`
  - `/api/integrations/google-calendar/status` контрольовано повідомляє про
    відсутні Calendar ID і credentials
  - sync без credentials повертає `400 validation_error`, а не падіння застосунку
- browser smoke підтвердив завантаження `clock-face.gif`, показ анімації лише
  під час Running і відсутність console errors
- browser smoke підтвердив `work -> Skip -> short_break -> Skip -> work`, статус
  `Running`, незмінний session count для пропусків і окремий облік нормально
  завершених focus/break інтервалів
- browser smoke на temporary SQLite підтвердив загальну `Save Settings`, Sheets
  Save у disabled mode, контрольовану missing-credentials помилку, disabled Sync
  до readiness, mocked click-path для обох sync-кнопок і відхилення Calendar
  embed URL до Google request
- фінальна desktop/dark/mobile перевірка integration cards: без horizontal
  overflow, `0` console errors, `0` warnings
- Dockerfile прочитано й команди звірено; image build не запускався, бо локальний
  Docker Desktop/daemon був зупинений

## Відомі обмеження

- таймер активної сесії зберігається в `localStorage`, а не синхронізується між браузерами
- реальна подія Google Calendar не створювалася в цій сесії без зовнішніх credentials
- реальні Google Sheets rows не створювалися без зовнішніх credentials і shared spreadsheet
- Sheets duplicate protection залежить від незмінності першої ID-колонки; для
  великої таблиці повне читання A:I треба буде оптимізувати
- у проєкті все ще доступний dev-маршрут `/api/docs` від Flask-Smorest, але він не потрібен для HR-перевірки
- немає авторизації й мультикористувацького режиму
- локальна SQLite підходить для навчання й демо, але не для серйозного production-сценарію
