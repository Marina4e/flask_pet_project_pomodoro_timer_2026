# Pomodoro Work Tracker

`Pomodoro Work Tracker` — це невеликий навчальний Flask-проєкт для локального
запуску Pomodoro-таймера, збереження завершених сесій у SQLite, перегляду
статистики, календаря активності, експорту в CSV і простої синхронізації
останньої робочої сесії в Google Calendar.

## Реально реалізовані можливості

- `Start`, `Pause`, `Resume`, `Reset` для браузерного таймера
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
```

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

### Змінні `.env`

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
5. Скопіюйте `Calendar ID`.
6. Перетворіть JSON у один рядок і вставте в `GOOGLE_CALENDAR_CREDENTIALS_JSON`.
7. Вставте ID календаря в `GOOGLE_CALENDAR_ID`.

### Що реально перевірено

- відсутність credentials повертає зрозумілу помилку
- успішний шлях покрито mocked-тестом
- повторна синхронізація тієї самої останньої сесії блокується тестом

### Що не перевірялося з реальним Google акаунтом у цій сесії

- створення реальної події у зовнішньому календарі

## Команди для перевірки

```powershell
python -m compileall app scripts run.py
ruff check .
black --check .
flask --app run.py routes
pytest -v
python scripts/check_database.py
```

## Як працює Flask-проєкт

1. `run.py` створює Flask-застосунок через `create_app()`.
2. `app/__init__.py` підключає конфігурацію, розширення, маршрути й error handlers.
3. `app/static/js/timer.js` керує активним countdown у браузері.
4. Після завершення таймер надсилає `POST /api/sessions`.
5. Flask зберігає завершену сесію в SQLite.
6. `statistics.js` і `calendar.js` запитують API для оновлення статистики й календаря.
7. `integrations.js` перевіряє Google Calendar status і запускає sync для останньої `work`-сесії.

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
- дає кнопки `Start`, `Pause`, `Resume`, `Reset`
- показує кількість completed `work`-сесій через денну статистику
- містить Bootstrap Carousel
- дозволяє експортувати CSV
- містить блок Google Calendar sync

Ручна перевірка:

1. Відкрийте `/`.
2. Переконайтеся, що видно Carousel і перший слайд активний.
3. Натисніть `Next`, потім `Previous`.
4. Натисніть один з індикаторів слайда.
5. Натисніть `Start`.
6. Натисніть `Pause`.
7. Натисніть `Resume`.
8. Натисніть `Reset`.
9. Перевірте `Export CSV`.

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
| `Test mode 10с / 5с` | `/` | натиснути | короткий пресет стає активним | без запису |
| `Зберегти налаштування` | `/` | змінити значення і зберегти | форма повертає повідомлення про успіх | оновлюється `user_settings` |
| `Export CSV` | `/` | натиснути | завантажується CSV-файл | без зміни |
| `Next` / `Previous` у календарі | `/calendar` | натиснути | змінюється місяць | без зміни |
| вибір дати | `/calendar` | натиснути день | оновлюються деталі дня | без зміни |
| перемикач теми | `/` | вибрати `light` або `dark` | змінюється тема інтерфейсу | оновлюється `user_settings.theme` |
| `sound_enabled` | `/` | увімкнути / вимкнути | змінюється поведінка звуку після завершення сесії | оновлюється `user_settings.sound_enabled` |
| Bootstrap Carousel | `/` | натиснути індикатори або `Previous` / `Next` | змінюється активний слайд | без зміни |
| `Sync to Google Calendar` | `/` | натиснути після завершення `work`-сесії | створюється одна подія або повертається зрозуміла помилка | записується `google_calendar_event_id` |

## Що реально перевірено в цій сесії

- `pytest tests/test_pages.py tests/test_statistics_api.py -v`
- `python -m compileall app`
- `ruff check .`
- `black --check .`
- `pytest -v` — `45 passed`
- live HTTP-запити:
  - `/` повернув `200`
  - `/api/statistics/month?timezone=Europe/Kyiv` повернув `200`
  - `/api/statistics/week?timezone=Europe/Kyiv` повернув `200`
  - `/api/statistics/chart?timezone=Europe/Kyiv` повернув `200`
  - `/api/statistics/month?timezone=UTC` повернув `200`
  - усі три `/api/statistics/*?timezone=Invalid/Timezone` повернули `400`
- browser smoke у цьому проході не завершено: Windows browser-control не зміг
  безпечно визначити поточний URL відкритого Chrome-вікна.

## Відомі обмеження

- таймер активної сесії зберігається в `localStorage`, а не синхронізується між браузерами
- реальна подія Google Calendar не створювалася в цій сесії без зовнішніх credentials
- у проєкті все ще доступний dev-маршрут `/api/docs` від Flask-Smorest, але він не потрібен для HR-перевірки
- немає авторизації й мультикористувацького режиму
- локальна SQLite підходить для навчання й демо, але не для серйозного production-сценарію
