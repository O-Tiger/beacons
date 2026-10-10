"""Exporta o site para HTML estático em dist/ (Cloudflare Pages, GitHub Pages, Netlify...).
Usa as mesmas rotas e templates do app Flask, então o resultado é idêntico."""
import shutil
from pathlib import Path
from app import app
import content as C

out = Path("dist")
shutil.rmtree(out, ignore_errors=True)
out.mkdir()
shutil.copytree("static", out / "static")
client = app.test_client()
for pg in C.PAGES:
    html = client.get(pg["path"]).get_data(as_text=True)
    target = out / "index.html" if pg["path"] == "/" else out / pg["path"].strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    print("ok", target)
