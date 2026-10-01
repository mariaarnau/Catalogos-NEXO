#!/usr/bin/env python3
"""Genera datos FICTICIOS de un mes de Héctor (1º Bachillerato, American School of Valencia).

Horario real del plan: lunes a viernes 9-13 h, bono de 20 h/semana
(Matemáticas 6 h, Física 5 h, Química 5 h, Biología 4 h).
Las cifras (horas, sesiones, medias, semanas) se calculan desde la tabla de sesiones,
para que el texto nunca se contradiga con los datos.

Uso: python3 crear_ejemplo_hector.py   ->   hector_ejemplo_2026-09.json
"""
import datetime as dt, json
from pathlib import Path

AQUI = Path(__file__).parent
D, B, S = 1, 2, 3                      # comprensión: con dificultad, bien, con soltura
AUT = {"c": 25, "p": 55, "s": 90}      # autonomía: ayuda constante / puntual / resuelve solo
MUY, NOR = "M", "N"                    # implicación: muy implicado / normal
r = lambda x: int(x + 0.5)

# (día de septiembre, horas, tema, comprensión, autonomía, implicación)
SES = {
 "Matemáticas": (["Números reales, potencias y radicales", "Álgebra: polinomios, ecuaciones y sistemas", "Trigonometría"], [
   (7, 2, 0, B, "p", NOR), (9, 2, 0, B, "p", MUY), (10, 2, 0, S, "s", MUY),
   (14, 2, 1, B, "p", MUY), (16, 2, 1, S, "s", MUY), (17, 2, 1, S, "s", MUY), (21, 2, 1, B, "s", MUY),
   (23, 2, 2, D, "c", MUY), (24, 2, 2, D, "p", MUY), (28, 2, 2, B, "p", MUY), (30, 2, 2, B, "s", MUY)]),
 "Física": (["Cinemática: MRU y MRUA", "Cinemática: tiro parabólico y movimiento circular", "Dinámica: leyes de Newton y rozamiento"], [
   (7, 2, 0, B, "p", NOR), (9, 2, 0, D, "c", NOR), (11, 1, 0, D, "p", NOR), (14, 2, 0, B, "p", MUY),
   (16, 2, 1, D, "c", MUY), (18, 1, 1, D, "p", MUY), (21, 2, 1, B, "s", MUY),
   (23, 2, 2, D, "c", NOR), (25, 1, 2, B, "p", MUY), (28, 2, 2, B, "p", MUY), (30, 2, 2, D, "p", MUY)]),
 "Química": (["Formulación y nomenclatura inorgánica", "El mol, masas y gases ideales", "Disoluciones y concentración"], [
   (8, 2, 0, B, "p", MUY), (10, 2, 0, S, "s", MUY), (11, 1, 0, B, "s", MUY), (15, 2, 0, S, "s", MUY),
   (17, 2, 1, B, "p", MUY), (18, 1, 1, D, "p", NOR), (22, 2, 1, B, "p", MUY),
   (24, 2, 2, B, "p", MUY), (25, 1, 2, S, "s", MUY), (29, 2, 2, S, "s", MUY)]),
 "Biología": (["Bioelementos, agua y sales minerales", "Glúcidos y lípidos", "Proteínas y ácidos nucleicos"], [
   (8, 2, 0, B, "s", MUY), (11, 2, 0, S, "s", MUY), (15, 2, 1, B, "s", NOR), (18, 2, 1, D, "p", NOR),
   (22, 2, 1, B, "p", NOR), (25, 2, 2, D, "p", NOR), (29, 2, 2, B, "p", MUY)]),
}
COLOR = {"Matemáticas": "blue", "Física": "purple", "Química": "green", "Biología": "gold"}
SEMANAS = [(7, 11, "7–11 sep"), (14, 18, "14–18 sep"), (21, 25, "21–25 sep"), (28, 30, "28–30 sep")]


