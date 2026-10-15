"""API for nexus-dash: the dash hosts the content editor, this service stores the content.

Server to server only: Authorization: Bearer $DASH_API_TOKEN (constant-time comparison). Without the variable the
whole API answers 404, so it is off by default. Validation is the same store.save() the legacy /admin used.
"""
import hmac
import json
import os
from functools import wraps

from flask import Blueprint, Response, abort, jsonify, request

import store
from icons import GLYPHS

bp = Blueprint("dash_api", __name__, url_prefix="/api/dash")


def _token():
    return os.environ.get("DASH_API_TOKEN", "").strip()


def guarded(fn):
    @wraps(fn)
    def wrapper(*a, **k):
        expected = _token()
        if not expected:
            abort(404)
        auth = request.headers.get("Authorization", "")
        given = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
        if not given or not hmac.compare_digest(given.encode(), expected.encode()):
            return jsonify(error="forbidden"), 403
        return fn(*a, **k)
    return wrapper


@bp.after_request
def headers(resp):
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resp


@bp.get("/content")
@guarded
def content():
    return jsonify(data=store.load(), defaults=store.defaults(), glyphs=list(GLYPHS), persistent=store.persistent())


@bp.post("/content")
@guarded
def save():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify(error="JSON inválido"), 400
    try:
        clean = store.save(body)
    except ValueError as e:
        return jsonify(error=str(e)), 422
    except OSError:
        return jsonify(error="Não consegui gravar o arquivo no servidor."), 500
    return jsonify(ok=True, data=clean)


@bp.post("/reset")
@guarded
def reset():
    store.reset()
    return jsonify(ok=True, data=store.load())


@bp.get("/backup")
@guarded
def backup():
    return Response(json.dumps(store.load(), ensure_ascii=False, indent=2), mimetype="application/json",
                    headers={"Content-Disposition": "attachment; filename=beacons-conteudo.json"})
