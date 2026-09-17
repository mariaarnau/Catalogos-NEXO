# -*- coding: utf-8 -*-
"""Genera el HTML completo de la Prueba de Nivel de Inglés (Nexo Académico)
y lo imprime a PDF con Chromium headless."""

import base64
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import content as C

HERE = Path(__file__).parent
REPO = Path("/home/user/Catalogos-NEXO")
OUT_HTML = HERE / "nexo_english_placement_test.html"
OUT_PDF = HERE / "nexo_english_placement_test.pdf"

LOGO_B64 = base64.b64encode(
    (REPO / "LOGO_NEXO_horizontal-2-removebg-preview.png").read_bytes()
).decode("ascii")
FONTS_CSS = (HERE / "fonts_embedded.css").read_text(encoding="utf-8")

LETTERS = "ABCD"

# ===========================================================================
# CSS
# ===========================================================================

CSS_TEMPLATE = """
{FONTS}

:root {
  --navy-deep:#04071b; --blue:#154ca9; --blue-light:#6eaef0;
  --cream:#f4f1e8; --white:#ffffff;
  --green-deep:#146b46; --green:#2f9e6f; --green-light:#6fcf9e;
  --amber:#d99a3e; --amber-deep:#a9701e; --alert:#c1502e;
}
* { box-sizing:border-box; margin:0; padding:0; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
html,body { background:#e9e9e9; }
body { font-family:'Lora',serif; color:var(--navy-deep); line-height:1.5; font-size:10.3pt; }
@page { size:A4; margin:0; }

.page { width:210mm; min-height:297mm; box-sizing:border-box; padding:14mm 16mm 20mm;
  position:relative; background:#fff; page-break-after:always; break-after:page; overflow:hidden; }
.page:last-of-type { page-break-after:auto; break-after:auto; }

.runhead { display:flex; align-items:center; justify-content:space-between;
  padding-bottom:8px; margin-bottom:14px; border-bottom:1.5px solid var(--cream); }
.runhead .brand { display:flex; align-items:center; gap:7px; font-family:'Playfair Display',serif;
  font-weight:700; color:var(--navy-deep); font-size:.82rem; }
.runhead .brand img { height:16px; display:block; }
.runhead .sect { font-size:.68rem; text-transform:uppercase; letter-spacing:.08em; color:var(--blue); font-weight:700; text-align:right; }

.runfoot { position:absolute; left:16mm; right:16mm; bottom:9mm; display:flex; justify-content:space-between;
  font-size:.66rem; color:var(--navy-deep); opacity:.55; border-top:1px solid var(--cream); padding-top:6px; }

.confidential-banner { background:linear-gradient(120deg,var(--alert),var(--amber-deep)); color:#fff;
  padding:9px 16px; border-radius:9px; font-weight:700; text-transform:uppercase; letter-spacing:.05em;
  font-size:.72rem; margin-bottom:14px; text-align:center; }

.sect-title { margin-bottom:14px; }
.sect-title .eyebrow { font-size:.7rem; text-transform:uppercase; letter-spacing:.1em; color:var(--blue); font-weight:700; margin-bottom:3px; }
.sect-title h2 { font-family:'Playfair Display',serif; font-size:1.4rem; color:var(--navy-deep); margin:0 0 3px; }
.sect-title .meta { font-size:.82rem; color:var(--navy-deep); opacity:.65; }

.part-instructions { background:var(--cream); border-radius:8px; padding:9px 13px; font-size:.82rem;
  margin-bottom:12px; }

.blank { display:inline-block; width:58px; border-bottom:1.5px solid var(--navy-deep); vertical-align:middle; }

.cols2 { column-count:2; column-gap:22px; }
.mcq { break-inside:avoid; page-break-inside:avoid; margin-bottom:8px; }
.mcq .mcq-q { font-size:.86rem; line-height:1.32; margin-bottom:2px; }
.mcq .qn { color:var(--blue); font-weight:700; }
.mcq .opts { display:flex; flex-wrap:wrap; gap:1px 13px; font-size:.78rem; padding-left:13px; opacity:.9; }
.mcq .opts b { color:var(--navy-deep); margin-right:2px; }

table.wf-table, table.rubric-table, table.plain-table { width:100%; border-collapse:collapse; font-size:.8rem; }
table.wf-table th, table.wf-table td,
table.plain-table th, table.plain-table td { border:1px solid var(--cream); padding:7px 9px; text-align:left; vertical-align:top; }
table.wf-table th, table.plain-table th { background:var(--cream); font-size:.68rem; text-transform:uppercase; letter-spacing:.05em; color:var(--blue); }
table.wf-table td.root { font-weight:700; letter-spacing:.03em; white-space:nowrap; }
table.wf-table td.ans { width:32mm; }

.kwt-item { border:1px solid var(--cream); border-radius:10px; padding:10px 14px; margin-bottom:9px; break-inside:avoid; }
.kwt-item .orig { font-size:.86rem; margin-bottom:5px; }
.kwt-item .orig b { color:var(--blue); }
.kwt-row { display:flex; align-items:center; gap:10px; font-size:.86rem; flex-wrap:wrap; }
.badge { display:inline-block; padding:2px 10px; border-radius:11px; font-size:.68rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.04em; background:rgba(21,76,169,.12); color:var(--blue); }
.blank-line { display:inline-block; min-width:170px; border-bottom:1.5px solid var(--navy-deep); height:1.1em; vertical-align:middle; }

.cover-page { display:flex; flex-direction:column; align-items:center; padding-top:22mm; }
.cover-logo { height:80px; margin-bottom:22px; }
.cover-banner { width:100%; background:linear-gradient(120deg,var(--navy-deep),var(--blue)); border-radius:18px;
  padding:34px 36px; color:#fff; text-align:center; box-shadow:0 10px 40px rgba(4,7,27,.25); }
.cover-banner .eyebrow { font-size:.8rem; text-transform:uppercase; letter-spacing:.16em; opacity:.82; margin-bottom:10px; font-weight:600; }
.cover-banner h1 { font-family:'Playfair Display',serif; font-weight:700; font-size:2.3rem; margin:0 0 10px; }
.cover-banner .levels { font-size:1.05rem; letter-spacing:.08em; opacity:.94; margin-bottom:3px; font-family:'Lora',serif; }
.cover-banner .sub { font-size:.85rem; opacity:.78; margin-top:12px; line-height:1.5; }
.cover-fields { width:100%; margin-top:26px; border:1px solid var(--cream); border-radius:14px; padding:20px 24px; }
.cover-fields .row { display:flex; gap:20px; margin-bottom:13px; }
.cover-fields .row:last-child { margin-bottom:0; }
.cover-fields .field { flex:1; }
.cover-fields label { display:block; font-size:.66rem; text-transform:uppercase; letter-spacing:.06em; color:var(--blue); font-weight:700; margin-bottom:4px; }
.cover-fields .line { border-bottom:1.4px solid var(--navy-deep); height:18px; }
.cover-methodology { margin-top:22px; font-size:.74rem; color:var(--navy-deep); opacity:.62; text-align:center; line-height:1.55; max-width:160mm; }
.cover-parts { width:100%; display:flex; gap:10px; margin-top:20px; }
.cover-parts .cp { flex:1; background:var(--cream); border-radius:10px; padding:10px 8px; text-align:center; }
.cover-parts .cp .n { font-family:'Playfair Display',serif; font-weight:700; color:var(--blue); font-size:1.1rem; }
.cover-parts .cp .l { font-size:.62rem; text-transform:uppercase; letter-spacing:.04em; opacity:.7; margin-top:2px; }

.toc { margin-top:6px; }
.toc-row { display:flex; justify-content:space-between; padding:7px 0; border-bottom:1px solid var(--cream); font-size:.86rem; }
.toc-row .pg { color:var(--blue); font-weight:700; }

.info-card { border:1px solid var(--cream); border-radius:12px; padding:16px 18px; margin-bottom:14px; }
.info-card h3 { font-family:'Playfair Display',serif; font-size:1.02rem; color:var(--navy-deep); margin-bottom:8px; }
.info-card p, .info-card li { font-size:.86rem; margin-bottom:6px; }
.info-card ul, .info-card ol { padding-left:20px; }

.timing-table td, .timing-table th { font-size:.78rem; }

.field-row { display:flex; gap:20px; margin-bottom:12px; }
.field-row .field { flex:1; }
.field-row label { display:block; font-size:.68rem; text-transform:uppercase; letter-spacing:.05em; color:var(--blue); font-weight:700; margin-bottom:5px; }
.field-row .line { border-bottom:1.4px solid var(--navy-deep); height:20px; }

.cloze-card { border:1px solid var(--cream); border-radius:12px; padding:16px 20px; margin-bottom:16px; }
.cloze-card h4 { font-family:'Playfair Display',serif; font-size:1rem; margin-bottom:8px; color:var(--navy-deep); }
.cloze-card .txt { font-size:.92rem; line-height:1.9; }
.cloze-card .txt u { text-decoration:none; border-bottom:1.5px solid var(--blue); color:var(--blue); font-weight:700; padding:0 2px; }
.cloze-card .txt b { color:var(--green-deep); }

.ans-grid { display:grid; gap:5px 6px; margin-bottom:8px; }
.ans-cell { display:flex; flex-direction:column; align-items:center; border:1px solid var(--cream); border-radius:6px; padding:5px 2px 6px; }
.ans-cell .n { font-size:.6rem; opacity:.55; }
.ans-cell .line { width:80%; border-bottom:1.2px solid var(--navy-deep); height:12px; margin-top:2px; }
.ans-block-title { font-size:.72rem; text-transform:uppercase; letter-spacing:.06em; color:var(--blue); font-weight:700; margin:12px 0 6px; }
.ans-block-title:first-child { margin-top:0; }

.kwt-ans-line { display:flex; align-items:center; gap:8px; margin-bottom:9px; }
.kwt-ans-line .n { font-weight:700; color:var(--blue); width:16px; }
.kwt-ans-line .line { flex:1; border-bottom:1.2px solid var(--navy-deep); height:16px; }

.speak-part { border:1px solid var(--cream); border-radius:12px; padding:14px 18px; margin-bottom:14px; }
.speak-part h3 { font-family:'Playfair Display',serif; font-size:1.05rem; color:var(--navy-deep); margin-bottom:3px; }
.speak-part .dur { font-size:.72rem; color:var(--blue); font-weight:700; text-transform:uppercase; letter-spacing:.05em; margin-bottom:8px; }
.speak-part p.desc { font-size:.84rem; margin-bottom:8px; opacity:.85; }
.q-theme { font-size:.72rem; text-transform:uppercase; letter-spacing:.05em; color:var(--green-deep); font-weight:700; margin:8px 0 3px; }
.q-list { list-style:none; padding-left:0; }
.q-list li { font-size:.86rem; padding:2px 0 2px 16px; position:relative; }
.q-list li::before { content:"—"; position:absolute; left:0; opacity:.5; }
.card-topic { background:var(--cream); border-radius:9px; padding:10px 13px; margin-bottom:8px; }
.card-topic .lvl { display:inline-block; font-size:.62rem; font-weight:700; color:#fff; background:var(--blue);
  border-radius:8px; padding:1px 8px; margin-bottom:5px; text-transform:uppercase; letter-spacing:.04em; }
.card-topic .ttl { font-weight:700; font-size:.88rem; margin-bottom:3px; }
.card-topic .body { font-size:.82rem; opacity:.85; }
.opt-list { list-style:none; padding-left:0; margin-top:6px; }
.opt-list li { font-size:.82rem; padding:2px 0 2px 16px; position:relative; }
.opt-list li::before { content:"›"; position:absolute; left:0; color:var(--blue); font-weight:700; }

table.rubric-table th, table.rubric-table td { border:1px solid var(--cream); padding:6px 7px; font-size:.66rem; line-height:1.35; vertical-align:top; }
table.rubric-table th { background:var(--navy-deep); color:#fff; text-transform:uppercase; letter-spacing:.04em; font-size:.62rem; }
table.rubric-table td.crit { font-weight:700; background:var(--cream); white-space:nowrap; }

.score-box { display:flex; gap:10px; margin:10px 0; }
.score-box .sb { flex:1; border:1.5px solid var(--cream); border-radius:8px; padding:8px; text-align:center; }
.score-box .sb .lab { font-size:.62rem; text-transform:uppercase; opacity:.6; margin-bottom:3px; }
.score-box .sb .val { font-family:'Playfair Display',serif; font-weight:700; font-size:1rem; color:var(--blue); }

.key-grid { display:grid; gap:3px 5px; margin-bottom:10px; }
.key-cell { display:flex; flex-direction:column; align-items:center; background:var(--cream); border-radius:5px; padding:3px 2px; }
.key-cell .kn { font-size:.56rem; opacity:.55; }
.key-cell .ka { font-weight:700; color:var(--navy-deep); font-family:'Lora',serif; font-size:.78rem; }
.key-h4 { font-family:'Playfair Display',serif; font-size:.86rem; margin:10px 0 5px; color:var(--blue); }
.key-h4:first-child { margin-top:0; }
.key-list { font-size:.82rem; columns:2; column-gap:24px; margin-bottom:8px; }
.key-list div { break-inside:avoid; padding:2px 0; }

.kpi-row { display:flex; gap:10px; margin:14px 0; flex-wrap:wrap; }
.kpi-card { flex:1; min-width:100px; border:1px solid var(--cream); border-top:3px solid var(--blue); border-radius:9px; padding:12px 10px; }
.kpi-card .num { font-family:'Playfair Display',serif; font-size:1.25rem; font-weight:700; }
.kpi-card .lab { font-size:.62rem; text-transform:uppercase; letter-spacing:.04em; opacity:.6; margin-top:2px; }
.kpi-card .line { border-bottom:1.3px solid var(--navy-deep); height:16px; margin-top:4px; }

.final-level { background:linear-gradient(120deg,var(--navy-deep),var(--blue)); color:#fff; border-radius:14px;
  padding:22px 26px; text-align:center; margin:16px 0; }
.final-level .lab { font-size:.72rem; text-transform:uppercase; letter-spacing:.1em; opacity:.8; margin-bottom:8px; }
.final-level .lvl-line { display:flex; justify-content:center; gap:14px; }
.final-level .lvl-opt { width:44px; height:44px; border:2px solid rgba(255,255,255,.5); border-radius:50%;
  display:flex; align-items:center; justify-content:center; font-family:'Playfair Display',serif; font-weight:700; font-size:1.1rem; }

.puntos-grupo { margin-bottom:12px; }
.puntos-grupo h4 { font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.05em; margin-bottom:6px; color:var(--green-deep); }
.puntos-grupo.atencion h4 { color:var(--amber-deep); }
.puntos-grupo .wline { border-bottom:1px dotted rgba(4,7,27,.35); height:15px; margin-bottom:5px; }

.two-col { display:flex; gap:20px; }
.two-col > div { flex:1; }
"""

