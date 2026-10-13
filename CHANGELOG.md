# Changelog

## v0.1 — Ітерація 1
- Каркас FastAPI + SQLAlchemy/SQLite, pytest із тимчасовою БД (SVL-8, SVL-9)
- Формат і фікстури графіків 6 черг (SVL-13)
- `GET /queue` — черга за адресою, 404 для невідомої (SVL-10)
- `GET /streets` — автопідказка вулиць (SVL-11)
- Парсер інтервалів з перетином опівночі (SVL-12)

## v0.2 — Ітерація 2
- `POST /schedules/import` з виявленням змінених черг, `GET /schedule/{queue}` (SVL-14)
- `GET /status`: planned on/off, next_change (SVL-15), next_outage і minutes_to_outage (SVL-16)
- `POST /subscriptions`, `GET /notifications/due` — сповіщення за 15/30/60 хв у вікні ±2 хв (SVL-17)
- Тихі години 23:00–07:00 (SVL-18)
- Модульні та інтеграційні тести, покриття 98 % (SVL-25, SVL-26)

## v1.0 — Ітерація 3
- `POST /reports` — репорт «Світло є / немає» (SVL-19)
- Агрегація: ≥ 3 однакових репорти з вулиці за 30 хв → поле `actual` у `/status` (SVL-20)
- Антиспам: 1 репорт від user_id на адресу за 10 хв, інакше 429 (SVL-21)
- Веб-сторінка `/` з автопідказкою, графіком, індикатором і кнопками репорту (SVL-22, SVL-23)
- Telegram-бот на aiogram 3: `/start`, `/address`, `/status` (SVL-24)
- E2E-тести Playwright, звіт про тестування (SVL-27, SVL-28)
