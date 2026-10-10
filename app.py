"""Nexus Beacons: páginas de links do Tiger, em Flask + Jinja2.

Rodar local:   python app.py            (http://127.0.0.1:5000)
Produção:      gunicorn app:app
Site estático: python build.py          (gera a pasta dist/)
"""
import hashlib
import os
import re

from flask import Flask, render_template, redirect, request
from markupsafe import Markup
from werkzeug.middleware.proxy_fix import ProxyFix

import content as C
import store
import admin
from icons import ICONS, GLYPHS

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)  # atrás do proxy do Railway/Cloudflare
app.secret_key = admin.secret_key()
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=bool(os.environ.get("RAILWAY_PROJECT_ID") or os.environ.get("RAILWAY_ENVIRONMENT_NAME")),
    PERMANENT_SESSION_LIFETIME=14 * 24 * 3600,
    MAX_CONTENT_LENGTH=256 * 1024,
)
app.jinja_env.globals.update(
    PAGES=C.PAGES,
    ICONS={k: Markup(v) for k, v in ICONS.items()},
    GLYPHS={k: Markup(v) for k, v in GLYPHS.items()},
)
app.jinja_env.filters["short"] = lambda u: re.sub(r"^https?://(www\.)?", "", u or "").rstrip("/")
app.register_blueprint(admin.bp)


@app.context_processor
def content_vars():
    """Conteúdo editável: relido do disco quando o arquivo muda, sem reiniciar."""
    d = store.load()
    return dict(SITE=d["site"], LINKS=d["links"], EMAIL=d["email"], DISCORD_USER=d["discord_user"])


def page(template, key):
    return render_template(template, p=store.load()["pages"][key], current=key)

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")


@app.route("/")
def sobre(): return page("sobre.html", "sobre")

@app.route("/setup")
def setup(): return page("setup.html", "setup")

@app.route("/horarios")
def horarios(): return page("horarios.html", "horarios")

@app.route("/contatos")
def contatos(): return page("contatos.html", "contatos")

@app.route("/etc")
def etc(): return page("etc.html", "etc")

@app.route("/sobre")
def sobre_alias(): return redirect("/", code=301)

@app.after_request
def cache(resp):
    # HTML sempre revalida (ETag): edições do /admin aparecem na hora e o 304 continua barato.
    if resp.mimetype == "text/html" and not request.path.startswith("/admin") and resp.status_code == 200:
        resp.headers["Cache-Control"] = "no-cache"
        resp.set_etag(f"{store.version()}-{hashlib.md5(resp.get_data()).hexdigest()[:12]}")
        resp.make_conditional(request)
    return resp

if __name__ == "__main__":
    app.run(debug=True)
