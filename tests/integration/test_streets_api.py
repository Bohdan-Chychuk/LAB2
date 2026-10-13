def test_streets_autocomplete(client):
    response = client.get("/streets", params={"q": "Шев"})
    assert response.status_code == 200
    assert response.json() == ["Шевченка"]


def test_streets_autocomplete_at_most_ten(client):
    response = client.get("/streets", params={"q": "а"})
    assert response.status_code == 200
    assert 0 < len(response.json()) <= 10
