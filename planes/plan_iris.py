"""Plan para los hermanos Pedro José (5º Primaria) y Pablo (2º Primaria), Burjassot. Madre: Iris."""
import base64, subprocess
import generar_plan as G
from generar_plan import e, footer, eur

G.LOGO_URI = "data:image/png;base64," + base64.b64encode(G.LOGO.read_bytes()).decode()
L = G.LOGO_URI
FT = "Nexo Académico · Plan personalizado"

d = {"nombre": "Pedro José y Pablo", "etapa": "primaria", "curso": "Primaria", "asignaturas": [], "voz": "familia",
     "hijos": [{"nombre": "Pedro José", "curso": "5º Primaria"}, {"nombre": "Pablo", "curso": "2º Primaria"}],
     "cover_title": "Vuestro plan a medida en", "presencial_label": "en vuestra casa", "bonos_recomendados": [{"horas": 12, "frecuencia": ""}], "modalidades_recomendadas": ["casa_alumno"]}
t = G.textos(d)
t.update({"cover_sub": "Un plan a medida para Pedro José y Pablo: clases presenciales en vuestra casa, en Burjassot, los martes y jueves, con un 10% de descuento por hermanos.",
          "cover_foot": "CURSO 2026–2027 — CONDICIONES VÁLIDAS PARA ESTA FAMILIA"})
d["semana"] = {"etiqueta": "SU SEMANA", "pill": "HORARIO ORIENTATIVO", "titulo": "Martes y jueves, los dos hermanos seguidos",
    "lead": "El profesor va a vuestra casa, en Burjassot, y da las dos clases seguidas: 1 hora a Pedro José y media hora a Pablo, los martes y los jueves. Las horas exactas las ajustamos a vuestro horario.",
    "hora_ini": 17, "hora_fin": 19, "alto": 100,
    "asignaturas": ["Pedro José · 5º Primaria", "Pablo · 2º Primaria"], "asig_cortas": ["Pedro José", "Pablo"],
    "bloques": [[1, 17, 18, 0], [1, 18, 18.5, 1], [3, 17, 18, 0], [3, 18, 18.5, 1]],
    "extra_titulo": "Un solo desplazamiento, dos clases", "extra_texto": "Como el profesor atiende a los dos hermanos la misma tarde, os aplicamos un 10% de descuento en los bonos de Pablo.",
    "repartos": [{"nombre": "Cada semana · 3h", "horas": [2, 1]}]}

def page_agencia():
    it = [("01", "El profesor lo elegimos nosotros", "Seleccionamos al profesor que mejor encaja con cada niño, por nivel, carácter y forma de enseñar. Se asigna en 24–48 horas."),
          ("02", "Sustitución garantizada", "Si el profesor se pone enfermo, no puede venir o no encaja con los niños, ponemos a otro de nuestro equipo en 24–48 horas. Las clases no se paran."),
          ("03", "Un interlocutor para todo", "Horarios, cambios, dudas o pagos: hablas con nosotros, no tienes que gestionar nada con el profesor."),
          ("04", "Informes cada mes", "Recibís un informe de cada hijo con lo que ha trabajado, sus notas por sesión, puntos fuertes y lo que toca reforzar."),
          ("05", "La App de Nexo", "Material, tareas y tests de repaso entre clase y clase, y el acceso a los informes, todo en el móvil."),
          ("06", "Sin permanencia", "Pagáis bonos de horas por adelantado y solo se descuentan las horas que se dan. Ninguna hora se pierde.")]
    cards = "".join(f'<div class="ag{" o" if i < 2 else ""}"><em>{n}</em><b>{e(a)}</b><p>{e(b)}</p></div>' for i, (n, a, b) in enumerate(it))
    return f'''<section class="page glow">
  <div class="hdr"><img class="logo-sm" src="{L}"><span class="hdr-r">POR QUÉ NEXO</span></div><div class="rule"></div>
  <div class="pill gold">UNA AGENCIA, NO UN PROFESOR SUELTO</div>
  <h2>Lo que os da Nexo que no os da un profesor particular</h2>
  <p class="lead">Detrás de cada profesor hay un equipo que lo elige, lo sustituye si hace falta y os cuenta cada mes cómo van los niños.</p>
  <div class="ags">{cards}</div>
  {footer(FT)}
</section>'''

