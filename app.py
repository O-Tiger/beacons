"""Nexus Beacons: páginas de links do Tiger, em Flask + Jinja2.

Rodar local:   python app.py            (http://127.0.0.1:5000)
Produção:      gunicorn app:app
Site estático: python build.py          (gera a pasta dist/)
"""
from flask import Flask, render_template, redirect
from markupsafe import Markup
import content as C
from icons import ICONS, GLYPHS

app = Flask(__name__)
app.jinja_env.globals.update(
    SITE=C.SITE, LINKS=C.LINKS, EMAIL=C.EMAIL, DISCORD_USER=C.DISCORD_USER, PAGES=C.PAGES,
    ICONS={k: Markup(v) for k, v in ICONS.items()},
    GLYPHS={k: Markup(v) for k, v in GLYPHS.items()},
)

def page(template, data):
    return render_template(template, p=data, current=template.split(".")[0])

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")


@app.route("/")
def sobre(): return page("sobre.html", C.SOBRE)

@app.route("/setup")
def setup(): return page("setup.html", C.SETUP)

@app.route("/horarios")
def horarios(): return page("horarios.html", C.HORARIOS)

@app.route("/contatos")
def contatos(): return page("contatos.html", C.CONTATOS)

@app.route("/etc")
def etc(): return page("etc.html", C.ETC)

@app.route("/sobre")
def sobre_alias(): return redirect("/", code=301)

@app.after_request
def cache(resp):
    if resp.mimetype in ("text/html",):
        resp.headers["Cache-Control"] = "public, max-age=300"
    return resp

if __name__ == "__main__":
    app.run(debug=True)
