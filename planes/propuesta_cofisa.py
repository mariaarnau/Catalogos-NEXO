"""Propuesta (primer contacto) para la Asociación Cultural Cofisa, con el estilo de los planes NEXO."""
import base64, subprocess
import generar_plan as G
from generar_plan import e, footer

G.LOGO_URI = "data:image/png;base64," + base64.b64encode(G.LOGO.read_bytes()).decode()
L = G.LOGO_URI

d = {"nombre": "Asociación Cultural Cofisa", "curso": "Zona Joven de Montañana", "asignaturas": ["Inglés"],
     "cover_card_sub": "Zona Joven de Montañana · Clases de inglés en grupo",
     "cover_title": "Vuestra propuesta a medida en", "cover_pill": "PROPUESTA PERSONALIZADA · CURSO 2026–2027"}
t = {"cover_sub": "Clases presenciales de inglés para dos grupos, los jueves por la tarde, de noviembre de 2026 a junio de 2027, con un profesor de inglés de Nexo Académico.",
     "cover_foot": "CURSO 2026–2027 — PROPUESTA PARA LA ASOCIACIÓN CULTURAL COFISA"}
d["semana"] = {"etiqueta": "VUESTRA SEMANA", "pill": "CADA JUEVES", "titulo": "Dos grupos, una misma tarde",
    "lead": "Todos los jueves en la Zona Joven de Montañana: primero el grupo de niños y, a continuación, el de mayores. Un/a mismo/a profesor/a de inglés de Nexo para los dos grupos.",
    "hora_ini": 17, "hora_fin": 19, "alto": 100,
    "asignaturas": ["Grupo 1 · Niños 9–12", "Grupo 2 · Mayores de 60"], "asig_cortas": ["Grupo 1 · Niños de 9 a 12 años", "Grupo 2 · Mayores de 60 años"],
    "bloques": [[3, 17, 18, 0], [3, 18, 19, 1]],
    "extra_titulo": "Aula en la Zona Joven de Montañana", "extra_texto": "Av. de Montañana, 374. Las clases se dan en el aula del centro, con pizarra, mesas y sillas.",
    "repartos": [{"nombre": "Cada jueves · 2h", "horas": [1, 1]}]}

def page_grupos():
    g = [("GRUPO 1 · JUEVES 17:00–18:00", "Niños de 9 a 12 años", "Unos 8 alumnos",
          ["Refuerzo de inglés dinámico: vocabulario, juegos y speaking.", "Adaptado a lo que trabajan en el cole, aunque vayan a cursos distintos.", "Actividades en grupo para que pierdan la vergüenza a hablar."]),
         ("GRUPO 2 · JUEVES 18:00–19:00", "Adultos mayores de 60 años", "Unos 8 alumnos",
          ["Inglés básico desde cero, a su ritmo.", "Práctico para el día a día: presentarse, viajes y conversaciones sencillas.", "Clases cercanas y participativas, sin presión."])]
    cards = "".join(f'''<div class="pg"><small>{e(a)}</small><b>{e(b)}</b><span>{e(c)}</span><ul>{"".join(f"<li>{e(x)}</li>" for x in li)}</ul></div>''' for a, b, c, li in g)
    return f'''<section class="page glow">
  <div class="hdr"><img class="logo-sm" src="{L}"><span class="hdr-r">LOS GRUPOS</span></div><div class="rule"></div>
  <div class="pill gold">DOS GRUPOS · UN MISMO PROFESOR</div>
  <h2>Clases pensadas para cada grupo</h2>
  <p class="lead">Dos grupos muy distintos, cada uno con sus objetivos. El profesor prepara cada clase según su edad y su nivel.</p>
  <div class="pgs">{cards}</div>
  {footer("Nexo Académico · Propuesta para la Asociación Cultural Cofisa")}
</section>'''

def page_incluye():
    it = [("01", "Profesor/a de inglés de Nexo", "Especializado en inglés, el mismo para los dos grupos durante todo el curso."),
          ("02", "Sustitución garantizada", "Si el profesor no puede asistir, enviamos a otro de nuestro equipo en Zaragoza: ningún jueves se queda sin clase."),
          ("03", "Nuestra App, por grupos", "Un espacio para cada grupo donde el profesor hace tests cortos, envía tareas y material a todos y propone juegos dinámicos para practicar entre clase y clase."),
          ("04", "Clases y materiales preparados", "Cada sesión llega planificada, con el material de trabajo incluido."),
          ("05", "Seguimiento con la asociación", "Os contamos cómo avanza cada grupo y ajustamos las clases a lo que necesitéis."),
          ("06", "Precio fijo", "La cuota no cambia aunque cada grupo varíe en 2 alumnos arriba o abajo.")]
    cards = "".join(f'<div class="ic"><em>{n}</em><b>{e(a)}</b><p>{e(b)}</p></div>' for n, a, b in it)
    return f'''<section class="page glow">
  <div class="hdr"><img class="logo-sm" src="{L}"><span class="hdr-r">QUÉ INCLUYE</span></div><div class="rule"></div>
  <div class="pill gold">TODO INCLUIDO</div>
  <h2>Todo lo que incluye la propuesta</h2>
  <p class="lead">Sin preocupaciones para la asociación: nosotros ponemos el profesor, las clases y el seguimiento; vosotros, el aula.</p>
  <div class="ics">{cards}</div>
  {footer("Nexo Académico · Propuesta para la Asociación Cultural Cofisa")}
</section>'''

