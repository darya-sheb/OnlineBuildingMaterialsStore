def test_health(sync_client):
    r = sync_client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