def page_informe_nuevo():
    return f'''<section class="page glow">
  <div class="hdr"><img class="logo-sm" src="{L}"><span class="hdr-r">LOS INFORMES</span></div><div class="rule"></div>
  <div class="pill gold">ASÍ ES UN INFORME DE NEXO</div>
  <h2>Cada mes, un informe de cada hijo</h2>
  <p class="lead">El profesor puntúa cada sesión y nuestro equipo lo convierte en un informe claro: qué se ha trabajado, cómo ha ido y qué hacer el mes siguiente. Ejemplo con datos ficticios.</p>
  <div class="rp">
   <div class="rpp">
    <div class="rpk">INFORME DE SEGUIMIENTO MENSUAL</div>
    <div class="rpn">Pedro José</div><div class="rps">Matemáticas · Octubre 2026 · <i>ejemplo</i></div>
    <div class="rpt"><div><b>8</b>SESIONES</div><div><b>8 h</b>DEDICADAS</div><div><b>7,5</b>NOTA MEDIA</div><div><b>1 h</b>DURACIÓN MEDIA</div></div>
    <div class="rpl"><small>MAYOR LOGRO DEL MES</small>Ya resuelve las divisiones de dos cifras sin ayuda: de 5/10 a 8/10</div>
    <div class="rph">Matemáticas · 8 sesiones · 8 h</div>
    <div class="rpi p">＋ Entiende bien los enunciados de los problemas</div>
    <div class="rpi p">＋ Calcula con orden y sin prisas</div>
    <div class="rpi w">! Le cuesta elegir la operación en problemas de dos pasos</div>
    <div class="rpi m">→ Fracciones: comparar y ordenar</div>
   </div>
   <div class="rpp">
    <div class="rpk">DE CARA AL MES QUE VIENE</div>
    <div class="rpn s">Qué tener en cuenta</div>
    <div class="rpx"><b>18<small>NOV</small></b><span>Examen de Matemáticas · fracciones</span></div>
    <div class="rpb"><div><small>ORGANIZACIÓN DE OCTUBRE</small>8 sesiones (8 h) · martes y jueves</div>
      <div><small>PROPUESTA PARA NOVIEMBRE</small><span class="tag r">REFORZAR</span> Fracciones antes del examen<br><span class="tag g">AVANZAR</span> Problemas de dos pasos</div></div>
    <div class="rpc">Las recomendaciones se apoyan en técnicas de estudio con evidencia científica: practicar recordando y repasar de forma espaciada.</div>
   </div>
  </div>
  <ul class="dash" style="margin-top:22px"><li>Un informe para Pedro José y otro para Pablo, cada mes, en la App y en PDF.</li><li>Nota de cada sesión, puntos fuertes (＋), lo que hay que vigilar (!) y lo que toca mejorar (→).</li></ul>
  {footer(FT)}
</section>'''

def page_app():
    it = [("📚", "Material y tareas", "El profesor sube fichas, resúmenes y deberes de cada clase."),
          ("✅", "Tests de repaso", "Ejercicios cortos para practicar entre clase y clase."),
          ("📊", "Informes", "El informe mensual de cada hijo, siempre a mano."),
          ("🗓️", "Organización", "Qué toca repasar cada semana y los próximos exámenes.")]
    cards = "".join(f'<div class="ap"><i>{a}</i><b>{e(b)}</b><p>{e(c)}</p></div>' for a, b, c in it)
    return f'''<section class="page glow">
  <div class="hdr"><img class="logo-sm" src="{L}"><span class="hdr-r">LA APP</span></div><div class="rule"></div>
  <div class="pill gold">TODO EN EL MÓVIL</div>
  <h2>La App de Nexo</h2>
  <p class="lead">Al empezar os damos acceso. Un espacio para cada hijo, para que el aprendizaje siga entre clase y clase.</p>
  <div class="aps">{cards}</div>
  {footer(FT)}
</section>'''

