# Nexus Beacons

Páginas de links (Sobre, Setup, Horários, Contatos, ETC.) em Flask + Jinja2, pensadas para `beacons.nexusheim.com`.

## Estrutura
- `content.py`: todos os textos, links e especificações. É o único arquivo que você edita no dia a dia.
- `templates/base.html`: moldura, abas, cabeçalho e rodapé (compartilhados por todas as páginas).
- `templates/_macros.html`: botão de link e cartão reutilizáveis.
- `templates/*.html`: uma página por aba, só com o conteúdo.
- `static/nexus.css`: o CSS único. Cor da marca em `--acc`.
- `static/app.js`: troca de aba sem recarregar, botões de copiar e cálculo da próxima live.

## Rodar
```
pip install -r requirements.txt
python app.py                # http://127.0.0.1:5000
gunicorn app:app             # produção
```

## Site estático (opcional)
```
python build.py              # gera dist/ com a mesma saída do Flask
```
Suba `dist/` no Cloudflare Pages, GitHub Pages ou Netlify e aponte o CNAME `beacons` para o serviço.
Rotas: `/`, `/setup`, `/horarios`, `/contatos`, `/etc`.


## Editar sem novo deploy (painel /admin)

O conteúdo de `content.py` é o **padrão**. As edições feitas em `/admin` ficam em `DATA_DIR/content.json` e valem por cima dele, na hora, sem deploy.

Variáveis de ambiente (Railway → Variables):

| Variável | Para quê |
|---|---|
| `ADMIN_PASSWORD` | Senha do painel. Sem ela, `/admin` fica desligado. |
| `DATA_DIR` | Pasta onde as edições são gravadas. No Railway use `/data`. |
| `SECRET_KEY` | (opcional) Chave da sessão. Se omitida, é derivada da senha. |

Para as edições sobreviverem a novos deploys, crie um **Volume** no serviço (Railway → serviço → Volumes → mount path `/data`) e defina `DATA_DIR=/data`. Sem volume, o painel avisa e as edições somem no próximo deploy.
