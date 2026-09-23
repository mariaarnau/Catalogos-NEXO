"""Genera la ficha de un profesor de Nexo Académico a partir de un JSON.

Uso: python3 generar_ficha.py datos/<profesor>.json
Salida: salida/<slug>.html, .png y .pdf (PNG y PDF requieren Playwright).
"""
import base64
import html
import json
import mimetypes
import re
import sys
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parent
LOGO = BASE / "assets" / "logo_nexo.png"


def data_uri(path):
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(Path(path).read_bytes()).decode()}"


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def e(t):
    return html.escape(str(t))


def iniciales(nombre):
    partes = [p for p in nombre.split() if p]
    return "".join(p[0] for p in partes[:2]).upper()


def bloque_lista(items):
    filas = []
    for it in items:
        titulo = e(it["titulo"])
        detalle = f'<div class="det">{e(it["detalle"])}</div>' if it.get("detalle") else ""
        fecha = f'<span class="fecha">{e(it["fecha"])}</span>' if it.get("fecha") else ""
        filas.append(f'<li><div class="fila"><span class="tit">{titulo}</span>{fecha}</div>{detalle}</li>')
    return f'<ul class="lista">{"".join(filas)}</ul>'


def seccion(num, titulo, cuerpo, full=False):
    clase = "sec full" if full else "sec"
    return (f'<section class="{clase}"><div class="sec-h"><span class="num">{num:02d}</span>'
            f'<h3>{e(titulo)}</h3></div>{cuerpo}</section>')


