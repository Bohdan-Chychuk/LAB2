# СвітлоЛьвів Lite

Сервіс для мешканців Львова: черга відключень за адресою, графік на сьогодні, поточний статус світла,
сповіщення перед відключенням і краудсорсингові репорти «Світло є / немає».

Лабораторна робота №2 «Методології розробки ПЗ» — Extreme Programming (TDD, парне програмування,
малі релізи, спільний стандарт коду). Специфікація: [CLAUDE_CODE_SPEC.md](CLAUDE_CODE_SPEC.md),
беклог Jira: [svitlolviv_xp_jira.csv](svitlolviv_xp_jira.csv).

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (Linux/macOS: source .venv/bin/activate)
pip install -r requirements-dev.txt
uvicorn app.main:create_app --factory --reload
```

Відкрити http://127.0.0.1:8000/ (Swagger — http://127.0.0.1:8000/docs).

## API

| Метод | Шлях | Опис |
|---|---|---|
| GET | `/streets?q=` | автопідказка вулиць (до 10) |
| GET | `/queue?street=&house=` | черга за адресою або 404 |
| POST | `/schedules/import` | імпорт графіка, повертає `changed_queues` |
| GET | `/schedule/{queue}` | інтервали відключень на сьогодні |
| GET | `/status?street=&house=&now=` | planned, next_change, next_outage, minutes_to_outage |
| POST | `/subscriptions` | підписка: user_id, адреса, notify_before 15/30/60, quiet_hours |
| GET | `/notifications/due?now=` | кому надіслати сповіщення зараз (±2 хв) |
| POST | `/reports?now=` | репорт user_id + адреса + status on/off; 429 при спамі |
| GET | `/` | веб-сторінка |

Параметр `now` (ISO-дата) необов'язковий — за замовчуванням поточний час; потрібен для демо й тестів.

## Тести

```bash
pytest tests/unit tests/integration --cov=app --cov-report=term-missing
playwright install chromium   # один раз
pytest tests/e2e
```

Звіт: [docs/TEST_REPORT.md](docs/TEST_REPORT.md) — 102 тести, покриття `app` 99 %.

## Telegram-бот (опційно)

```bash
pip install -r requirements-bot.txt
set SVL_BOT_TOKEN=<токен від @BotFather>   # Linux/macOS: export SVL_BOT_TOKEN=...
python -m bot.bot
```

## Структура

```
app/
  main.py, db.py, models.py, seed.py
  services/   addresses, parser, schedules, status, notifications, reports — чисті функції з now
  api/routes.py
  web/templates/index.html
bot/          aiogram-адаптер над services
data/         адреси (~30) і графіки 6 черг
tests/        unit / integration / e2e
docs/         PLANNING.md (Planning Game, XP-практики), TEST_REPORT.md
```

## XP-процес

Ітерації, оцінки та практики — [docs/PLANNING.md](docs/PLANNING.md). Кожен коміт містить ключ Jira
(`SVL-10: red — ...`, `SVL-10: green — ...`), релізи позначені тегами `v0.1`, `v0.2`, `v1.0`.

## Стандарт коду

```bash
ruff check . && black --check .
```