def page_precio():
    def row(n, c, b1, p1, b2, p2, dto):
        tach = lambda x: f'<s>{eur(x, 0)}</s>' if dto else ""
        return f'''<div class="pr2{" d" if dto else ""}">
  <div class="pr2h"><b>{e(n)}</b><span>{e(c)}</span>{'<em>−10% HERMANOS</em>' if dto else ''}</div>
  <div class="pr2r"><small>PASO 1 · BONO DE PRUEBA</small><b>2 horas</b><div>{tach(40)}<strong>{eur(p1, 0)}</strong></div></div>
  <div class="pr2r"><small>PASO 2 · DESPUÉS</small><b>Bono de {b2} horas</b><div>{tach(round(p2 / 0.9))}<strong>{eur(p2, 0)}</strong></div></div>
  <div class="pr2x"><b>{eur(p2 / b2)}</b><span>por hora en el bono de {b2}h</span></div>
</div>'''
    return f'''<section class="page glow">
  <div class="hdr"><img class="logo-sm" src="{L}"><span class="hdr-r">VUESTRO PLAN</span></div><div class="rule"></div>
  <div class="pill gold">DESCUENTO POR HERMANOS</div>
  <h2>Vuestro plan, en dos pasos</h2>
  <p class="lead">Primero un bono de prueba para que los niños conozcan al profesor. Después, el bono de horas de cada uno, con un 10% de descuento en los de Pablo.</p>
  <div class="pr2s">{row("Pedro José", "5º Primaria · 2 h a la semana", 2, 40, 12, 250, False)}{row("Pablo", "2º Primaria · 1 h a la semana", 2, 36, 8, 153, True)}</div>
  <ul class="dash" style="margin-top:22px">
   <li>Bonos de Pedro José y Pablo por separado: cada uno gasta solo sus horas.</li>
   <li>A este ritmo, el bono de 12h de Pedro José dura unas 6 semanas y el de 8h de Pablo, unas 8.</li>
   <li>Sin permanencia: pagáis por adelantado y solo se descuentan las horas de clase que se dan.</li></ul>
  {footer(FT)}
</section>'''

def page_fin():
    return f'''<section class="page cover">
  <img class="logo-md" src="{L}">
  <div class="pill gold">PLAN VÁLIDO CURSO 2026–2027</div>
  <h2 class="c">¿Empezamos?</h2>
  <p class="cover-sub">Escríbenos para reservar los bonos de prueba de Pedro José y Pablo. Os asignamos el profesor en 24–48 horas.</p>
  <a class="wa" href="https://wa.me/34699529399">💬 Escríbenos por WhatsApp</a>
  <div class="contact"><span>🌐 nexoacademico.com</span><span>📞 699 52 93 99</span><span>✉️ nexoacademicopremium@gmail.com</span></div>
</section>'''

