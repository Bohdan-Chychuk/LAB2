# СвітлоЛьвів Lite — специфікація для Claude Code

Лабораторна робота №2 з дисципліни «Методології розробки ПЗ»: розробка за Extreme Programming.
Кожна user story робиться через TDD: спершу тест (Red), потім мінімальний код (Green), потім рефакторинг.
Один коміт на крок, у повідомленні коміту — ключ Jira: `SVL-10: red — тест визначення черги`.

## Стек
- Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2 + SQLite, Jinja2
- pytest, pytest-cov, httpx (TestClient), Playwright (pytest-playwright)
- ruff + black (спільний стандарт кодування)
- Опційно: aiogram 3 для Telegram-бота (тонкий адаптер над services/)

## Структура
```
app/
  main.py            # FastAPI app, підключення роутерів і шаблонів
  db.py              # engine, SessionLocal, Base
  models.py          # Address, Schedule, Subscription, Report
  services/
    addresses.py     # find_queue(street, house), suggest_streets(q)
    parser.py        # parse_intervals("08:00-12:00, 16:00-20:00") -> list[(time, time)]
    schedules.py     # import_schedule(json) -> changed_queues, diff з попередньою версією
    status.py        # is_power_on(queue, dt), next_outage(queue, dt), next_change(queue, dt)
    notifications.py # due_notifications(now) з урахуванням N хв і тихих годин
    reports.py       # add_report(...), actual_status(street, now) — поріг 3 за 30 хв, антиспам 10 хв
  api/routes.py      # REST-ендпоінти
  web/templates/index.html
data/
  addresses.json     # ~30 адрес Львова з чергами 1–6
  schedules/today.json, schedules/changed.json
bot/bot.py           # опційно
tests/
  unit/ integration/ e2e/
```

Сервіси — чисті функції, час передається параметром `now` (без datetime.now() всередині), щоб тести були детермінованими.

## API
| Метод | Шлях | Що робить |
|---|---|---|
| GET | /streets?q= | автопідказка, до 10 вулиць |
| GET | /queue?street=&house= | номер черги або 404 |
| POST | /schedules/import | імпорт JSON графіка, повертає changed_queues |
| GET | /schedule/{queue} | інтервали на сьогодні |
| GET | /status?street=&house=&now= | planned (on/off), next_change, next_outage, minutes_to_outage, actual |
| POST | /subscriptions | user_id, адреса, notify_before (15/30/60), quiet_hours |
| GET | /notifications/due?now= | кому треба надіслати сповіщення (вікно ±2 хв) |
| POST | /reports | user_id, адреса, status (on/off); 429 при спамі |
| GET | / | веб-сторінка |

## Веб-сторінка
Поле адреси з автопідказкою → черга, таблиця графіка на сьогодні, поточний статус (великий індикатор),
кнопки «Світло є» / «Світла немає», поле user_id (для демо). Адаптивна верстка.

## Тести (мінімум по одному кожного виду, краще більше)
- **Модульні** (`tests/unit`): parse_intervals (звичайний, перетин опівночі, некоректний рядок),
  is_power_on / next_outage (зараз є світло, зараз немає, відключення завтра, без відключень),
  due_notifications (потрапляє у вікно, тихі години), actual_status (менше порогу, поріг досягнуто, старі репорти не рахуються), антиспам.
- **Інтеграційні** (`tests/integration`): TestClient + тимчасова SQLite.
  Імпорт графіка → GET /status повертає очікуваний стан; повторний імпорт зміненого графіка → changed_queues містить змінену чергу.
- **E2E** (`tests/e2e`): Playwright запускає uvicorn у фікстурі, відкриває /, вводить адресу,
  перевіряє графік, натискає «Світла немає» від трьох user_id, перевіряє, що фактичний стан став «немає».

Цільове покриття — не менше 70 %. Команди:
```
pytest tests/unit tests/integration --cov=app --cov-report=term-missing
pytest tests/e2e
```

## Порядок роботи (ітерації XP)
1. Ітерація 1: SVL каркас, pytest, черга за адресою, автопідказка, парсер → tag v0.1
2. Ітерація 2: diff графіків, статус, наступне відключення, сповіщення, тихі години, unit + integration → tag v0.2
3. Ітерація 3: репорти, агрегація, антиспам, веб-сторінка, e2e, (бот) → tag v1.0
