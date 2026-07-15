# Покрокове створення Pomodoro Work Tracker на Flask

## 1. З чого почалося створення проєкту

- Проєкт стартував з порожньої директорії.
- Спочатку було створено базову структуру папок `app/`, `tests/`, `docs/`, `migrations/`.
- Це дозволило одразу будувати Flask-проєкт як багатофайлову систему, а не як один скрипт.
- Автоматична перевірка етапу: створення файлової структури.
- Ручна перевірка: переконатися, що є `app`, `tests`, `docs`, `migrations`.
- Типова помилка: почати писати маршрути до того, як визначено структуру шарів.

## 2. Чому для проєкту обрано Flask

- Flask достатньо легкий для навчального проєкту й не ховає базові механізми за надмірною магією.
- На цьому проєкті добре видно application factory, Blueprint, Jinja, request-flow і розширення.
- Flask дозволяє окремо показати серверний HTML і REST API.
- Ручна перевірка: відкрити `app/__init__.py`, `app/config.py`, `app/blueprints/`.

## 3. Створення структури папок

- Було створено окремі каталоги для моделей, репозиторіїв, сервісів, API-схем, Blueprints, шаблонів, static-файлів і тестів.
- Задіяні файли: вся верхня структура проєкту, `AGENTS.md`, компактні `docs/*`.
- Flask-концепція: розділення відповідальностей до написання бізнес-логіки.
- Перевірка: переглянути структуру проєкту або командою `Get-ChildItem -Recurse`.
- Типова помилка: змішувати HTML, SQL і бізнес-логіку в одному файлі.

## 4. Створення Flask application factory

- У `app/__init__.py` створено `create_app()`.
- Там підтягується конфігурація, підключаються розширення, маршрути й error handlers.
- Це демонструє application-factory pattern.
- Команда перевірки: `flask --app run.py routes`.
- Успішний результат: у списку є `/`, `/calendar`, `/api/health`, `/api/docs`.
- Типова помилка: створювати глобальний `Flask(__name__)` і прив’язувати все до нього напряму.

## 5. Створення конфігурації

- У `app/config.py` створено `BaseConfig`, `DevelopmentConfig`, `TestingConfig`, `ProductionConfig`.
- Конфігурація читає `SECRET_KEY`, `DATABASE_URL`, `DEFAULT_TIMEZONE`, `ENABLE_TEST_DURATIONS`, `DEBUG`.
- Flask-концепція: конфігурація через класи й environment variables.
- Перевірка: `python -c "from app import create_app; app = create_app('production'); print(app.config['ENV_NAME'])"`.
- Успішний результат: `production`.

## 6. Підключення Flask-SQLAlchemy

- У `app/extensions.py` створено `db = SQLAlchemy()`.
- У factory цей об’єкт ініціалізується через `db.init_app(app)`.
- Це дозволяє моделям імпортувати `db`, не тягнучи весь Flask app.
- Перевірка: `python -m compileall app`.
- Типова помилка: імпортувати app усередині моделей і отримати circular import.

## 7. Підключення Flask-Migrate

- У `app/extensions.py` додано `migrate = Migrate()`.
- У factory є `migrate.init_app(app, db)`.
- Flask-концепція: інтеграція Alembic через Flask-Migrate.
- Перевірка: `flask --app run.py db init`, `flask --app run.py db migrate -m "Initial migration"`, `flask --app run.py db upgrade`.
- Успішний результат: створений каталог `migrations/` і початкова міграція.

## 8. Створення моделей бази даних

- Створено `app/models/work_session.py` і `app/models/user_settings.py`.
- `work_sessions` зберігає завершені сесії, `user_settings` — конфігурацію користувача.
- `client_session_id` має унікальне обмеження для захисту від дублювання.
- Перевірка: `flask --app run.py db upgrade`.
- Типова помилка: намагатися зберігати щосекундний стан таймера в базу.

## 9. Створення repository layer

- Створено `SessionRepository` і `SettingsRepository`.
- Вони інкапсулюють SQLAlchemy-запити й не займаються HTML або API-валідацією.
- Flask-концепція: thin routes + repository abstraction.
- Ручна перевірка: прочитати `app/repositories/session_repository.py`.
- Типова помилка: писати SQLAlchemy-запити безпосередньо в маршрутах.

## 10. Створення service layer

- Створено сервіси для таймера, сесій, статистики, календаря, налаштувань і CSV.
- Там зосереджено правила UTC-конвертації, фільтрації, duplicate prevention і обчислення агрегацій.
- Flask-концепція: service layer поверх repositories.
- Перевірка: `pytest -v`.
- Успішний результат: проходять тести `tests/test_services.py`.

## 11. Створення Flask Blueprints

- Створено окремі Blueprints для pages, health, sessions, statistics, calendar, settings, export.
- Це розбиває HTTP-поверхню на логічні модулі.
- Команда перевірки: `flask --app run.py routes`.
- Успішний результат: маршрути згруповані за Blueprint-ами.
- Типова помилка: тримати весь routing в одному `routes.py`.

## 12. Створення REST API

- Реалізовано JSON API для сесій, статистики, календаря, налаштувань і health.
- Задіяні файли: `app/blueprints/*/routes.py`, `app/services/*`.
- Flask-концепція: MethodView + Flask-Smorest.
- Перевірка: `pytest -v`.
- Ручна перевірка: відкрити `/api/health`, `/api/settings`, `/api/statistics/today`.

## 13. Створення OpenAPI та Swagger UI

