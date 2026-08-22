import re

def page(step, kicker, title, intro, shot, caption, points, zoom=None, arrow_note=None, extra_shot=None, extra_caption=None, shot_contain=False, extra_contain=False):
    zoom_html = ""
    if zoom:
        zimg, ztitle, ztext = zoom
        zoom_html = f'''
        <div class="zoom-row">
          <div class="lupa-wrap">
            <div class="lupa-frame"><img src="img/{zimg}"></div>
            <div class="lupa-badge">🔍</div>
          </div>
          <div class="zoom-text"><b>{ztitle}</b>{ztext}</div>
        </div>'''

    shot_class = "shot-card small" if extra_shot else "shot-card"
    if shot_contain:
        shot_class += " contain"
    extra_html = ""
    if extra_shot:
        extra_class = "shot-card small" + (" contain" if extra_contain else "")
        extra_html = f'''
        <div class="{extra_class}">
          <img src="img/{extra_shot}">
          <div class="shot-caption">{extra_caption}</div>
        </div>'''

    arrow_html = ""
    if arrow_note:
        arrow_html = f'<div class="arrow-note">➜ {arrow_note}</div>'

    points_html = "\n".join(
        f'<li><span class="dot">{i+1}</span><span>{p}</span></li>'
        for i, p in enumerate(points)
    )

    return f'''
<div class="page">
  <div class="topbar"><img src="img/logo_white.png"><span class="tag">Área del Alumno</span></div>
  <div class="content">
    <div class="stepline"><div class="stepnum">{step}</div><span class="kicker">{kicker}</span></div>
    <h1 class="title">{title}</h1>
    <p class="intro">{intro}</p>
    {arrow_html}
    <div class="{shot_class}">
      <img src="img/{shot}">
      <div class="shot-caption">{caption}</div>
    </div>
    {extra_html}
    <ul class="points">
      {points_html}
    </ul>
    {zoom_html}
  </div>
  <div class="footer"><span class="brand">NEXO ACADÉMICO</span><span>Guía del alumno · app.nexoacademico.com</span></div>
</div>'''

pages = []

# 1. Login
pages.append(page(
  step=1, kicker="Primer acceso", title="Entra en tu área personal",
  intro="El equipo de Nexo Académico te entregará un usuario y una contraseña. Con esos datos accedes cada vez a tu panel, disponible tanto desde el ordenador como desde el móvil.",
  shot="login.png", caption="Pantalla de acceso — pestaña «Soy alumno»",
  shot_contain=True,
  points=[
    "Selecciona siempre la pestaña <b>«Soy alumno»</b> (la de «Soy profesor» es para tus profesores).",
    "Introduce el <b>usuario</b> y la <b>contraseña</b> que te ha facilitado Nexo Académico.",
    "Pulsa <b>Entrar</b> y accederás directamente a tu panel de Inicio.",
    "¿Problemas para entrar? Usa el enlace <b>«Contacta con Nexo»</b> al pie de la pantalla."
  ]
))

# 2. Inicio
pages.append(page(
  step=2, kicker="Panel principal", title="Inicio: tu resumen de un vistazo",
  intro="Es la primera pantalla que ves al entrar. Aquí tienes un resumen rápido de tu situación: horas de bono, sesiones del mes, tu próxima clase y accesos directos a lo más importante.",
  shot="inicio.png", caption="Inicio — panel general del alumno",
  points=[
    "<b>Horas restantes del bono</b>: cuántas horas de clase te quedan disponibles.",
    "<b>Sesiones este mes</b>: número de clases y horas ya trabajadas.",
    "<b>Próxima clase</b>: fecha y hora de tu siguiente sesión programada.",
    "<b>Informes recientes</b>, accesos directos a <b>Material</b> y <b>Tests</b>, y el bloque de <b>Próximas clases</b>."
  ],
  zoom=("zoom_bono.png", "Estado del bono y renovación por WhatsApp",
        " Cuando el bono se agota, aparece el aviso en rojo con el botón <b>«Renovar bono»</b>. "
        "Al pulsarlo se abre WhatsApp con un mensaje ya preparado para pedir la renovación directamente al equipo de Nexo, sin tener que escribir nada.")
))

