import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

TOKEN = "dash-test-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DASH_API_TOKEN", TOKEN)
    import importlib

    import app as app_module
    importlib.reload(app_module)
    return app_module.app.test_client()


def test_off_without_a_token_and_closed_to_wrong_ones(client, monkeypatch):
    assert client.get("/api/dash/content").status_code == 403
    assert client.get("/api/dash/content", headers={"Authorization": "Bearer nope"}).status_code == 403
    assert client.post("/api/dash/reset", headers={"Authorization": "Bearer nope"}).status_code == 403
    monkeypatch.delenv("DASH_API_TOKEN")
    assert client.get("/api/dash/content", headers=AUTH).status_code == 404  # fail closed: the API does not exist


def test_read_save_validate_reset_backup(client):
    r = client.get("/api/dash/content", headers=AUTH)
    assert r.status_code == 200
    body = r.get_json()
    assert set(body) >= {"data", "defaults", "glyphs", "persistent"}
    data = body["data"]
    data["email"] = "hello@example.com"
    ok = client.post("/api/dash/content", headers=AUTH, json=data)
    assert ok.status_code == 200 and client.get("/api/dash/content", headers=AUTH).get_json()["data"]["email"] == "hello@example.com"
    bad = dict(data, links=dict(data["links"], twitch="javascript:alert(1)"))
    assert client.post("/api/dash/content", headers=AUTH, json=bad).status_code == 422  # only http(s) links
    assert client.post("/api/dash/content", headers=AUTH, data="not json", content_type="application/json").status_code == 400
    assert json.loads(client.get("/api/dash/backup", headers=AUTH).data)["email"] == "hello@example.com"
    assert client.post("/api/dash/reset", headers=AUTH).status_code == 200


def test_public_pages_and_the_panel_editor(client):
    assert client.get("/").status_code == 200
    r = client.get("/editor-paineis")
    html = r.get_data(as_text=True)
    assert r.status_code == 200 and r.headers["X-Robots-Tag"] == "noindex, nofollow"
    assert "<script>" not in html and "/static/editor-paineis/editor.js" in html
    assert client.get("/static/editor-paineis/editor.js").status_code == 200
