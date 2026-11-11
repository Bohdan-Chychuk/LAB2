def test_index_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    html = response.text
    assert "СвітлоЛьвів" in html
    assert 'name="viewport"' in html
    for element_id in ("street", "house", "queue", "schedule", "status-indicator", "actual"):
        assert f'id="{element_id}"' in html


def test_index_page_has_report_buttons(client):
    html = client.get("/").text
    for element_id in ("user-id", "btn-on", "btn-off", "report-message"):
        assert f'id="{element_id}"' in html
    assert "Світло є" in html and "Світла немає" in html


def test_static_assets_are_served(client):
    html = client.get("/").text
    assert '<link rel="stylesheet" href="/static/style.css">' in html
    assert '<script src="/static/app.js" defer></script>' in html
    js = client.get("/static/app.js")
    assert js.status_code == 200 and "javascript" in js.headers["content-type"]
    assert ".innerHTML" not in js.text
    assert client.get("/static/style.css").status_code == 200
