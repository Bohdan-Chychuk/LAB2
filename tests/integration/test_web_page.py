def test_index_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    html = response.text
    assert "СвітлоЛьвів" in html
    assert 'name="viewport"' in html
    for element_id in ("street", "house", "queue", "schedule", "status-indicator", "actual"):
        assert f'id="{element_id}"' in html
