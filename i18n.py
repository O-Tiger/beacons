"""Pt-BR is the default language; English is the optional one.

The Portuguese text (the site's own content and the labels in the templates) is the catalog key; `EN` maps it to
English. A text with no entry (for example a line the owner wrote himself in the dash) is shown as it is, so editing
the content never breaks the page.
"""
from __future__ import annotations

from flask import Flask, Response, redirect, request

LANGS = ("pt-BR", "en")
DEFAULT_LANG = "pt-BR"
COOKIE = "nx_lang"

EN = {
    # tabs and cards
    "Sobre": "About", "Setup": "Setup", "Horários": "Schedule", "Contatos": "Contact", "ETC.": "ETC.",
    "Páginas": "Pages", "Quem sou": "Who I am", "Onde me achar": "Where to find me", "Especificações": "Specs",
    "Próxima live prevista": "Next expected stream", "Calculado pelo horário de Brasília": "Calculated in Brasília time",
    "Semana": "Week", "folga": "day off", "Acompanhe": "Follow",
    "Os horários podem mudar sem aviso. Avisos ficam na Twitch e no Discord.": "Times may change without notice. Announcements are on Twitch and Discord.",
    "Entrar no servidor": "Join the server", "Avisos e comunidade": "Announcements and community",
    "Falar comigo": "Talk to me", "Discord (servidor)": "Discord (server)", "Discord (usuário)": "Discord (user)",
    "Regras do chat": "Chat rules", "Comandos": "Commands", "Perguntas frequentes": "Frequently asked questions",
    "Canal": "Channel", "Estatísticas públicas de otigerjoga": "Public stats for otigerjoga",
    "Copiar": "Copy", "Abrir ↗": "Open ↗",
    "Mudar idioma": "Change language", "Alternar tema": "Toggle theme",
    # page content (defaults from content.py)
    "Sobre mim": "About me", "Criador do Nexus · Dev": "Creator of Nexus · Dev",
    "Dev Java e full-stack. Um bloco de cada vez, até o topo.": "Java and full-stack dev. One block at a time, all the way to the top.",
    "Tiger, criador do Nexus. Dev Java e full-stack.": "Tiger, creator of Nexus. Java and full-stack dev.",
    "Desenvolvedor full-stack em formação": "Full-stack developer in training",
    "Criador do <b>Nexus</b>: bot, Lynx, plugins (Prism, ATS, Spells), loja, texturas, catálogo e wiki":
        "Creator of <b>Nexus</b>: bot, Lynx, plugins (Prism, ATS, Spells), store, textures, catalog and wiki",
    "Também desenvolvo o <b>NexoraEDU</b>, uma plataforma de ensino à parte, sem relação com o Nexus":
        "I also develop <b>NexoraEDU</b>, a separate learning platform, unrelated to Nexus",
    "Entusiasta de jogos indie: Minecraft, Stardew Valley, Peak, Roblox e mais": "Indie game enthusiast: Minecraft, Stardew Valley, Peak, Roblox and more",
    "PC setup": "PC setup", "O computador de onde saem as lives e o código.": "The computer the streams and the code come from.",
    "Especificações do PC usado nas lives do Tiger.": "Specs of the PC used on Tiger's streams.",
    "Placa-mãe": "Motherboard", "Fonte": "Power supply", "Processador": "Processor", "Memória": "Memory", "Placa de vídeo": "Graphics card",
    "Horário das lives": "Stream schedule", "Fuso de Brasília": "Brasília time zone",
    "Live praticamente todos os dias, a partir das 17h. Exceção às segundas e quartas.": "Live almost every day, from 5 PM. Except Mondays and Wednesdays.",
    "Dias e horários das lives do Tiger na Twitch.": "Days and times of Tiger's streams on Twitch.",
    "Segunda": "Monday", "Terça": "Tuesday", "Quarta": "Wednesday", "Quinta": "Thursday", "Sexta": "Friday", "Sábado": "Saturday", "Domingo": "Sunday",
    "GitHub · Discord · E-mail": "GitHub · Discord · Email",
    "Escolha o canal. Para trabalho e parcerias, e-mail é o mais rápido.": "Pick a channel. For work and partnerships, email is the fastest.",
    "Formas de contato com o Tiger.": "Ways to get in touch with Tiger.",
    "Estatísticas do canal": "Channel stats",
    "Números do canal e atalhos que não cabem nos outros painéis.": "Channel numbers and shortcuts that do not fit the other panels.",
    "Estatísticas do canal do Tiger e atalhos extras.": "Tiger's channel stats and extra shortcuts.",
    # scripts
    "Copiado: ": "Copied: ", "Hoje às {h}h": "Today at {h}h", "Previsão para hoje ({day})": "Expected today ({day})",
    "Hoje, a partir das {h}h": "Today, from {h}h", "Confira na Twitch se está no ar": "Check on Twitch whether it is live",
    "Amanhã": "Tomorrow", "{day} às {h}h": "{day} at {h}h", "{day}, horário de Brasília": "{day}, Brasília time",
    "domingo": "Sunday", "segunda": "Monday", "terça": "Tuesday", "quarta": "Wednesday", "quinta": "Thursday", "sexta": "Friday", "sábado": "Saturday",
}


def current_lang() -> str:
    code = request.cookies.get(COOKIE, "") if request else ""
    return code if code in LANGS else DEFAULT_LANG


def translate(text: str, **values: object) -> str:
    out = text
    if current_lang() == "en" and isinstance(text, str):
        out = EN.get(text, text)
    for k, v in values.items():
        out = out.replace("{" + k + "}", str(v))
    return out


def init_app(app: Flask) -> None:
    app.jinja_env.globals["_"] = translate
    app.jinja_env.globals["current_lang"] = current_lang

    @app.get("/lang/<code>")
    def set_lang(code: str):
        target = request.args.get("next", "/")
        if not target.startswith("/") or target.startswith("//") or "\\" in target:
            target = "/"
        resp = redirect(target)
        if code in LANGS:
            resp.set_cookie(COOKIE, code, max_age=365 * 24 * 3600, samesite="Lax",
                            secure=request.is_secure, httponly=False, path="/")
        return resp

    @app.get("/i18n.js")
    def i18n_js():
        import json
        lang = current_lang()
        body = ("window.NEXUS_LANG=" + json.dumps(lang) + ";window.NEXUS_I18N="
                + json.dumps(EN if lang == "en" else {}, ensure_ascii=False) + ";")
        return Response(body, mimetype="application/javascript", headers={"Cache-Control": "no-store"})
