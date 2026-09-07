#!/usr/bin/env python3
"""
Gerador do Painel Diário de Artigos Científicos.

Busca artigos recentes por tema na API pública do Semantic Scholar
(https://api.semanticscholar.org/, sem necessidade de chave de API) e
monta uma página HTML autocontida (index.html) com o mesmo layout do
painel publicado neste repositório.

Na versão originalmente usada por Darci de Borba, a busca e a curadoria
eram feitas por um assistente de IA (Claude, via Cowork) consultando as
bases Consensus e Scite (ver PROMPT.md). Este script automatiza a parte
reprodutível do processo com uma fonte pública e gratuita; a curadoria
fina (relevância, resumo em português, exclusão de trabalhos de nicho)
continua sendo mais bem feita por um revisor humano ou por IA.

Uso:
    python gerar_painel.py

Gera/atualiza o arquivo index.html na pasta atual.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import urllib.parse
import urllib.request

# Temas de interesse e a consulta usada para cada um na API do Semantic Scholar.
TEMAS: dict[str, str] = {
    "Transformação Digital e Governo Digital": "digital transformation government digital public sector",
    "Administração Pública e Governança": "public administration governance public value",
    "Capacidades Dinâmicas e Processos": "dynamic capabilities business process management organizations",
    "Inteligência Artificial no Setor Público": "artificial intelligence public sector government",
    "Ciência de Dados para Políticas Públicas": "data science public policy analytics",
    "Comportamento Organizacional e Gestão": "organizational behavior public management",
}

ARTIGOS_POR_TEMA = 5
JANELA_DIAS_NOVO = 30
API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


def buscar_artigos(query: str, limite: int = ARTIGOS_POR_TEMA) -> list[dict]:
    """Consulta a API do Semantic Scholar e retorna os artigos mais relevantes."""
    params = {
        "query": query,
        "limit": limite,
        "fields": "title,abstract,year,venue,authors,externalIds,publicationDate,url",
        "sort": "publicationDate:desc",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "painel-artigos-cientificos/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("data", [])
    except Exception as exc:  # rede indisponível, limite de requisições, etc.
        print(f"[aviso] falha ao buscar '{query}': {exc}")
        return []


def eh_novo(publication_date: str | None) -> bool:
    if not publication_date:
        return False
    try:
        data_pub = dt.date.fromisoformat(publication_date)
    except ValueError:
        return False
    return (dt.date.today() - data_pub).days <= JANELA_DIAS_NOVO


def link_do_artigo(artigo: dict) -> str:
    doi = (artigo.get("externalIds") or {}).get("DOI")
    if doi:
        return f"https://doi.org/{doi}"
    return artigo.get("url") or "#"


def resumo_curto(artigo: dict, max_chars: int = 220) -> str:
    abstract = artigo.get("abstract") or "Resumo não disponível na fonte."
    abstract = abstract.strip().replace("\n", " ")
    return (abstract[:max_chars] + "…") if len(abstract) > max_chars else abstract


def render_card(artigo: dict) -> str:
    titulo = html.escape(artigo.get("title") or "Sem título")
    autores = ", ".join(a.get("name", "") for a in (artigo.get("authors") or [])[:3])
    ano = artigo.get("year") or ""
    periodico = html.escape(artigo.get("venue") or "")
    meta = html.escape(f"{autores} ({ano}) — {periodico}".strip(" —"))
    resumo = html.escape(resumo_curto(artigo))
    link = html.escape(link_do_artigo(artigo))
    tag_novo = '<span class="tag novo">novo</span>' if eh_novo(artigo.get("publicationDate")) else ""
    return f"""
      <a class="card" href="{link}" target="_blank" rel="noopener">
        <div class="card-title">{titulo}</div>
        <div class="card-meta">{meta}</div>
        <div class="card-summary">{resumo}</div>
        <div class="card-footer">{tag_novo}</div>
      </a>"""


def render_secao(tema: str, artigos: list[dict]) -> str:
    cards = "\n".join(render_card(a) for a in artigos) or "<p class='muted'>Nenhum artigo encontrado nesta rodada.</p>"
    return f"""
    <section class="theme">
      <div class="theme-header"><h2>{html.escape(tema)}</h2><span class="count">{len(artigos)} artigo(s)</span></div>
      <div class="grid">{cards}
      </div>
    </section>"""


def montar_html(secoes_html: str, data_geracao: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Painel Diário de Artigos Científicos — Darci de Borba</title>
<style>
  :root{{
    --bg:#0f1626; --panel:#161f33; --panel2:#1c2740; --border:#2a3654;
    --text:#e8ecf5; --muted:#96a2bf; --accent:#5b8def; --tag3:#7ad0c6;
  }}
  *{{box-sizing:border-box;}}
  body{{margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    background:linear-gradient(180deg,#0b1120,#0f1626 400px); color:var(--text); line-height:1.55;}}
  header{{padding:36px 24px 20px; max-width:1100px; margin:0 auto;}}
  header h1{{margin:0 0 6px; font-size:1.7rem; font-weight:700;}}
  header .sub{{color:var(--muted); font-size:0.95rem;}}
  main{{max-width:1100px; margin:0 auto; padding:0 24px 60px;}}
  section.theme{{margin-top:34px;}}
  .theme-header{{display:flex; align-items:baseline; gap:10px; margin-bottom:14px; border-bottom:1px solid var(--border); padding-bottom:8px;}}
  .theme-header h2{{font-size:1.15rem; margin:0; font-weight:650;}}
  .theme-header .count{{color:var(--muted); font-size:0.85rem;}}
  .grid{{display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:16px;}}
  a.card{{display:flex; flex-direction:column; gap:10px; background:var(--panel); border:1px solid var(--border);
    border-radius:12px; padding:18px; text-decoration:none; color:var(--text);}}
  a.card:hover{{border-color:var(--accent); background:var(--panel2);}}
  .card-title{{font-size:1rem; font-weight:650;}}
  .card-meta{{font-size:0.78rem; color:var(--muted);}}
  .card-summary{{font-size:0.86rem; color:#c4cbdf;}}
  .tag.novo{{font-size:0.72rem; font-weight:600; padding:3px 9px; border-radius:6px; background:rgba(122,208,198,0.15); color:var(--tag3); border:1px solid rgba(122,208,198,0.35);}}
  .muted{{color:var(--muted);}}
</style>
</head>
<body>
<header>
  <h1>Painel Diário de Artigos Científicos</h1>
  <div class="sub">Gerado em {data_geracao} — curadoria de Darci de Borba, com apoio de IA</div>
</header>
<main>{secoes_html}
</main>
</body>
</html>"""


def main() -> None:
    data_geracao = dt.date.today().strftime("%d/%m/%Y")
    secoes = []
    for tema, query in TEMAS.items():
        artigos = buscar_artigos(query)
        secoes.append(render_secao(tema, artigos))
    pagina = montar_html("\n".join(secoes), data_geracao)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(pagina)
    print("index.html atualizado.")


if __name__ == "__main__":
    main()
