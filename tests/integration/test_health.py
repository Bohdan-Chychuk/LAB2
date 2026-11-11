def test_app_starts_and_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_engine_is_disposed_on_shutdown(db_url):
    from fastapi.testclient import TestClient
    from sqlalchemy import event

    from app.main import create_app

    app = create_app(db_url)
    closed = []
    event.listen(app.state.engine.pool, "close", lambda *_: closed.append(1))
    with TestClient(app) as client:
        client.get("/queue", params={"street": "Шевченка", "house": "10"})
    assert closed, "пул з’єднань має закриватися при зупинці застосунку"
