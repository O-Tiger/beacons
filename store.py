"""Armazenamento do conteúdo editável.

Os valores de content.py são o PADRÃO. As edições feitas em /admin ficam em
DATA_DIR/content.json e valem por cima do padrão, sem precisar de novo deploy.
Em produção, aponte DATA_DIR para um volume persistente (ex.: /data no Railway).
"""
import json
import os
import re
import tempfile
import threading

import content as C
from icons import GLYPHS

DATA_DIR = os.environ.get("DATA_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FILE = os.path.join(DATA_DIR, "content.json")
MAX_BYTES = 100_000
_lock = threading.Lock()
_cache = (object(), None)


def defaults():
    d = {
        "site": C.SITE, "links": C.LINKS, "email": C.EMAIL, "discord_user": C.DISCORD_USER,
        "pages": {"sobre": C.SOBRE, "setup": C.SETUP, "horarios": C.HORARIOS, "contatos": C.CONTATOS, "etc": C.ETC},
    }
    return json.loads(json.dumps(d))  # cópia profunda; tuplas viram listas


def _merge(base, over):
    if isinstance(base, dict) and isinstance(over, dict):
        out = {k: _merge(v, over[k]) if k in over else v for k, v in base.items()}
        return out
    return over


def _same_type(base, val, path):
    if isinstance(base, bool) or isinstance(val, bool):
        raise ValueError(f"{path}: valor inválido")
    if isinstance(base, dict):
        if not isinstance(val, dict):
            raise ValueError(f"{path}: deveria ser um objeto")
        for k in base:
            _same_type(base[k], val[k], f"{path}.{k}")
    elif isinstance(base, list):
        if not isinstance(val, list):
            raise ValueError(f"{path}: deveria ser uma lista")
    elif isinstance(base, str):
        if not isinstance(val, str):
            raise ValueError(f"{path}: deveria ser texto")
        if len(val) > 4000:
            raise ValueError(f"{path}: texto longo demais")
    elif isinstance(base, int):
        if not isinstance(val, int):
            raise ValueError(f"{path}: deveria ser número")


def validate(data):
    """Devolve o conteúdo limpo (mesclado ao padrão) ou levanta ValueError em português."""
    if not isinstance(data, dict):
        raise ValueError("O conteúdo precisa ser um objeto JSON")
    base = defaults()
    out = _merge(base, {k: v for k, v in data.items() if k in base})
    for k, v in out["pages"].items():  # mesma regra para as chaves de cada página
        if not isinstance(v, dict):
            raise ValueError(f"pages.{k}: deveria ser um objeto")
    _same_type(base, out, "conteúdo")

    for k, v in out["links"].items():
        if not re.match(r"^https?://\S+$", v):
            raise ValueError(f"Link '{k}' precisa começar com http:// ou https://")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", out["email"]):
        raise ValueError("E-mail inválido")
    if not re.match(r"^https?://\S+$", out["site"]["main_site"]):
        raise ValueError("Site principal precisa começar com http:// ou https://")

    for k, p in out["pages"].items():
        if p["glyph"] not in GLYPHS:
            raise ValueError(f"{k}: ícone '{p['glyph']}' não existe")
    for b in out["pages"]["sobre"]["bullets"]:
        if not isinstance(b, str) or len(b) > 1000:
            raise ValueError("Cada tópico de 'Sobre' precisa ser um texto curto")
    for row in out["pages"]["setup"]["specs"]:
        if not (isinstance(row, list) and len(row) == 2 and all(isinstance(x, str) for x in row)):
            raise ValueError("Cada item do Setup precisa ter nome e valor")
    # descarta linhas em branco (clique em "+ Adicionar" sem preencher)
    pg = out["pages"]
    for lst in (pg["sobre"], pg["etc"]):
        for key in ("bullets", "rules"):
            if key in lst and isinstance(lst[key], list):
                lst[key] = [x for x in lst[key] if not (isinstance(x, str) and not x.strip())]
    for lst, key in ((pg["setup"], "specs"), (pg["etc"], "commands"), (pg["etc"], "faq")):
        if isinstance(lst[key], list):
            lst[key] = [r for r in lst[key] if not (isinstance(r, list) and all(isinstance(x, str) and not x.strip() for x in r))]
    e = out["pages"]["etc"]
    if not (isinstance(e["rules"], list) and all(isinstance(r, str) and len(r) <= 1000 for r in e["rules"])):
        raise ValueError("Cada regra precisa ser um texto curto")
    for key, nome in (("commands", "comando"), ("faq", "pergunta")):
        if not (isinstance(e[key], list) and all(isinstance(r, list) and len(r) == 2 and all(isinstance(x, str) for x in r) for r in e[key])):
            raise ValueError(f"Cada {nome} precisa ter dois campos de texto")
    h = out["pages"]["horarios"]
    if not 0 <= h["start_hour"] <= 23:
        raise ValueError("Hora de início precisa estar entre 0 e 23")
    if not (isinstance(h["off_days"], list) and all(isinstance(d, int) and not isinstance(d, bool) and 0 <= d <= 6 for d in h["off_days"])):
        raise ValueError("Dias de folga inválidos")
    if not all(isinstance(r, list) and len(r) == 2 and isinstance(r[0], str) and isinstance(r[1], int) and 0 <= r[1] <= 6 for r in h["week"]):
        raise ValueError("Lista da semana inválida")
    if len(json.dumps(out)) > MAX_BYTES:
        raise ValueError("Conteúdo grande demais")
    return out


def _key():
    try:
        return os.stat(FILE).st_mtime_ns
    except FileNotFoundError:
        return None


def load():
    """Conteúdo atual. Relê o arquivo só quando ele muda (vale para todos os workers)."""
    global _cache
    key = _key()
    if _cache[0] == key and _cache[1] is not None:
        return _cache[1]
    data = defaults()
    if key is not None:
        try:
            with open(FILE, encoding="utf-8") as f:
                data = validate(json.load(f))
        except Exception:
            data = defaults()  # arquivo corrompido: volta ao padrão em vez de derrubar o site
    _cache = (key, data)
    return data


def version():
    return str(_key() or 0)


def save(data):
    clean = validate(data)
    with _lock:
        os.makedirs(DATA_DIR, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(clean, f, ensure_ascii=False, indent=2)
            os.replace(tmp, FILE)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    return clean


def reset():
    with _lock:
        try:
            os.remove(FILE)
        except FileNotFoundError:
            pass


def persistent():
    """True quando DATA_DIR é um volume montado (sobrevive a novos deploys)."""
    return os.path.ismount(DATA_DIR)