CSS_X = """
.ags { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 26px; }
.ag { border: 1px solid #2a3350; border-radius: 16px; padding: 20px; background: #0e1629; }
.ag.o { border-color: #c9a24b; background: linear-gradient(160deg, #2a2618, #0e1629); }
.ag em { font: italic 700 15px 'Liberation Serif', serif; color: #e9d18f; }
.ag b { display: block; font: 700 18px 'Liberation Serif', serif; margin: 8px 0 6px; }
.ag p { color: #a49f8e; font-size: 13.5px; line-height: 1.42; }
.rp { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 24px; }
.rpp { text-align: left; background: #f7f8fb; color: #1c2433; border-radius: 14px; padding: 20px 22px; border-top: 5px solid #2a5bb0; }
.rpk { display: inline-block; font-size: 9.5px; font-weight: 700; letter-spacing: .12em; color: #9a7a2a; border: 1px solid #d9c27c; border-radius: 999px; padding: 4px 10px; }
.rpn { font: 700 24px 'Liberation Serif', serif; color: #0B1B3A; margin-top: 10px; } .rpn.s { font-size: 20px; }
.rps { color: #5b6578; font-size: 12px; margin-top: 2px; }
.rpt { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 12px; }
.rpt div { border: 1px solid #dfe4ee; border-radius: 6px; padding: 6px; font-size: 8.5px; color: #5b6578; letter-spacing: .06em; }
.rpt b { display: block; font: 700 17px 'Liberation Serif', serif; color: #b08a2e; letter-spacing: 0; }
.rpl { background: #0B1B3A; color: #fff; border-radius: 6px; padding: 9px 12px; margin-top: 10px; font: 700 12.5px 'Liberation Serif', serif; }
.rpl small { display: block; font: 700 8.5px 'Liberation Sans', sans-serif; letter-spacing: .12em; color: #9fb4da; margin-bottom: 3px; }
.rph { font: 700 13.5px 'Liberation Serif', serif; color: #0B1B3A; margin: 12px 0 4px; }
.rpi { font-size: 12px; padding: 3px 0; } .rpi.p { color: #1f7a4f; } .rpi.w { color: #9a6b00; } .rpi.m { color: #2a5bb0; }
.rpx { display: flex; gap: 12px; align-items: center; border: 1px solid #dfe4ee; border-radius: 8px; padding: 10px 12px; margin-top: 12px; font-size: 12.5px; }
.rpx b { font: 700 22px 'Liberation Serif', serif; color: #0B1B3A; text-align: center; line-height: 1; } .rpx b small { display: block; font: 700 9px 'Liberation Sans', sans-serif; color: #b08a2e; }
.rpb { display: grid; gap: 8px; margin-top: 10px; } .rpb div { border: 1px solid #dfe4ee; border-radius: 8px; padding: 9px 12px; font-size: 12px; line-height: 1.6; }
.rpb small { display: block; font-size: 9px; font-weight: 700; letter-spacing: .1em; color: #5b6578; }
.tag { font-size: 8.5px; font-weight: 700; padding: 2px 7px; border-radius: 999px; letter-spacing: .08em; } .tag.r { background: #fbecc4; color: #8a5a00; } .tag.g { background: #d6f0e1; color: #1f7a4f; }
.rpc { font-size: 10.5px; color: #5b6578; margin-top: 10px; line-height: 1.4; }
.aps { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 28px; }
.ap { border: 1px solid #2a3350; border-radius: 16px; padding: 24px; background: #0e1629; }
.ap i { font-style: normal; font-size: 30px; } .ap b { display: block; font: 700 20px 'Liberation Serif', serif; margin: 10px 0 6px; } .ap p { color: #a49f8e; font-size: 14px; line-height: 1.45; }
.pr2s { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 24px; }
.pr2 { border: 1px solid #2a3350; border-radius: 18px; padding: 22px 24px; background: #0e1629; }
.pr2.d { border-color: #c9a24b; background: linear-gradient(160deg, #2a2618, #0e1629); }
.pr2h b { font: 700 24px 'Liberation Serif', serif; } .pr2h span { display: block; color: #8fb8ec; font-size: 13px; margin-top: 2px; }
.pr2h em { display: inline-block; margin-top: 8px; font-style: normal; font-size: 11px; font-weight: 700; letter-spacing: .1em; background: #c9a24b; color: #0a1226; padding: 4px 10px; border-radius: 999px; }
.pr2r { display: grid; grid-template-columns: 1fr auto; align-items: center; border-top: 1px solid #1d2744; padding: 13px 0; margin-top: 12px; }
.pr2r small { grid-column: 1; font-size: 9.5px; font-weight: 700; letter-spacing: .14em; color: #8fb8ec; } .pr2r b { grid-column: 1; font: 700 16px 'Liberation Serif', serif; }
.pr2r div { grid-column: 2; grid-row: 1 / span 2; text-align: right; } .pr2r s { display: block; color: #7d7f8a; font-size: 12px; }
.pr2r strong { font: 700 28px 'Liberation Serif', serif; color: #e9d18f; }
.pr2x { border-top: 1px solid #1d2744; padding-top: 12px; } .pr2x b { font: 700 32px 'Liberation Serif', serif; color: #e9d18f; margin-right: 8px; } .pr2x span { color: #a49f8e; font-size: 13px; }
"""

pages = [G.page_cover(d, t), G.page_semana(d, t), page_agencia(), page_informe_nuevo(), page_app(),
         G.page_tarifas(d, t, "casa_alumno"), page_precio(), page_fin()]
doc = f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Plan NEXO — Pedro José y Pablo</title><style>{G.CSS}{CSS_X}</style></head><body>{"".join(pages)}</body></html>'
out = G.ROOT / "output" / "Plan_NEXO_Pedro_Jose_y_Pablo_Primaria_Burjassot"
out.with_suffix(".html").write_text(doc, encoding="utf-8")
subprocess.run(["node", str(G.ROOT / "render_pdf.js"), str(out.with_suffix(".html")), str(out.with_suffix(".pdf"))], check=True)
print(out.with_suffix(".pdf"))
