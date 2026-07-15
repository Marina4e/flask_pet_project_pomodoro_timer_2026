# Google Cloud Setup Guide: Pomodoro Timer, Google Calendar, and Google Sheets

[Українська версія](#українська-версія) · [English version](#english-version) ·
[Український README](../README.md) · [English README](../README.en.md)

This standalone guide explains how to configure the Pomodoro Timer project in
Google Cloud and connect Google Calendar and Google Sheets. It documents only
the integration behavior implemented in this repository. Calendar accepts a
direct Calendar ID or an official Google embed URL containing `src`, exposes no
real keys, and does not claim that Flask sends Google push notifications.

## Українська версія

### 1. Що саме інтегровано

Google Calendar і Google Sheets — дві **незалежні optional-інтеграції**.

| Властивість | Google Calendar | Google Sheets |
| --- | --- | --- |
| Призначення | Створити event для latest completed work | Експортувати completed work як rows |
| Trigger | Ручний click / API POST | Ручний click / API POST |
| Кількість даних | Одна latest work-сесія | Усі work-сесії, яких ще немає у sheet |
| External resource | Календар із write access | Spreadsheet із Editor access |
| Optional switch | Порожні required values = unconfigured | `GOOGLE_SHEETS_ENABLED` + browser setting |
| Duplicate guard | `google_calendar_event_id` у SQLite | `client_session_id` у колонці A |
| Breaks | Не синхронізуються | Не експортуються |
| Автоматичний background sync | Ні | Ні |
| Push/email notifications від Flask | Ні | Ні |

Вимкнена або неналаштована інтеграція не заважає timer, SQLite, statistics,
activity calendar чи CSV. Calendar не викликає Sheets; Sheets не викликає
Calendar.

### 2. Точний результат debugging і виправлення 2026-07-15

Без розкриття значень `.env` перевірка реального runtime показала:

```text
Configured value present:     yes, official Google embed URL
Normalized Calendar ID valid: yes, extracted from src
Credentials present:          yes
Credentials structure:        complete required shape
Latest completed work:        #63
Real Calendar sync:           success, event created
SQLite event marker:          saved for #63
Frontend next state:          disabled until the next completed focus
```

Початковий screenshot правильно показував blocker: старий validator відхиляв
навіть офіційний embed URL, хоча той містив percent-encoded Calendar ID у
параметрі `src`. Тепер `_normalize_calendar_id()` приймає тільки direct ID або
офіційний Google Calendar URL із непорожнім `src`, декодує ID і передає в
`events.insert()` саме нормалізоване значення. Реальний sync work `#63` повернув
`200`, створив event і зберіг duplicate-protection marker у SQLite.

### 3. Що означає `Save the latest focus session as an event`

`Latest focus session` у цьому коді — результат
`SessionRepository.get_latest_work_session()`:

```text
SELECT work_sessions
WHERE mode = "work"
ORDER BY completed_at_utc DESC
LIMIT 1
```

Тобто Calendar sync бере:

- останню **завершену і вже збережену** `work`-сесію;
- звичайну 25-хвилинну або коротку 10-секундну test-mode сесію;
- сесію з `google_calendar_event_id IS NULL`.

Він не бере:

- поточний running timer;
- paused timer;
- interval після `Reset` або `Skip`, бо такий interval не записується;
- `short_break` або `long_break`;
- уже synchronized latest work.

Якщо найновіший запис у таблиці є break, repository не помиляється: він шукає
найновіший запис саме серед `mode="work"`.

### 4. Коли Calendar button visible, enabled і disabled

HTML завжди показує кнопку, спочатку з атрибутом `disabled`. Після
`GET /api/integrations/google-calendar/status` browser-функція `canSync(status)`
перевіряє:

```javascript
status.configured &&
status.latest_work_session_id &&
!status.latest_work_session_synced
```

| Умова | UI state | API result |
| --- | --- | --- |
| ID і credentials порожні | `Setup required`, disabled | Sync: `400`, not configured |
| Порожній тільки ID | disabled | `400`, missing `GOOGLE_CALENDAR_ID` |
| Порожні тільки credentials | disabled | `400`, missing credentials |
| Офіційний Google embed URL має `src` | `Ready` для unsynced work | `src` декодується в ID |
| Інший URL або embed URL без `src` | `Fix Calendar ID`, disabled | `400`, invalid ID |
| ID містить whitespace | disabled | `400`, invalid ID |
| Configuration shape ready, work немає | disabled | `400`, no completed work |
| Completed unsynced work є | `Ready`, enabled | Google call starts on click |
| Latest work already synced | `already synced`, disabled | Direct POST: `409` |
| Credentials не є valid JSON | Може бути enabled | Click: controlled `400` |
| Credentials JSON incomplete | Може бути enabled | Click: controlled `400` + missing fields |
| Calendar не shared / access denied | Enabled до click | Click: generic safe `400` |
| Network/API unavailable | Enabled до click | Click: generic safe `400` |

Чому invalid credentials можуть не вимкнути кнопку заздалегідь: Calendar status
навмисно перевіряє лише presence та форму ID. Повний private-key JSON ліниво
парситься у `_build_calendar_service()` тільки після ручного sync. Startup
ніколи не потребує Google credentials і не звертається до Google.

### 5. Calendar configuration: тільки реальні variables

```dotenv
# Optional integration. Leave the two required values blank to keep it unconfigured.
GOOGLE_CALENDAR_ID=
GOOGLE_CALENDAR_CREDENTIALS_JSON=

# Optional event appearance.
GOOGLE_CALENDAR_EVENT_PREFIX=Pomodoro
GOOGLE_CALENDAR_EVENT_COLOR_ID=
```

У final code немає `GOOGLE_CALENDAR_ENABLED`. Додавати таку variable до `.env`
без окремої code change немає сенсу: Flask її не читає. Optional boundary зараз
такий:

- required values blank → status is unconfigured, no Google call;
- both values present + ID shape valid → button може стати ready;
- full credentials і external permissions перевіряються на sync.

Required service-account JSON fields:

```text
type = service_account
client_email
private_key
token_uri
```

### 6. Повний Google Cloud setup для Calendar

#### 6.1 Cloud project та API

1. Відкрийте [Google Cloud Console](https://console.cloud.google.com/).
2. Створіть окремий project або виберіть наявний.
3. Відкрийте `APIs & Services → Library`.
4. Знайдіть та увімкніть **Google Calendar API**.

API вмикається в Cloud project, до якого належить service account. Це ще не дає
доступу до вашого особистого календаря.

#### 6.2 Service account та JSON key

1. Відкрийте `IAM & Admin → Service Accounts`.
2. Натисніть `Create service account`.
3. Дайте зрозуміле ім’я, наприклад `pomodoro-integrations`.
4. Для цього local demo не потрібно видавати broad Cloud IAM roles лише заради
   Calendar/Sheets resource access.
5. Відкрийте створений account → `Keys`.
6. `Add key → Create new key → JSON → Create`.
7. Збережіть downloaded JSON поза public/repository folders.
8. Скопіюйте `client_email` для sharing.

JSON private key є повноцінним credential. Якщо key потрапив у Git або чат,
видаліть/disable його в Google Cloud і створіть новий.

#### 6.3 Створіть або виберіть Calendar

Для навчального проєкту зручно створити окремий secondary calendar, наприклад
`Pomodoro Work`, щоб тестові events не змішувалися з особистими.

1. Відкрийте [Google Calendar](https://calendar.google.com/) на desktop.
2. Біля `Other calendars` натисніть `+ → Create new calendar` або виберіть
   існуючий calendar, яким ви володієте.
3. Відкрийте `Settings and sharing` цього calendar.

#### 6.4 Поділіться Calendar із service account

1. Знайдіть `Share with specific people or groups`.
2. Додайте `client_email` із JSON key.
3. Виберіть **Make changes to events**.
4. Збережіть sharing.

`See all event details` недостатньо для `events.insert()`. Broad IAM role у
Cloud Console також не замінює Calendar sharing. Work/school administrator може
обмежувати зовнішні service-account addresses; тоді потрібна допомога domain
admin або інший authorization design.

#### 6.5 Знайдіть правильний Calendar ID

Шлях у desktop UI:

```text
Google Calendar
→ Settings
→ Settings for my calendars
→ <target calendar>
→ Integrate calendar
→ Calendar ID
```

Можливі значення:

- primary personal calendar часто має ID у формі account email;
- secondary calendar часто має ID на кшталт
  `...@group.calendar.google.com`;
- точним джерелом завжди є поле `Calendar ID` у settings.

Рекомендовано вставляти direct Calendar ID. Як fallback застосунок також
приймає повний офіційний Google Calendar embed URL із параметром `src` і
автоматично декодує цей параметр.

Не використовуйте:

- URL сторінки Google Calendar;
- `Public URL to this calendar`;
- embed `<iframe>`;
- share link;
- arbitrary third-party URL;
- percent-encoded `src` окремо без повного official embed URL.

Calendar API підтримує special keyword `primary`, але в цьому service-account
flow він стосується authenticated identity, а не автоматично вашого user
calendar. Для прозорої діагностики використовуйте фактичний ID календаря,
яким поділилися з service account.

#### 6.6 Перетворіть JSON у один рядок

PowerShell:

```powershell
(Get-Content .\service-account.json -Raw |
    ConvertFrom-Json |
    ConvertTo-Json -Compress)
```

Python:

```powershell
python -c "import json; print(json.dumps(json.load(open('service-account.json', encoding='utf-8')), separators=(',', ':')))"
```

Скопіюйте output, але не публікуйте його. В `.env` outer single quotes
захищають internal JSON double quotes:

```dotenv
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
GOOGLE_CALENDAR_CREDENTIALS_JSON='{"type":"service_account","project_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","token_uri":"https://oauth2.googleapis.com/token"}'
```

Приклад вище містить placeholders, не real key. Після editing перезапустіть
Flask. Не вставляйте JSON із literal multi-line private key у `.env`.

### 7. Event payload і timezone

`GoogleCalendarService._build_event_payload()` формує:

```json
{
  "summary": "Pomodoro focus session",
  "description": "Pomodoro Work Tracker session #<id>\nclient_session_id: <uuid>\nDuration (minutes): <value>",
  "start": {
    "dateTime": "<timezone-aware ISO datetime>",
    "timeZone": "Europe/Kyiv"
  },
  "end": {
    "dateTime": "<timezone-aware ISO datetime>",
    "timeZone": "Europe/Kyiv"
  }
}
```

- prefix походить із `GOOGLE_CALENDAR_EVENT_PREFIX`;
- optional `colorId` додається лише для non-empty
  `GOOGLE_CALENDAR_EVENT_COLOR_ID`;
- start/end беруться зі stored UTC timestamps і конвертуються до selected
  timezone;
- 10 секунд відображаються як `0.17` minutes;
- model не має project name, тому він не вигадується;
- payload не містить attendees або custom reminders.

Calendar API викликається як:

```text
service.events().insert(calendarId=<Calendar ID>, body=<payload>).execute()
```

Scope: `https://www.googleapis.com/auth/calendar.events`.

### 8. Duplicate protection

Після successful Google response:

1. `response["id"]` записується в
   `work_sessions.google_calendar_event_id`;
2. SQLAlchemy commit зберігає marker;
3. status повертає `latest_work_session_synced=true`;
4. UI вимикає кнопку;
5. direct repeated POST повертає `409 Conflict` із `session_id` та
   `sync_status="already_synced"`, без external event ID.

Artificial session створюється з `google_calendar_event_id=NULL` автоматично,
бо `SessionService.create_session()` не приймає цей field від client.

Важливе edge case: якщо Google event створена, але SQLite commit не вдався, API
повертає `Calendar event was created but could not be stored locally`. Перед
retry потрібно перевірити Calendar вручну, інакше external duplicate можливий.

### 9. Test mode і штучна completed session

#### 9.1 Browser test mode

```powershell
$env:POMODORO_TEST_MODE="true"
python run.py
```

1. Відкрийте `http://127.0.0.1:5000`.
2. Запустіть work.
3. Не натискайте Reset або Skip; дочекайтеся приблизно 10 секунд.
4. Переконайтеся, що work завершилася та збережена.
5. Calendar card має показати latest session як ready.
6. Натисніть sync та перевірте event за timestamp.

Test-mode record залишається в SQLite. Short duration не є filter criterion.

#### 9.2 Artificial record через existing API

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

$created | Select-Object id, mode, started_at_utc, completed_at_utc, google_calendar_event_id
```

Щоб після цієї команди використати browser button, reload сторінку `/`:
PowerShell request не dispatch-ить `pomodoro:sessions-changed` у вже відкритій
вкладці. Direct status/sync API calls reload не потребують.

Команда:

- створює один completed `work` record;
- використовує realistic UTC timestamps;
- генерує unique `client_session_id`;
- не змінює settings;
- не видаляє existing data;
- не викликає Google;
- використовує вже існуючий sessions API, а не hidden test endpoint.

Local cleanup:

```powershell
Invoke-RestMethod `
  -Method Delete `
  -Uri "http://127.0.0.1:5000/api/sessions/$($created.id)"
```

Це не видаляє external Calendar event. Її треба видалити в Google Calendar
окремо.

### 10. Calendar API requests і responses

#### 10.1 Safe status

```powershell
$status = Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:5000/api/integrations/google-calendar/status"

$status | Select-Object configured, calendar_id_valid, calendar_id_normalized, missing, latest_work_session_id, latest_work_session_synced
```

Response fields:

| Field | Значення |
| --- | --- |
| `configured` | Required values present + direct/normalized Calendar ID valid |
| `calendar_id` | Direct або normalized ID; embed URL не повертається |
| `calendar_id_valid` | False для blank, unsupported URL або whitespace value |
| `calendar_id_normalized` | True, якщо ID декодовано з official embed URL `src` |
| `missing` | Names of missing required env variables |
| `latest_work_session_id` | Latest completed work ID або `null` |
| `latest_work_session_synced` | Чи є event marker у latest work |

#### 10.2 Manual sync

Request schema має optional `timezone`, але надсилайте JSON body:

```powershell
$syncBody = @{ timezone = "Europe/Kyiv" } | ConvertTo-Json
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/integrations/google-calendar/sync" `
  -ContentType "application/json" `
  -Body $syncBody
```

Success shape:

```json
{
  "status": {
    "configured": true,
    "calendar_id": "<configured ID>",
    "calendar_id_valid": true,
    "calendar_id_normalized": false,
    "missing": [],
    "latest_work_session_id": 30,
    "latest_work_session_synced": true
  },
  "timezone": "Europe/Kyiv",
  "session_id": 30,
  "event_id": "<Google event ID>",
  "html_link": "<Google Calendar link>"
}
```

Не публікуйте real `event_id`, `html_link` або email-like Calendar ID у public
debug output.

#### 10.3 Controlled errors

```json
{
  "error": {
    "code": "validation_error",
    "message": "<safe message>",
    "details": {}
  }
}
```

| HTTP | Message / situation |
| --- | --- |
| `400` | Invalid Calendar ID |
| `400` | Integration not configured + missing names |
| `400` | No completed work session |
| `400` | Credentials missing, invalid JSON, or incomplete |
| `400` | Google client/external call failed; generic safe message |
| `409` | Latest work already synchronized |

### 11. Google Sheets setup

#### 11.1 Environment

```dotenv
GOOGLE_SHEETS_ENABLED=false
GOOGLE_SHEETS_SPREADSHEET_ID=
GOOGLE_SHEETS_CREDENTIALS_JSON=
```

`GOOGLE_SHEETS_ENABLED` є default/fallback. Після першого browser save enable
flag та Spreadsheet ID зберігаються в `user_settings`; private JSON завжди
залишається тільки в server config.

#### 11.2 Cloud і sharing

1. Увімкніть **Google Sheets API** у Cloud project.
2. Можна використати той самий service account, якщо обидва APIs enabled і
   обидва resources shared, або окремий account для least privilege.
3. Створіть spreadsheet у своєму Google Drive.
4. Натисніть `Share`.
5. Додайте `client_email` як **Editor**.
6. Вимкніть `Notify people`: service account не має inbox.
7. Скопіюйте Spreadsheet ID між `/d/` і `/edit`:

```text
https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit
```

Sharing конкретного file достатнє для цього flow; broad Workspace admin role
або domain-wide delegation для однієї явно shared таблиці не потрібні.

#### 11.3 Browser buttons

- `Save Settings` приймає `enabled` і `spreadsheet_id`, валідовує presence/shape
  server credentials та зберігає лише non-secret values у SQLite. Google rows
  не створюються.
- `Sync Completed Sessions` перевіряє full configuration, читає completed work
  sessions, відкриває Sheets API та додає лише missing rows.

#### 11.4 Columns and duplicates

| Column | Header | Source |
| --- | --- | --- |
| A | `Session ID` | stable `client_session_id` |
| B | `Date` | local start date |
| C | `Start Time` | local start time |
| D | `End Time` | local completion time |
| E | `Planned Duration` | seconds |
| F | `Actual Duration` | seconds |
| G | `Mode` | `work` |
| H | `Timezone` | selected IANA timezone |
| I | `Created At` | local ISO datetime |

Якщо sheet порожній, service записує exact header A1:I1. Якщо existing header
відрізняється, sync зупиняється з safe error і не додає rows. Existing column-A
IDs формують duplicate set; повторний sync повертає `exported=0` та відповідний
`skipped` count.

#### 11.5 Manual Sheets API calls

Safe settings:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:5000/api/integrations/google-sheets/settings"
```

Save non-secret settings:

```powershell
$settingsBody = @{
  enabled = $true
  spreadsheet_id = "<SPREADSHEET_ID>"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Put `
  -Uri "http://127.0.0.1:5000/api/integrations/google-sheets/settings" `
  -ContentType "application/json" `
  -Body $settingsBody
```

Sync:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/integrations/google-sheets/sync"
```

### 12. Notifications: що робить Flask, а що Google

Поточний проєкт не реалізує Google push channel, webhook, Gmail email, browser
Notification API або attendee invitation flow.

Фактичний flow:

1. Flask створює звичайну Calendar event.
2. Service account авторизує API request, але не надсилає повідомлення
   користувачу.
3. Event payload не задає custom `reminders` і не містить attendees.
4. Google Calendar може застосувати calendar/user notification settings.
5. User налаштовує email, desktop або Calendar alerts у Google Calendar.
6. Browser/OS permission для `calendar.google.com` контролюється поза Flask.

Шлях:

```text
Google Calendar
→ Settings
→ Settings for my calendars
→ <Pomodoro calendar>
→ Event notifications
```

Або відкрийте конкретну created event → `Edit` → додайте notification. Settings
є персональними; shared editor не може змінити notification preferences іншого
користувача.

### 13. Troubleshooting

| Проблема | Ймовірна причина | Точна дія |
| --- | --- | --- |
| Button disabled + `Fix Calendar ID` | Unsupported URL або embed URL без `src` | Вставте direct ID або повний official embed URL із `src` |
| `Setup required` | ID або credentials blank | Заповніть обидва values і restart Flask |
| `No completed focus sessions` | Work ще не завершилася / Reset / Skip | Завершіть work або створіть artificial record |
| Latest UI record — break | Це нормально | Calendar шукає latest `work`, не latest row загалом |
| `not valid JSON` | Multiline/broken quoting | Re-compress JSON, wrap in single quotes, restart |
| `invalid or incomplete` | Missing required JSON fields / wrong credential type | Створіть новий JSON service-account key |
| `Failed to create... permissions` | API disabled, no sharing, wrong ID, network | Enable API, share Calendar with `client_email`, verify ID |
| `403` from Google | Service account не має writer access | Grant `Make changes to events`; check domain policy |
| `404` from Google | Wrong/nonexistent Calendar ID | Copy ID again from target Calendar settings |
| `already synced` | Event marker уже stored | Завершіть нову work-сесію; не очищуйте marker вручну |
| Event має неправильний час | Wrong app timezone | Save valid IANA timezone and retry with new work |
| Event не видно | Дивитесь інший calendar/time | Open shared target calendar and session timestamp |
| Немає reminder | Flask не задає custom reminder | Configure Calendar/event notifications |
| Google package missing | Dependencies not installed | `pip install -r requirements.txt` |
| Sheets button disabled | Not enabled/saved/configured | Add server JSON, enable, enter ID, Save Settings |
| Sheets `403/404` | Sheet not shared / wrong ID | Share as Editor with `client_email`; recopy ID |
| Sheets header error | A1:I1 changed | Use empty sheet or restore exact documented headers |

Safe diagnostic without values:

```powershell
python -c "from app import create_app; from app.services.google_calendar_service import GoogleCalendarService; app=create_app(); ctx=app.app_context(); ctx.push(); s=GoogleCalendarService().get_status(); print({k:s[k] for k in ['configured','calendar_id_valid','calendar_id_normalized','missing','latest_work_session_id','latest_work_session_synced']})"
```

Database inspector:

```powershell
python scripts/check_database.py
```

### 14. Privacy та secret handling

- `.env` уже gitignored; `service-account.json` зберігайте поза repository або
  додайте його exact filename до local Git exclude до першого `git add`.
- `.env.example` містить тільки blank placeholders.
- Не друкуйте raw credentials у terminal recordings або CI logs.
- Status endpoints не повертають credentials.
- Sheets browser settings не містять private JSON.
- Calendar status може повернути Calendar ID; не показуйте personal email у
  public screenshot.
- Success API повертає external event ID/link; не вставляйте їх у public issue.
- Conflict response навмисно не повертає external event ID.
- При compromise видаліть key у Google Cloud і створіть новий.
- Для production віддавайте перевагу Secret Manager та short-lived credentials
  / Workload Identity Federation, якщо hosting це підтримує.

### 15. Data flow

```mermaid
flowchart LR
    A["Completed work countdown"] --> B["POST /api/sessions"]
    B --> C["WorkSession in SQLite"]
    C --> D["GET Calendar status"]
    D --> E{"Configured + unsynced work?"}
    E -- No --> F["Button remains disabled"]
    E -- Yes --> G["POST Calendar sync"]
    G --> H["Validate ID and credentials"]
    H --> I["Build timezone-aware event"]
    I --> J["Google Calendar events.insert"]
    J --> K["Store google_calendar_event_id"]
    K --> L["409 on repeated sync"]
```

### 16. Файли та symbols: input, output, side effects, errors, caller

| Symbol | Type / file | Parameters | Return | Side effects | Errors | Caller |
| --- | --- | --- | --- | --- | --- | --- |
| `create_app` | function, `app/__init__.py` | optional config name | Flask app | loads env, registers extensions/routes, local migration | startup/config/database exceptions | `run.py`, tests, Gunicorn |
| `BaseConfig` | class, `app/config.py` | env at import/runtime | config attributes | none | invalid ints fall back safely | app factory |
| `_apply_runtime_environment` | function, `app/__init__.py` | Flask app | `None` | overlays env values | none for blank optional Google values | `create_app` |
| `WorkSession` | model, `app/models/work_session.py` | SQLAlchemy fields | ORM object | persists completed session and Calendar marker | DB constraints | services/repository |
| `SessionService.create_session` | method | completed payload dict | serialized session | insert + commit | validation, duplicate `409`, DB `400` | sessions POST / artificial command |
| `SessionService.delete_session` | method | integer ID | message dict | deletes one local row | `404` | sessions DELETE |
| `SessionRepository.get_latest_work_session` | method | none | model or `None` | none | DB errors | Calendar status/sync |
| `GoogleCalendarService.get_status` | method | none | safe status dict | DB read only | DB errors | GET status, sync precheck |
| `sync_latest_work_session` | method | optional timezone | sync result dict | Google insert + SQLite marker commit | `400`, `409` | POST sync |
| `_build_event_payload` | method | session, timezone | event dict | none | timezone validation from shared utility | sync service |
| `_build_calendar_service` | classmethod | none; reads config | Google client | parses private JSON, initializes client | missing dependency, invalid JSON/key | sync service only |
| `_missing_credential_fields` | classmethod | parsed object | list of field names | none | none | client builder/tests |
| `_is_calendar_id_valid` | classmethod | object | bool | none | none | status/sync |
| `_normalize_calendar_id` | classmethod | direct ID or URL | normalized ID or `None` | none | none | status/validation |
| `GoogleCalendarStatusResource.get` | route method | HTTP GET | `200` schema | DB read | API error handler | browser/status command |
| `GoogleCalendarSyncResource.post` | route method | JSON `{timezone?}` | `200` schema | delegates external/local write | `400/409` | browser/manual command |
| Browser `canSync` | function, `integrations.js` | status object | bool | none | none | status renderer/click guard |
| Browser `loadGoogleCalendarStatus` | async function | none | Promise | GET + DOM state | safe UI error | page load/session change |
| Browser `syncGoogleCalendar` | async function | none | Promise | POST + DOM state | safe UI error | Calendar click handler |
| `GoogleSheetsService.get_settings_payload` | method | none | safe settings dict | DB/config read | none for disabled flow | GET settings/UI |
| `update_settings` | method | enable + ID | safe settings dict | SQLite commit | missing/invalid configuration | PUT settings |
| `sync_completed_sessions` | method | none | counts/status dict | Sheets read/header/append | safe validation/external errors | POST Sheets sync |
| `_prepare_sheet` | method | values API, ID, rows | existing ID set | may write header | header mismatch | Sheets sync |

### 17. Automated та manual verification

```powershell
pytest tests/test_integrations_api.py -v
pytest tests/test_google_sheets_api.py tests/test_google_sheets_service.py -v
python -m compileall app scripts run.py
ruff check .
black --check .
pytest -v
flask --app run.py routes
python scripts/check_database.py
python run.py
```

Automated tests mock Google; вони перевіряють 10-second work, newer break
filtering, missing config, invalid credentials, successful payload, external
failure, duplicate prevention, secret non-leakage та Calendar/Sheets
independence. Real Google event потребує user resources і не підмінюється mock
claim.

### 18. Official Google references

- [Enable Google Workspace APIs](https://developers.google.com/workspace/guides/enable-apis)
- [Create access credentials and service accounts](https://developers.google.com/workspace/guides/create-credentials)
- [Create and protect service-account keys](https://cloud.google.com/iam/docs/keys-create-delete)
- [Create Calendar events](https://developers.google.com/workspace/calendar/api/guides/create-events)
- [Calendar events.insert reference](https://developers.google.com/workspace/calendar/api/v3/reference/events/insert)
- [Share a Google Calendar](https://support.google.com/calendar/answer/37082)
- [Change Calendar notifications](https://support.google.com/calendar/answer/37242)
- [Google Sheets Python quickstart](https://developers.google.com/workspace/sheets/api/quickstart/python)
- [Google Sheets API limits](https://developers.google.com/workspace/sheets/api/limits)

### 19. Що можна покращити наступним prompt

1. Додати explicit `GOOGLE_CALENDAR_ENABLED` із coordinated backend status,
   schema, exact Calendar UI state та tests — не частковою env-only зміною.
2. Додати `flask diagnose-google-integrations`, який перевіряє лише safe flags,
   dependencies, resource-ID shape і optional read/write probe за confirmation.
3. Дати користувачу вибір конкретної work-сесії для sync, а не лише latest.
4. Додати update/delete linkage між local session і existing Calendar event.
5. Додати optional reminder fields до event payload із чітким UI/config.
6. Перейти з long-lived JSON key на OAuth user consent або WIF/Secret Manager
   для production deployment.
7. Додати mocked browser E2E для всіх Calendar button states.
8. Додати structured external error categories (`permission_denied`,
   `resource_not_found`, `api_disabled`) без витоку Google response body.

---

## English Version

### 1. What is integrated

Google Calendar and Google Sheets are two **independent optional integrations**.

| Property | Google Calendar | Google Sheets |
| --- | --- | --- |
| Purpose | Create an event for latest completed work | Export completed work as rows |
| Trigger | Manual click / API POST | Manual click / API POST |
| Data amount | One latest work session | All work sessions not yet in the sheet |
| External resource | Calendar with write access | Spreadsheet with Editor access |
| Optional switch | Blank required values = unconfigured | `GOOGLE_SHEETS_ENABLED` + browser setting |
| Duplicate guard | `google_calendar_event_id` in SQLite | `client_session_id` in column A |
| Breaks | Not synchronized | Not exported |
| Automatic background sync | No | No |
| Push/email notifications from Flask | No | No |

A disabled or unconfigured integration does not affect the timer, SQLite,
statistics, activity calendar, or CSV. Calendar never calls Sheets; Sheets
never calls Calendar.

### 2. Exact 2026-07-15 debugging result and fix

A safe runtime check of the real local configuration showed:

```text
Configured value present:     yes, official Google embed URL
Normalized Calendar ID valid: yes, extracted from src
Credentials present:          yes
Credentials structure:        complete required shape
Latest completed work:        #63
Real Calendar sync:           success, event created
SQLite event marker:          saved for #63
Frontend next state:          disabled until the next completed focus
```

The initial screenshot correctly identified the blocker: the old validator
rejected even an official embed URL although its `src` query parameter contained
the percent-encoded Calendar ID. `_normalize_calendar_id()` now accepts only a
direct ID or an official Google Calendar URL with a non-empty `src`, decodes the
ID, and passes that normalized value to `events.insert()`. A real sync of work
`#63` returned `200`, created the event, and stored the duplicate-protection
marker in SQLite.

### 3. Meaning of `Save the latest focus session as an event`

In this code, `latest focus session` is the result of
`SessionRepository.get_latest_work_session()`:

```text
SELECT work_sessions
WHERE mode = "work"
ORDER BY completed_at_utc DESC
LIMIT 1
```

Calendar sync selects:

- the latest **completed and already persisted** `work` session;
- either a normal 25-minute or short 10-second test-mode session;
- a session whose `google_calendar_event_id IS NULL`.

It does not select:

- a currently running timer;
- a paused timer;
- an interval discarded by `Reset` or `Skip`, because no row is stored;
- `short_break` or `long_break`;
- an already synchronized latest work session.

If the newest database row is a break, the repository still behaves correctly:
it finds the newest row within `mode="work"`.

### 4. When the Calendar button is visible, enabled, or disabled

HTML always renders the button with an initial `disabled` attribute. After
`GET /api/integrations/google-calendar/status`, browser function
`canSync(status)` checks:

```javascript
status.configured &&
status.latest_work_session_id &&
!status.latest_work_session_synced
```

| Condition | UI state | API result |
| --- | --- | --- |
| ID and credentials blank | `Setup required`, disabled | Sync: `400`, not configured |
| Only ID missing | disabled | `400`, missing `GOOGLE_CALENDAR_ID` |
| Only credentials missing | disabled | `400`, missing credentials |
| Official Google embed URL has `src` | `Ready` for unsynced work | `src` is decoded into ID |
| Other URL or embed URL without `src` | `Fix Calendar ID`, disabled | `400`, invalid ID |
| ID contains whitespace | disabled | `400`, invalid ID |
| Configuration shape ready, no work | disabled | `400`, no completed work |
| Completed unsynced work exists | `Ready`, enabled | Google call starts on click |
| Latest work is already synced | `already synced`, disabled | Direct POST: `409` |
| Credentials are not valid JSON | May be enabled | Click: controlled `400` |
| Credentials JSON is incomplete | May be enabled | Click: controlled `400` + missing fields |
| Calendar is not shared / access denied | Enabled before click | Click: generic safe `400` |
| Network/API unavailable | Enabled before click | Click: generic safe `400` |

Invalid credentials may not disable the button in advance because Calendar
status intentionally checks only presence and ID shape. The full private-key
JSON is parsed lazily in `_build_calendar_service()` only during manual sync.
Startup never requires credentials and never contacts Google.

### 5. Calendar configuration: actual variables only

```dotenv
# Optional integration. Leave the two required values blank to keep it unconfigured.
GOOGLE_CALENDAR_ID=
GOOGLE_CALENDAR_CREDENTIALS_JSON=

# Optional event appearance.
GOOGLE_CALENDAR_EVENT_PREFIX=Pomodoro
GOOGLE_CALENDAR_EVENT_COLOR_ID=
```

The final code has no `GOOGLE_CALENDAR_ENABLED`. Adding such a variable to
`.env` alone has no effect because Flask does not read it. The current optional
boundary is:

- required values blank → unconfigured status, no Google call;
- both values present + valid ID shape → button can become ready;
- full credentials and external permissions are checked on sync.

Required service-account JSON fields:

```text
type = service_account
client_email
private_key
token_uri
```

### 6. Complete Google Cloud Calendar setup

#### 6.1 Cloud project and API

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Create a separate project or select an existing one.
3. Open `APIs & Services → Library`.
4. Find and enable the **Google Calendar API**.

The API is enabled in the project that owns the service account. This does not
grant access to your personal calendar.

#### 6.2 Service account and JSON key

1. Open `IAM & Admin → Service Accounts`.
2. Click `Create service account`.
3. Use a clear name, such as `pomodoro-integrations`.
4. This local demo does not need broad Cloud IAM roles merely for access to a
   specifically shared Calendar or Sheet.
5. Open the created account → `Keys`.
6. Select `Add key → Create new key → JSON → Create`.
7. Store the downloaded JSON outside public/repository folders.
8. Copy `client_email` for resource sharing.

The JSON private key is a powerful credential. If it reaches Git or chat,
delete/disable that key in Google Cloud and create a new one.

#### 6.3 Create or select a Calendar

For a learning project, a dedicated secondary calendar such as `Pomodoro Work`
keeps test events separate from personal events.

1. Open [Google Calendar](https://calendar.google.com/) on desktop.
2. Next to `Other calendars`, select `+ → Create new calendar`, or select an
   existing calendar you own.
3. Open that calendar's `Settings and sharing`.

#### 6.4 Share the Calendar with the service account

1. Find `Share with specific people or groups`.
2. Add the `client_email` from the JSON key.
3. Grant **Make changes to events**.
4. Save sharing.

`See all event details` is not enough for `events.insert()`. A broad IAM role in
Cloud Console also does not replace Calendar sharing. A work/school
administrator may restrict external service-account addresses; that requires a
domain administrator or a different authorization design.

#### 6.5 Find the correct Calendar ID

Desktop UI path:

```text
Google Calendar
→ Settings
→ Settings for my calendars
→ <target calendar>
→ Integrate calendar
→ Calendar ID
```

Possible values:

- a primary personal calendar often has an email-shaped ID;
- a secondary calendar often ends in `@group.calendar.google.com`;
- the authoritative source is always the `Calendar ID` field in settings.

Using the direct Calendar ID is recommended. As a fallback, the application
also accepts a complete official Google Calendar embed URL containing `src` and
automatically decodes that parameter.

Do not use:

- the Google Calendar page URL;
- `Public URL to this calendar`;
- an embed `<iframe>`;
- a share link;
- an arbitrary third-party URL;
- the percent-encoded `src` value by itself without the complete official URL.

The Calendar API supports the special `primary` keyword, but in this
service-account flow it refers to the authenticated identity, not automatically
to your user calendar. Use the actual ID of the calendar shared with the service
account for transparent diagnostics.

#### 6.6 Convert JSON to one line

PowerShell:

```powershell
(Get-Content .\service-account.json -Raw |
    ConvertFrom-Json |
    ConvertTo-Json -Compress)
```

Python:

```powershell
python -c "import json; print(json.dumps(json.load(open('service-account.json', encoding='utf-8')), separators=(',', ':')))"
```

Copy the output without publishing it. Outer single quotes in `.env` preserve
the internal JSON double quotes:

```dotenv
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
GOOGLE_CALENDAR_CREDENTIALS_JSON='{"type":"service_account","project_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","token_uri":"https://oauth2.googleapis.com/token"}'
```

This is a placeholder, not a real key. Restart Flask after editing. Do not paste
a literal multi-line private key into `.env`.

### 7. Event payload and timezone

`GoogleCalendarService._build_event_payload()` creates:

```json
{
  "summary": "Pomodoro focus session",
  "description": "Pomodoro Work Tracker session #<id>\nclient_session_id: <uuid>\nDuration (minutes): <value>",
  "start": {
    "dateTime": "<timezone-aware ISO datetime>",
    "timeZone": "Europe/Kyiv"
  },
  "end": {
    "dateTime": "<timezone-aware ISO datetime>",
    "timeZone": "Europe/Kyiv"
  }
}
```

- prefix comes from `GOOGLE_CALENDAR_EVENT_PREFIX`;
- optional `colorId` is included only for a non-empty
  `GOOGLE_CALENDAR_EVENT_COLOR_ID`;
- start/end are converted from stored UTC timestamps to the selected timezone;
- 10 seconds is represented as `0.17` minutes;
- the model has no project name, so none is invented;
- the payload contains no attendees or custom reminders.

Calendar API call:

```text
service.events().insert(calendarId=<Calendar ID>, body=<payload>).execute()
```

Scope: `https://www.googleapis.com/auth/calendar.events`.

### 8. Duplicate protection

After a successful Google response:

1. `response["id"]` is assigned to
   `work_sessions.google_calendar_event_id`;
2. SQLAlchemy commits the marker;
3. status returns `latest_work_session_synced=true`;
4. the UI disables the button;
5. a repeated direct POST returns `409 Conflict` with `session_id` and
   `sync_status="already_synced"`, without the external event ID.

An artificial session starts with `google_calendar_event_id=NULL` automatically
because `SessionService.create_session()` does not accept this field from the
client.

Important edge case: if Google creates the event but the SQLite commit fails,
the API reports `Calendar event was created but could not be stored locally`.
Check Calendar before retrying or an external duplicate can be created.

### 9. Test mode and artificial completed session

#### 9.1 Browser test mode

```powershell
$env:POMODORO_TEST_MODE="true"
python run.py
```

1. Open `http://127.0.0.1:5000`.
2. Start work.
3. Do not Reset or Skip; let all 10 seconds finish.
4. Confirm that work was completed and stored.
5. The Calendar card should show the latest session as ready.
6. Click sync and inspect the event at that timestamp.

The test-mode record remains in SQLite. Short duration is not a filter.

#### 9.2 Artificial record through the existing API

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

$created | Select-Object id, mode, started_at_utc, completed_at_utc, google_calendar_event_id
```

To use the browser button after this command, reload `/`: the PowerShell
request does not dispatch `pomodoro:sessions-changed` in an already open tab.
Direct status/sync API calls do not require a reload.

This command:

- creates one completed `work` record;
- uses realistic UTC timestamps;
- generates a unique `client_session_id`;
- changes no settings;
- deletes no existing data;
- does not call Google;
- uses the existing sessions API rather than a hidden test endpoint.

Local cleanup:

```powershell
Invoke-RestMethod `
  -Method Delete `
  -Uri "http://127.0.0.1:5000/api/sessions/$($created.id)"
```

This does not delete an external Calendar event. Remove it separately in Google
Calendar.

### 10. Calendar API requests and responses

#### 10.1 Safe status

```powershell
$status = Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:5000/api/integrations/google-calendar/status"

$status | Select-Object configured, calendar_id_valid, calendar_id_normalized, missing, latest_work_session_id, latest_work_session_synced
```

Response fields:

| Field | Meaning |
| --- | --- |
| `configured` | Required values present + direct/normalized Calendar ID valid |
| `calendar_id` | Direct or normalized ID; the embed URL is not returned |
| `calendar_id_valid` | False for blank, unsupported URL, or whitespace value |
| `calendar_id_normalized` | True when ID was decoded from official embed URL `src` |
| `missing` | Names of missing required env variables |
| `latest_work_session_id` | Latest completed work ID or `null` |
| `latest_work_session_synced` | Whether latest work has an event marker |

#### 10.2 Manual sync

The request schema has an optional `timezone`, but send a JSON body:

```powershell
$syncBody = @{ timezone = "Europe/Kyiv" } | ConvertTo-Json
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/integrations/google-calendar/sync" `
  -ContentType "application/json" `
  -Body $syncBody
```

Success shape:

```json
{
  "status": {
    "configured": true,
    "calendar_id": "<configured ID>",
    "calendar_id_valid": true,
    "calendar_id_normalized": false,
    "missing": [],
    "latest_work_session_id": 30,
    "latest_work_session_synced": true
  },
  "timezone": "Europe/Kyiv",
  "session_id": 30,
  "event_id": "<Google event ID>",
  "html_link": "<Google Calendar link>"
}
```

Do not publish real event IDs, links, or email-shaped Calendar IDs in public
debug output.

#### 10.3 Controlled errors

```json
{
  "error": {
    "code": "validation_error",
    "message": "<safe message>",
    "details": {}
  }
}
```

| HTTP | Message / situation |
| --- | --- |
| `400` | Invalid Calendar ID |
| `400` | Integration not configured + missing names |
| `400` | No completed work session |
| `400` | Credentials missing, invalid JSON, or incomplete |
| `400` | Google client/external call failed; generic safe message |
| `409` | Latest work already synchronized |

### 11. Google Sheets setup

#### 11.1 Environment

```dotenv
GOOGLE_SHEETS_ENABLED=false
GOOGLE_SHEETS_SPREADSHEET_ID=
GOOGLE_SHEETS_CREDENTIALS_JSON=
```

`GOOGLE_SHEETS_ENABLED` is the default/fallback. After the first browser save,
the enable flag and Spreadsheet ID live in `user_settings`; private JSON always
remains server-side.

#### 11.2 Cloud and sharing

1. Enable the **Google Sheets API** in the Cloud project.
2. Reuse the same service account if both APIs are enabled and both resources
   are shared, or use separate accounts for least privilege.
3. Create a spreadsheet in your Google Drive.
4. Click `Share`.
5. Add `client_email` as **Editor**.
6. Disable `Notify people`; a service account has no inbox.
7. Copy the ID between `/d/` and `/edit`:

```text
https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit
```

Direct file sharing is sufficient for this flow; a broad Workspace admin role
or domain-wide delegation is unnecessary for one explicitly shared sheet.

#### 11.3 Browser buttons

- `Save Settings` accepts `enabled` and `spreadsheet_id`, validates server
  credential presence/shape, and stores only non-secret values in SQLite. It
  creates no rows.
- `Sync Completed Sessions` validates full configuration, reads completed work,
  opens the Sheets API, and appends only missing rows.

#### 11.4 Columns and duplicates

| Column | Header | Source |
| --- | --- | --- |
| A | `Session ID` | stable `client_session_id` |
| B | `Date` | local start date |
| C | `Start Time` | local start time |
| D | `End Time` | local completion time |
| E | `Planned Duration` | seconds |
| F | `Actual Duration` | seconds |
| G | `Mode` | `work` |
| H | `Timezone` | selected IANA timezone |
| I | `Created At` | local ISO datetime |

For an empty sheet, the service writes the exact A1:I1 header. If an existing
header differs, sync stops safely and adds no rows. Existing column-A IDs form
the duplicate set; a repeated sync returns `exported=0` and an appropriate
`skipped` count.

#### 11.5 Manual Sheets API calls

Safe settings:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:5000/api/integrations/google-sheets/settings"
```

Save non-secret settings:

```powershell
$settingsBody = @{
  enabled = $true
  spreadsheet_id = "<SPREADSHEET_ID>"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Put `
  -Uri "http://127.0.0.1:5000/api/integrations/google-sheets/settings" `
  -ContentType "application/json" `
  -Body $settingsBody
```

Sync:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/integrations/google-sheets/sync"
```

### 12. Notifications: what Flask and Google do

The current project implements no Google push channel, webhook, Gmail email,
browser Notification API, or attendee invitation flow.

Actual flow:

1. Flask creates a standard Calendar event.
2. The service account authorizes the API request but does not notify the user.
3. The event payload defines no custom `reminders` and no attendees.
4. Google Calendar may apply calendar/user notification settings.
5. The user configures email, desktop, or Calendar alerts in Google Calendar.
6. Browser/OS permission for `calendar.google.com` is outside Flask.

Path:

```text
Google Calendar
→ Settings
→ Settings for my calendars
→ <Pomodoro calendar>
→ Event notifications
```

Alternatively, open the created event → `Edit` → add a notification.
Notification settings are personal; a shared editor cannot change another
user's preferences.

### 13. Troubleshooting

| Problem | Likely cause | Exact action |
| --- | --- | --- |
| Button disabled + `Fix Calendar ID` | Unsupported URL or embed URL without `src` | Use direct ID or a complete official embed URL with `src` |
| `Setup required` | ID or credentials blank | Fill both values and restart Flask |
| `No completed focus sessions` | Work did not complete / Reset / Skip | Complete work or create an artificial record |
| Latest UI record is a break | This is expected | Calendar selects latest `work`, not latest row overall |
| `not valid JSON` | Multiline/broken quoting | Re-compress JSON, single-quote it, restart |
| `invalid or incomplete` | Required fields missing / wrong credential type | Create a new JSON service-account key |
| `Failed to create... permissions` | API disabled, no sharing, wrong ID, network | Enable API, share with `client_email`, verify ID |
| Google `403` | Service account lacks writer access | Grant `Make changes to events`; inspect domain policy |
| Google `404` | Wrong/nonexistent Calendar ID | Copy ID again from target Calendar settings |
| `already synced` | Event marker is already stored | Complete a new work session; do not clear marker manually |
| Event time is wrong | Wrong app timezone | Save a valid IANA timezone and retry with new work |
| Event is not visible | Looking at another calendar/time | Open shared target calendar at session timestamp |
| No reminder | Flask defines no custom reminder | Configure Calendar/event notifications |
| Google package missing | Dependencies not fully installed | `pip install -r requirements.txt` |
| Sheets button disabled | Not enabled/saved/configured | Add server JSON, enable, enter ID, Save Settings |
| Sheets `403/404` | Sheet not shared / wrong ID | Share as Editor with `client_email`; recopy ID |
| Sheets header error | A1:I1 was changed | Use an empty sheet or restore exact headers |

Safe diagnostic without values:

```powershell
python -c "from app import create_app; from app.services.google_calendar_service import GoogleCalendarService; app=create_app(); ctx=app.app_context(); ctx.push(); s=GoogleCalendarService().get_status(); print({k:s[k] for k in ['configured','calendar_id_valid','calendar_id_normalized','missing','latest_work_session_id','latest_work_session_synced']})"
```

Database inspector:

```powershell
python scripts/check_database.py
```

### 14. Privacy and secret handling

- `.env` is already gitignored. Keep `service-account.json` outside the
  repository, or add its exact filename to the local Git exclude before the
  first `git add`.
- `.env.example` contains blank placeholders only.
- Never print raw credentials in terminal recordings or CI logs.
- Status endpoints do not return credentials.
- Sheets browser settings contain no private JSON.
- Calendar status can return a Calendar ID; do not expose a personal email in a
  public screenshot.
- Success API returns an external event ID/link; do not paste them into issues.
- Conflict response intentionally omits the external event ID.
- If compromised, delete the key in Google Cloud and create a replacement.
- For production, prefer Secret Manager and short-lived credentials / Workload
  Identity Federation where supported.

### 15. Data flow

```mermaid
flowchart LR
    A["Completed work countdown"] --> B["POST /api/sessions"]
    B --> C["WorkSession in SQLite"]
    C --> D["GET Calendar status"]
    D --> E{"Configured + unsynced work?"}
    E -- No --> F["Button remains disabled"]
    E -- Yes --> G["POST Calendar sync"]
    G --> H["Validate ID and credentials"]
    H --> I["Build timezone-aware event"]
    I --> J["Google Calendar events.insert"]
    J --> K["Store google_calendar_event_id"]
    K --> L["409 on repeated sync"]
```

### 16. Files and symbols: input, output, side effects, errors, caller

| Symbol | Type / file | Parameters | Return | Side effects | Errors | Caller |
| --- | --- | --- | --- | --- | --- | --- |
| `create_app` | function, `app/__init__.py` | optional config name | Flask app | loads env, registers extensions/routes, local migration | startup/config/database exceptions | `run.py`, tests, Gunicorn |
| `BaseConfig` | class, `app/config.py` | env at import/runtime | config attributes | none | invalid ints fall back safely | app factory |
| `_apply_runtime_environment` | function, `app/__init__.py` | Flask app | `None` | overlays env values | none for blank optional Google values | `create_app` |
| `WorkSession` | model, `app/models/work_session.py` | SQLAlchemy fields | ORM object | persists completed session and Calendar marker | DB constraints | services/repository |
| `SessionService.create_session` | method | completed payload dict | serialized session | insert + commit | validation, duplicate `409`, DB `400` | sessions POST / artificial command |
| `SessionService.delete_session` | method | integer ID | message dict | deletes one local row | `404` | sessions DELETE |
| `SessionRepository.get_latest_work_session` | method | none | model or `None` | none | DB errors | Calendar status/sync |
| `GoogleCalendarService.get_status` | method | none | safe status dict | DB read only | DB errors | GET status, sync precheck |
| `sync_latest_work_session` | method | optional timezone | sync result dict | Google insert + SQLite marker commit | `400`, `409` | POST sync |
| `_build_event_payload` | method | session, timezone | event dict | none | timezone validation from shared utility | sync service |
| `_build_calendar_service` | classmethod | none; reads config | Google client | parses private JSON, initializes client | missing dependency, invalid JSON/key | sync service only |
| `_missing_credential_fields` | classmethod | parsed object | list of field names | none | none | client builder/tests |
| `_is_calendar_id_valid` | classmethod | object | bool | none | none | status/sync |
| `_normalize_calendar_id` | classmethod | direct ID or URL | normalized ID or `None` | none | none | status/validation |
| `GoogleCalendarStatusResource.get` | route method | HTTP GET | `200` schema | DB read | API error handler | browser/status command |
| `GoogleCalendarSyncResource.post` | route method | JSON `{timezone?}` | `200` schema | delegates external/local write | `400/409` | browser/manual command |
| Browser `canSync` | function, `integrations.js` | status object | bool | none | none | status renderer/click guard |
| Browser `loadGoogleCalendarStatus` | async function | none | Promise | GET + DOM state | safe UI error | page load/session change |
| Browser `syncGoogleCalendar` | async function | none | Promise | POST + DOM state | safe UI error | Calendar click handler |
| `GoogleSheetsService.get_settings_payload` | method | none | safe settings dict | DB/config read | none for disabled flow | GET settings/UI |
| `update_settings` | method | enable + ID | safe settings dict | SQLite commit | missing/invalid configuration | PUT settings |
| `sync_completed_sessions` | method | none | counts/status dict | Sheets read/header/append | safe validation/external errors | POST Sheets sync |
| `_prepare_sheet` | method | values API, ID, rows | existing ID set | may write header | header mismatch | Sheets sync |

### 17. Automated and manual verification

```powershell
pytest tests/test_integrations_api.py -v
pytest tests/test_google_sheets_api.py tests/test_google_sheets_service.py -v
python -m compileall app scripts run.py
ruff check .
black --check .
pytest -v
flask --app run.py routes
python scripts/check_database.py
python run.py
```

Automated tests mock Google and cover a 10-second work session, newer-break
filtering, missing configuration, invalid credentials, successful payload,
external failure, duplicate prevention, secret non-leakage, and
Calendar/Sheets independence. A real event requires user-owned resources and is
not replaced by a mocked-success claim.

### 18. Official Google references

- [Enable Google Workspace APIs](https://developers.google.com/workspace/guides/enable-apis)
- [Create access credentials and service accounts](https://developers.google.com/workspace/guides/create-credentials)
- [Create and protect service-account keys](https://cloud.google.com/iam/docs/keys-create-delete)
- [Create Calendar events](https://developers.google.com/workspace/calendar/api/guides/create-events)
- [Calendar events.insert reference](https://developers.google.com/workspace/calendar/api/v3/reference/events/insert)
- [Share a Google Calendar](https://support.google.com/calendar/answer/37082)
- [Change Calendar notifications](https://support.google.com/calendar/answer/37242)
- [Google Sheets Python quickstart](https://developers.google.com/workspace/sheets/api/quickstart/python)
- [Google Sheets API limits](https://developers.google.com/workspace/sheets/api/limits)

### 19. Good next-prompt improvements

1. Add an explicit `GOOGLE_CALENDAR_ENABLED` with coordinated backend status,
   schema, exact Calendar UI state, and tests — not an env-only partial change.
2. Add `flask diagnose-google-integrations` that checks safe flags,
   dependencies, ID shape, and an optional confirmed read/write probe.
3. Let users choose a specific completed work session instead of latest only.
4. Add update/delete linkage between local sessions and existing Calendar events.
5. Add optional reminder fields to the event payload with clear UI/config.
6. Replace long-lived JSON keys with user OAuth or WIF/Secret Manager for
   production deployment.
7. Add mocked browser E2E coverage for all Calendar button states.
8. Add structured external error categories (`permission_denied`,
   `resource_not_found`, `api_disabled`) without leaking Google response bodies.
