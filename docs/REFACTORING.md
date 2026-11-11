# Рефакторинг — СвітлоЛьвів Lite v1.1 (ЛР № 3)

Аналіз коду v1.0: `radon` (цикломатична складність, індекс підтримуваності), `ruff --select ALL`,
`bandit`, ручне код-рев’ю і прогін тестів з `-W default`. Кожен недолік заведено окремою задачею
в Jira (епік «Рефакторинг (ЛР3)») і усунено окремим комітом `SVL-xx: red/green/refactor`.

| Jira | Недолік v1.0 | Категорія | Спосіб усунення |
|---|---|---|---|
| SVL-34 | `datetime.now()` без часового поясу (4 місця): у Docker/CI (UTC) статус зсунутий на 2–3 год | Дефект | `app/clock.py` (Europe/Kyiv), залежність `NowDep`, `tzdata` |
| SVL-35 | Логіка статусу продубльована в `routes.get_status` і `bot.texts.status_text` | Дублювання | Extract Function `address_status()` → `AddressStatus` |
| SVL-36 | Магічні рядки `"on"`/`"off"` у 5 модулях | Магічні значення | `PowerState(StrEnum)` |
| SVL-37 | `get_address`/`suggest_streets` читають усю таблицю і фільтрують у Python | Продуктивність | Індексовані `street_key`/`house_key`, фільтр і LIMIT у SQL |
| SVL-38 | Ручна валідація графіка через `except (KeyError, AttributeError…)`; `{"1": 5}` → 500 | Дефект, обробка помилок | Pydantic-схема `ScheduleIn` (422 + опис у Swagger) |
| SVL-39 | Відповіді API — довільні `dict`, OpenAPI не описує формати | Контракт API | `app/api/schemas.py`, response models |
| SVL-40 | Хак `dict(zip(…, format_intervals([i]).split("-")))` | Неочевидний код | `format_interval()` |
| SVL-41 | Пул з’єднань SQLite не закривається (27 ResourceWarning у тестах) | Витік ресурсів | `lifespan` + `engine.dispose()`, ResourceWarning = помилка |
| SVL-42 | Ініціалізація БД продубльована в `main.py` і `bot.py`; бот створює БД під час імпорту, глобальний стан | Дублювання, глобальний стан | `app/bootstrap.init_database()`, DI через `workflow_data` aiogram |
| SVL-43 | `add_report` має 6 позиційних параметрів (PLR0913/PLR0917) | Довгий список параметрів | Introduce Parameter Object `NewReport` |
| SVL-44 | `actual_status` — CC 9, три відповідальності в одній функції | Складність | Decompose: `_recent_reports`, `_latest_per_user`, `_decide` |
| SVL-45 | 216-рядковий шаблон з inline CSS/JS; дані з сервера вставляються через `innerHTML` (XSS) | Безпека, розділення відповідальностей | `app/web/static/{style.css,app.js}`, DOM API замість `innerHTML` |

## Метрики до / після

| Метрика | v1.0 | v1.1 |
|---|---|---|
| Зауваження `ruff --select ALL` | 6 | 0 |
| Функції зі складністю ≥ B (radon) | 5 (макс. 9) | 3 (макс. 6) |
| Середня цикломатична складність | 2,47 | 1,91 |
| Індекс підтримуваності `routes.py` | 40,5 | 46,7 |
| ResourceWarning під час тестів | 27 | 0 |
| Відповідей 500 на некоректний графік | так | ні (422) |
| Рядків у `index.html` | 216 | 54 (+ `app.js`, `style.css`) |
| Тестів | 102 | 135 |
| Покриття `app` + `bot` | 99 % (бот не враховано) | 99 % |

Після оновлення локальну БД треба створити заново (видалити `svitlolviv.db`): у таблиці
`addresses` з’явилися стовпці `street_key` і `house_key`.