CSS = CSS_TEMPLATE.replace("{FONTS}", FONTS_CSS)


# ===========================================================================
# Helpers
# ===========================================================================

def blankify(text):
    return text.replace("___", '<span class="blank"></span>')


def mcq_html(n, question, options):
    q = blankify(question)
    opts = "".join(
        f'<span><b>{LETTERS[i]}</b> {o}</span>' for i, o in enumerate(options)
    )
    return (f'<div class="mcq"><p class="mcq-q"><span class="qn">{n}.</span> {q}</p>'
            f'<div class="opts">{opts}</div></div>')


def section_title(eyebrow, title, meta=""):
    meta_html = f'<div class="meta">{meta}</div>' if meta else ""
    return f'<div class="sect-title"><div class="eyebrow">{eyebrow}</div><h2>{title}</h2>{meta_html}</div>'


def ans_grid(start_num, count, per_row):
    cells = "".join(
        f'<div class="ans-cell"><span class="n">{start_num + i}</span><span class="line"></span></div>'
        for i in range(count)
    )
    return f'<div class="ans-grid" style="grid-template-columns:repeat({per_row},1fr)">{cells}</div>'


def key_grid(start_num, letters, cols):
    cells = "".join(
        f'<div class="key-cell"><span class="kn">{start_num + i}</span><span class="ka">{l}</span></div>'
        for i, l in enumerate(letters)
    )
    return f'<div class="key-grid" style="grid-template-columns:repeat({cols},1fr)">{cells}</div>'