- Налаштування OpenAPI й Swagger UI додані в `app/config.py`.
- `flask-smorest` автоматично публікує `/api/openapi.json` та `/api/docs`.
- Команда перевірки: `flask --app run.py routes`.
- Ручна перевірка: відкрити `http://127.0.0.1:5000/api/docs`.
- Типова помилка: змішувати кілька бібліотек документації API одночасно.

## 14. Створення Jinja templates

- Створено `base.html`, `index.html`, `statistics.html`, `calendar.html` і компонентні шаблони.
- Jinja використовується лише для структури сторінки, а не для бази даних.
- Flask-концепція: серверний HTML через templates.
- Ручна перевірка: відкрити `/`, `/statistics`, `/calendar`.

## 15. Підключення CSS і JavaScript

- Додано `styles.css`, `responsive.css`, `api.js`, `settings.js`, `timer.js`, `statistics.js`, `calendar.js`, `theme.js`.
- CSS реалізує light/dark/system themes і адаптивність.
- JS реалізує таймер, localStorage, API-виклики, графік і календар.
- Ручна перевірка: перевірити на сторінці підключення CSS/JS у HTML.

## 16. Реалізація Pomodoro-таймера

- Логіка активного таймера винесена у `app/static/js/timer.js`.
- `PomodoroTimerService` в Python використовується як чиста бізнес-модель для тестів правил.
- Команди перевірки: `pytest -v`.
- Ручна перевірка: `Start`, `Pause`, `Resume`, `Reset`.
- Типова помилка: робити довгі блокуючі цикли всередині Flask-маршрутів.

## 17. Збереження стану в localStorage

- Активний таймер зберігається у ключі `pomodoro.timerState`.
- Це дозволяє відновити countdown після reload.
- Flask-концепція: розмежування клієнтського й серверного стану.
- Ручна перевірка: запустити таймер, оновити сторінку, перевірити відновлення.

## 18. Збереження завершеної сесії

- Після завершення фронтенд надсилає `POST /api/sessions`.
- `SessionService` перевіряє payload і зберігає його через repository.
- Унікальний `client_session_id` блокує дублікати.
- Перевірка: `pytest -v`.
- Ручна перевірка: завершити коротку сесію та перевірити статистику.

## 19. Реалізація статистики

- `StatisticsService` рахує метрики за день, тиждень, місяць і 7-денний графік.
- UTC-часи конвертуються в обрану часову зону.
- Команда перевірки: `pytest -v`, `pytest --cov=app --cov-report=term-missing`.
- Ручна перевірка: `/statistics` і `/api/statistics/*`.

## 20. Реалізація календаря

- `CalendarService` повертає summary для місяця і деталі для конкретної дати.
- `calendar.js` рендерить grid і список сесій для вибраного дня.
- Ручна перевірка: `/calendar`, клік по даті.
- Типова помилка: будувати календар прямо в SQL без коректної timezone-конвертації.

## 21. Реалізація CSV export

- `CSVExportService` формує CSV у пам’яті через `io.StringIO` і `csv.writer`.
- Маршрут `/api/export/sessions.csv` повертає файл із заголовком `Content-Disposition`.
- Перевірка: `pytest -v`.
- Ручна перевірка: натиснути `Експорт CSV`.

## 22. Створення міграцій

- Flask-Migrate згенерував Alembic-середовище в `migrations/`.
- Початкова міграція створює `user_settings` і `work_sessions`.
- Команди перевірки: `flask --app run.py db migrate -m "Initial migration"`, `flask --app run.py db upgrade`.
- Успішний результат: upgrade проходить без помилок.

## 23. Написання тестів

- Написані тести для app factory, сторінок, health API, sessions API, statistics API, calendar API, settings API, export API і service layer.
- Flask-концепція: ізольований test app + Flask test client.
- Команди перевірки: `pytest -v`, `pytest --cov=app --cov-report=term-missing`.
- Успішний результат: `27 passed`, `90% coverage`.

## 24. Налаштування Docker

- Додано `Dockerfile` і `start.sh`.
- У production-start flow спочатку застосовуються міграції, потім стартує Gunicorn.
- Ручна перевірка: `docker build -t pomodoro-work-tracker .` у Docker-сумісному середовищі.
- У цьому сеансі Docker build не запускався.

## 25. Налаштування Render

- Додано `render.yaml` для Python web service.
- Health-check спрямований на `/api/health`.
- `DATABASE_URL` винесено в env vars, тому БД можна замінити без зміни коду.
- У цьому сеансі Render-деплой не виконувався.

## 26. Фінальна перевірка

- Виконано: `python -m compileall app run.py wsgi.py`.
- Виконано: `ruff check .`.
- Виконано: `black --check .`.
- Виконано: `pytest -v`.
- Виконано: `pytest --cov=app --cov-report=term-missing`.
- Виконано: `flask --app run.py routes`.
- Виконано: `flask --app run.py db upgrade`.
- Виконано: локальний HTTP smoke check через `Invoke-RestMethod`.
- Виконано: `python -c "from app import create_app; app = create_app('production'); print(app.config['ENV_NAME'])"`.
- Не пройшло на Windows: `gunicorn --check-config "app:create_app()"` через відсутність `fcntl`.

## 27. Майбутні покращення

- PostgreSQL-перевірка в Linux-контейнері або CI;
- реальний Render-деплой із публічною URL;
- браузерна e2e-перевірка;
- автентифікація користувачів;
- реальна інтеграція з Google Calendar;
- додаткові аналітичні звіти.
