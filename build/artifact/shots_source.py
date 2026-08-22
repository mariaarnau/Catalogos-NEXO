import base64

with open("nexo-guia.html") as f:
    body = f.read()

logo_b64 = open("logo_white_b64.txt").read().strip()
logo_uri = f"data:image/png;base64,{logo_b64}"

lines = body.split("\n", 1)
title_line = lines[0]
rest = lines[1]

cover_css = """
<style>
  .cover-page{
    width:480px; box-sizing:border-box; padding:60px 30px;
    background:radial-gradient(ellipse at 28% 12%, #17233d 0%, #0b1220 55%, #060a13 100%);
    color:#fff; display:flex; flex-direction:column; align-items:center; justify-content:center;
    text-align:center;
  }
  .cover-page img.logo{ width:230px; margin-bottom:34px; }
  .cover-page .eyebrow{
    font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.28em; text-transform:uppercase;
    color:#7fa3e8; margin-bottom:16px;
  }
  .cover-page h1{
    font-family:"Newsreader",Georgia,serif; font-style:italic; font-weight:600;
    font-size:34px; line-height:1.14; margin:0 0 20px; color:#fff;
  }
  .cover-page p.lead{
    font-size:15px; line-height:1.65; color:#aab6cc; margin:0 0 30px;
  }
  .cover-page .pillgrid{
    display:flex; flex-wrap:wrap; gap:9px; justify-content:center; margin-bottom:30px;
  }
  .cover-page .pillgrid span{
    border:1px solid #2c3c5c; color:#9db3dd; background:#101a30;
    border-radius:20px; padding:7px 13px; font-size:11.5px; font-family:"IBM Plex Sans",sans-serif;
  }
  .cover-page .foot{ font-size:10px; letter-spacing:.08em; color:#57607a; font-family:"IBM Plex Mono",monospace; }

  .pdf-head{
    display:flex; align-items:center; justify-content:space-between;
    background:#0b1220; padding:10px 16px; margin-bottom:20px; border-radius:8px;
    width:100%; box-sizing:border-box;
  }
  .pdf-head img{ height:16px; display:block; }
  .pdf-head span{
    font-family:"IBM Plex Mono",monospace; font-size:9px; letter-spacing:.1em; text-transform:uppercase;
    color:#7f8ba3;
  }
</style>
"""

cover_html = f"""
<section class="cover-page" id="cover">
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

pdf_head = f'<div class="pdf-head"><img src="{logo_uri}"><span>Área del Alumno</span></div>'
rest = rest.replace('<div class="hero">', '<div class="hero">' + pdf_head, 1)
import re
rest = re.sub(
    r'(<section class="screen-block" id="[a-z]+">)',
    r'\1' + pdf_head.replace("\\", "\\\\"),
    rest,
)

extra_body_css = """
<style>
  body{ display:flex; flex-direction:column; align-items:center; }
  .hero{ width:480px; box-sizing:border-box; padding:44px 26px 34px; }
  .screen-block{ width:480px; box-sizing:border-box; padding:40px 26px; border-bottom:1px solid var(--line); }
  main{ padding:0; max-width:none; width:auto; }
  .railnav{ display:none; }
  .footer-note{ width:480px; box-sizing:border-box; padding:22px 26px 50px; }
</style>
"""

html = (
    "<!DOCTYPE html>\n<html lang=\"es\"><head><meta charset=\"UTF-8\">\n"
    + title_line + "\n" + cover_css + "\n</head><body>\n"
    + cover_html + "\n"
    + rest
    + extra_body_css
    + "\n</body></html>"
)

with open("shots.html", "w") as f:
    f.write(html)

print("written", len(html))