# ===========================================================================
# PORTADA (cover)
# ===========================================================================

def build_cover():
    body = f'''
    <img class="cover-logo" src="data:image/png;base64,{LOGO_B64}" alt="Nexo Académico">
    <div class="cover-banner">
      <div class="eyebrow">Nexo Académico</div>
      <h1>English Placement Test</h1>
      <div class="levels">B1 &middot; B2 &middot; C1 &middot; C2</div>
      <div class="sub">Prueba de nivel de inglés — Gramática, Vocabulario y Speaking<br>
      Alineada con el Marco Común Europeo de Referencia para las Lenguas (MCER / CEFR)</div>
    </div>
    <div class="cover-parts">
      <div class="cp"><div class="n">109</div><div class="l">Preguntas escritas</div></div>
      <div class="cp"><div class="n">117</div><div class="l">Puntos totales</div></div>
      <div class="cp"><div class="n">4</div><div class="l">Partes de Speaking</div></div>
      <div class="cp"><div class="n">~90</div><div class="l">Minutos (escrito)</div></div>
    </div>
    <div class="cover-fields">
      <div class="row">
        <div class="field"><label>Nombre del candidato / de la candidata</label><div class="line"></div></div>
        <div class="field"><label>Fecha</label><div class="line"></div></div>
      </div>
      <div class="row">
        <div class="field"><label>Examinador / Profesor</label><div class="line"></div></div>
        <div class="field"><label>Nivel autopercibido (opcional)</label><div class="line"></div></div>
      </div>
    </div>
    <div class="cover-methodology">
      Diseñada siguiendo la estructura y metodología de referencia de los exámenes de Cambridge
      English Qualifications (Use of English), el Oxford Online Placement Test y los descriptores
      de competencia oral y escrita del MCER/CEFR, adaptada al formato de evaluación presencial de Nexo Académico.
    </div>
    '''
    return [body]