def render(d, foto_uri):
    nombre = d["nombre"]
    foto = (f'<img class="foto" src="{foto_uri}" alt="{e(nombre)}">' if foto_uri
            else f'<div class="foto ini">{e(iniciales(nombre))}</div>')

    meta = []
    if d.get("edad"):
        meta.append(f'{e(d["edad"])} años')
    if d.get("ubicacion"):
        meta.append(e(d["ubicacion"]))
    meta_html = " · ".join(meta)

    materias = "".join(f'<span class="chip">{e(m)}</span>' for m in d.get("materias", []))

    contacto = []
    if d.get("telefono"):
        contacto.append(f'<div class="ct"><span class="ct-l">Teléfono</span><span>{e(d["telefono"])}</span></div>')
    if d.get("email"):
        contacto.append(f'<div class="ct"><span class="ct-l">Email</span><span>{e(d["email"])}</span></div>')

    secciones = []
    n = 1
    if d.get("situacion_actual"):
        secciones.append(seccion(n, "Situación actual", f'<p class="txt">{e(d["situacion_actual"])}</p>', full=True))
        n += 1
    if d.get("estudios"):
        secciones.append(seccion(n, "Formación", bloque_lista(d["estudios"])))
        n += 1
    if d.get("idiomas"):
        filas = "".join(
            f'<div class="idi"><span class="idi-n">{e(i["idioma"])}</span>'
            f'<span class="idi-v">{e(i["nivel"])}</span>'
            + (f'<span class="idi-c">{e(i["certificado"])}</span>' if i.get("certificado") else "")
            + "</div>"
            for i in d["idiomas"])
        secciones.append(seccion(n, "Idiomas y certificados", f'<div class="idiomas">{filas}</div>'))
        n += 1
    if d.get("experiencia_docente"):
        secciones.append(seccion(n, "Experiencia docente", bloque_lista(d["experiencia_docente"])))
        n += 1
    if d.get("aptitudes"):
        chips = "".join(f'<span class="apt">{e(a)}</span>' for a in d["aptitudes"])
        secciones.append(seccion(n, "Aptitudes", f'<div class="apts">{chips}</div>'))
        n += 1

    # En la rejilla de dos columnas, una sección suelta al final ocupa todo el ancho.
    resto = [x for x in secciones if 'class="sec full"' not in x]
    if len(resto) % 2:
        i = secciones.index(resto[-1])
        secciones[i] = secciones[i].replace('class="sec"', 'class="sec full"', 1)

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ficha profesor · {e(nombre)}</title>
<style>
:root {{
  --navy:#091225; --navy2:#0c1224; --blue:#14285a; --card:#0b1428;
  --gold:#e9d18f; --gold2:#c8a24a; --gold3:#cdb57a;
  --white:#ffffff; --muted:#a49f8e; --dim:#7d7f8a; --line:rgba(233,209,143,.18);
  --serif:"Liberation Serif","Times New Roman",Georgia,serif;
  --sans:"Liberation Sans",Arial,Helvetica,sans-serif;
}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{ background:#05080f; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
body {{ font-family:var(--sans); color:var(--white); display:flex; justify-content:center; padding:24px 16px; }}
.ficha {{ width:100%; max-width:720px; border-radius:18px; overflow:hidden; position:relative;
  background:radial-gradient(circle at 18% 12%, rgba(233,209,143,.07), transparent 38%),
             linear-gradient(150deg, #070c1b 0%, var(--navy) 55%, var(--blue) 100%);
  border:1px solid var(--line); padding:32px 36px 26px; }}
.top {{ display:flex; justify-content:space-between; align-items:center; }}
.top img {{ height:44px; }}
.tag {{ font-size:10px; letter-spacing:.22em; color:var(--gold); font-weight:700; }}
.rule {{ height:1px; margin:18px 0 26px; background:linear-gradient(90deg, transparent, var(--gold2), transparent); opacity:.55; }}
.head {{ display:flex; gap:24px; align-items:center; }}
.foto {{ width:118px; height:118px; border-radius:50%; object-fit:cover; flex-shrink:0;
  border:3px solid var(--gold2); box-shadow:0 0 0 6px rgba(200,162,74,.12); }}
.foto.ini {{ display:flex; align-items:center; justify-content:center; font-family:var(--serif); font-weight:700;
  font-size:40px; color:var(--navy); background:linear-gradient(145deg, var(--gold), var(--gold2)); }}
.pill {{ display:inline-block; font-size:9.5px; letter-spacing:.16em; font-weight:700; color:var(--gold);
  border:1px solid rgba(233,209,143,.55); border-radius:999px; padding:5px 12px; margin-bottom:10px; }}
h1 {{ font-family:var(--serif); font-size:31px; line-height:1.1; font-weight:700; }}
.cargo {{ font-family:var(--serif); font-style:italic; color:var(--gold); font-size:17px; margin-top:5px; }}
.meta {{ color:var(--muted); font-size:12.5px; margin-top:6px; }}
.chips {{ margin-top:10px; display:flex; flex-wrap:wrap; gap:6px; }}
.chip {{ font-size:10.5px; font-weight:700; letter-spacing:.06em; color:var(--navy);
  background:var(--gold3); border-radius:999px; padding:4px 10px; }}
.contacto {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:10px; margin:24px 0 6px; }}
.ct {{ background:rgba(12,18,36,.75); border:1px solid rgba(255,255,255,.07); border-radius:12px; padding:10px 14px;
  display:flex; flex-direction:column; gap:3px; font-size:13px; word-break:break-word; }}
.ct-l {{ font-size:9px; letter-spacing:.18em; text-transform:uppercase; color:var(--dim); }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:16px; }}
.sec {{ background:rgba(12,18,36,.75); border:1px solid rgba(255,255,255,.07); border-radius:14px; padding:16px 18px; }}
.sec.full {{ grid-column:1 / -1; }}
.sec-h {{ display:flex; align-items:baseline; gap:10px; margin-bottom:10px; }}
.num {{ font-family:var(--serif); color:var(--gold); font-size:12px; }}
h3 {{ font-family:var(--serif); font-size:16px; font-weight:700; }}
.txt {{ color:#d6d4cc; font-size:13px; line-height:1.5; }}
.lista {{ list-style:none; display:flex; flex-direction:column; gap:9px; }}
.lista li {{ border-left:2px solid var(--gold2); padding-left:10px; }}
.fila {{ display:flex; justify-content:space-between; gap:8px; }}
.tit {{ font-size:13px; font-weight:700; color:#f1efe8; }}
.fecha {{ font-size:11px; color:var(--gold3); white-space:nowrap; }}
.det {{ font-size:12px; color:var(--muted); margin-top:2px; line-height:1.4; }}
.idiomas {{ display:flex; flex-direction:column; gap:8px; }}
.idi {{ display:flex; flex-wrap:wrap; align-items:center; gap:8px; font-size:13px; }}
.idi-n {{ font-weight:700; min-width:70px; }}
.idi-v {{ font-family:var(--serif); font-weight:700; color:var(--gold); font-size:15px; }}
.idi-c {{ font-size:11px; color:var(--muted); border:1px solid rgba(255,255,255,.12); border-radius:6px; padding:2px 7px; }}
.apts {{ display:flex; flex-wrap:wrap; gap:6px; }}
.apt {{ font-size:12px; color:#e7e7ea; border:1px solid rgba(233,209,143,.35); border-radius:999px; padding:4px 11px; }}
.foot {{ display:flex; justify-content:space-between; margin-top:22px; padding-top:14px;
  border-top:1px solid rgba(255,255,255,.08); font-size:10.5px; color:var(--dim); }}
@media (max-width:560px) {{
  .ficha {{ padding:24px 18px; }}
  .head {{ flex-direction:column; text-align:center; }}
  .chips {{ justify-content:center; }}
  .grid {{ grid-template-columns:1fr; }}
}}
@page {{ size:A4; margin:10mm; }}
@media print {{ html,body {{ background:none; }} body {{ padding:0; }} .ficha {{ max-width:none; }} }}
</style></head>
<body>
<article class="ficha">
  <div class="top"><img src="{data_uri(LOGO)}" alt="Nexo Académico"><span class="tag">FICHA DE PROFESOR</span></div>
  <div class="rule"></div>
  <div class="head">
    {foto}
    <div>
      <span class="pill">EQUIPO DOCENTE NEXO</span>
      <h1>{e(nombre)}</h1>
      {f'<div class="cargo">{e(d["titular"])}</div>' if d.get("titular") else ""}
      {f'<div class="meta">{meta_html}</div>' if meta_html else ""}
      {f'<div class="chips">{materias}</div>' if materias else ""}
    </div>
  </div>
  {f'<div class="contacto">{"".join(contacto)}</div>' if contacto else ""}
  <div class="grid">{"".join(secciones)}</div>
  <div class="foot"><span>Nexo Académico · Equipo docente</span><span>nexoacademico.com</span></div>
</article>
</body></html>"""


def main():
    ruta = Path(sys.argv[1])
    d = json.loads(ruta.read_text(encoding="utf-8"))
    foto = d.get("foto")
    foto_uri = data_uri((ruta.parent / foto).resolve()) if foto else None
    salida = BASE / "salida"
    salida.mkdir(exist_ok=True)
    nombre = slug(d["nombre"])
    html_path = salida / f"{nombre}.html"
    html_path.write_text(render(d, foto_uri), encoding="utf-8")
    print(html_path)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium") if Path("/opt/pw-browsers/chromium").is_file() else p.chromium.launch()
        pg = b.new_page(viewport={"width": 800, "height": 1000}, device_scale_factor=2)
        pg.goto(html_path.as_uri())
        pg.locator(".ficha").screenshot(path=str(salida / f"{nombre}.png"))
        pg.pdf(path=str(salida / f"{nombre}.pdf"), format="A4", print_background=True)
        b.close()
    print(salida / f"{nombre}.png")


if __name__ == "__main__":
    main()