def stats(nombre):
    temas, ses = SES[nombre]
    horas = sum(s[1] for s in ses)
    aut = [AUT[s[4]] for s in ses]
    sem = []
    for a, b, et in SEMANAS:
        v = [AUT[s[4]] for s in ses if a <= s[0] <= b]
        sem.append({"e": et, "v": r(sum(v) / len(v))})
    return {
        "horas": horas, "n": len(ses), "aut": r(sum(aut) / len(aut)), "sem": [x["v"] for x in sem], "sem_graf": sem,
        "dif": sum(s[3] == D for s in ses), "muy": sum(s[5] == MUY for s in ses), "nor": sum(s[5] == NOR for s in ses),
        "temas": [{"nombre": t, "horas": sum(s[1] for s in ses if s[2] == i)} for i, t in enumerate(temas)],
        "comp": [{"e": str(s[0]), "v": s[3]} for s in ses],
    }


M, F, Q, Bi = (stats(n) for n in ("Matemáticas", "Física", "Química", "Biología"))
tot_h = sum(x["horas"] for x in (M, F, Q, Bi)); tot_n = sum(x["n"] for x in (M, F, Q, Bi))
tot_muy = sum(x["muy"] for x in (M, F, Q, Bi))
tot_aut = r(sum(AUT[s[4]] for n in SES for s in SES[n][1]) / tot_n)
dias = {s[0] for n in SES for s in SES[n][1]}
assert (tot_h, tot_n, len(dias)) == (72, 39, 18), (tot_h, tot_n, len(dias))
assert (M["horas"], F["horas"], Q["horas"], Bi["horas"]) == (22, 19, 17, 14)
p = lambda x: f"{x} %"

# ---- calendario de octubre -------------------------------------------------
festivos = ["2026-10-09", "2026-10-12"]
examen = "2026-10-15"
oct_lab = [dt.date(2026, 10, d) for d in range(2, 31) if dt.date(2026, 10, d).weekday() < 5]
sesiones_oct = [x.isoformat() for x in oct_lab if x.isoformat() not in festivos + [examen]]