# ===========================================================================
# OVERVIEW / instrucciones para el examinador (con índice)
# ===========================================================================

def build_overview():
    body = f'''
    {section_title("Guía del examinador", "Cómo usar esta prueba")}
    <div class="info-card">
      <h3>Estructura de la prueba</h3>
      <table class="wf-table timing-table">
        <thead><tr><th>Parte</th><th>Contenido</th><th>Ítems</th><th>Puntos</th><th>Tiempo aprox.</th></tr></thead>
        <tbody>
          <tr><td>1</td><td>Grammar &amp; Vocabulary (opción múltiple)</td><td>60</td><td>60</td><td>35 min</td></tr>
          <tr><td>2</td><td>Open Cloze (huecos en texto)</td><td>16</td><td>16</td><td>12 min</td></tr>
          <tr><td>3</td><td>Word Formation</td><td>10</td><td>10</td><td>8 min</td></tr>
          <tr><td>4</td><td>Key Word Transformation</td><td>8</td><td>16</td><td>12 min</td></tr>
          <tr><td>5</td><td>Vocabulary in Use (colocaciones, phrasal verbs, idioms)</td><td>15</td><td>15</td><td>13 min</td></tr>
          <tr><td>Speaking</td><td>Entrevista guiada en 4 partes</td><td>—</td><td>4 criterios &times; 4</td><td>12–15 min</td></tr>
        </tbody>
      </table>
    </div>
    <div class="info-card">
      <h3>Regla de parada (opcional)</h3>
      <p>Si el candidato obtiene menos del 40% en la Sección A de la Parte 1 (preguntas 1–15),
      se puede interrumpir la prueba escrita: es muy probable que su nivel sea Pre-B1 y continuar
      solo generaría frustración. En cualquier otro caso, se recomienda completar toda la prueba
      escrita para obtener un perfil diagnóstico fiable.</p>
    </div>
    <div class="info-card">
      <h3>Materiales necesarios</h3>
      <ul>
        <li>Un ejemplar impreso de esta prueba por candidato (o proyectada, si se responde en la Hoja de Respuestas).</li>
        <li>Hoja de Respuestas independiente (incluida) y bolígrafo.</li>
        <li>Cronómetro o reloj visible.</li>
        <li>La Clave de Respuestas y la Rúbrica de Speaking, solo en poder del examinador.</li>
      </ul>
    </div>
    '''
    return [body]


# ===========================================================================
# Datos del candidato / instrucciones para el candidato
# ===========================================================================

def build_candidate_info():
    body = f'''
    {section_title("Antes de empezar", "Datos e instrucciones para el candidato")}
    <div class="field-row">
      <div class="field"><label>Nombre completo</label><div class="line"></div></div>
      <div class="field"><label>Fecha</label><div class="line"></div></div>
    </div>
    <div class="field-row">
      <div class="field"><label>¿Cuántos años llevas estudiando inglés?</label><div class="line"></div></div>
      <div class="field"><label>¿Tienes algún título o certificado de inglés?</label><div class="line"></div></div>
    </div>
    <div class="info-card">
      <h3>Instrucciones</h3>
      <ul>
        <li>Esta prueba tiene 5 partes escritas (109 preguntas) y una parte oral (Speaking).</li>
        <li>Las preguntas están ordenadas de más fáciles a más difíciles dentro de cada parte.
        Es completamente normal que las últimas te resulten más difíciles — sigue intentándolo.</li>
        <li>Escribe todas tus respuestas en la <b>Hoja de Respuestas</b>, no en este cuadernillo.</li>
        <li>No se permite el uso de traductores, diccionarios ni dispositivos electrónicos.</li>
        <li>Si no sabes una respuesta, continúa con la siguiente. Puedes volver atrás si te sobra tiempo.</li>
        <li>Tiempo orientativo para la parte escrita: 90 minutos.</li>
      </ul>
    </div>
    <div class="info-card">
      <h3>¿Qué mide esta prueba?</h3>
      <p>Esta prueba evalúa tu nivel de inglés según el Marco Común Europeo de Referencia para las
      Lenguas (MCER), desde B1 (intermedio) hasta C2 (maestría). Combina el control de la gramática,
      la amplitud de vocabulario y, en la parte oral, tu capacidad real de comunicarte hablando.</p>
    </div>
    '''
    return [body]


