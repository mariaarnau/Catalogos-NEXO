"""Hoja de explicación 'Cómo funciona Nexo' (una página, estilo NEXO)."""
import base64, pathlib, subprocess
R = pathlib.Path(__file__).resolve().parent
logo = base64.b64encode((R.parent / "nexo_blanco_transparente (2).png").read_bytes()).decode()
PASOS = [
    ("01", "Bono de prueba", "Empezáis con 2 horas para conocer al profesor y ver el nivel del alumno."),
    ("02", "Asignación del profesor", "Elegimos al profesor que mejor encaja con el alumno y la asignatura. Se asigna en 24–48 horas."),
    ("03", "Las clases", "Online o presencial en casa, con el ritmo que necesite cada alumno."),
    ("04", "App y área privada", "Seguimiento de las clases en un único sitio, siempre a mano."),
    ("05", "Informes", "Cada mes, un informe con la evolución, los puntos fuertes y lo que toca reforzar."),
]
filas = "".join(f'<div class="r"><em>{n}</em><div><b>{t}</b><p>{d}</p></div></div>' for n, t, d in PASOS)
html = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
@page {{ size: 960px 904px; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font-family: 'Liberation Sans', Arial, sans-serif; color: #fff; background: #0a1226; }}
.page {{ width: 960px; height: 904px; overflow: hidden; padding: 56px 88px 0; position: relative;
  background: linear-gradient(160deg, #0b0d18 0%, #0a1226 55%, #10214a 100%); }}
.logo {{ height: 46px; }}
.k {{ margin-top: 54px; color: #e9d18f; font-size: 11.5px; font-weight: 700; letter-spacing: .2em; }}
h1 {{ font: 700 44px 'Liberation Serif', serif; margin-top: 12px; }}
.sub {{ color: #a49f8e; font-size: 16px; margin-top: 10px; }}
.l {{ height: 1px; background: #2a3350; margin: 34px 0 6px; }}
.r {{ display: grid; grid-template-columns: 70px 1fr; align-items: baseline; padding: 17px 0; border-bottom: 1px solid #1d2744; }}
.r em {{ font: italic 700 24px 'Liberation Serif', serif; color: #e9d18f; }}
.r b {{ font: 700 21px 'Liberation Serif', serif; }}
.r p {{ color: #a49f8e; font-size: 14.5px; margin-top: 5px; line-height: 1.45; }}
.pie {{ margin-top: 30px; display: flex; gap: 40px; color: #a49f8e; font-size: 13.5px; }}
.pie b {{ color: #fff; display: block; font-size: 14px; margin-bottom: 3px; }}
.foot {{ position: absolute; left: 88px; right: 88px; bottom: 34px; display: flex; justify-content: space-between; color: #7d7f8a; font-size: 12px; }}
</style></head><body><section class="page">
<img class="logo" src="data:image/png;base64,{logo}">
<div class="k">CÓMO FUNCIONA</div>
<h1>Clases particulares, bien organizadas.</h1>
<div class="sub">Así trabajamos en Nexo Académico, paso a paso.</div>
<div class="l"></div>
{filas}
<div class="pie">
<div><b>Sin permanencia</b>Pagáis por adelantado el bono de horas.</div>
<div><b>Sustitución garantizada</b>Si el profesor no encaja, lo cambiamos.</div>
<div><b>Online o presencial</b>Presencial en casa, en Valencia.</div>
</div>
<div class="foot"><span>Nexo Académico</span><span>nexoacademico.com</span></div>
</section></body></html>'''
out = R / "output"
(out / "Hoja_NEXO_Como_funciona.html").write_text(html, encoding="utf-8")
subprocess.run(["node", str(R / "render_pdf.js"), str(out / "Hoja_NEXO_Como_funciona.html"), str(out / "Hoja_NEXO_Como_funciona.pdf")], check=True)
