# Конвеєр CI/CD — СвітлоЛьвів Lite (ЛР № 4)

Конфігурація: [`.github/workflows/ci-cd.yml`](../.github/workflows/ci-cd.yml). Запускається на кожен
push у будь-яку гілку, на pull request у `main`, на теги `v*` і вручну (workflow_dispatch).

```
 CI ┌────────────────────┐
    │ lint               │  ruff · black · bandit · xenon
    └─────────┬──────────┘
              ├──────────> ┌──────────────────┐   ┌───────────────────┐   ┌──────────────────────┐
    ┌─────────┴──────────┐ │ e2e (Playwright) │──>│ CD: docker → GHCR │──>│ CD: deploy-staging   │
    │ test               │ └──────────────────┘   └───────────────────┘   │ docker run + smoke   │
    │ збірка, unit+integ │                                                └──────────────────────┘
    │ покриття ≥ 90 %    │
    └────────────────────┘
```

| Стадія | Job | Що робить | Зупиняє конвеєр, якщо |
|---|---|---|---|
| CI | `lint` | ruff, black --check, bandit, xenon (складність ≤ B) | є зауваження аналізаторів |
| CI | `test` | встановлення залежностей, `compileall`, pytest unit + integration, звіти JUnit і coverage.xml | падає тест або покриття < 90 % |
| CI | `e2e` | Playwright + Chromium проти uvicorn, трасування невдалих тестів | падає e2e-тест |
| CD | `docker` | збірка образу, публікація `ghcr.io/<owner>/lab2:<sha>` і `:latest` / `:<тег>` | не збирається образ |
| CD | `deploy-staging` | запуск контейнера з опублікованого образу в environment `staging`, очікування `healthy`, smoke-тести | контейнер не стартує або падає smoke-тест |

На pull request виконується лише CI (без публікації образу та розгортання).

## Чому GitHub Actions

| Критерій | GitHub Actions | GitLab CI | Jenkins |
|---|---|---|---|
| Інтеграція з репозиторієм | вбудована (код уже на GitHub) | потрібне дзеркало або перенесення | вебхуки, плагін GitHub |
| Інфраструктура | хмарні runner’и GitHub | runner’и GitLab | власний сервер, підтримка, оновлення |
| Вартість для публічного репо | безкоштовно | безкоштовно з лімітом хвилин | безкоштовно, але потрібен сервер |
| Реєстр артефактів | GHCR через `GITHUB_TOKEN` | GitLab Container Registry | окремо (Nexus, Docker Hub) |
| Середовища та approvals | `environment` з правилами захисту | `environment` | плагіни |
| Готові дії | Marketplace (checkout, setup-python, docker/*) | шаблони | плагіни |
| Конфігурація | YAML у репозиторії | YAML у репозиторії | Jenkinsfile (Groovy) |

Висновок: для командного навчального проєкту на GitHub найменше накладних витрат дає GitHub Actions —
не потрібні сервер, окремі облікові записи чи секрети (образ публікується з `GITHUB_TOKEN`).

## Тестове середовище (staging)

Job `deploy-staging` прив’язаний до GitHub environment `staging`: завантажує зібраний артефакт
(образ з GHCR, а не вихідний код), запускає контейнер так само, як на сервері, чекає на
`HEALTHCHECK` і проганяє `tests/smoke`. Середовище живе протягом job’а — цього достатньо для
перевірки розгортання без платного хостингу. Для постійного staging той самий образ можна
розгорнути на Render / Fly.io / VPS, змінивши лише крок «Розгорнути контейнер».

## Демонстрація невдалого запуску

Гілка `demo/failing-test` містить навмисну регресію (поріг агрегації репортів 2 замість 3).
На push у цю гілку `lint` проходить, `test` падає на `test_below_threshold_actual_is_unknown`,
а `e2e`, `docker` і `deploy-staging` отримують статус *skipped* — неперевірений код не потрапляє
ні в реєстр, ні в тестове середовище.

## Захист гілки main

Settings → Branches → Add branch ruleset для `main`: Require a pull request before merging,
Require status checks to pass — `CI · Статичний аналіз`, `CI · Збірка, модульні та інтеграційні тести`,
`CI · E2E-тести (Playwright)`. Після цього PR з гілки `demo/failing-test` неможливо злити.

## Локальний прогін тих самих перевірок

```bash
pip install -r requirements-dev.txt -r requirements-bot.txt
ruff check . && black --check . && bandit -q -r app bot && xenon --max-absolute B app bot
pytest tests/unit tests/integration --cov=app --cov=bot --cov-fail-under=90
pytest tests/e2e
docker build -t svitlolviv . && docker run -d -p 8000:8000 svitlolviv
BASE_URL=http://127.0.0.1:8000 pytest tests/smoke -v
```
