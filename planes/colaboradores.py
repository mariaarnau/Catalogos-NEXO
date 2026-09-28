#!/usr/bin/env python3
"""Documento del programa de colaboradores externos de NEXO Académico.

Usa el mismo diseño (CSS, logo, tipografías) que los planes personalizados.
Uso:  python3 planes/colaboradores.py
Salida: planes/output/NEXO_Programa_Colaboradores.html y .pdf
"""
import base64
import subprocess

import generar_plan as gp
from generar_plan import ROOT, TARIFAS, e, eur, footer

COMISION = 0.10
BONOS = (4, 8, 12)
FILAS = [("Primaria", "primaria", "casa_alumno", "Presencial"),
         ("ESO", "eso", "casa_alumno", "Presencial"),
         ("ESO", "eso", "online", "Online"),
         ("Bachillerato", "bachillerato", "casa_alumno", "Presencial"),
         ("Bachillerato", "bachillerato", "online", "Online"),
         ("Universidad", "universidad", "casa_alumno", "Presencial"),
         ("Universidad", "universidad", "online", "Online")]


def hdr(label):
    return (f'<div class="hdr"><img class="logo-sm" src="{gp.LOGO_URI}"><span class="hdr-r">{e(label)}</span></div>'
            f'<div class="rule"></div>')


def portada():
    return f'''<section class="page cover glow">
  <img class="logo-lg" src="{gp.LOGO_URI}">
  <div class="pill gold">DOCUMENTO PARA COLABORADORES</div>
  <h1 class="cover-h">Programa de colaboradores<br><em>NEXO Académico</em></h1>
  <p class="cover-sub">Para psicólogos, psicopedagogos y profesionales que recomiendan NEXO a las familias con las que trabajan.</p>
  <div class="name-card"><div class="nm big">10% de comisión</div><div class="cs">SOBRE EL PRIMER BONO DE CADA ALUMNO</div></div>
  <div class="cover-foot">CURSO 2026–2027 — PROGRAMA DE COLABORACIÓN</div>
</section>'''


def como_funciona():
    return f'''<section class="page">
  {hdr("CÓMO FUNCIONA")}
  <div class="pill gold">EL PROGRAMA</div>
  <h2>Recomiendas, la familia confía, tú cobras</h2>
  <p class="lead">Si trabajas con familias que necesitan apoyo académico, puedes recomendarles NEXO. Por cada alumno que contrate su primer bono, te llevas el 10% de lo que paga la familia.</p>
  <div class="steps">
    <div><span class="num">01</span><h4>Recomiendas NEXO</h4><p>Le hablas de nosotros a una familia que busca clases particulares o apoyo en los estudios.</p></div>
    <div><span class="num">02</span><h4>La familia contrata</h4><p>El alumno empieza con nosotros y contrata su primer bono de 4h, 8h o 12h.</p></div>
    <div><span class="num">03</span><h4>Te pagamos el 10%</h4><p>En cuanto la familia abona el bono, te transferimos tu comisión por Bizum o transferencia.</p></div>
  </div>
  <div class="stats">
    <div><b>10%</b><span>DEL PRIMER BONO</span></div>
    <div><b>1</b><span>PAGO ÚNICO POR ALUMNO</span></div>
    <div><b>Directo</b><span>SIN ESPERAR A LA 1ª CLASE</span></div>
    <div><b>Bizum</b><span>O TRANSFERENCIA</span></div>
  </div>
  {footer("Nexo Académico · Programa de colaboradores")}
</section>'''


def regla():
    ej_precio = TARIFAS["bachillerato"]["precios"]["casa_alumno"][12]
    return f'''<section class="page glow">
  {hdr("LA COMISIÓN")}
  <div class="pill gold">LA REGLA, CLARA</div>
  <h2>Qué genera comisión y qué no</h2>
  <p class="lead">Una sola regla, sin letra pequeña: el 10% del primer bono que contrata cada alumno que nos recomiendas.</p>
  <div class="flujo">
    <div class="fl no"><small>BONO DE PRUEBA</small><b>2h</b><span>Sin comisión</span></div>
    <div class="fl-a">→</div>
    <div class="fl si"><small>PRIMER BONO</small><b>4h · 8h · 12h</b><span>10% para ti</span></div>
    <div class="fl-a">→</div>
    <div class="fl no"><small>BONOS SIGUIENTES</small><b>2º mes en adelante</b><span>Sin comisión</span></div>
  </div>
  <div class="reglas">
    <div class="rg si"><i>✓</i><div><b>10% del primer bono</b><span>De 4h, 8h o 12h, en cualquier nivel y modalidad.</span></div></div>
    <div class="rg si"><i>✓</i><div><b>Sobre lo que paga la familia</b><span>La comisión se calcula sobre el importe que abona la familia.</span></div></div>
    <div class="rg si"><i>✓</i><div><b>Pago único por alumno</b><span>Una comisión por cada alumno, sin pagos recurrentes.</span></div></div>
    <div class="rg no"><i>✕</i><div><b>El bono de prueba no cuenta</b><span>El bono de 2h no genera comisión.</span></div></div>
  </div>
  <div class="ejemplo-c"><span>Ejemplo</span>Una familia contrata un bono de 12h de Bachillerato presencial por <b>{eur(ej_precio, 0)}</b> → tu comisión: <b class="g">{eur(ej_precio * COMISION)}</b></div>
  {footer("Nexo Académico · Programa de colaboradores")}
</section>'''