# ===========================================================================
# PARTE 1
# ===========================================================================

def build_part1_pages():
    pages = []
    section_letters = ["A", "B", "C", "D"]
    for i in range(4):
        block = C.PART1[i * 15:(i + 1) * 15]
        items_html = "".join(
            mcq_html(i * 15 + j + 1, q, opts) for j, (_lvl, q, opts, _ans) in enumerate(block)
        )
        instructions = ('<p class="part-instructions">Elige la opción (A, B, C o D) que complete '
                         'correctamente cada frase. Escribe tus respuestas en la Hoja de Respuestas.</p>'
                         if i == 0 else "")
        body = (section_title("Parte 1 · Grammar &amp; Vocabulary",
                               "Elige la opción correcta",
                               f"Sección {section_letters[i]} &middot; Preguntas {i*15+1}–{i*15+15}")
                + instructions
                + f'<div class="cols2">{items_html}</div>')
        pages.append(body)
    return pages


# ===========================================================================
# PARTE 2 — Open Cloze
# ===========================================================================

def build_part2_page():
    cards = ""
    for idx, t in enumerate(C.PART2_TEXTS, start=1):
        cards += f'''
        <div class="cloze-card">
          <h4>Texto {idx}</h4>
          <div class="txt">{t["text"]}</div>
        </div>
        '''
    body = (section_title("Parte 2 · Open Cloze", "Completa los huecos",
                           "Escribe UNA sola palabra en cada hueco numerado. La palabra (0) es un ejemplo.")
            + cards)
    return [body]


# ===========================================================================
# PARTE 3 — Word Formation
# ===========================================================================

def build_part3_page():
    rows = ""
    for i, (sentence, root, _ans) in enumerate(C.PART3, start=1):
        rows += (f'<tr><td>{i}</td><td>{blankify(sentence)}</td>'
                 f'<td class="root">{root}</td><td class="ans"></td></tr>')
    body = (section_title("Parte 3 · Word Formation", "Forma la palabra correcta",
                           "Usa la palabra en mayúsculas para formar una palabra que encaje en el hueco.")
            + f'''<table class="wf-table">
                 <thead><tr><th>#</th><th>Frase</th><th>Palabra raíz</th><th>Tu respuesta</th></tr></thead>
                 <tbody>{rows}</tbody></table>''')
    return [body]


# ===========================================================================
# PARTE 4 — Key Word Transformation
# ===========================================================================

def build_part4_page():
    items = ""
    for i, (orig, key, prefix, suffix, _ans) in enumerate(C.PART4, start=1):
        gap_line = (f'{prefix} <span class="blank-line"></span> {suffix}'
                    if prefix else f'<span class="blank-line"></span> {suffix}')
        items += f'''
        <div class="kwt-item">
          <p class="orig"><span class="qn">{i}.</span> {orig}</p>
          <div class="kwt-row"><span class="badge">{key}</span> <span>{gap_line}</span></div>
        </div>
        '''
    body = (section_title("Parte 4 · Key Word Transformation",
                           "Reescribe la frase sin cambiar su significado",
                           "Completa el espacio usando entre 3 y 6 palabras, incluyendo la "
                           "palabra clave (que no puede modificarse).")
            + items)
    return [body]


# ===========================================================================
# PARTE 5 — Vocabulary in Use
# ===========================================================================

def build_part5_pages():
    coll_html = "".join(mcq_html(i, q, o) for i, (q, o, _a) in enumerate(C.PART5_COLLOCATIONS, start=1))
    phr_html = "".join(mcq_html(i, q, o) for i, (q, o, _a) in
                        enumerate(C.PART5_PHRASAL_VERBS, start=6))
    page1 = (section_title("Parte 5 · Vocabulary in Use", "Colocaciones y Phrasal Verbs",
                            "Elige la opción correcta (A, B, C o D).")
             + f'<div class="ans-block-title">Collocations (1–5)</div>{coll_html}'
             + f'<div class="ans-block-title">Phrasal Verbs (6–10)</div>{phr_html}')

    idi_html = "".join(mcq_html(i, q, o) for i, (q, o, _a) in enumerate(C.PART5_IDIOMS, start=11))
    page2 = (section_title("Parte 5 · Vocabulary in Use", "Idioms (Modismos)",
                            "Elige el significado correcto de cada expresión (A, B, C o D).")
             + idi_html)
    return [page1, page2]


# ===========================================================================
# HOJA DE RESPUESTAS
# ===========================================================================

def build_answer_sheet_pages():
    p1 = (f'<div class="ans-block-title">Parte 1 · Grammar &amp; Vocabulary (1–60)</div>'
          + ans_grid(1, 60, 10))
    p2 = (f'<div class="ans-block-title">Parte 2 · Open Cloze (1–16)</div>'
          + ans_grid(1, 16, 8))
    page1 = section_title("Hoja de Respuestas", "Parte 1 y Parte 2") + p1 + p2

    p3 = (f'<div class="ans-block-title">Parte 3 · Word Formation (1–10)</div>'
          + ans_grid(1, 10, 10))
    p5 = (f'<div class="ans-block-title">Parte 5 · Vocabulary in Use (1–15)</div>'
          + ans_grid(1, 15, 15))
    kwt_lines = "".join(
        f'<div class="kwt-ans-line"><span class="n">{i}.</span><span class="line"></span></div>'
        for i in range(1, 9)
    )
    p4 = f'<div class="ans-block-title">Parte 4 · Key Word Transformation (1–8)</div>{kwt_lines}'
    page2 = section_title("Hoja de Respuestas", "Parte 3, Parte 4 y Parte 5") + p3 + p4 + p5
    return [page1, page2]


