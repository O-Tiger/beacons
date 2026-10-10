"""Todo o conteúdo editável do site fica aqui. Para mudar um texto, link ou
especificação, edite este arquivo; o HTML e o CSS são reaproveitados dos templates."""

SITE = {"name": "Nexus", "domain": "beacons.nexusheim.com", "main_site": "https://nexusheim.com"}

LINKS = {
    "twitch": "https://twitch.tv/otigerjoga",
    "github": "https://github.com/O-Tiger",
    "discord": "https://discord.gg/ZTkXjtxbxe",
    "nexus": "https://nexusheim.com",
    "tracker": "https://twitchtracker.com/otigerjoga",
}
EMAIL = "contact@nexusheim.com"   # confirme se o alias existe no Cloudflare Email Routing
DISCORD_USER = "_tigersv"

# Ordem das abas. endpoint = nome da função de rota em app.py
PAGES = [
    {"endpoint": "sobre", "path": "/", "label": "Sobre"},
    {"endpoint": "setup", "path": "/setup", "label": "Setup"},
    {"endpoint": "horarios", "path": "/horarios", "label": "Horários"},
    {"endpoint": "contatos", "path": "/contatos", "label": "Contatos"},
    {"endpoint": "etc", "path": "/etc", "label": "ETC."},
]

SOBRE = {
    "title": "Sobre mim", "tag": "Criador do Nexus · Dev", "glyph": "tri",
    "lede": "Dev Java e full-stack. Um bloco de cada vez, até o topo.",
    "desc": "Tiger, criador do Nexus. Dev Java e full-stack.",
    "bullets": [
        "Desenvolvedor full-stack em formação",
        "Criador do <b>Nexus</b>: bot, Lynx, plugins (Prism, ATS, Spells), loja, texturas, catálogo e wiki",
        "Também desenvolvo o <b>NexoraEDU</b>, uma plataforma de ensino à parte, sem relação com o Nexus",
        "Entusiasta de jogos indie: Minecraft, Stardew Valley, Peak, Roblox e mais",
    ],
}

SETUP = {
    "title": "PC setup", "tag": "Ryzen 7 · RX 7600 · 32 GB", "glyph": "chip",
    "lede": "O computador de onde saem as lives e o código.",
    "desc": "Especificações do PC usado nas lives do Tiger.",
    "specs": [
        ("Placa-mãe", "Gigabyte B550M Aorus Elite"),
        ("Fonte", "MSI MAG A650BN · 650&nbsp;W"),
        ("Processador", "AMD Ryzen 7 3700X"),
        ("Memória", "Kingston Fury Beast DDR4 · 16&nbsp;GB · 3200&nbsp;MHz<br>Viper DDR4 · 16&nbsp;GB · 3200&nbsp;MHz"),
        ("Placa de vídeo", "AMD Radeon RX 7600 · 8&nbsp;GB"),
        ("SSD", "Kingston NV3 · 1&nbsp;TB"),
    ],
}

HORARIOS = {
    "title": "Horário das lives", "tag": "Fuso de Brasília", "glyph": "clock",
    "lede": "Live praticamente todos os dias, a partir das 17h. Exceção às segundas e quartas.",
    "desc": "Dias e horários das lives do Tiger na Twitch.",
    "start_hour": 17,
    "off_days": [1, 3],  # 0=domingo, 1=segunda ... 6=sábado
    "week": [("Segunda", 1), ("Terça", 2), ("Quarta", 3), ("Quinta", 4), ("Sexta", 5), ("Sábado", 6), ("Domingo", 0)],
}

CONTATOS = {
    "title": "Contatos", "tag": "GitHub · Discord · E-mail", "glyph": "signal",
    "lede": "Escolha o canal. Para trabalho e parcerias, e-mail é o mais rápido.",
    "desc": "Formas de contato com o Tiger.",
}

ETC = {
    "title": "ETC.", "tag": "Estatísticas do canal", "glyph": "chart",
    "lede": "Números do canal e atalhos que não cabem nos outros painéis.",
    "desc": "Estatísticas do canal do Tiger e atalhos extras.",
}
