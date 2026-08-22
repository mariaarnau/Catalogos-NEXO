import base64, subprocess, re

with open("nexo-guia.html") as f:
    body = f.read()

logo_b64 = open("logo_white_b64.txt").read().strip()
logo_uri = f"data:image/png;base64,{logo_b64}"

lines = body.split("\n", 1)
title_line = lines[0]
rest = lines[1]

cover_css = """
<style>
  @page { size: A4; margin: 0; }
  @media print { body { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }

  .cover-page{
    width:210mm; height:297mm; box-sizing:border-box;
    background:radial-gradient(ellipse at 28% 12%, #17233d 0%, #0b1220 55%, #060a13 100%);
    color:#fff; display:flex; flex-direction:column; align-items:center; justify-content:center;
    text-align:center; page-break-after:always; padding:24mm;
  }
  .cover-page img.logo{ width:78mm; margin-bottom:14mm; }
  .cover-page .eyebrow{
    font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.28em; text-transform:uppercase;
    color:#7fa3e8; margin-bottom:7mm;
  }
  .cover-page h1{
    font-family:"Newsreader",Georgia,serif; font-style:italic; font-weight:600;
    font-size:33px; line-height:1.12; margin:0 0 8mm; color:#fff;
  }
  .cover-page p.lead{
    font-size:13.5px; line-height:1.65; color:#aab6cc; max-width:120mm; margin:0 0 14mm;
  }
  .cover-page .pillgrid{
    display:flex; flex-wrap:wrap; gap:5mm; justify-content:center; max-width:150mm; margin-bottom:16mm;
  }
  .cover-page .pillgrid span{
    border:1px solid #2c3c5c; color:#9db3dd; background:#101a30;
    border-radius:20pt; padding:3mm 6mm; font-size:9.5px; font-family:"IBM Plex Sans",sans-serif;
  }
  .cover-page .foot{ font-size:9px; letter-spacing:.08em; color:#57607a; font-family:"IBM Plex Mono",monospace; }
</style>
"""

cover_html = f"""
<section class="cover-page">
  <img class="logo" src="{logo_uri}">
  <span class="eyebrow">Guía para alumnos</span>
  <h1>Así funciona<br>Nexo Académico</h1>
  <p class="lead">Nexo Académico es la plataforma donde cada alumno hace seguimiento de sus clases particulares: consulta sus sesiones, sus notas, sus tareas y su material de estudio, y mantiene el contacto con su profesor y con el equipo de Nexo, todo desde el móvil.</p>
  <div class="pillgrid">
    <span>Acceso</span><span>Inicio</span><span>Sesiones</span><span>Informes</span>
    <span>Bonos</span><span>Calendario</span><span>Mi Profesor</span><span>Material</span>
    <span>Tareas</span><span>Tests</span><span>Avisos</span>
  </div>
  <div class="foot">NEXO ACADÉMICO &middot; app.nexoacademico.com</div>
</section>
"""

print_css = """
<style>
  @media print {
    body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .railnav { display: none !important; }
    .hero { padding: 4mm 0 10mm; }
    .screen-block { page-break-inside: avoid; break-inside: avoid; page-break-after: always; padding: 4mm 0 6mm; border-bottom: none; }
    .screen-block:last-of-type { page-break-after: auto; }
    main { padding: 0; max-width: 100%; }
    .footer-note { page-break-before: avoid; }
  }

  @media print {
    .phone { width: 210px; padding: 9px; }
    .phone .notch { width: 66px; height: 14px; top: 9px; }
    .screen { height: 400px; border-radius: 20px; }
    .scr-body { padding: 2px 11px 11px; }
    .scr-title { font-size: 13.5px; margin: 5px 0 2px; }
    .scr-sub { font-size: 8.5px; margin-bottom: 9px; }
    .topb { padding: 8px 12px 9px; }
    .card { padding: 8px 9px; margin-bottom: 6px; border-radius: 9px; }
    .btn { font-size: 9px; padding: 7px; margin-top: 6px; }
    .screen-block { gap: 14px; }
    .note h2 { font-size: 21px; margin-bottom: 7px; }
    .note p { font-size: 12.5px; margin: 0 0 7px; }
    .script { padding: 9px 11px; margin-top: 8px; }
    .script q { font-size: 12px; }
    .hero { padding: 0 0 6mm; }
    .hero h1 { font-size: 30px; }
    .hero p { font-size: 13.5px; margin-top: 10px; }
  }
</style>
"""

html = (
    "<!DOCTYPE html>\n<html lang=\"es\"><head><meta charset=\"UTF-8\">\n"
    + title_line + "\n" + cover_css + "\n</head><body>\n"
    + cover_html + "\n"
    + rest
    + "\n" + print_css
    + "\n</body></html>"
)

with open("nexo-guia-print.html", "w") as f:
    f.write(html)

print("written", len(html))