# 3. Sesiones
pages.append(page(
  step=3, kicker="Mi área", title="Sesiones: el historial de tus clases",
  intro="En esta sección se registran automáticamente todas las clases que tu profesor va impartiendo, para que siempre puedas consultar cuándo y con quién has dado cada sesión.",
  shot="sesiones.png", caption="Sesiones — historial de clases confirmadas",
  points=[
    "Cada fila muestra la <b>fecha</b>, la <b>asignatura</b> y el <b>profesor</b> que impartió la clase.",
    "La columna <b>Dur.</b> indica la duración de esa sesión en horas.",
    "El <b>estado</b> («Confirmada») indica que la clase ha quedado registrada correctamente.",
    "Es tu comprobante de las horas realmente impartidas frente a las horas de tu bono."
  ]
))

# 4. Informes
pages.append(page(
  step=4, kicker="Mi área", title="Informes: seguimiento mensual",
  intro="Cada mes, el equipo de Nexo Académico elabora un informe de seguimiento con la evolución del alumno: temario trabajado, progreso y observaciones del profesor.",
  shot="informes.png", caption="Informes — informe mensual disponible para descargar",
  points=[
    "Los informes aparecen ordenados por fecha, el más reciente arriba del todo.",
    "Pulsa <b>Descargar</b> para guardar el informe en PDF en tu móvil u ordenador.",
    "Es la mejor forma de compartir tu progreso con tu familia."
  ],
  extra_shot=None
))

# 5. Bonos
pages.append(page(
  step=5, kicker="Mi área", title="Bonos: tus horas contratadas",
  intro="Aquí controlas todo lo relacionado con tus horas de clase: el bono activo, el historial de bonos anteriores y cómo contratar nuevas horas cuando las necesites.",
  shot="bonos1.png", caption="Bonos — estado, historial y planes disponibles",
  points=[
    "Arriba se muestra si tienes un <b>bono activo</b> o si necesitas solicitar uno nuevo.",
    "El <b>historial de bonos</b> guarda todos los bonos que has contratado, con fecha de compra, precio y si están agotados.",
    "Más abajo puedes elegir entre clases <b>Presenciales</b> u <b>Online</b>, con paquetes de 2, 4, 8 o 12 horas.",
  ],
  zoom=("zoom_precio.png", "Contratar un bono nuevo",
        " Elige el número de horas que necesitas y pulsa sobre el plan: se abrirá <b>WhatsApp</b> con Nexo Académico "
        "para confirmar la contratación directamente, sin gestiones adicionales.")
))

# 6. Calendario
pages.append(page(
  step=6, kicker="Mi área", title="Calendario: organiza tu semana",
  intro="Tu agenda personal de clases. Te permite ver de un vistazo cómo se reparten tus sesiones a lo largo del mes y añadir tus propias anotaciones (exámenes, repasos, etc.).",
  shot="calendario.png", caption="Calendario — vista mensual de clases",
  points=[
    "Cada clase programada aparece marcada en el día correspondiente con su asignatura.",
    "Usa las flechas ‹ › para moverte entre meses.",
    "Con el botón <b>«+ Añadir entrada»</b> puedes crear tú mismo un recordatorio."
  ],
  zoom=("zoom_bono.png" if False else "nueva_entrada.png", "Añadir una entrada al calendario",
        " Elige profesor, asignatura, hora de inicio y duración, añade notas si quieres y activa "
        "<b>«Repetir semanalmente»</b> si es una cita fija cada semana. Pulsa <b>Guardar</b> para confirmarla.")
))

# 7. Mi Profesor
pages.append(page(
  step=7, kicker="Mi área", title="Mi Profesor: quién te da clase",
  intro="Un listado con los profesores que tienes asignados, la asignatura que imparten, el número de sesiones realizadas y la modalidad de las clases.",
  shot="miprofesor1.png", caption="Mi Profesor — ficha de cada profesor asignado",
  points=[
    "Cada tarjeta muestra el <b>nombre del profesor</b>, su formación y la <b>asignatura</b> que imparte.",
    "Indica el número de <b>sesiones</b> realizadas y la <b>modalidad</b> (presencial u online).",
    "Si tienes varios profesores (por ejemplo, uno de Matemáticas y otro de Valenciano), aparecerán todos aquí."
  ],
  zoom=("zoom_contactar.png", "¿Algún problema o quieres un cambio?",
        " Al final de la página tienes el botón <b>«Contactar con Nexo»</b>: te abre WhatsApp directamente "
        "para pedir un cambio de profesor o resolver cualquier incidencia con el equipo de Nexo Académico.")
))