# ===========================================================================
# SPEAKING TEST — guía del examinador
# ===========================================================================

def build_speaking_pages():
    # Página 1: overview + Part 1
    overview_table = '''
    <table class="wf-table timing-table">
      <thead><tr><th>Parte</th><th>Formato</th><th>Duración</th></tr></thead>
      <tbody>
        <tr><td>1. Interview</td><td>Preguntas personales, cara a cara con el examinador</td><td>2–3 min</td></tr>
        <tr><td>2. Long Turn</td><td>Monólogo de 1 minuto a partir de una tarjeta-tema</td><td>2 min</td></tr>
        <tr><td>3. Collaborative Task</td><td>Tarea conjunta de negociación/decisión</td><td>3–4 min</td></tr>
        <tr><td>4. Discussion</td><td>Debate guiado sobre temas más generales/abstractos</td><td>3–4 min</td></tr>
      </tbody>
    </table>
    '''
    p1_themes = "".join(
        f'<div class="q-theme">{theme}</div><ul class="q-list">'
        + "".join(f"<li>{q}</li>" for q in qs) + "</ul>"
        for theme, qs in C.SPEAKING_PART1_QUESTIONS
    )
    part1_block = f'''
    <div class="speak-part">
      <h3>Part 1 — Interview</h3>
      <div class="dur">2–3 minutos</div>
      <p class="desc">Preguntas de calentamiento para establecer un nivel base. Elige 4–5 preguntas de entre los siguientes bloques temáticos.</p>
      {p1_themes}
    </div>
    '''
    page1 = section_title("Speaking Test", "Guía del examinador",
                           "Formato en 4 partes, adaptado del examen oral de Cambridge English.") \
        + overview_table + part1_block

    # Página 2: Part 2
    p2_cards = "".join(
        f'<div class="card-topic"><span class="lvl">{lvl}</span><div class="ttl">{title}</div>'
        f'<div class="body">{desc}</div></div>'
        for lvl, title, desc in C.SPEAKING_PART2_CARDS
    )
    page2 = section_title("Speaking Test", "Part 2 — Individual Long Turn",
                           "1 minuto de monólogo + 1 pregunta de seguimiento. Entrega UNA tarjeta al "
                           "candidato: empieza por la B1 si no conoces su nivel y sube de tarjeta si "
                           "responde con soltura.") + p2_cards

    # Página 3: Part 3
    scen_html = ""
    for lvl, title, desc, opts in C.SPEAKING_PART3_SCENARIOS:
        opts_html = "".join(f"<li>{o}</li>" for o in opts)
        scen_html += f'''
        <div class="card-topic">
          <span class="lvl">{lvl}</span><div class="ttl">{title}</div>
          <div class="body">{desc}</div>
          <ul class="opt-list">{opts_html}</ul>
        </div>
        '''
    page3 = section_title("Speaking Test", "Part 3 — Collaborative Task",
                           "3–4 minutos. Idealmente con dos candidatos; con uno solo, el examinador "
                           "puede asumir el otro rol.") + scen_html

    # Página 4: Part 4
    disc_html = ""
    for theme, qs in C.SPEAKING_PART4_DISCUSSION:
        qs_html = "".join(f"<li>{q}</li>" for q in qs)
        disc_html += f'<div class="q-theme">{theme}</div><ul class="q-list">{qs_html}</ul>'
    page4 = section_title("Speaking Test", "Part 4 — Discussion",
                           "3–4 minutos. Preguntas más abstractas y generales que amplían el tema de la Part 3.") \
        + f'<div class="speak-part">{disc_html}</div>'

    return [page1, page2, page3, page4]


# ===========================================================================
# RÚBRICA DE SPEAKING
# ===========================================================================

def build_rubric_page():
    head = "".join(f"<th>{lvl}</th>" for lvl in ["B1 (1 pt)", "B2 (2 pts)", "C1 (3 pts)", "C2 (4 pts)"])
    rows = ""
    for crit in C.SPEAKING_RUBRIC:
        cells = "".join(f'<td>{crit["bands"][lvl]}</td>' for lvl in ["B1", "B2", "C1", "C2"])
        rows += f'<tr><td class="crit">{crit["criterion"]}<br><span style="font-weight:400;opacity:.7;font-size:.6rem">{crit["criterion_es"]}</span></td>{cells}</tr>'

    bands_rows = "".join(
        f"<tr><td>{lo}–{hi}</td><td>{lvl}</td></tr>" for lo, hi, lvl in C.SPEAKING_SCORING_BANDS
    )

    page1 = (section_title("Rúbrica de evaluación oral", "Speaking Assessment Grid",
                            "Puntúa cada criterio de 1 (B1) a 4 (C2) según el desempeño global del "
                            "candidato en las 4 partes.")
             + f'<table class="rubric-table"><thead><tr><th>Criterio</th>{head}</tr></thead><tbody>{rows}</tbody></table>')

    page2 = (section_title("Rúbrica de evaluación oral", "Puntuación y conversión a nivel",
                            "Suma los 4 criterios (rango 4–16) y convierte el resultado en un nivel oral.")
             + '''<div class="two-col">
                    <div>
                      <table class="plain-table">
                        <thead><tr><th>Suma (4–16)</th><th>Nivel oral</th></tr></thead>
                        <tbody>''' + bands_rows + '''</tbody>
                      </table>
                    </div>
                    <div>
                      <div class="score-box">
                        <div class="sb"><div class="lab">Gram. &amp; Vocab.</div><div class="val">___</div></div>
                        <div class="sb"><div class="lab">Discourse</div><div class="val">___</div></div>
                      </div>
                      <div class="score-box">
                        <div class="sb"><div class="lab">Pronunciation</div><div class="val">___</div></div>
                        <div class="sb"><div class="lab">Interaction</div><div class="val">___</div></div>
                      </div>
                      <div class="score-box"><div class="sb" style="border-color:var(--blue)">
                        <div class="lab">Total / Nivel oral</div><div class="val">___ &rarr; ____</div></div></div>
                    </div>
                  </div>''')
    return [page1, page2]


