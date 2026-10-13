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

## Тести

```bash
pytest tests/unit tests/integration --cov=app --cov-report=term-missing
```

## Стандарт коду

```bash
ruff check . && black --check .
```