# 8. Material
pages.append(page(
  step=8, kicker="Estudiar", title="Material: tus recursos de estudio",
  intro="Todo el material de estudio que tu profesor prepara para ti, organizado y siempre disponible. Se divide en dos bloques según su origen.",
  shot="material.png", caption="Material — recursos genéricos y exclusivos",
  points=[
    "<b>Genérico</b>: material común, el mismo que pueden usar otros alumnos del mismo nivel.",
    "<b>Exclusivo</b>: fichas y recursos preparados específicamente para ti por tu profesor.",
    "Dentro de cada bloque, el material se organiza por <b>asignatura</b> y, dentro de ella, por <b>tema</b>."
  ],
  zoom=("zoom_exclusivo.png", "Material exclusivo, solo para ti",
        " El icono de la corona indica que ese contenido ha sido creado a medida por tu profesor. "
        "Pulsa sobre la asignatura y después sobre el tema para ver y descargar los archivos.")
))

# 9. Tareas
pages.append(page(
  step=9, kicker="Estudiar", title="Tareas: ejercicios y correcciones",
  intro="Tu profesor puede enviarte tareas para practicar entre clase y clase. Aquí las entregas y consultas la corrección, sin tener que esperar a la siguiente sesión.",
  shot="tareas.png", caption="Tareas — por entregar y corregidas",
  points=[
    "<b>Por entregar</b>: tareas pendientes, agrupadas por asignatura.",
    "<b>Corregidas</b>: tareas que tu profesor ya ha revisado, con su nota correspondiente.",
    "Pulsa sobre cualquier tarea para ver el enunciado adjunto y el detalle de la corrección."
  ],
  extra_shot="enunciado.png",
  extra_caption="Ejemplo de enunciado adjunto, con la marca de agua de Nexo Académico",
  zoom=("zoom_nota.png", "Detalle de una tarea corregida",
        " Dentro de cada tarea puedes pulsar <b>«Ver enunciado adjunto»</b> para descargar el ejercicio, "
        "y consultar la <b>nota</b> que te ha puesto tu profesor tras corregirla.")
))

# 10. Tests
pages.append(page(
  step=10, kicker="Estudiar", title="Tests: autoevaluación al momento",
  intro="Tu profesor puede asignarte tests de autoevaluación por asignatura. Los realizas desde el móvil y obtienes el resultado al instante, con la corrección detallada.",
  shot="tests.png", caption="Tests — organizados por asignatura",
  points=[
    "Cada asignatura muestra cuántos tests tienes <b>completados</b> sobre el total asignado.",
    "Pulsa sobre un test para responder a todas las preguntas.",
    "Al terminar, obtienes tu <b>nota sobre 10</b> y si el test está aprobado o no."
  ],
  zoom=("zoom_test.png", "Corrección al instante",
        " Las respuestas correctas se marcan en <b>verde</b> y las incorrectas en <b>rojo</b>, para que veas exactamente "
        "en qué has fallado. Si quieres repetir el test, tu profesor deberá habilitarte de nuevo.")
))

# 11. Avisos
pages.append(page(
  step=11, kicker="Avisos", title="Avisos: no te pierdas nada",
  intro="Nexo Académico te avisa cuando hay novedades: una nueva tarea, un test asignado, un cambio de horario... Puedes recibir estos avisos también como notificación en el móvil.",
  shot="avisos.png", caption="Avisos — comunicaciones del equipo de Nexo Académico",
  points=[
    "Cada aviso indica qué ha ocurrido (por ejemplo, un nuevo test asignado) y la fecha.",
    "En el menú lateral, <b>«Avisos al móvil»</b> te permite activar las notificaciones en tu dispositivo.",
    "Una vez activadas, recibirás un aviso directamente en el móvil cada vez que tu profesor suba algo nuevo."
  ],
  arrow_note="Menú lateral → Avisos → «Avisos al móvil» → Activar",
  extra_shot="avisos_modal.png",
  extra_contain=True,
  extra_caption="Confirmación al activar los avisos en el dispositivo"
))

with open("template.html") as f:
    html = f.read()

html = html.replace("PAGES_PLACEHOLDER", "\n".join(pages))

with open("catalogo.html", "w") as f:
    f.write(html)

print("OK, pages:", len(pages))