# ===========================================================================
# CLAVE DE RESPUESTAS
# ===========================================================================

def build_answer_key_pages():
    block_names = ["B1 (1–15)", "B2 (16–30)", "C1 (31–45)", "C2 (46–60)"]
    p1_html = ""
    for i, name in enumerate(block_names):
        letters = [LETTERS[ans] for (_l, _q, _o, ans) in C.PART1[i * 15:(i + 1) * 15]]
        p1_html += f'<div class="key-h4">Parte 1 — Bloque {name}</div>' + key_grid(i * 15 + 1, letters, 15)

    p5_letters = [LETTERS[a] for (_q, _o, a) in C.PART5]
    p5_html = f'<div class="key-h4">Parte 5 · Vocabulary in Use (1–15)</div>' + key_grid(1, p5_letters, 15)

    page1 = (section_title("Clave de Respuestas", "Parte 1 y Parte 5", "Confidencial — solo para el examinador")
             + '<div class="confidential-banner">Solo para el profesor / examinador — No entregar al alumnado</div>'
             + p1_html + p5_html)

    p2_html = ""
    for idx, t in enumerate(C.PART2_TEXTS, start=1):
        entries = "".join(
            f'<div>({n}) {" / ".join(opts)}</div>' for n, opts in t["gaps"]
        )
        p2_html += f'<div class="key-h4">Texto {idx} ({t["level"]})</div><div class="key-list">{entries}</div>'

    p3_html = "".join(f'<div>{i}. {ans}</div>' for i, (_s, _r, ans) in enumerate(C.PART3, start=1))
    p3_html = f'<div class="key-h4">Parte 3 · Word Formation</div><div class="key-list">{p3_html}</div>'

    p4_html = ""
    for i, (orig, key, prefix, suffix, ans) in enumerate(C.PART4, start=1):
        full = f"{prefix} {ans} {suffix}".strip() if prefix else f"{ans} {suffix}".strip()
        p4_html += f'<div>{i}. <b>{full}</b></div>'
    p4_html = (f'<div class="key-h4">Parte 4 · Key Word Transformation</div>'
               f'<div class="key-list">{p4_html}</div>'
               '<p style="font-size:.76rem;opacity:.75;margin-top:4px">Criterio de corrección: 2 puntos '
               'si la frase es gramaticalmente correcta y usa bien la palabra clave; 1 punto si hay un '
               'error menor que no afecta al significado ni a la estructura clave; 0 puntos si la palabra '
               'clave falta, se modifica, o el significado cambia.</p>')

    page2 = (section_title("Clave de Respuestas", "Parte 2, Parte 3 y Parte 4", "Confidencial — solo para el examinador")
             + '<div class="confidential-banner">Solo para el profesor / examinador — No entregar al alumnado</div>'
             + p2_html + p3_html + p4_html)
    return [page1, page2]


# ===========================================================================
# GUÍA DE PUNTUACIÓN Y NIVELES
# ===========================================================================

def build_scoring_guide_page():
    bands_rows = "".join(
        f"<tr><td>{lo}–{hi}</td><td><b>{lvl}</b></td><td>{desc}</td></tr>"
        for lo, hi, lvl, desc in C.SCORING["bands"]
    )
    body = (section_title("Guía de puntuación", "De la puntuación bruta al nivel MCER",
                           "Prueba escrita: 117 puntos posibles (109 ítems, Parte 4 vale 2 puntos por ítem).")
            + f'''<table class="plain-table">
                 <thead><tr><th>Puntuación total</th><th>Nivel</th><th>Descripción</th></tr></thead>
                 <tbody>{bands_rows}</tbody></table>'''
            + '''<div class="info-card" style="margin-top:14px;">
                  <h3>Diagnóstico por bloque (Parte 1)</h3>
                  <p>Para confirmar el nivel, comprueba el dominio por bloque: el candidato debería acertar
                  &ge;80% (12/15) en su nivel y en todos los inferiores, y &lt;60% (9/15) en el bloque siguiente.
                  Si el patrón no es claro (por ejemplo, domina C1 pero falla mucho en B2), trátalo como
                  perfil irregular y confírmalo con la parte oral.</p>
                  <div class="score-box">
                    <div class="sb"><div class="lab">B1 (/15)</div><div class="val">___</div></div>
                    <div class="sb"><div class="lab">B2 (/15)</div><div class="val">___</div></div>
                    <div class="sb"><div class="lab">C1 (/15)</div><div class="val">___</div></div>
                    <div class="sb"><div class="lab">C2 (/15)</div><div class="val">___</div></div>
                  </div>
                </div>
                <div class="info-card">
                  <h3>Nivel final: combinar escrito + oral</h3>
                  <table class="plain-table">
                    <thead><tr><th>Escrito</th><th>Oral</th><th>Nivel final recomendado</th></tr></thead>
                    <tbody>
                      <tr><td>Mismo nivel</td><td>Mismo nivel</td><td>Ese nivel</td></tr>
                      <tr><td colspan="2">Bandas adyacentes (1 de diferencia)</td>
                          <td>El nivel más bajo de los dos; revisar en las 2 primeras semanas de clase</td></tr>
                      <tr><td colspan="2">Diferencia de 2 bandas o más</td>
                          <td>Resultado inconsistente — repetir o confirmar con una sesión adicional</td></tr>
                    </tbody>
                  </table>
                </div>''')
    return [body]


