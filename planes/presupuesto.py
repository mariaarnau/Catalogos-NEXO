"""Presupuesto oficial de Nexo Académico (A4). Identidad: banda azul #0B1B3A, logo blanco, acento #156082."""
import base64, pathlib, subprocess, textwrap
R = pathlib.Path(__file__).resolve().parent
logo = base64.b64encode((R.parent / "nexo_blanco_transparente (2).png").read_bytes()).decode()
PEND = '<span class="pend">[PENDIENTE]</span>'
CIF = '<span class="pend">[CIF PENDIENTE]</span>'

html = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Presupuesto 2026-P001</title><style>
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font-family: 'Liberation Sans', Arial, sans-serif; color: #1c2433; font-size: 8.6pt; line-height: 1.35; }}
.page {{ width: 210mm; height: 297mm; position: relative; overflow: hidden; background: #fff; }}
.band {{ background: #0B1B3A; height: 34mm; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; padding: 0 14mm; color: #fff; }}
.band img {{ height: 17mm; }}
.band .l b {{ display: block; font: 700 17pt 'Liberation Serif', serif; letter-spacing: .06em; }}
.band .r {{ text-align: right; font-size: 8pt; line-height: 1.5; }} .band .r b {{ font-size: 10pt; }}
.wrap {{ padding: 7mm 14mm 0; }}
.cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; }}
.box {{ border: 0.3mm solid #d3dae6; border-radius: 2mm; padding: 3mm 4mm; }}
.box h4 {{ font-size: 7pt; letter-spacing: .14em; color: #156082; margin-bottom: 1.5mm; }}
.box b.n {{ font: 700 10pt 'Liberation Serif', serif; color: #0B1B3A; }}
.box p {{ margin-top: .6mm; }} .box p span {{ color: #5b6578; }}
.pend {{ background: #fff3c4; color: #8a5a00; font-weight: 700; padding: 0 1.2mm; border-radius: 1mm; }}
h3 {{ background: #156082; color: #fff; font-size: 8pt; letter-spacing: .12em; padding: 1.4mm 3mm; margin: 5mm 0 2.5mm; }}
.svc {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }}
.g {{ border: 0.3mm solid #d3dae6; border-radius: 2mm; padding: 2.6mm 3.4mm; }} .g b {{ color: #0B1B3A; }}
.g small {{ display: block; color: #156082; font-weight: 700; letter-spacing: .08em; margin-bottom: .6mm; }}
.note {{ margin-top: 2.2mm; color: #3a4558; }}
.price {{ display: grid; grid-template-columns: 1fr auto; gap: 5mm; align-items: center; border: 0.4mm solid #0B1B3A; border-radius: 2mm; padding: 3.5mm 5mm; background: #f3f6fb; }}
.price .a {{ font: 700 20pt 'Liberation Serif', serif; color: #0B1B3A; }} .price .a small {{ font: 400 9pt 'Liberation Sans', sans-serif; color: #5b6578; }}
.price .b {{ font-size: 9pt; color: #0B1B3A; text-align: right; }} .price .b b {{ font: 700 15pt 'Liberation Serif', serif; color: #156082; display: block; }}
ul {{ list-style: none; }} ul li {{ padding-left: 4mm; position: relative; margin-bottom: .8mm; }}
ul li::before {{ content: "✓"; position: absolute; left: 0; color: #156082; font-weight: 700; }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; }}
.acc {{ border: 0.3mm dashed #7d8aa3; border-radius: 2mm; padding: 3mm 4mm; margin-top: 5mm; }}
.acc h4 {{ font-size: 7.5pt; letter-spacing: .14em; color: #0B1B3A; margin-bottom: 2mm; }}
.sig {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4mm; }}
.sig div {{ border-bottom: 0.3mm solid #7d8aa3; height: 11mm; font-size: 7pt; color: #5b6578; padding-top: 1mm; }}
.sig div.sello {{ grid-row: span 1; }}
.foot {{ position: absolute; bottom: 0; left: 0; right: 0; background: #0B1B3A; color: #cdd6e6; font-size: 7.3pt; padding: 3mm 14mm; display: flex; justify-content: space-between; }}
</style></head><body><div class="page">
<div class="band"><div class="l"><b>PRESUPUESTO</b></div><img src="data:image/png;base64,{logo}"><div class="r"><b>Nº 2026-P001</b><br>Fecha: 5 de noviembre de 2026<br>Validez: 15 días (hasta el 20/11/2026)</div></div>
<div class="wrap">
<div class="cols">
 <div class="box"><h4>EMISOR</h4><b class="n">Nexo Académico</b>
  <p><span>Titular:</span> Manuel Sánchez Carrascosa</p>
  <p><span>NIF:</span> {PEND}</p>
  <p><span>Dirección fiscal:</span> {PEND}</p>
  <p><span>Email:</span> nexoacademicopremium@gmail.com</p>
  <p><span>Teléfono:</span> 699 52 93 99 · <span>Web:</span> nexoacademico.com</p></div>
 <div class="box"><h4>CLIENTE</h4><b class="n">Asociación Cultural Cofisa</b>
  <p><span>CIF:</span> {CIF}</p>
  <p><span>Lugar del servicio:</span> Zona Joven de Montañana — Av. de Montañana, 374, 50059 Zaragoza</p>
  <p><span>Persona de contacto:</span> Paula</p></div>
</div>

<h3>SERVICIO</h3>
<p>Clases presenciales de inglés en la Zona Joven de Montañana, los <b>jueves por la tarde</b>, desde noviembre de 2026 hasta junio de 2027. Un/a mismo/a profesor/a de inglés de Nexo para los dos grupos. El aula la pone el cliente (pizarra, mesas y sillas).</p>
<div class="svc" style="margin-top:2.5mm">
 <div class="g"><small>GRUPO 1 · NIÑOS DE 9 A 12 AÑOS</small><b>Jueves 17:00–18:00</b> · unos 8 alumnos<br>Refuerzo de inglés dinámico: vocabulario, juegos y speaking, adaptado a lo que trabajan en el cole aunque vayan a cursos distintos.</div>
 <div class="g"><small>GRUPO 2 · ADULTOS MAYORES DE 60 AÑOS</small><b>Jueves 18:00–19:00</b> · unos 8 alumnos<br>Inglés básico desde cero y práctico para el día a día: presentarse, viajes y conversaciones sencillas.</div>
</div>

<h3>PRECIO</h3>
<div class="price"><div><div class="a">480,00 € <small>/ mes · los dos grupos</small></div><div style="margin-top:1mm;color:#5b6578">Servicio exento de IVA. Cuota fija mensual.</div></div>
 <div class="b">Equivale de media a<b>unos 6,9 € por alumno y hora</b></div></div>

<div class="two" style="margin-top:0">
<div><h3>QUÉ INCLUYE</h3><ul>
 <li>Profesor/a de inglés de Nexo Académico.</li>
 <li><b>Sustitución garantizada:</b> si el profesor no puede asistir, enviamos a otro de nuestro equipo en Zaragoza para que ningún jueves se quede sin clase.</li>
 <li>Preparación de clases y materiales.</li>
 <li>Seguimiento con la asociación.</li>
 <li>Precio fijo aunque cada grupo varíe en 2 alumnos arriba o abajo.</li></ul></div>
<div><h3>CONDICIONES</h3><ul>
 <li>Factura mensual a nombre de la Asociación Cultural Cofisa.</li>
 <li>Pago por transferencia durante los 5 primeros días de cada mes.</li>
 <li>Noviembre de 2026 se factura de forma proporcional a las semanas de clase.</li>
 <li>La cuota es la misma todos los meses (ya incluye festivos y vacaciones).</li>
 <li>Duración: hasta junio de 2027. Cualquier cambio o cancelación requiere 30 días de preaviso.</li>
 <li>Inicio: la semana siguiente a la aceptación del presupuesto.</li></ul></div>
</div>

<div class="acc"><h4>ACEPTACIÓN DEL PRESUPUESTO</h4>
 <div class="sig"><div>Nombre</div><div>Cargo</div><div>Fecha</div></div>
 <div class="sig" style="margin-top:3mm"><div style="height:16mm">Firma</div><div style="height:16mm">Sello de la entidad</div><div style="border:0"></div></div>
</div>
</div>
<div class="foot"><span>Nexo Académico · Presupuesto 2026-P001</span><span>nexoacademico.com · 699 52 93 99</span></div>
</div></body></html>'''
out = R / "output"
(out / "Presupuesto_Nexo_ZonaJovenMontanana_2026-11.html").write_text(html, encoding="utf-8")
js = textwrap.dedent("""
const path = require('path');
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
(async () => {
  const [inp, out] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.resolve(inp), { waitUntil: 'networkidle' });
  await p.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
""")
(R / "render_a4.js").write_text(js)
subprocess.run(["node", str(R / "render_a4.js"), str(out / "Presupuesto_Nexo_ZonaJovenMontanana_2026-11.html"), str(out / "Presupuesto_Nexo_ZonaJovenMontanana_2026-11.pdf")], check=True)