def tabla():
    head = "".join(f"<div class='th'>Bono {h}h</div>" for h in BONOS)
    rows = ""
    for nivel, etapa, mod, mod_txt in FILAS:
        celdas = ""
        for h in BONOS:
            p = TARIFAS[etapa]["precios"][mod][h]
            celdas += f"<div class='td'><b>{eur(p * COMISION)}</b><span>bono de {eur(p, 0)}</span></div>"
        rows += (f"<div class='tr'><div class='tl'><b>{e(nivel)}</b><span class='m {mod_txt.lower()}'>{e(mod_txt)}</span></div>"
                 f"{celdas}</div>")
    return f'''<section class="page">
  {hdr("TABLA DE COMISIONES")}
  <div class="pill gold">LO QUE TE LLEVAS</div>
  <h2>Tu comisión, bono a bono</h2>
  <p class="lead">El 10% del primer bono según el nivel del alumno y la modalidad de las clases.</p>
  <div class="ctab"><div class="tr hd"><div class="tl"></div>{head}</div>{rows}</div>
  <p class="nota-bono">En dorado, tu comisión; debajo, el precio del bono que paga la familia. Tarifas del curso 2026–2027.</p>
  {footer("Nexo Académico · Programa de colaboradores")}
</section>'''


def cobro():
    return f'''<section class="page glow">
  {hdr("EL PAGO")}
  <div class="pill gold">CÓMO Y CUÁNDO COBRAS</div>
  <h2>Cobras en cuanto la familia paga</h2>
  <p class="lead">Sin esperar a la primera clase ni a final de mes: cada comisión se paga de forma individual, alumno a alumno.</p>
  <div class="pasos">
    <div class="ps"><em>1</em><b>La familia abona su primer bono</b><span>De 4h, 8h o 12h.</span></div>
    <div class="ps"><em>2</em><b>Calculamos tu 10%</b><span>Sobre el importe que ha pagado la familia.</span></div>
    <div class="ps meta"><em>3</em><b>Te lo enviamos</b><span>Por Bizum o transferencia a la cuenta que nos indiques.</span></div>
  </div>
  <div class="metodos">
    <div><b>Bizum</b><span>Al número de teléfono que nos facilites.</span></div>
    <div><b>Transferencia</b><span>Al número de cuenta que nos facilites.</span></div>
    <div><b>Por alumno</b><span>Un pago por cada alumno, sin agrupar a fin de mes.</span></div>
  </div>
  {footer("Nexo Académico · Programa de colaboradores")}
</section>'''


def cierre():
    return f'''<section class="page cover">
  <img class="logo-md" src="{gp.LOGO_URI}">
  <div class="pill gold">PROGRAMA DE COLABORADORES 2026–2027</div>
  <h2 class="c">¿Empezamos a colaborar?</h2>
  <p class="cover-sub">Escríbenos y te explicamos cómo empezar a recomendar NEXO a tus familias.</p>
  <a class="wa" href="https://wa.me/34699529399">💬 Escríbenos por WhatsApp</a>
  <div class="contact"><span>🌐 nexoacademico.com</span><span>📞 699 52 93 99</span><span>✉️ nexoacademicopremium@gmail.com</span></div>
</section>'''