datos = {
  "ejemplo": True,
  "alumno": "Héctor",
  "curso": "1º Bachillerato · American School of Valencia · Clases online",
  "profesor_completo": "Profesor de referencia asignado por Nexo",
  "mes": 9, "anio": 2026, "fecha_informe": "2026-10-01", "hay_mes_anterior": False,
  "comprension_sub": "Comprensión del tema, sesión a sesión (días de septiembre)",
  "progreso_destacado": "Matemáticas — en álgebra pasó de ayuda puntual (14 sep) a resolver solo en las tres sesiones siguientes (16, 17 y 21 sep)",
  "resumen_parrafos": [
    {"titulo": "El mes en general", "color": "gold", "parrafos": [
      f"En septiembre, Héctor ha completado {tot_n} sesiones en 18 días de clase, {tot_h} horas en total y sin faltar a ninguna: {M['horas']} h de Matemáticas, {F['horas']} h de Física, {Q['horas']} h de Química y {Bi['horas']} h de Biología.",
      f"Es su primer mes con Nexo, así que este informe recoge su punto de partida. Lo más sólido es la constancia (asistencia completa y «muy implicado» en {tot_muy} de las {tot_n} sesiones) y la autonomía en Química y Matemáticas. El punto a vigilar es Física, que además tiene examen el 15 de octubre."]},
    {"titulo": "Matemáticas", "color": "blue", "parrafos": [
      "Dominó pronto los números reales, las potencias y los radicales, y en álgebra pasó de ayuda puntual a resolver solo en las tres sesiones siguientes.",
      "Al empezar trigonometría (23 sep) bajó el rendimiento, como ocurre con cada contenido nuevo, y a final de mes ya remontaba: el 30 resolvió solo."]},
    {"titulo": "Física", "color": "purple", "parrafos": [
      f"Es la asignatura con menos autonomía ({p(F['aut'])} de media) y la que más sesiones concentra «con dificultad» ({F['dif']} de {F['n']}).",
      "Cada vez que llega un tema nuevo —MRUA, tiro parabólico, leyes de Newton— necesita ayuda constante y después va afianzando. Es el foco de octubre por el examen del día 15."]},
    {"titulo": "Química", "color": "green", "parrafos": [
      "La formulación inorgánica quedó consolidada y las disoluciones las resolvió solo y con soltura en las dos últimas sesiones.",
      "El tramo más exigente fue el mol y los gases ideales (17 y 18 sep)."]},
    {"titulo": "Biología", "color": "gold", "parrafos": [
      f"Empezó muy bien (bioelementos y agua, resueltos solo), pero la autonomía bajó del {p(Bi['sem'][0])} de la semana 1 al {p(Bi['sem'][2])} de las semanas 3 y 4 al llegar los lípidos y las proteínas, con mucho vocabulario y estructuras.",
      "Es una asignatura de memoria: se trabaja mejor con esquemas propios y autotest que releyendo."]}],
  "asignaturas": [
    {"nombre": "Matemáticas", "color": "blue", "profesor": "Profesor de referencia", "profesor_completo": "Profesor de referencia asignado por Nexo",
     "horario": "Lunes y miércoles (2 h) · jueves (2 h)", "sesiones": M["n"], "horas": M["horas"], "temas": M["temas"],
     "puntos_fuertes": [
       "Números reales, potencias y radicales dominados pronto: el 10 de septiembre ya los resolvía solo y con soltura",
       "Álgebra: tras necesitar ayuda puntual el 14 de septiembre, resolvió solo en las tres sesiones siguientes (16, 17 y 21)",
       f"Muy implicado en {M['muy']} de las {M['n']} sesiones"],
     "a_tener_en_cuenta": [
       "Cada tema nuevo baja el rendimiento: al empezar trigonometría (23 sep) la comprensión fue «con dificultad» y necesitó ayuda constante",
       "Se recupera rápido: el 28 de septiembre volvió a «bien» y el 30 resolvió solo"],
     "puntos_a_mejorar": [
       "Autonomía al empezar contenido nuevo: la primera sesión de cada tema todavía requiere apoyo",
       "Trigonometría: elegir la razón o identidad adecuada antes de operar"],
     "refuerzo": [
       "Repaso de 20 minutos por la tarde de las razones e identidades trigonométricas, tapando la fórmula e intentando recordarla",
       "Al empezar cada tema, mirar primero un ejemplo resuelto y después hacer los ejercicios solo",
       "Los tests dinámicos de la App de Nexo, filtrados por «Trigonometría»"],
     "autonomia_por_sesion": M["sem_graf"], "autonomia_sub": "media por semana",
     "autonomia_nota": "Media de la semana · Escala a partir de la respuesta del profesor: ayuda constante 25 % · ayuda puntual 55 % · resuelve solo 90 %",
     "comprension_por_sesion": M["comp"]},
    {"nombre": "Física", "color": "purple", "profesor": "Profesor de referencia", "profesor_completo": "Profesor de referencia asignado por Nexo",
     "horario": "Lunes y miércoles (2 h) · viernes (1 h)", "sesiones": F["n"], "horas": F["horas"], "temas": F["temas"],
     "puntos_fuertes": [
       "Cuando el planteamiento está claro, resuelve con orden: el 21 de septiembre resolvió solo los ejercicios de tiro parabólico",
       f"Muy implicado en {F['muy']} de las {F['n']} sesiones"],
     "a_tener_en_cuenta": [
       "Los tres miércoles de las semanas 1 a 3 (9, 16 y 23 sep) necesitó ayuda constante, coincidiendo con contenido nuevo: MRUA, tiro parabólico y leyes de Newton",
       "Examen de Física el 15 de octubre (cinemática y dinámica): es la asignatura prioritaria de octubre"],
     "puntos_a_mejorar": [
       "Planteamiento de los problemas: identificar datos e incógnita y hacer el esquema (diagrama de fuerzas) antes de operar",
       f"Comprensión: «con dificultad» en {F['dif']} de las {F['n']} sesiones",
       f"Autonomía: {p(F['aut'])} de media, la más baja de las cuatro asignaturas"],
     "refuerzo": [
       "Tres pasos fijos antes de cada problema: datos, incógnita y esquema",
       "Formulario de Física al día: repaso de 20 minutos por la tarde",
       "Dos problemas diarios mezclando cinemática y dinámica, en vez de bloques de un solo tipo",
       "Los tests dinámicos de la App de Nexo, filtrados por «Cinemática» y «Dinámica»"],
     "autonomia_por_sesion": F["sem_graf"], "autonomia_sub": "media por semana",
     "autonomia_nota": "Media de la semana · Escala a partir de la respuesta del profesor: ayuda constante 25 % · ayuda puntual 55 % · resuelve solo 90 %",
     "comprension_por_sesion": F["comp"]},
    {"nombre": "Química", "color": "green", "profesor": "Profesor de referencia", "profesor_completo": "Profesor de referencia asignado por Nexo",
     "horario": "Martes y jueves (2 h) · viernes (1 h)", "sesiones": Q["n"], "horas": Q["horas"], "temas": Q["temas"],
     "puntos_fuertes": [
       "Formulación inorgánica consolidada: de ayuda puntual (8 sep) a resolver solo en las tres sesiones siguientes (10, 11 y 15)",
       "Disoluciones resueltas solo y con soltura en las dos últimas sesiones (25 y 29 sep)",
       f"Muy implicado en {Q['muy']} de las {Q['n']} sesiones"],
     "a_tener_en_cuenta": [
       "El mol y los gases ideales fueron el tramo más exigente: ayuda puntual el 17 y comprensión «con dificultad» el 18 (sesión de 1 h)"],
     "puntos_a_mejorar": [
       "Conversión entre moles, gramos y litros: es la base de la estequiometría que viene en octubre",
       "Plantear los cálculos de concentración (molaridad) sin ayuda desde el primer ejercicio"],
     "refuerzo": [
       "Diez minutos diarios de ejercicios cortos de mol, gramos y litros",
       "Repasar la formulación cinco minutos al día, sin mirar los apuntes",
       "Los tests dinámicos de la App de Nexo, filtrados por «El mol»"],
     "autonomia_por_sesion": Q["sem_graf"], "autonomia_sub": "media por semana",
     "autonomia_nota": "Media de la semana · Escala a partir de la respuesta del profesor: ayuda constante 25 % · ayuda puntual 55 % · resuelve solo 90 %",
     "comprension_por_sesion": Q["comp"]},
    {"nombre": "Biología", "color": "gold", "profesor": "Profesor de referencia", "profesor_completo": "Profesor de referencia asignado por Nexo",
     "horario": "Martes y viernes (2 h)", "sesiones": Bi["n"], "horas": Bi["horas"], "temas": Bi["temas"],
     "puntos_fuertes": [
       "Bioelementos y agua: «bien» y «con soltura», resolviendo solo (8 y 11 sep)",
       "Proteínas y ácidos nucleicos: el 29 de septiembre volvió a «bien» y a «muy implicado»"],
     "a_tener_en_cuenta": [
       "Lípidos y proteínas, con mucho vocabulario y estructuras, son lo más exigente: comprensión «con dificultad» el 18 y el 25 de septiembre",
       f"La autonomía bajó del {p(Bi['sem'][0])} (semana 1) al {p(Bi['sem'][2])} (semanas 3 y 4) a medida que el contenido se vuelve más denso"],
     "puntos_a_mejorar": [
       "Retener vocabulario y estructuras: estudiar con esquemas y autotest en vez de releer",
       f"Implicación «normal» en {Bi['nor']} de las {Bi['n']} sesiones (en Matemáticas y Química fue «muy implicado» casi siempre)"],
     "refuerzo": [
       "Un esquema propio de cada biomolécula (glúcidos, lípidos, proteínas) en una sola hoja",
       "Autotest: tapar el esquema y reconstruirlo de memoria, repitiéndolo a los 2-3 días",
       "Los tests dinámicos de la App de Nexo, filtrados por «Biomoléculas»"],
     "autonomia_por_sesion": Bi["sem_graf"], "autonomia_sub": "media por semana",
     "autonomia_nota": "Media de la semana · Escala a partir de la respuesta del profesor: ayuda constante 25 % · ayuda puntual 55 % · resuelve solo 90 %",
     "comprension_por_sesion": Bi["comp"]},
  ],
  "kpis_conclusion": [[p(tot_aut), "AUTONOMÍA MEDIA"], [f"{tot_h}h", "TOTAL DEDICADAS"], [f"{tot_n}/{tot_n}", "SESIONES SIN FALTAR"], ["12", "TEMAS TRABAJADOS"]],
  "temas_trabajados": 12,
  "conclusion": f"Septiembre cierra con un mes muy constante: {tot_n} sesiones, {tot_h} horas y asistencia completa. Química ({p(Q['aut'])} de autonomía media) y Matemáticas ({p(M['aut'])}) avanzan con buena soltura. Física ({p(F['aut'])}) y Biología ({p(Bi['aut'])}) necesitan más apoyo: Física, por el examen del 15 de octubre y porque cada tema nuevo arranca con ayuda constante; Biología, porque la autonomía baja a medida que sube el vocabulario. Al ser el primer informe, es una foto de partida: desde el próximo mes se podrá comparar con septiembre.",
  "evolucion_intro": "Al ser el primer informe de Héctor, todavía no hay un mes anterior con el que comparar. Desde el próximo informe esta sección comparará mes a mes; por ahora resume su evolución semana a semana durante septiembre.",
  "evolucion": [
    {"titulo": "Matemáticas", "etiqueta": "Autonomía semanal", "tendencia": "irregular", "estado": "sólida, con bajón en trigonometría",
     "texto": f"Media semanal: {p(M['sem'][0])} → {p(M['sem'][1])} → {p(M['sem'][2])} → {p(M['sem'][3])}. La semana 3 baja al empezar trigonometría (25 % el 23 de septiembre) y la 4 vuelve a subir: el patrón se repite con cada tema nuevo y se recupera en pocos días."},
    {"titulo": "Física", "etiqueta": "Autonomía semanal", "tendencia": "sube", "estado": "mejora leve desde la semana 3",
     "texto": f"Media semanal: {p(F['sem'][0])} → {p(F['sem'][1])} → {p(F['sem'][2])} → {p(F['sem'][3])}. Es la media más baja de las cuatro. El 21 de septiembre resolvió solo el tiro parabólico y en la última semana no hubo ninguna sesión de ayuda constante, aunque con solo cuatro semanas de datos conviene confirmarlo en octubre."},
    {"titulo": "Química", "etiqueta": "Autonomía semanal", "tendencia": "sube", "estado": f"de {p(Q['sem'][0])} a {p(Q['sem'][3])}",
     "texto": f"Media semanal: {p(Q['sem'][0])} → {p(Q['sem'][1])} → {p(Q['sem'][2])} → {p(Q['sem'][3])}. Bajó con el mol y los gases (semanas 2 y 3) y cerró septiembre resolviendo solo y con soltura las disoluciones."},
    {"titulo": "Biología", "etiqueta": "Autonomía semanal", "tendencia": "baja", "estado": f"de {p(Bi['sem'][0])} a {p(Bi['sem'][3])}",
     "texto": f"Media semanal: {p(Bi['sem'][0])} → {p(Bi['sem'][1])} → {p(Bi['sem'][2])} → {p(Bi['sem'][3])}. Con bioelementos y agua resolvía solo; con lípidos y proteínas necesita ayuda puntual y la comprensión fue «con dificultad» el 18 y el 25 de septiembre."},
  ],
  "examenes": [{"asignatura": "Física", "tema": "cinemática y dinámica", "fecha": examen,
                "fuente": "Héctor, en la sesión de Física del 28 de septiembre"}],
  "sesiones_proximo_mes": sesiones_oct, "sesiones_extra": ["2026-10-13"], "festivos": festivos,
  "texto_examen": "Antes del examen Héctor tiene 6 sesiones de Física, 10 horas en total: 8 h de mañana (una de ellas cedida por Matemáticas el 8 de octubre) y 2 h de tarde el martes 13. El viernes 9 y el lunes 12 son festivos y no hay clase. El examen cubre los tres bloques trabajados en septiembre: MRU y MRUA, tiro parabólico y movimiento circular, y leyes de Newton.",
  "plan_examen": [
    ["2–8 de octubre", "Repasar cinemática con problemas mezclados (MRU, MRUA, tiro parabólico). El jueves 8, la hora de 12:00 a 13:00 de Matemáticas pasa a Física."],
    ["13–14 de octubre", "Martes 13 por la tarde (2 h): sesión práctica con exámenes de otros años. Miércoles 14: dinámica —diagrama de fuerzas, rozamiento y planos inclinados— y repaso del formulario."],
    ["Jueves 15", "Examen de Física."]],
  "organizacion_actual": [
    "Jornada: lunes a viernes, de 9:00 a 13:00, online · bono de 20 h semanales",
    f"Matemáticas — {M['horas']} h en {M['n']} sesiones",
    f"Física — {F['horas']} h en {F['n']} sesiones",
    f"Química — {Q['horas']} h en {Q['n']} sesiones",
    f"Biología — {Bi['horas']} h en {Bi['n']} sesiones",
    f"Total: {tot_h} h en {tot_n} sesiones, repartidas en 18 días de clase"],
  "semana_tipo": {
    "Lunes": [["Matemáticas", "9:00 – 11:00", "blue"], ["Física", "11:00 – 13:00", "purple"]],
    "Martes": [["Química", "9:00 – 11:00", "green"], ["Biología", "11:00 – 13:00", "gold"]],
    "Miércoles": [["Matemáticas", "9:00 – 11:00", "blue"], ["Física", "11:00 – 13:00", "purple"]],
    "Jueves": [["Química", "9:00 – 11:00", "green"], ["Matemáticas", "11:00 – 13:00", "blue"]],
    "Viernes": [["Física", "9:00 – 10:00", "purple"], ["Química", "10:00 – 11:00", "green"], ["Biología", "11:00 – 13:00", "gold"]]},
  "propuesta": [
    {"asignatura": "Física", "accion": "REFORZAR", "texto": "Prioridad hasta el examen del 15 de octubre: 1 h más el jueves 8 (cedida por Matemáticas) y sesión práctica de tarde el martes 13. Después del examen, entrar en trabajo y energía."},
    {"asignatura": "Matemáticas", "accion": "MANTENER", "texto": "Mantener las 6 h semanales (1 h menos solo el 8 de octubre) para consolidar trigonometría y empezar vectores y geometría analítica."},
    {"asignatura": "Química", "accion": "AVANZAR", "texto": "Pasar a la estequiometría de las reacciones y al rendimiento, apoyándose en lo que ya domina: formulación y disoluciones."},
    {"asignatura": "Biología", "accion": "REFORZAR", "texto": "Pasar de leer a recordar: esquema propio de cada biomolécula y autotest. Continuar con la estructura de la célula y sus orgánulos."}],
  "base_cientifica": {
    "texto": "Las recomendaciones se apoyan en técnicas con evidencia sólida: la práctica espaciada y la autoevaluación (recuperar en lugar de releer) mejoran la retención a largo plazo; mezclar tipos de problemas en el repaso mejora el aprendizaje en matemáticas; y los ejemplos resueltos ayudan al empezar contenido nuevo.",
    "referencias": [
      "Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., & Willingham, D. T. (2013). Improving students' learning with effective learning techniques. Psychological Science in the Public Interest, 14(1), 4–58.",
      "Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., & Rohrer, D. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. Psychological Bulletin, 132(3), 354–380.",
      "Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. Psychological Science, 17(3), 249–255.",
      "Rohrer, D., & Taylor, K. (2007). The shuffling of mathematics problems improves learning. Instructional Science, 35(6), 481–498.",
      "Sweller, J., & Cooper, G. A. (1985). The use of worked examples as a substitute for problem solving in learning algebra. Cognition and Instruction, 2(1), 59–89."]},
}

salida = AQUI / "hector_ejemplo_2026-09.json"
salida.write_text(json.dumps(datos, ensure_ascii=False, indent=2))
print("Generado:", salida)
for n, x in (("Matemáticas", M), ("Física", F), ("Química", Q), ("Biología", Bi)):
    print(f"{n:12} {x['horas']:>2} h · {x['n']:>2} ses · autonomía {x['aut']} % · semanas {x['sem']} · dif {x['dif']} · muy {x['muy']} · temas {[t['horas'] for t in x['temas']]}")
print("TOTAL", tot_h, "h ·", tot_n, "ses ·", len(dias), "días · autonomía", tot_aut, "% · muy implicado", tot_muy)