def page_tarifa():
    pts = ["Cuota mensual fija por los dos grupos (2 horas cada jueves).", "La cuota es la misma todos los meses: ya incluye festivos y vacaciones.",
           "Noviembre de 2026 se calcula de forma proporcional a las semanas de clase.", "Desde noviembre de 2026 hasta junio de 2027.",
           "Empezamos la semana siguiente a vuestra confirmación."]
    lis = "".join(f"<li>{e(x)}</li>" for x in pts)
    return f'''<section class="page glow">
  <div class="hdr"><img class="logo-sm" src="{L}"><span class="hdr-r">TARIFA</span></div><div class="rule"></div>
  <div class="pill gold">VUESTRA TARIFA</div>
  <h2>Una cuota mensual, los dos grupos</h2>
  <p class="lead">Un precio sencillo y fijo, pensado para una asociación.</p>
  <div class="tf">
    <div class="tf-a"><small>CUOTA MENSUAL · LOS DOS GRUPOS</small><b>480 €<i>/mes</i></b><span>Exento de IVA</span></div>
    <div class="tf-b"><small>EQUIVALE DE MEDIA A</small><b>≈ 6,9 €</b><span>por alumno y hora</span></div>
  </div>
  <ul class="dash tfl">{lis}</ul>
  {footer("Nexo Académico · Propuesta para la Asociación Cultural Cofisa")}
</section>'''

def page_fin():
    return f'''<section class="page cover">
  <img class="logo-md" src="{L}">
  <div class="pill gold">PROPUESTA CURSO 2026–2027</div>
  <h2 class="c">¿Empezamos?</h2>
  <p class="cover-sub">Escríbenos para confirmar la propuesta o resolver cualquier duda. Os asignamos el profesor y empezamos la semana siguiente.</p>
  <a class="wa" href="https://wa.me/34699529399">💬 Escríbenos por WhatsApp</a>
  <div class="contact"><span>🌐 nexoacademico.com</span><span>📞 699 52 93 99</span><span>✉️ nexoacademicopremium@gmail.com</span></div>
</section>'''

CSS_X = """
.pgs { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin-top: 30px; }
.pg { border: 1px solid #2a3350; border-radius: 18px; padding: 26px 26px 22px; background: #0e1629; }
.pg small { display: block; color: #e9d18f; font-size: 11px; font-weight: 700; letter-spacing: .14em; }
.pg b { display: block; font: 700 26px 'Liberation Serif', serif; margin: 10px 0 4px; }
.pg span { color: #8fb8ec; font-size: 14px; }
.pg ul { list-style: none; margin-top: 18px; } .pg li { color: #c9c6ba; font-size: 14.5px; line-height: 1.45; padding: 9px 0 9px 22px; border-top: 1px solid #1d2744; position: relative; }
.pg li::before { content: "✓"; position: absolute; left: 0; color: #e9d18f; font-weight: 700; }
.ics { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 28px; }
.ic { border: 1px solid #2a3350; border-radius: 16px; padding: 20px 20px 18px; background: #0e1629; }
.ic em { font: italic 700 15px 'Liberation Serif', serif; color: #e9d18f; }
.ic b { display: block; font: 700 18px 'Liberation Serif', serif; margin: 8px 0 6px; }
.ic p { color: #a49f8e; font-size: 13.5px; line-height: 1.42; }
.ic:nth-child(2), .ic:nth-child(3) { border-color: #c9a24b; background: linear-gradient(160deg, #2a2618, #0e1629); }
.tf { display: grid; grid-template-columns: 1.3fr 1fr; gap: 22px; margin-top: 30px; }
.tf > div { border-radius: 18px; padding: 28px 30px; }
.tf-a { border: 1px solid #c9a24b; background: linear-gradient(160deg, #2a2618, #0e1629); }
.tf-b { border: 1px solid #2a3350; background: #0e1629; }
.tf small { display: block; color: #e9d18f; font-size: 11px; font-weight: 700; letter-spacing: .14em; }
.tf b { display: block; font: 700 64px 'Liberation Serif', serif; color: #e9d18f; margin: 10px 0 4px; line-height: 1; }
.tf b i { font: 400 20px 'Liberation Sans', sans-serif; color: #a49f8e; font-style: normal; margin-left: 6px; }
.tf-b b { color: #fff; font-size: 54px; }
.tf span { color: #a49f8e; font-size: 14px; }
.tfl { margin-top: 26px; }
"""

pages = [G.page_cover(d, t), G.page_semana(d, t), page_grupos(), page_incluye(), page_tarifa(), page_fin()]
doc = f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Propuesta NEXO — Asociación Cultural Cofisa</title><style>{G.CSS}{CSS_X}</style></head><body>{"".join(pages)}</body></html>'
out = G.ROOT / "output" / "Propuesta_NEXO_Asociacion_Cofisa_ZonaJovenMontanana"
out.with_suffix(".html").write_text(doc, encoding="utf-8")
subprocess.run(["node", str(G.ROOT / "render_pdf.js"), str(out.with_suffix(".html")), str(out.with_suffix(".pdf"))], check=True)
print(out.with_suffix(".pdf"))