CSS_EXTRA = r"""
.nm.big { font-size: 30px; }
.flujo { display: grid; grid-template-columns: 1fr 40px 1.2fr 40px 1fr; align-items: center; margin-top: 30px; }
.fl { border-radius: 14px; padding: 16px 18px; text-align: center; border: 1px solid #2a3350; background: #0e1629; }
.fl small { display: block; font-size: 10.5px; font-weight: 700; letter-spacing: 0.14em; color: #7d7f8a; }
.fl b { display: block; font: 700 21px 'Liberation Serif', serif; margin: 6px 0 4px; }
.fl span { font-size: 13px; font-weight: 700; color: #7d7f8a; }
.fl.si { border-color: #9c8550; background: linear-gradient(160deg, #3a3322, #1a1c24); }
.fl.si small { color: #e9d18f; } .fl.si span { color: #7fcfa0; } .fl.si b { color: #e9d18f; font-size: 24px; }
.fl-a { text-align: center; color: #56607a; font-size: 22px; }
.reglas { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 24px; }
.rg { display: flex; gap: 14px; align-items: flex-start; border: 1px solid #2a3350; border-radius: 12px; padding: 14px 16px; background: #0e1629; }
.rg i { flex: none; width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-style: normal; font-weight: 700; font-size: 14px; }
.rg.si i { background: #1f4a37; color: #7fcfa0; } .rg.no i { background: #4a2620; color: #f0a283; }
.rg b { display: block; font: 700 15.5px 'Liberation Serif', serif; }
.rg span { color: #a49f8e; font-size: 13px; line-height: 1.3; }
.ejemplo-c { margin-top: 20px; border: 1px dashed #5d5438; border-radius: 12px; padding: 14px 18px; color: #a49f8e; font-size: 14.5px; }
.ejemplo-c span { display: inline-block; margin-right: 10px; color: #0a1226; background: #c9a24b; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; padding: 3px 10px; border-radius: 999px; }
.ejemplo-c b { color: #e7e7ea; } .ejemplo-c b.g { color: #e9d18f; font-size: 17px; }
.ctab { margin-top: 24px; border: 1px solid #2a3350; border-radius: 16px; overflow: hidden; background: #0c1428; }
.tr { display: grid; grid-template-columns: 1.25fr 1fr 1fr 1fr; align-items: center; border-top: 1px solid #1d2744; }
.tr:nth-child(odd):not(.hd) { background: #0f182e; }
.tr.hd { border-top: 0; background: #121c36; }
.th { text-align: center; padding: 12px 8px; color: #8fb8ec; font-size: 12px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
.tl { padding: 11px 20px; display: flex; align-items: center; gap: 10px; }
.tl b { font: 700 16px 'Liberation Serif', serif; }
.m { font-size: 10.5px; font-weight: 700; letter-spacing: 0.06em; padding: 3px 9px; border-radius: 999px; text-transform: uppercase; }
.m.presencial { background: #3a3322; color: #e9d18f; } .m.online { background: #1a2d52; color: #8fb8ec; }
.td { text-align: center; padding: 9px 8px; border-left: 1px solid #1d2744; }
.td b { display: block; font: 700 21px 'Liberation Serif', serif; color: #e9d18f; }
.td span { color: #7d7f8a; font-size: 11.5px; }
.pasos { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; margin-top: 34px; position: relative; }
.ps { border: 1px solid #2a3350; border-radius: 14px; padding: 20px 20px 22px; background: #0e1629; }
.ps em { display: flex; width: 36px; height: 36px; border-radius: 50%; align-items: center; justify-content: center; font: italic 700 17px 'Liberation Serif', serif; background: #1a2d52; color: #8fb8ec; }
.ps.meta { border-color: #9c8550; background: linear-gradient(160deg, #3a3322, #1a1c24); }
.ps.meta em { background: linear-gradient(135deg, #f6e2a6, #c9a24b); color: #0a1226; }
.ps b { display: block; font: 700 17px 'Liberation Serif', serif; margin: 14px 0 6px; }
.ps span { color: #a49f8e; font-size: 13.5px; line-height: 1.35; }
.metodos { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; margin-top: 18px; }
.metodos > div { border-radius: 14px; padding: 18px 20px; background: #121c36; border: 1px solid #2a3350; }
.metodos b { display: block; font: 700 22px 'Liberation Serif', serif; color: #e9d18f; }
.metodos span { color: #a49f8e; font-size: 13px; }
"""


def main():
    gp.LOGO_URI = "data:image/png;base64," + base64.b64encode(gp.LOGO.read_bytes()).decode()
    pages = [portada(), como_funciona(), regla(), tabla(), cobro(), cierre()]
    doc = (f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>NEXO — Programa de colaboradores</title>'
           f'<style>{gp.CSS}{CSS_EXTRA}</style></head><body>{"".join(pages)}</body></html>')
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    base = out / "NEXO_Programa_Colaboradores"
    base.with_suffix(".html").write_text(doc, encoding="utf-8")
    subprocess.run(["node", str(ROOT / "render_pdf.js"), str(base.with_suffix(".html")), str(base.with_suffix(".pdf"))], check=True)
    print(base.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