# ===========================================================================
# INFORME DE RESULTADOS
# ===========================================================================

def build_results_summary_page():
    body = f'''
    {section_title("Informe de Resultados", "Nivel de Inglés — Nexo Académico")}
    <div class="field-row">
      <div class="field"><label>Candidato / Candidata</label><div class="line"></div></div>
      <div class="field"><label>Fecha</label><div class="line"></div></div>
    </div>
    <div class="kpi-row">
      <div class="kpi-card"><div class="lab">Parte 1 (/60)</div><div class="line"></div></div>
      <div class="kpi-card"><div class="lab">Parte 2 (/16)</div><div class="line"></div></div>
      <div class="kpi-card"><div class="lab">Parte 3 (/10)</div><div class="line"></div></div>
      <div class="kpi-card"><div class="lab">Parte 4 (/16)</div><div class="line"></div></div>
      <div class="kpi-card"><div class="lab">Parte 5 (/15)</div><div class="line"></div></div>
    </div>
    <div class="kpi-row">
      <div class="kpi-card" style="border-top-color:var(--green)"><div class="lab">Total escrito (/117)</div><div class="line"></div></div>
      <div class="kpi-card" style="border-top-color:var(--amber)"><div class="lab">Total oral (/16)</div><div class="line"></div></div>
    </div>
    <div class="final-level">
      <div class="lab">Nivel final MCER / CEFR</div>
      <div class="lvl-line">
        <div class="lvl-opt">B1</div><div class="lvl-opt">B2</div><div class="lvl-opt">C1</div><div class="lvl-opt">C2</div>
      </div>
    </div>
    <div class="two-col">
      <div class="puntos-grupo">
        <h4>Puntos fuertes</h4>
        <div class="wline"></div><div class="wline"></div><div class="wline"></div>
      </div>
      <div class="puntos-grupo atencion">
        <h4>Áreas de atención</h4>
        <div class="wline"></div><div class="wline"></div><div class="wline"></div>
      </div>
    </div>
    <div class="info-card">
      <h3>Recomendación de clase / grupo</h3>
      <div class="wline"></div><div class="wline"></div>
    </div>
    <div class="field-row" style="margin-top:24px;">
      <div class="field"><label>Firma del examinador</label><div class="line"></div></div>
      <div class="field"><label>Próxima revisión</label><div class="line"></div></div>
    </div>
    '''
    return [body]


# ===========================================================================
# ENSAMBLADO FINAL
# ===========================================================================

def main():
    pre_cover = build_cover()
    overview_pages = build_overview()
    pre_candidate = build_candidate_info()
    p1_pages = build_part1_pages()
    p2_pages = build_part2_page()
    p3_pages = build_part3_page()
    p4_pages = build_part4_page()
    p5_pages = build_part5_pages()
    ans_sheet = build_answer_sheet_pages()
    speaking = build_speaking_pages()
    rubric = build_rubric_page()
    key_pages = build_answer_key_pages()
    scoring = build_scoring_guide_page()
    results = build_results_summary_page()

    section_map = [
        ("Portada", pre_cover, "cover"),
        ("Instrucciones para el examinador", overview_pages, "normal"),
        ("Datos del candidato", pre_candidate, "normal"),
        ("Parte 1 · Grammar &amp; Vocabulary", p1_pages, "normal"),
        ("Parte 2 · Open Cloze", p2_pages, "normal"),
        ("Parte 3 · Word Formation", p3_pages, "normal"),
        ("Parte 4 · Key Word Transformation", p4_pages, "normal"),
        ("Parte 5 · Vocabulary in Use", p5_pages, "normal"),
        ("Hoja de Respuestas", ans_sheet, "normal"),
        ("Speaking Test", speaking, "normal"),
        ("Rúbrica de Speaking", rubric, "normal"),
        ("Clave de Respuestas", key_pages, "confidential"),
        ("Guía de puntuación", scoring, "normal"),
        ("Informe de Resultados", results, "normal"),
    ]

    all_pages = []
    for label, htmls, variant in section_map:
        for h in htmls:
            all_pages.append((label, h, variant))

    total_pages = len(all_pages)

    rendered = []
    for i, (label, body_html, variant) in enumerate(all_pages, start=1):
        if variant == "cover":
            rendered.append(f'<section class="page cover-page">{body_html}</section>')
            continue
        banner = ""
        rendered.append(f'''<section class="page">
          <div class="runhead">
            <div class="brand"><img src="data:image/png;base64,{LOGO_B64}" alt="Nexo"><span>Nexo Académico</span></div>
            <div class="sect">English Placement Test &middot; {label}</div>
          </div>
          <div class="page-body">{body_html}</div>
          <div class="runfoot"><span>B1 &middot; B2 &middot; C1 &middot; C2 — English Placement Test</span><span>Página {i} de {total_pages}</span></div>
        </section>''')

    html_doc = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Nexo Académico — English Placement Test</title>
<style>{CSS}</style>
</head>
<body>
{''.join(rendered)}
</body>
</html>'''

    OUT_HTML.write_text(html_doc, encoding="utf-8")
    print(f"HTML escrito: {OUT_HTML} ({len(html_doc)} bytes, {total_pages} páginas)")

    cmd = [
        "/opt/pw-browsers/chromium",
        "--headless=new", "--disable-gpu", "--no-sandbox",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={OUT_PDF}",
        f"file://{OUT_HTML}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        raise SystemExit(result.returncode)
    print(f"PDF generado: {OUT_PDF}")


if __name__ == "__main__":
    main()
