"""Genera la ficha de un profesor de Nexo Académico a partir de un JSON.

Uso: python3 generar_ficha.py datos/<profesor>.json
Salida: salida/<Nombre_Apellidos_Año>.html, .png y .pdf (PNG y PDF requieren Playwright).
"""
import base64
import html
import json
import mimetypes
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent
LOGO = BASE / "assets" / "logo_nexo.png"


def data_uri(path):
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(Path(path).read_bytes()).decode()}"


def nombre_archivo(nombre, anio):
    """Nombre_Apellidos_Año, sin tildes ni espacios (p. ej. Miryam_Iborra_Garcia_2026)."""
    t = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return "_".join(re.findall(r"[A-Za-z0-9]+", t) + [str(anio)])


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
    pos = f' style="object-position:{e(d["foto_posicion"])}"' if d.get("foto_posicion") else ""
    foto = (f'<img class="foto" src="{foto_uri}" alt="{e(nombre)}"{pos}>' if foto_uri
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
        titulo_idi = "Idiomas y certificados" if any(i.get("certificado") for i in d["idiomas"]) else "Idiomas"
        secciones.append(seccion(n, titulo_idi, f'<div class="idiomas">{filas}</div>'))
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
body {{ font-family:var(--sans); color:var(--white); display:flex; justify-content:center; padding:24px 0; }}
/* La ficha es una hoja A4 completa (210 × 297 mm). */
.ficha {{ width:210mm; height:297mm; overflow:hidden; position:relative; flex-shrink:0;
  display:flex; flex-direction:column;
  background:radial-gradient(circle at 18% 10%, rgba(233,209,143,.08), transparent 36%),
             linear-gradient(155deg, #070c1b 0%, var(--navy) 52%, var(--blue) 100%);
  padding:15mm 15mm 11mm; }}
.top {{ display:flex; justify-content:space-between; align-items:center; }}
.top img {{ height:58px; }}
.tag {{ font-size:12px; letter-spacing:.24em; color:var(--gold); font-weight:700; }}
.rule {{ height:1px; margin:22px 0 34px; background:linear-gradient(90deg, transparent, var(--gold2), transparent); opacity:.6; }}
.head {{ display:flex; gap:32px; align-items:center; }}
.foto {{ width:168px; height:168px; border-radius:50%; object-fit:cover; flex-shrink:0;
  border:4px solid var(--gold2); box-shadow:0 0 0 9px rgba(200,162,74,.12); }}
.foto.ini {{ display:flex; align-items:center; justify-content:center; font-family:var(--serif); font-weight:700;
  font-size:56px; color:var(--navy); background:linear-gradient(145deg, var(--gold), var(--gold2)); }}
.pill {{ display:inline-block; font-size:11px; letter-spacing:.18em; font-weight:700; color:var(--gold);
  border:1px solid rgba(233,209,143,.55); border-radius:999px; padding:6px 14px; margin-bottom:12px; }}
h1 {{ font-family:var(--serif); font-size:42px; line-height:1.08; font-weight:700; }}
.cargo {{ font-family:var(--serif); font-style:italic; color:var(--gold); font-size:22px; margin-top:6px; }}
.meta {{ color:var(--muted); font-size:15px; margin-top:8px; }}
.chips {{ margin-top:12px; display:flex; flex-wrap:wrap; gap:8px; }}
.chip {{ font-size:12px; font-weight:700; letter-spacing:.07em; color:var(--navy);
  background:var(--gold3); border-radius:999px; padding:5px 13px; }}
.contacto {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin:34px 0 0; }}
.ct {{ background:rgba(12,18,36,.75); border:1px solid rgba(255,255,255,.08); border-radius:14px; padding:14px 18px;
  display:flex; flex-direction:column; gap:5px; font-size:16px; word-break:break-word; }}
.ct-l {{ font-size:10.5px; letter-spacing:.2em; text-transform:uppercase; color:var(--dim); }}
/* La rejilla absorbe el alto sobrante para que la ficha llene la hoja. */
.grid {{ flex:1; display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:18px; }}
.sec {{ background:rgba(12,18,36,.75); border:1px solid rgba(255,255,255,.08); border-radius:16px; padding:22px 24px; }}
.sec.full {{ grid-column:1 / -1; }}
.sec-h {{ display:flex; align-items:baseline; gap:12px; margin-bottom:16px; padding-bottom:12px;
  border-bottom:1px solid rgba(233,209,143,.14); }}
.num {{ font-family:var(--serif); color:var(--gold); font-size:14px; }}
h3 {{ font-family:var(--serif); font-size:21px; font-weight:700; }}
.txt {{ color:#d6d4cc; font-size:16px; line-height:1.55; }}
.lista {{ list-style:none; display:flex; flex-direction:column; gap:14px; }}
.lista li {{ border-left:3px solid var(--gold2); padding-left:13px; }}
.fila {{ display:flex; justify-content:space-between; gap:10px; }}
.tit {{ font-size:16px; font-weight:700; color:#f1efe8; line-height:1.3; }}
.fecha {{ font-size:13px; color:var(--gold3); white-space:nowrap; }}
.det {{ font-size:14.5px; color:var(--muted); margin-top:4px; line-height:1.45; }}
.idiomas {{ display:flex; flex-direction:column; gap:14px; }}
.idi {{ display:flex; flex-wrap:wrap; align-items:center; gap:10px; font-size:16px; }}
.idi-n {{ font-weight:700; min-width:110px; }}
.idi-v {{ font-family:var(--serif); font-weight:700; color:var(--gold); font-size:19px; }}
.idi-c {{ font-size:13px; color:var(--muted); border:1px solid rgba(255,255,255,.14); border-radius:7px; padding:3px 9px; }}
.apts {{ display:flex; flex-wrap:wrap; gap:8px; }}
.apt {{ font-size:14.5px; color:#e7e7ea; border:1px solid rgba(233,209,143,.35); border-radius:999px; padding:6px 14px; }}
.foot {{ display:flex; justify-content:space-between; margin-top:20px; padding-top:14px;
  border-top:1px solid rgba(255,255,255,.08); font-size:12px; color:var(--dim); }}
@page {{ size:A4; margin:0; }}
@media print {{ html,body {{ background:none; }} body {{ padding:0; display:block; }} }}
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
    nombre = nombre_archivo(d["nombre"], d.get("anio", date.today().year))
    html_path = salida / f"{nombre}.html"
    html_path.write_text(render(d, foto_uri), encoding="utf-8")
    print(html_path)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium") if Path("/opt/pw-browsers/chromium").is_file() else p.chromium.launch()
        pg = b.new_page(viewport={"width": 900, "height": 1200}, device_scale_factor=2)
        pg.goto(html_path.as_uri())
        pg.locator(".ficha").screenshot(path=str(salida / f"{nombre}.png"))
        pg.pdf(path=str(salida / f"{nombre}.pdf"), format="A4", print_background=True, prefer_css_page_size=True)
        b.close()
    print(salida / f"{nombre}.png")


if __name__ == "__main__":
    main()
