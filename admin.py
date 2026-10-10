"""Painel /admin: edita o conteúdo do site sem novo deploy.

Defina a variável ADMIN_PASSWORD para ativar. Sem ela, o painel fica desligado.
"""
import hashlib
import hmac
import json
import os
import time
from functools import wraps

from flask import Blueprint, Response, abort, jsonify, redirect, render_template, request, session

import store
from icons import GLYPHS

bp = Blueprint("admin", __name__, url_prefix="/admin")
_fails = {}  # ip -> [contagem, início da janela]


def password():
    return os.environ.get("ADMIN_PASSWORD", "")


def secret_key():
    return os.environ.get("SECRET_KEY") or hashlib.sha256(("beacons-admin:" + password()).encode()).hexdigest()


def authed():
    return session.get("ok") is True


def api(fn):
    @wraps(fn)
    def w(*a, **k):
        if not password():
            abort(404)
        if not authed():
            return jsonify(error="Sessão expirada. Entre de novo."), 401
        if request.method == "POST" and request.headers.get("X-Requested-With") != "fetch":
            abort(400)
        return fn(*a, **k)
    return w


@bp.after_request
def headers(resp):
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resp


@bp.get("/")
def index():
    if not password():
        return render_template("admin.html", mode="off"), 503
    return render_template("admin.html", mode="app" if authed() else "login", error=None)


@bp.post("/login")
def login():
    if not password():
        abort(404)
    ip = request.remote_addr or "?"
    n, t0 = _fails.get(ip, [0, time.time()])
    if time.time() - t0 > 600:
        n, t0 = 0, time.time()
    if n >= 5:
        return render_template("admin.html", mode="login", error="Muitas tentativas. Aguarde alguns minutos."), 429
    given = request.form.get("password", "")
    if hmac.compare_digest(given.encode(), password().encode()):
        _fails.pop(ip, None)
        session.clear()
        session["ok"] = True
        session.permanent = True
        return redirect("/admin/")
    _fails[ip] = [n + 1, t0]
    time.sleep(0.6)
    return render_template("admin.html", mode="login", error="Senha incorreta."), 401


@bp.post("/logout")
@api
def logout():
    session.clear()
    return jsonify(ok=True)


@bp.get("/data")
@api
def data():
    return jsonify(data=store.load(), defaults=store.defaults(), glyphs=list(GLYPHS), persistent=store.persistent())


@bp.post("/save")
@api
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
@api
def reset():
    store.reset()
    return jsonify(ok=True, data=store.load())


@bp.get("/backup")
@api
def backup():
    body = json.dumps(store.load(), ensure_ascii=False, indent=2)
    return Response(body, mimetype="application/json",
                    headers={"Content-Disposition": "attachment; filename=beacons-conteudo.json"})
