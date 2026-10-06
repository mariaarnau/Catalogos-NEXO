#!/usr/bin/env python3
"""Genera el plan personalizado de NEXO Académico para un lead.

Uso:  python3 planes/generar_plan.py planes/leads/<lead>.json
Salida: planes/output/Plan_NEXO_<Nombre>.html y .pdf
"""
import base64
import calendar
import datetime as dt
import html
import json
import re
import subprocess
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
LOGO = REPO / "nexo_blanco_transparente (2).png"

# Tarifas 26/27. La base (€/h) sirve para el precio tachado de 2h y para el ahorro del bono recomendado.
# Casa del profesor = mismas tarifas que online. Primaria: solo presencial en casa del alumno.
TARIFAS = {
    "primaria": {"nombre": "Primaria", "corto": "Primaria",
                 "base": {"casa_alumno": 22},
                 "precios": {"casa_alumno": {2: 40, 4: 86, 8: 170, 12: 250}}},
    "eso": {"nombre": "ESO", "corto": "ESO",
            "base": {"online": 23, "casa_alumno": 24},
            "precios": {"online": {2: 40, 4: 90, 8: 175, 12: 260},
                        "casa_alumno": {2: 44, 4: 94, 8: 185, 12: 270}}},
    "bachillerato": {"nombre": "Bachillerato", "corto": "Bach",
                     "base": {"online": 24, "casa_alumno": 25},
                     "precios": {"online": {2: 42, 4: 94, 8: 185, 12: 270},
                                 "casa_alumno": {2: 46, 4: 98, 8: 195, 12: 285}}},
    "universidad": {"nombre": "Universidad", "corto": "Universidad",
                    "base": {"online": 25, "casa_alumno": 27.5},
                    "precios": {"online": {2: 44, 4: 98, 8: 195, 12: 285},
                                "casa_alumno": {2: 49, 4: 105, 8: 205, 12: 300}}},
}
for _t in TARIFAS.values():
    if "online" in _t["precios"]:
        _t["precios"]["casa_profesor"] = _t["precios"]["online"]
        _t["base"]["casa_profesor"] = _t["base"]["online"]

MOD_TITULO = {"online": "Online", "casa_profesor": "En casa del profesor",
              "casa_alumno": "Presencial en casa del alumno"}
FEATURES = {2: ["Evaluación inicial", "Sustitución garantizada"],
            4: ["Evaluación inicial", "Sustitución garantizada"],
            8: ["Plan de trabajo", "Ajuste de horas entre bloques", "Área privada alumno"],
            12: ["Plan de trabajo", "Ajuste de horas entre bloques", "Área privada alumno"]}

e = html.escape


def eur(x, dec=2):
    x = Decimal(str(x)).quantize(Decimal(1).scaleb(-dec), rounding=ROUND_HALF_UP)
    s = f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"


def pct(ahorro, total):
    # Redondeo a entero, mitad hacia arriba
    return int(ahorro / total * 100 + 0.5)


def lista_asig(a):
    if not a:
        return ""
    return a[0] if len(a) == 1 else ", ".join(a[:-1]) + " y " + a[-1]


def textos(d):
    n, asig = d["nombre"] or "vuestro hijo o hija", lista_asig(d["asignaturas"])
    una = len(d["asignaturas"]) == 1
    pl = len(d["bonos_recomendados"]) > 1
    esp = asig or TARIFAS[d["etapa"]]["nombre"]  # especialidad del profesor si no hay asignaturas
    solo_casa = d["modalidades_recomendadas"] == ["casa_alumno"]
    if asig:
        con_tu, con_su = f"con clases de {asig}", f"con clases de {asig}"
    elif solo_casa:
        con_tu, con_su = "con el profesor en tu propia casa", "con el profesor en su propia casa"
    else:
        con_tu, con_su = "con clases a tu medida", "con clases a su medida"
    if d["voz"] == "tu":
        return dict(
            cover_sub=f"Un acompañamiento diseñado específicamente para ti, {n}, {con_tu}.",
            cover_foot="CURSO 2026–2027 — CONDICIONES VÁLIDAS PARA ESTE PLAN",
            p2_title=f"Así te acompañamos cada mes, {n}",
            p2_sub=f"Un profesor especializado en {esp}, con sesiones centradas en {'tu asignatura' if una else 'tus asignaturas'} y ajuste continuo según lo que necesites reforzar.",
            c1=f"Tienes tu profesor de referencia asignado, especializado en {esp}, con horario fijo cada semana.",
            c2t="Enfoque a tus exámenes",
            c2="Cada sesión se centra en lo que tienes más cerca: trabajos, entregas o el próximo examen.",
            c3="Si necesitas reforzar un bloque concreto antes de un examen, el enfoque de las sesiones se adapta sin coste extra.",
            gestiones="GESTIONES A TU CARGO",
            p3_sub="Tienes tu propio informe de seguimiento dentro del plan, sin coste adicional. Esto es lo que incluye cada mes:",
            p4_pill="ASÍ LO VERÁS TÚ",
            p4_sub="Cuatro pantallas de ejemplo del informe que recibirás en tu área privada.",
            pagais="Pagas por adelantado. Sin letra pequeña. Más horas, mejor precio.",
            p8_pill="TU BONO MENSUAL",
            p8_para="Te recomendamos",
            su_casa=d.get("presencial_label", "en tu casa"),
            p8_badge=(f"BONOS RECOMENDADOS PARA {n.upper()}" if pl else f"BONO RECOMENDADO PARA {n.upper()}"),
            p9_sub=("Tus bonos recomendados" if pl else "Tu bono recomendado") + ", de un vistazo.",
            p9_l1="El bono cubre tus clases mensuales" + (f" de {asig}" if asig else ""),
            p9_l2="Sin permanencia: si un mes necesitas menos horas, se ajusta el bono contratado.",
            quote="Un plan a medida para acompañarte" + (f" en {asig}" if asig else ""),
            p10_sub="Escríbenos para confirmar tu bono de cada mes o cualquier ajuste de horas.",
        )
    fam = dict(
        cover_sub=f"Un acompañamiento diseñado específicamente para {n}, {con_su}.",
        cover_foot="CURSO 2026–2027 — CONDICIONES VÁLIDAS PARA ESTA FAMILIA",
        p2_title=f"Así acompañamos a {n} cada mes",
        p2_sub=f"Un profesor especializado en {esp}, con sesiones centradas en {'su asignatura' if una else 'sus asignaturas'} y ajuste continuo según lo que necesite reforzar.",
        c1=f"{n} tiene su profesor de referencia asignado, especializado en {esp}, con horario fijo cada semana.",
        c2t="Enfoque a sus exámenes",
        c2="Cada sesión se centra en lo que tiene más cerca: trabajos, entregas o el próximo examen.",
        c3="Si necesita reforzar un bloque concreto antes de un examen, el enfoque de las sesiones se adapta sin coste extra.",
        gestiones="GESTIONES A CARGO TUYO",
        p3_sub=f"{n} tiene su propio informe de seguimiento dentro del plan, sin coste adicional. Esto es lo que incluye cada mes:",
        p4_pill="ASÍ LO VERÉIS VOSOTROS",
        p4_sub="Cuatro pantallas de ejemplo del informe que recibiréis en vuestra área privada.",
        pagais="Pagáis por adelantado. Sin letra pequeña. Más horas, mejor precio.",
        p8_pill="SU BONO MENSUAL",
        p8_para=f"Para {n} te recomendamos",
        su_casa=d.get("presencial_label", "en su casa"),
        p8_badge=(f"BONOS RECOMENDADOS DE {n.upper()}" if pl else f"BONO RECOMENDADO DE {n.upper()}"),
        p9_sub=(f"Los bonos recomendados de {n}" if pl else f"El bono recomendado de {n}") + ", de un vistazo.",
        p9_l1=f"El bono cubre las clases mensuales de {n}" + (f" de {asig}" if asig else ""),
        p9_l2="Sin permanencia: si un mes necesita menos horas, se ajusta el bono contratado.",
        quote=f"Un plan a medida para acompañar a {n}" + (f" en {asig}" if asig else ""),
        p10_sub=f"Escríbenos para confirmar el bono de cada mes o cualquier ajuste de horas de {n}.",
    )
    if not d["nombre"]:  # lead sin nombre: textos genéricos para la familia
        fam.update(
            c1=cap(fam["c1"]), p3_sub=cap(fam["p3_sub"]), p8_para="Os recomendamos",
            p8_badge="BONOS RECOMENDADOS" if pl else "BONO RECOMENDADO",
            p9_sub=("Los bonos recomendados" if pl else "El bono recomendado") + ", de un vistazo.",
            p9_l1="El bono cubre las clases mensuales" + (f" de {asig}" if asig else ""),
            p10_sub="Escríbenos para confirmar el bono de cada mes o cualquier ajuste de horas.",
        )
    return fam


def cap(x):
    return x[:1].upper() + x[1:]


def mod_corto(m, t):
    return {"online": "online", "casa_profesor": "en casa del profesor", "casa_alumno": t["su_casa"]}[m]


def header(label, logo=True):
    lg = f'<img class="logo-sm" src="{LOGO_URI}">' if logo else ""
    return f'<div class="hdr">{lg}<span class="hdr-l">{e(label)}</span></div><div class="rule"></div>'


def footer(txt="Nexo Académico · Plan personalizado"):
    return f'<div class="foot"><span>{e(txt)}</span><span>nexoacademico.com</span></div>'


def page_cover(d, t):
    sub = d["curso"] or " · ".join(d["asignaturas"])
    return f'''<section class="page cover glow">
  <img class="logo-lg" src="{LOGO_URI}">
  <div class="pill gold">{e(d.get("cover_pill", "DOCUMENTO PRIVADO · PLAN PERSONALIZADO"))}</div>
  <h1 class="cover-h">Tu plan a medida en<br><em>NEXO Académico</em></h1>
  <p class="cover-sub">{e(t["cover_sub"])}</p>
  <div class="name-card"><div class="nm">{e(d.get("nombre_completo") or d["nombre"] or d["curso"])}</div><div class="cs">{e((d.get("cover_card_sub") or (sub if d["nombre"] else lista_asig(d["asignaturas"]))).upper())}</div></div>
  <div class="cover-foot">{e(t["cover_foot"])}</div>
</section>'''


def page_ruta(d, t):
    """Hoja de ruta: calendario semanal de horas por asignatura hasta los exámenes."""
    r = d["ruta"]
    asigs = d["asignaturas"]
    num = lambda x: (f"{x:g}").replace(".", ",")
    stats = "".join(f"<div><b>{e(a)}</b><span>{e(b)}</span></div>" for a, b in r["stats"])
    esc = r.get("px_por_hora", 25)
    # Cabecera de meses: agrupa semanas consecutivas del mismo mes de bono
    grupos = []
    for w in r["semanas"]:
        if grupos and grupos[-1]["mes"] == w["mes"]:
            grupos[-1]["n"] += 1
            grupos[-1]["h"] += sum(w.get("horas", []))
        else:
            grupos.append({"mes": w["mes"], "n": 1, "h": sum(w.get("horas", []))})
    meses = ""
    for g in grupos:
        info = r["meses"].get(g["mes"], "")
        txt = e(info) if r.get("ocultar_total") else f'{num(g["h"])}h{" · " + e(info) if info else ""}'
        meses += (f'<div class="mes" style="grid-column: span {g["n"]}"><b>{e(g["mes"])}</b>'
                  f'<span>{txt}</span></div>')
    cols = ""
    for w in r["semanas"]:
        if w.get("examen"):
            cols += (f'<div class="wk ex"><div class="exbox"><span>{e(w["examen"])}</span></div>'
                     f'<small>{e(w["label"])}</small></div>')
            continue
        segs = "".join(f'<i class="c{i}" style="height:{h*esc:.0f}px"></i>' for i, h in enumerate(w["horas"]) if h)
        tot = sum(w["horas"])
        top = w.get("top") or f"{num(tot)}h"
        cols += (f'<div class="wk{" pico" if tot >= 4.5 else ""}"><div class="stack"><b>{top}</b>{segs}</div>'
                 f'<small>{e(w["label"])}</small></div>')
    leg = "".join(f'<span><i class="c{i}"></i>{e(a)}</span>' for i, a in enumerate(r.get("leyenda") or asigs))
    bloques = "".join(f'<div class="blq"><small>{e(k)}</small><h4>{e(h)}</h4><p>{e(x)}</p></div>'
                      for k, h, x in r["bloques"])
    return f'''<section class="page glow ruta">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">{e(r["etiqueta"])}</span></div><div class="rule"></div>
  <div class="pill gold">{e(r["pill"])}</div>
  <h2>{e(r["titulo"])}</h2>
  <p class="lead">{e(r["lead"])}</p>
  <div class="bigstats">{stats}</div>
  <div class="cal">
    <div class="cal-h"><b>{e(r.get("cal_titulo", "Tus semanas hasta los exámenes"))}</b><div class="leg">{leg}</div></div>
    <div class="grid" style="grid-template-columns: repeat({len(r["semanas"])}, minmax(0, 1fr))">{meses}{cols}</div>
    <p class="cal-n">{e(r["nota"])}</p>
  </div>
  <div class="bloques" style="grid-template-columns: repeat({min(len(r["bloques"]), 4)}, 1fr)">{bloques}</div>
  {footer()}
</section>'''


MESES_ES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def page_calendario(d, t):
    """Calendario mensual real: clases, exámenes, festivos y hoy."""
    c = d["calendario"]
    hoy, hasta = dt.date.fromisoformat(c["hoy"]), dt.date.fromisoformat(c["hasta"])
    ses = {dt.date.fromisoformat(k): v for k, v in c["sesiones"].items()}
    exa = {dt.date.fromisoformat(k): v for k, v in c["examenes"].items()}
    fest = {dt.date.fromisoformat(k) for k in c["festivos"]}
    sem_ex = set()
    for a, b in c.get("semanas_examen", []):
        x = dt.date.fromisoformat(a)
        while x <= dt.date.fromisoformat(b):
            sem_ex.add(x)
            x += dt.timedelta(days=1)
    num = lambda x: (f"{x:g}").replace(".", ",")
    meses = ""
    for y, m in c["meses"]:
        cells = "".join(f"<span class='dh'>{x}</span>" for x in "LMXJVSD")
        horas_mes = 0
        for wk in calendar.Calendar(0).monthdatescalendar(y, m):
            for x in wk:
                if x.month != m:
                    cells += "<span class='dd o'></span>"
                    continue
                cls, sub = ["dd"], ""
                if x < hoy or x > hasta:
                    cls.append("off")
                if x in sem_ex:
                    cls.append("sx")
                if x in fest:
                    cls.append("fe")
                if x in ses:
                    horas_mes += ses[x]
                    cls.append("in" if ses[x] >= 2 else "se")
                    sub = f"<small>{num(ses[x])}h</small>"
                if x in exa:
                    cls.append("ex")
                    sub = f"<small>{e(exa[x])}</small>"
                if x == hoy:
                    cls.append("hoy")
                    sub = sub or "<small>HOY</small>"
                cells += f"<span class='{' '.join(cls)}'><b>{x.day}</b>{sub}</span>"
        info = c.get("mes_info", {}).get(f"{y}-{m:02d}", "")
        meses += (f'<div class="mc"><div class="mc-h"><b>{MESES_ES[m]}</b><span>{e(c.get("mes_top", {}).get(f"{y}-{m:02d}", f"{num(horas_mes)}h de clase"))}</span></div>'
                  f'<div class="mc-g">{cells}</div><div class="mc-i">{e(info)}</div></div>')
    leg = [("se", "Clase (1–1,5h)"), ("in", "Clase intensiva (2h)"), ("ex", "Examen"),
           ("sx", "Semana de parciales"), ("fe", "Festivo"), ("hoy", "Hoy")]
    legend = "".join(f"<div><span class='dd {k}'></span>{e(v)}</div>" for k, v in leg)
    resumen = "".join(f"<div class='rs-r'><b>{e(a)}</b><span>{e(b)}</span></div>" for a, b in c["resumen"])
    return f'''<section class="page glow calp">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">{e(c["etiqueta"])}</span></div><div class="rule"></div>
  <div class="pill gold">{e(c["pill"])}</div>
  <h2>{e(c["titulo"])}</h2>
  <p class="lead">{e(c["lead"])}</p>
  <div class="mgrid">{meses}<div class="mc side"><div class="mc-h"><b>Leyenda</b></div><div class="legend">{legend}</div>{resumen}</div></div>
  {footer()}
</section>'''


def page_camino(d, t):
    """Vista general limpia del curso: fases e hitos, sin horas."""
    c = d["camino"]
    meses = c["meses"]
    nm = len(meses)
    fases = "".join(f'<div class="cf f{i}" style="grid-column: span {f["span"]}"><small>{e(f["etiqueta"])}</small><b>{e(f["nombre"])}</b></div>'
                    for i, f in enumerate(c["fases"]))
    hitos = ""
    for h in c["hitos"]:
        pos = (h["pos"] - 0.5) / nm * 100
        hitos += (f'<div class="hito{" meta" if h.get("meta") else ""}" style="left:{pos:.2f}%">'
                  f'<i></i><span>{e(h["nombre"])}</span></div>')
    mlab = "".join(f"<span>{e(m)}</span>" for m in meses)
    cards = "".join(f'<div class="cc f{i}"><em>{i + 1:02d}</em><b>{e(f["nombre"])}</b><p>{e(f["foco"])}</p></div>'
                    for i, f in enumerate(c["fases"]))
    return f'''<section class="page glow camino">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">{e(c["etiqueta"])}</span></div><div class="rule"></div>
  <div class="pill gold">{e(c["pill"])}</div>
  <h2>{e(c["titulo"])}</h2>
  <p class="lead">{e(c["lead"])}</p>
  <div class="road">
    <div class="cfases" style="grid-template-columns: repeat({nm}, minmax(0,1fr))">{fases}</div>
    <div class="track"><div class="line"></div>{hitos}</div>
    <div class="mlab" style="grid-template-columns: repeat({nm}, minmax(0,1fr))">{mlab}</div>
  </div>
  <div class="ccards">{cards}</div>
  {footer()}
</section>'''


def page_ciclos(d, t):
    """Calendario grande de un mes con los ciclos de bono coloreados."""
    c = d["ciclos"]
    y, m = c["mes"]
    ciclos = [(dt.date.fromisoformat(x["desde"]), dt.date.fromisoformat(x["hasta"]), x) for x in c["ciclos"]]
    fest = {dt.date.fromisoformat(k): v for k, v in c.get("festivos", {}).items()}
    cells = "".join(f"<span class='bh'>{x}</span>" for x in ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"])
    for wk in calendar.Calendar(0).monthdatescalendar(y, m):
        for x in wk:
            cls, tag = ["bd"], ""
            for i, (a, b, info) in enumerate(ciclos):
                if a <= x <= b:
                    cls.append(f"k{i}")
                    if x == a:
                        tag = f"<em>{e(info['inicio'])}</em>"
            if x.month != m:
                cls.append("fuera")
            if x in fest:
                cls.append("fest")
                tag = f"<em>{e(fest[x])}</em>"
            cells += f"<div class='{' '.join(cls)}'><b>{x.day}</b>{tag}</div>"
    leyenda = "".join(f'<div class="kl k{i}"><i></i><div><b>{e(info["nombre"])}</b><span>{e(info["texto"])}</span></div></div>'
                      for i, (_, _, info) in enumerate(ciclos))
    return f'''<section class="page glow ciclos">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">{e(c["etiqueta"])}</span></div><div class="rule"></div>
  <div class="pill gold">{e(c["pill"])}</div>
  <h2>{e(c["titulo"])}</h2>
  <p class="lead">{e(c["lead"])}</p>
  <div class="bigcal"><div class="bc-h"><b>{MESES_ES[m]} {y}</b><span>{e(c["subtitulo"])}</span></div><div class="bc-g">{cells}</div></div>
  <div class="kleg">{leyenda}</div>
  {footer()}
</section>'''


def page_mes(d, t):
    """Mes de ejemplo a pantalla completa: cada clase en su día, coloreada por asignatura."""
    c = d["mes_ejemplo"]
    y, m = c["mes"]
    ses = {dt.date.fromisoformat(k): v for k, v in c["sesiones"].items()}
    fest = {dt.date.fromisoformat(k): v for k, v in c.get("festivos", {}).items()}
    etq = c["etiquetas"]
    num = lambda x: (f"{x:g}").replace(".", ",")
    cells = "".join(f"<span class='bh'>{x}</span>" for x in ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"])
    for wk in calendar.Calendar(0).monthdatescalendar(y, m):
        for x in wk:
            cls, tag = ["bd"], ""
            if x.month != m:
                cls.append("fuera")
            if x in fest:
                cls.append("fest")
                tag = f"<em>{e(fest[x])}</em>"
            if x in ses and x.month == m:
                i, h = ses[x]
                cls.append(f"s{i}")
                tag = f"<em>{e(etq[i])}<br><span class='hh2'>{num(h)} h</span></em>"
            cells += f"<div class='{' '.join(cls)}'><b>{x.day}</b>{tag}</div>"
    tot = {}
    for i, h in ses.values():
        tot[i] = tot.get(i, 0) + h
    leg = "".join(f'<div class="ml"><i class="s{i}"></i><b>{e(a)}</b><span>{num(tot.get(i, 0))}h</span></div>' for i, a in enumerate(etq))
    total = sum(tot.values())
    return f'''<section class="page glow ciclos">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">{e(c["etiqueta"])}</span></div><div class="rule"></div>
  <div class="pill gold">{e(c["pill"])}</div>
  <h2>{e(c["titulo"])}</h2>
  <p class="lead">{e(c["lead"])}</p>
  <div class="bigcal"><div class="bc-h"><b>{MESES_ES[m]} {y}</b><span>{num(total)}h de clase · {len(ses)} sesiones</span></div><div class="bc-g">{cells}</div></div>
  <div class="mleg">{leg}</div>
  {footer()}
</section>'''


def page_trayectoria(d, t):
    """Curva de 'preparación' creciente de octubre a la PAU, estilo gráfica de física."""
    c = d["trayectoria"]
    meses = c["meses"]
    n = len(meses)
    W, H, x0, x1, yb, yt = 832, 262, 34, 800, 232, 34
    X = lambda i: x0 + (x1 - x0) * i / (n - 1)
    Y = lambda i: yb - (yb - yt) * (i / (n - 1)) ** 1.45
    cols = c["colores"]
    # tramos de la curva coloreados por bloque
    segs, fill = "", []
    for k, (a, b) in enumerate(c["tramos"]):
        pts = [(X(a + (b - a) * j / 40), Y(a + (b - a) * j / 40)) for j in range(41)]
        segs += f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{cols[k]}" stroke-width="6" stroke-linecap="round"/>'
    pts = [(X((n - 1) * j / 120), Y((n - 1) * j / 120)) for j in range(121)]
    area = f"M{x0},{yb} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in pts) + f" L{x1},{yb} Z"
    grid = "".join(f'<line x1="{X(i):.1f}" y1="{yt - 10}" x2="{X(i):.1f}" y2="{yb}" stroke="#172243" stroke-width="1"/>' for i in range(n))
    grid += "".join(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#172243" stroke-width="1"/>' for y in range(yt, yb + 1, 50))
    hitos = ""
    for h in c["hitos"]:
        x, y = X(h["pos"]), Y(h["pos"])
        if h.get("meta"):
            hitos += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="22" fill="#3d3826"/><circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="url(#oro)"/>'
                      f'<text x="{x - 30:.1f}" y="{y + 5:.1f}" text-anchor="end" class="tm">{e(h["nombre"])}</text>')
        else:
            hitos += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="#0a1226" stroke="#e7e7ea" stroke-width="3"/>'
                      f'<text x="{x:.1f}" y="{y - 18:.1f}" text-anchor="middle" class="th2">{e(h["nombre"])}</text>')
    svg = f'''<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" class="tsvg">
  <defs><linearGradient id="oro" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6e2a6"/><stop offset="1" stop-color="#c9a24b"/></linearGradient>
  <linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#15294f"/><stop offset="1" stop-color="#0c1428"/></linearGradient></defs>
  {grid}<path d="{area}" fill="url(#area)"/>{segs}{hitos}
  <text x="{x0}" y="{yt - 16}" class="ax">PREPARACIÓN</text>
  <text x="{x1}" y="{yb + 22}" text-anchor="end" class="ax">TIEMPO →</text>
</svg>'''
    bandas = "".join(f'<div class="tb" style="grid-column: span {b["span"]}; background:{b["fondo"]}; border-color:{b["borde"]}">'
                     f'<em style="color:{b["borde"]}">{e(b["simbolo"])}</em><b>{e(b["nombre"])}</b></div>' for b in c["bloques"])
    mlab = "".join(f"<span>{e(m)}</span>" for m in meses)
    cards = "".join(f'<div class="tcd"><em style="color:{b["borde"]}">{e(b["simbolo"])}</em><b>{e(b["nombre"])}</b><p>{e(b["foco"])}</p></div>'
                    for b in c["bloques"] if b.get("foco"))
    return f'''<section class="page glow tray">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">{e(c["etiqueta"])}</span></div><div class="rule"></div>
  <div class="pill gold">{e(c["pill"])}</div>
  <h2>{e(c["titulo"])}</h2>
  <p class="lead">{e(c["lead"])}</p>
  <div class="tbox">{svg}
    <div class="tbands" style="grid-template-columns: repeat({n}, minmax(0,1fr))">{bandas}</div>
    <div class="mlab" style="grid-template-columns: repeat({n}, minmax(0,1fr))">{mlab}</div>
  </div>
  <div class="tcards">{cards}</div>
  {footer()}
</section>'''


def page_semana(d, t):
    """Horario semanal tipo (mañanas) con bloques por asignatura."""
    c = d["semana"]
    h0, h1 = c["hora_ini"], c["hora_fin"]
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    asig = c["asignaturas"]
    alto = c.get("alto", 58)  # px por hora
    hh = lambda x: f"{int(x)}:{int(round((x - int(x)) * 60)):02d}"
    horas = "".join(f'<div class="sh" style="top:{(h - h0) * alto}px">{h}:00</div>' for h in range(h0, h1 + 1))
    cols = ""
    for di, dia in enumerate(dias):
        bl = ""
        for (dd, ini, fin, a) in c["bloques"]:
            if dd != di:
                continue
            bl += (f'<div class="sb a{a}{" mini" if fin - ini < 1 else ""}" style="top:{(ini - h0) * alto + 3}px; height:{(fin - ini) * alto - 6}px">'
                   f'<b>{e(asig[a])}</b><span>{hh(ini)} – {hh(fin)}</span></div>')
        cols += f'<div class="sd"><div class="sdh">{dia}</div><div class="sdb" style="height:{(h1 - h0) * alto}px; background: repeating-linear-gradient(180deg, #0e1629 0 {alto - 1}px, #172243 {alto - 1}px {alto}px)">{bl}</div></div>'
    tot = {}
    for (_, ini, fin, a) in c["bloques"]:
        tot[a] = tot.get(a, 0) + (fin - ini)
    num = lambda x: (f"{x:g}").replace(".", ",")
    filas = ""
    for bono in c["repartos"]:
        cortas = c.get("asig_cortas", asig)
        celdas = "".join(f'<div class="rpc a{i}" style="flex:{h}"><b>{e(cortas[i])}</b><span>{num(h)}h</span></div>' for i, h in enumerate(bono["horas"]) if h)
        filas += f'<div class="rpf"><em>{e(bono["nombre"])}</em><div class="rpb">{celdas}</div></div>'
    return f'''<section class="page glow semp">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">{e(c["etiqueta"])}</span></div><div class="rule"></div>
  <div class="pill gold">{e(c["pill"])}</div>
  <h2>{e(c["titulo"])}</h2>
  <p class="lead">{e(c["lead"])}</p>
  <div class="sgrid"><div class="shs" style="height:{(h1 - h0) * alto}px">{horas}</div>{cols}</div>
  <div class="extra-t"><i></i><div><b>{e(c["extra_titulo"])}</b><span>{e(c["extra_texto"])}</span></div></div>
  <div class="rps">{filas}</div>
  {footer()}
</section>'''


def periodo(c):
    # Textos del periodo del bono (por defecto, semanal)
    return {"corto": "/semana", "largo": "a la semana", "cada": "cada semana", "cap": "Cada semana",
            "renov": "renovación semanal", "n4": 4, "ahorro4": "de ahorro cada 4 semanas", **c.get("periodo", {})}


def page_bonos_esp(d, t):
    c = d["bonos_especiales"]
    base = c["base"]
    P = periodo(c)
    cards = ""
    for b in c["bonos"]:
        ph = b["precio"] / b["horas"]
        top = f'<div class="bx-top">{e(b["etiqueta"])}</div>' if b.get("etiqueta") else ""
        cards += f'''<div class="bx{" star" if b.get("destacado") else ""}">{top}
  <div class="bx-h"><b>{b["horas"]}h</b><span>{P["largo"]}</span></div>
  <div class="bx-p">{eur(b["precio"], 0)}<small>{P["corto"]}</small></div>
  <div class="bx-hora"><b>{eur(ph)}</b><span>por hora</span><em>−{pct(base - ph, base)}%</em></div>
  {f'<div class="bx-hora ex"><b>{eur(b["extra"], 0)}</b><span>cada hora extra</span><em>−{pct(base - b["extra"], base)}%</em></div>' if b.get("extra") else ""}
  {"".join(f'<div class="bx-ref"><span>{e(lab)}</span><s>{eur(v, 0)}</s></div>' for lab, v in b.get("referencias", []))}
  <div class="bx-ah">Ahorráis <b>{eur(b["horas"] * base - b["precio"], 0)}</b> {P["cada"]} frente a la tarifa base</div>
</div>'''
    ej = "".join(f"<li>{x}</li>" for x in c["ejemplos"])
    n = d["nombre"]
    return f'''<section class="page">
  <div class="hdr"><span class="hdr-l">PLAN PERSONALIZADO · {e(n.upper())}</span></div><div class="rule"></div>
  <div class="who"><div class="av">{e(n[0])}</div><div><div class="wn">{e(n)}</div><div class="ws">{e(c["who"].upper())}</div></div></div>
  <div class="pill gold">{e(c["pill"])}</div>
  <h2>{e(c["titulo"])}</h2>
  <p class="lead">{e(c["lead"])}</p>
  <div class="bxs">{cards}</div>
  <div class="base-l">{e(c.get("base_txt", "Tarifa base online de Bachillerato"))}: <b>{eur(base)}/h</b></div>
  <ul class="dash ej">{ej}</ul>
  {footer()}
</section>'''


def page_ahorro_esp(d, t):
    c = d["bonos_especiales"]
    P = periodo(c)
    base = c["base"]
    mx = max(b["horas"] for b in c["bonos"]) * base
    filas = ""
    for b in c["bonos"]:
        ref = b["horas"] * base
        filas += f'''<div class="esc{" top" if b.get("destacado") else ""}">
  <div class="eh"><b>{b["horas"]}h</b><span>{P["largo"]}</span></div>
  <div class="eb">
    <div class="ebr"><span>Tarifa base</span><div><i class="base" style="width:{ref / mx * 100:.1f}%"></i></div><em>{eur(ref, 0)}</em></div>
    <div class="ebr"><span>Con el bono</span><div><i class="bono" style="width:{b["precio"] / mx * 100:.1f}%"></i></div><em>{eur(b["precio"], 0)}</em></div>
  </div>
  <div class="ea"><b>{eur((ref - b["precio"]) * P["n4"], 0)}</b><span>{P["ahorro4"]}</span>{"" if P["n4"] == 1 else f'<small>{eur(ref - b["precio"], 0)} {P["cada"]}</small>'}</div>
</div>'''
    cmp_rows = ""
    for h, a, b2 in c.get("comparativa", []):
        mejor = "b" if b2 < a else "a"
        cmp_rows += (f'<div class="cr"><span>{h}h</span><em class="{"w" if mejor == "a" else ""}">{eur(a, 0)}</em>'
                     f'<em class="{"w" if mejor == "b" else ""}">{eur(b2, 0)}</em></div>')
    cmpbox = ""
    if cmp_rows:
        cmpbox = ('<div class="cmpbox"><div class="cmp-h"><b>¿Qué bono os conviene?</b><span>Coste semanal según las horas que haga</span></div>'
                  f'<div class="cr hd"><span>Horas</span><em>Bono 15h</em><em>Bono 20h</em></div>{cmp_rows}'
                  f'<p>{e(c["comparativa_nota"])}</p></div>')
    nota = f'<p class="nota-bono">{e(c["ahorro_nota"])}</p>' if c.get("ahorro_nota") else ""
    return f'''<section class="page glow">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">LO QUE AHORRÁIS</span></div><div class="rule"></div>
  <div class="pill gold">EL DESCUENTO, EN NÚMEROS</div>
  <h2>{e(c["ahorro_titulo"])}</h2>
  <p class="lead">{e(c["ahorro_lead"])}</p>
  <div class="escs">{filas}</div>
  {cmpbox}
  {nota}
  {footer()}
</section>'''


def page_resumen_esp2(d, t):
    c = d["bonos_especiales"]
    P = periodo(c)
    n = d["nombre"]
    rows = ""
    for b in c["bonos"]:
        rows += f'''<div class="srow{" ref" if not b.get("destacado") else ""}"><div class="av w">{b["horas"]}</div>
  <div class="st"><b>Bono de {b["horas"]}h {P["cada"] if P["cada"] != "cada semana" else "semanales"}</b><small>{e(c.get("modalidad_txt", "Online"))} · {P["renov"]}{f" · hora extra a {eur(b['extra'], 0)}" if b.get("extra") else ""}</small></div>
  <div class="sps"><div class="sp"><small>{P["cap"]}</small><b>{eur(b["precio"], 0)}</b></div><div class="sp"><small>Por hora</small><b>{eur(b["precio"] / b["horas"])}</b></div></div></div>'''
    lis = "".join(f"<li>{e(x)}</li>" for x in c["resumen"])
    return f'''<section class="page">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">RESUMEN DEL PLAN</span></div><div class="rule"></div>
  <div class="pill gold">RESUMEN</div>
  <h2>Su plan, de un vistazo</h2>
  <p class="lead">Los dos bonos de {e(n)}, de un vistazo.</p>
  <div class="srows">{rows}</div>
  <ul class="dash">{lis}</ul>
  <div class="quote"><span>"</span><em>{e(c["quote"])}</em></div>
  {footer()}
</section>'''


def page_pasos(d, t):
    """Recomendación en dos pasos: bono de prueba y después bono mensual a elegir."""
    c = d["pasos"]
    base = c["base"]
    n = d["nombre"]
    p1 = c["prueba"]
    ph1 = p1["precio"] / p1["horas"]
    cards = ""
    for b in c["opciones"]:
        ph = b["precio"] / b["horas"]
        top = f'<div class="bx-top">{e(b["etiqueta"])}</div>' if b.get("etiqueta") else ""
        cards += f'''<div class="bx{" star" if b.get("destacado") else ""}">{top}
  <div class="bx-h"><b>{b["horas"]}h</b><span>al mes · {e(b["frecuencia"])}</span></div>
  <div class="bx-p">{eur(b["precio"], 0)}<small>/mes</small></div>
  <div class="bx-hora"><b>{eur(ph)}</b><span>por hora</span><em>−{pct(base - ph, base)}%</em></div>
  <div class="bx-ref"><span>Tarifa base ({b["horas"]} × {eur(base, 0 if base == int(base) else 2)})</span><s>{eur(b["horas"] * base, 0)}</s></div>
  <div class="bx-ah">Ahorráis <b>{eur(b["horas"] * base - b["precio"], 0)}</b> al mes frente a la tarifa base</div>
</div>'''
    return f'''<section class="page pasosp">
  <div class="hdr"><span class="hdr-l">PLAN PERSONALIZADO · {e(n.upper())}</span></div><div class="rule"></div>
  <div class="who"><div class="av">{e(n[0])}</div><div><div class="wn">{e(n)}</div><div class="ws">{e(c["who"].upper())}</div></div></div>
  <h2>{e(c["titulo"])}</h2>
  <p class="lead">{e(c["lead"])}</p>
  <div class="paso1">
    <div class="pnum">1</div>
    <div class="p1t"><small>PASO 1 · PARA EMPEZAR</small><b>Bono de prueba de {p1["horas"]}h</b><span>{e(p1["texto"])}</span></div>
    <div class="p1p"><s>{eur(p1["tachado"], 0)}</s><b>{eur(p1["precio"], 0)}</b><span>{eur(ph1)}/h · precio nuevos alumnos</span></div>
  </div>
  <div class="paso2h"><div class="pnum s">2</div><div><small>PASO 2 · DESPUÉS</small><b>{e(c["paso2_titulo"])}</b></div></div>
  <div class="bxs"{' style="grid-template-columns: 1fr; max-width: 520px"' if len(c["opciones"]) == 1 else ""}>{cards}</div>
  <div class="base-l">{e(c["base_txt"])}: <b>{eur(base)}/h</b>{f" · {e(c['nota'])}" if c.get("nota") else ""}</div>
  {footer()}
</section>'''


def page_resumen_pasos(d, t):
    c = d["pasos"]
    n = d["nombre"]
    p1 = c["prueba"]
    rows = (f'''<div class="srow"><div class="av w">1</div><div class="st"><b>Paso 1 — Bono de prueba de {p1["horas"]}h</b><small>{e(c["modalidad_txt"])} · para empezar</small></div>
  <div class="sps"><div class="sp"><small>Una vez</small><b>{eur(p1["precio"], 0)}</b></div></div></div>''')
    for b in c["opciones"]:
        rows += f'''<div class="srow ref"><div class="av w">2</div><div class="st"><b>Paso 2 — Bono de {b["horas"]}h al mes</b><small>{e(c["modalidad_txt"])} · {e(b["frecuencia"])}</small></div>
  <div class="sps"><div class="sp"><small>Al mes</small><b>{eur(b["precio"], 0)}</b></div><div class="sp"><small>Por hora</small><b>{eur(b["precio"] / b["horas"])}</b></div></div></div>'''
    lis = "".join(f"<li>{e(x)}</li>" for x in c["resumen"])
    return f'''<section class="page">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">RESUMEN DEL PLAN</span></div><div class="rule"></div>
  <div class="pill gold">RESUMEN</div>
  <h2>Su plan, de un vistazo</h2>
  <p class="lead">El plan de {e(n)}, paso a paso.</p>
  <div class="srows">{rows}</div>
  <ul class="dash">{lis}</ul>
  <div class="quote"><span>"</span><em>{e(c["quote"])}</em></div>
  {footer()}
</section>'''


def page_opciones(d, t):
    """Dos formas de pagar comparadas (suscripción semanal vs bono)."""
    c = d["opciones_comp"]
    cards = ""
    for o in c["opciones"]:
        como = "".join(f"<li>{e(x)}</li>" for x in o["como"])
        cards += f'''<div class="oc{" b" if o["letra"] == "B" else ""}">
  <div class="oc-t"><span>{e(o["letra"])}</span><div><b>{e(o["nombre"])}</b><small>{e(o["detalle"])}</small></div></div>
  <div class="oc-h">{eur(o["hora"])}<small>/hora</small></div>
  <div class="oc-p"><b>{e(o["paga"])}</b> {e(o["paga_txt"])}</div>
  <div class="oc-s">Cómo funcionan las horas</div><ul class="oc-l">{como}</ul>
  <div class="oc-s">Encaja mejor si…</div><p class="oc-e">{e(o["encaja"])}</p>
</div>'''
    return f'''<section class="page glow ocp">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">{e(c["etiqueta"])}</span></div><div class="rule"></div>
  <div class="pill gold">{e(c["pill"])}</div>
  <h2>{e(c["titulo"])}</h2>
  <p class="lead">{e(c["lead"])}</p>
  <div class="ocs">{cards}</div>
  <div class="oc-inc"><i>✓</i><span>{e(c["incluye"])}</span></div>
  <div class="oc-mas"><b>{e(c["mas_horas_t"])}</b><span>{e(c["mas_horas"])}</span></div>
  {footer()}
</section>'''


def page_recomendacion(d, t):
    c = d["opciones_comp"]["recomendacion"]
    razones = "".join(f'<div class="rz"><b>{e(a)}</b><strong>{e(b)}</strong><span>{e(x)}</span></div>' for a, b, x in c["razones"])
    a, b2 = c["hora_a"], c["hora_b"]
    pasos = "".join(f'<div class="rp2"><em>{i + 1}</em><span>{e(x)}</span></div>' for i, x in enumerate(c["pasos"]))
    return f'''<section class="page">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">NUESTRA RECOMENDACIÓN</span></div><div class="rule"></div>
  <div class="pill gold">{e(c["pill"])}</div>
  <h2>{e(c["titulo"])}</h2>
  <p class="lead">{e(c["lead"])}</p>
  <div class="rzs">{razones}</div>
  <div class="cmpx">
    <div class="cx"><span>Suscripción semanal</span><div><i class="bono" style="width:{a / b2 * 100:.1f}%"></i></div><em>{eur(a)}/h</em></div>
    <div class="cx"><span>Bono de 12h</span><div><i class="base" style="width:100%"></i></div><em>{eur(b2)}/h</em></div>
    <p>{e(c["ahorro_txt"])}</p>
  </div>
  <div class="oc-mas alt"><b>{e(c["cuando_bono_t"])}</b><span>{e(c["cuando_bono"])}</span></div>
  <div class="rps2">{pasos}</div>
  {footer()}
</section>'''


def page_dos_tarifas(d, t):
    """Fase 1: tarifa estándar vs premium, en frases cortas y con precio 'desde'."""
    c = d["dos_tarifas"]
    cols = ""
    for k, o in (("std", c["estandar"]), ("pre", c["premium"])):
        li = "".join(f'<li class="{"si" if ok else "no"}">{e(x)}</li>' for ok, x in o["puntos"])
        cols += f'''<div class="dt {k}">
  <div class="dt-n">{e(o["nombre"])}</div><div class="dt-s">{e(o["sub"])}</div>
  <div class="dt-d">desde</div>
  <div class="dt-h">{eur(o["desde"])}<small>/hora</small></div>
  <ul class="dt-l">{li}</ul>
  <div class="dt-q">{e(o["para"])}</div>
</div>'''
    return f'''<section class="page glow dtp">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">{e(c["etiqueta"])}</span></div><div class="rule"></div>
  <div class="pill gold">{e(c["pill"])}</div>
  <h2>{e(c["titulo"])}</h2>
  <div class="dts">{cols}</div>
  <div class="dt-next"><i>→</i><span>{e(c["siguiente"])}</span></div>
  {footer()}
</section>'''


def page_precios(d, t):
    """Opciones de pago en limpio: precio por hora y lo que se paga a la semana."""
    c = d["precios_comp"]
    cards = ""
    for o in c["opciones"]:
        top = f'<div class="pr-top">{e(o["etiqueta"])}</div>' if o.get("etiqueta") else ""
        cards += f'''<div class="pr{" rec" if o.get("etiqueta") else ""}">{top}
  <div class="pr-n">{e(o["nombre"])}</div>
  <div class="pr-h">{eur(o["hora"])}<small>/hora</small></div>
  <div class="pr-s"><b>{eur(o["semana"], 0 if o["semana"] == int(o["semana"]) else 2)}</b><span>a la semana</span></div>
  <div class="pr-p">{e(o["pago"])}</div>
</div>'''
    return f'''<section class="page glow prp">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">{e(c["etiqueta"])}</span></div><div class="rule"></div>
  <div class="pill gold">{e(c["pill"])}</div>
  <h2>{e(c["titulo"])}</h2>
  <p class="lead">{e(c["lead"])}</p>
  <div class="prs">{cards}</div>
  <p class="pr-foot">{e(c["pie"])}</p>
  {footer()}
</section>'''


def page_quincenal(d, t):
    b = d["bono_especial"]
    base = TARIFAS[d["etapa"]]["base"]["casa_alumno"]
    ph = b["precio"] / b["horas"]
    bars = [("Tarifa base presencial", base, "base"), (f"Bono de {b['horas']}h", ph, "bono"), ("Hora extra", b["extra"], "extra")]
    filas = ""
    for lab, v, k in bars:
        dto = "" if k == "base" else f'<span class="dto">−{pct(base - v, base)}%</span>'
        filas += (f'<div class="cmp"><span class="cl">{e(lab)}</span><div class="ct"><i class="{k}" style="width:{v / base * 100:.1f}%"></i></div>'
                  f'<span class="cv">{eur(v)}/h</span>{dto}</div>')
    ej_h = b["ejemplo_horas"]
    ej_total = b["precio"] + (ej_h - b["horas"]) * b["extra"]
    n = d["nombre"]
    return f'''<section class="page">
  <div class="hdr"><span class="hdr-l">PLAN PERSONALIZADO · {e(n.upper())}</span></div><div class="rule"></div>
  <div class="who"><div class="av">{e(n[0])}</div><div><div class="wn">{e(n)}</div><div class="ws">{e(b["who"].upper())}</div></div></div>
  <div class="pill gold">{e(b["pill"])}</div>
  <h2>{e(b["titulo"])}</h2>
  <p class="lead">{e(b["lead"])}</p>
  <div class="rwrap q"><div class="rbadge">{e(b["badge"])}</div>
    <div class="qhero">
      <div><b>{eur(b["precio"], 0)}</b><span>cada 2 semanas · {b["horas"]}h de clase</span></div>
      <div><b>{eur(ph)}<small>/h</small></b><span>precio por hora del bono</span></div>
      <div><b>{eur(b["extra"], 0)}</b><span>cada hora extra</span></div>
    </div>
    <div class="cmps">{filas}</div>
    <div class="ejemplo"><b>Ejemplo:</b> si en dos semanas hace {ej_h}h → {eur(b["precio"], 0)} + {ej_h - b["horas"]} × {eur(b["extra"], 0)} = <b>{eur(ej_total, 0)}</b></div>
  </div>
  {footer()}
</section>'''


def page_ahorro(d, t):
    b = d["bono_especial"]
    base = TARIFAS[d["etapa"]]["base"]["casa_alumno"]
    filas, mx = "", 0
    esc = []
    for hs in b["escenarios"]:
        h2 = hs * 2
        coste = b["precio"] + max(0, h2 - b["horas"]) * b["extra"]
        ref = h2 * base
        esc.append((hs, h2, coste, ref))
        mx = max(mx, ref)
    for hs, h2, coste, ref in esc:
        ah = ref - coste
        filas += f'''<div class="esc{" top" if hs == b["escenarios"][-1] else ""}">
  <div class="eh"><b>{hs}h</b><span>a la semana</span></div>
  <div class="eb">
    <div class="ebr"><span>Tarifa base</span><div><i class="base" style="width:{ref / mx * 100:.1f}%"></i></div><em>{eur(ref, 0)}</em></div>
    <div class="ebr"><span>Con su bono</span><div><i class="bono" style="width:{coste / mx * 100:.1f}%"></i></div><em>{eur(coste, 0)}</em></div>
  </div>
  <div class="ea"><b>{eur(ah * 2, 0)}</b><span>de ahorro cada 4 semanas</span><small>{eur(ah, 0)} por bono de 2 semanas</small></div>
</div>'''
    return f'''<section class="page glow">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">LO QUE AHORRÁIS</span></div><div class="rule"></div>
  <div class="pill gold">EL DESCUENTO, EN NÚMEROS</div>
  <h2>{e(b["ahorro_titulo"])}</h2>
  <p class="lead">{e(b["ahorro_lead"])}</p>
  <div class="escs">{filas}</div>
  <p class="nota-bono">{e(b["ahorro_nota"])}</p>
  {footer()}
</section>'''


def page_resumen_esp(d, t):
    b = d["bono_especial"]
    n = d["nombre"]
    lis = "".join(f"<li>{e(x)}</li>" for x in b["resumen"])
    return f'''<section class="page">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">RESUMEN DEL PLAN</span></div><div class="rule"></div>
  <div class="pill gold">RESUMEN</div>
  <h2>Su plan, de un vistazo</h2>
  <p class="lead">El bono de {e(n)}, de un vistazo.</p>
  <div class="srows">
    <div class="srow"><div class="av w">{e(n[0])}</div><div class="st"><b>{e(n)} — Bono de {b["horas"]}h</b><small>Cada 2 semanas · {e(b["who"])}</small></div>
      <div class="sps"><div class="sp"><small>Cada 2 semanas</small><b>{eur(b["precio"], 0)}</b></div><div class="sp"><small>Por hora</small><b>{eur(b["precio"] / b["horas"])}</b></div></div></div>
    <div class="srow ref"><div class="av w">+</div><div class="st"><b>Hora extra</b><small>Si una quincena hacen falta más de {b["horas"]}h</small></div>
      <div class="sps"><div class="sp"><small>Cada hora</small><b>{eur(b["extra"], 0)}</b></div></div></div>
  </div>
  <ul class="dash">{lis}</ul>
  <div class="quote"><span>"</span><em>{e(b["quote"])}</em></div>
  {footer()}
</section>'''


def page_proceso(d, t):
    return f'''<section class="page">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">CÓMO TRABAJAMOS</span></div><div class="rule"></div>
  <div class="pill gold">EL PROCESO</div>
  <h2>{e(t["p2_title"])}</h2>
  <p class="lead">{e(t["p2_sub"])}</p>
  <div class="steps">
    <div><span class="num">01</span><h4>Sesión con el profesor</h4><p>{e(t["c1"])}</p></div>
    <div><span class="num">02</span><h4>{e(t["c2t"])}</h4><p>{e(t["c2"])}</p></div>
    <div><span class="num">03</span><h4>Ajuste continuo</h4><p>{e(t["c3"])}</p></div>
  </div>
  <div class="stats">
    <div><b>1</b><span>PROFESOR DE REFERENCIA</span></div>
    <div><b>0</b><span>{e(t["gestiones"])}</span></div>
    <div><b>1</b><span>INTERLOCUTOR: NOSOTROS</span></div>
    <div><b>100%</b><span>SUSTITUCIÓN GARANTIZADA</span></div>
  </div>
  {footer()}
</section>'''


def page_informe(d, t):
    r = d["informe_ejemplo"]
    bars = "".join(
        f'<div class="bar"><span class="bl">{e(k)}</span><span class="bt"><i style="width:{v*10:.0f}%"></i></span>'
        f'<span class="bv">{str(v).replace(".", ",")}</span></div>' for k, v in r["barras"])
    items = ["Horas dedicadas y sesiones realizadas", "Evolución por asignatura, semana a semana",
             "Puntos fuertes y áreas de mejora detectadas", "Plan de trabajo propuesto para el mes siguiente",
             "Qué puede reforzarse en casa", "Acceso al área privada del alumno"]
    checks = "".join(f"<li>{e(i)}</li>" for i in items)
    return f'''<section class="page">
  <div class="hdr"><span class="hdr-l">LOS INFORMES</span></div><div class="rule"></div>
  <div class="pill gold">SEGUIMIENTO INCLUIDO</div>
  <h2>{e("Un informe real para " + d["nombre"] if d["nombre"] else "Un informe real, cada mes")}</h2>
  <p class="lead">{e(t["p3_sub"])}</p>
  <ul class="checks">{checks}</ul>
  <div class="panel">
    <div class="panel-h"><b>Informe de seguimiento mensual</b><span>EJEMPLO</span></div>
    <div class="kpis">
      <div><b>{e(r["horas"])}</b><span>SESIONES DEL MES</span></div>
      <div><b>100%</b><span>ASISTENCIA</span></div>
      <div><b>{len(r["barras"])}</b><span>{e(r["destrezas_label"].upper())}</span></div>
      <div><b>A+</b><span>PROGRESO DEL MES</span></div>
    </div>
    {bars}
  </div>
  {footer()}
</section>'''


def phones(d):
    r, n = d["informe_ejemplo"], d["nombre"] or d["curso"]
    asig = r.get("asignatura") or lista_asig(d["asignaturas"])
    # 1. Portada
    p1 = f'''<div class="scr">
  <div class="s-eyebrow">INFORME DE SEGUIMIENTO MENSUAL</div>
  <div class="s-name">{e(n)}</div><div class="s-sub">{e(asig)} · {e(r["mes"])}</div>
  <div class="s-kpis"><div><b>{e(r["nota"])}</b>NOTA EST.</div><div><b>{r["sesiones"]}</b>SESIONES</div><div><b>{e(r["horas"])}</b>DEDICADAS</div><div><b>{r["sesiones"]}/{r["sesiones"]}</b>ASISTENCIA</div></div>
  <div class="s-hl"><small>MAYOR PROGRESO DEL MES</small>{e(r["mayor_progreso"])}</div>
  <div class="s-h">Resumen del mes</div><p class="s-p">{e(r["resumen"])}</p>
  <div class="s-note"><b>{e(r["proxima_sesion"])}</b>{e(r["proxima_sesion_txt"])}</div>
</div>'''
    tmax = max(v for _, v in r["temas"])
    temas = "".join(f'<div class="s-t"><span>{e(k)}</span><span>{str(v).replace(".", ",")}h</span></div>'
                    f'<div class="s-tb"><i style="width:{v/tmax*85:.0f}%"></i></div>' for k, v in r["temas"])
    li = lambda xs: "".join(f"<div class='s-li'>— {e(x)}</div>" for x in xs)
    p2 = f'''<div class="scr">
  <div class="s-band"><b>{e(asig.upper())}</b><small>{e(r["horario"])}</small></div>
  {temas}
  <div class="s-sec g">PUNTOS FUERTES</div>{li(r["fuertes"])}
  <div class="s-sec a">A TENER EN CUENTA</div>{li(r["atencion"])}
  <div class="s-note"><b>PRÁCTICA EN CASA</b>{"".join(f"<div>· {e(x)}</div>" for x in r["casa"])}</div>
</div>'''
    smax = max(r["semanas"])
    cols = "".join(f'<div class="s-col"><b>{str(v).replace(".", ",")}</b><i style="height:{v/smax*38:.0f}px"></i><small>Sem {i+1}</small></div>'
                   for i, v in enumerate(r["semanas"]))
    mets = "".join(f"<div><b>{e(a)}</b>{e(b.upper())}</div>" for a, b in r["metricas"])
    evol = "".join(f'<div class="s-ev"><b>{e(a)}</b><div>{e(b)} <span>▲ {e(c)}</span></div><div>{e(x)}</div></div>'
                   for a, b, c, x in r["evol"])
    p3 = f'''<div class="scr">
  <div class="s-name l">Comparado con {e(r.get("comparado", "octubre"))}</div><div class="s-sub b">{e(n)} · {e(asig)} — Evolución nota estimada, 4 semanas</div>
  <div class="s-cols">{cols}</div>
  <div class="s-kpis m">{mets}</div>
  {evol}
  <div class="s-note"><b>CONCLUSIÓN</b>{e(r["conclusion"])}</div>
</div>'''
    y, m = r["cal_mes"]
    cal = calendar.Calendar(firstweekday=0).monthdayscalendar(y, m)
    cells = "".join(f"<span class='h'>{x}</span>" for x in "LMXJVSD")
    for wk in cal:
        for i, dd in enumerate(wk):
            cls = "" if dd else "o"
            if dd and dd == r["cal_examen"]:
                cls = "x"
            elif dd and i in r["cal_dias_sesion"]:
                cls = "s"
            cells += f"<span class='{cls}'>{dd or ''}</span>"
    p4 = f'''<div class="scr">
  <div class="s-name l">Planificación trimestral</div><div class="s-sub b">{e(n)} · {e(asig)}</div>
  <div class="s-cd"><b>{e(r["cal_semanas"])}</b><small>{e(r["cal_semanas_txt"])}</small></div>
  <div class="s-h sm">{e(r["cal_titulo"])}</div>
  <div class="s-cal">{cells}</div>
  <div class="s-leg"><span class="d1">●</span> Sesión de clase &nbsp; <span class="d2">●</span> Examen</div>
  <div class="s-aa"><div><small>Antes</small>{e(r["antes"])}</div><div><small class="b">Ahora</small>{e(r["ahora"])}</div></div>
</div>'''
    caps = [("Portada del informe", "Nota estimada, sesiones, horas dedicadas y el mayor progreso detectado."),
            ("Detalle por asignatura", "Temas trabajados con horas dedicadas, puntos fuertes y a mejorar."),
            ("Comparativa mensual", "Evolución de la nota estimada respecto al mes anterior, semana a semana."),
            ("Planificación trimestral", "Cuenta atrás y calendario de preparación antes del examen.")]
    return "".join(f'<div class="ph-wrap"><div class="phone"><div class="notch"></div>{s}</div>'
                   f'<h5>{e(a)}</h5><p>{e(b)}</p></div>' for s, (a, b) in zip([p1, p2, p3, p4], caps))


def phones_real(d):
    """Pantallas de móvil con el formato real de los informes mensuales de NEXO."""
    r = dict(d["informe_ejemplo"])
    r.setdefault("asignatura", lista_asig(d["asignaturas"]) or r["barras"][0][0])
    n = d.get("nombre_completo") or d["nombre"] or d["curso"]
    prof = d.get("profesor_completo") or d.get("profesor") or "Profesor de referencia"
    subs = [b[0] for b in r["barras"]]
    mes = r["mes"]
    mi = next((i for i, m in enumerate(MESES_ES) if m and mes.lower().startswith(m.lower())), 11)
    sig = MESES_ES[mi % 12 + 1].lower()
    abbr = MESES_ES[mi][:3].lower()
    niveles = ["No entendido", "Con dificultad", "Bien", "Con soltura"]
    patrones = [[1, 2, 2, 3], [2, 1, 2, 2]]
    cols = ["#8fb8ec", "#7fcfa0"]

    def chart(i):
        pts = patrones[i % 2]
        W, H, x0, x1, yt, yb = 150, 70, 30, 144, 6, 58
        X = lambda k: x0 + (x1 - x0) * k / 3
        Y = lambda v: yb - (yb - yt) * v / 3
        grid = "".join(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="#1d2744" stroke-width="0.6"/>'
                       f'<text x="{x0 - 2}" y="{Y(v) + 1.5:.1f}" text-anchor="end" class="rk">{niveles[v]}</text>' for v in range(4))
        poly = " ".join(f"{X(k):.1f},{Y(v):.1f}" for k, v in enumerate(pts))
        area = f"{X(0):.1f},{yb} " + poly + f" {X(3):.1f},{yb}"
        dots = "".join(f'<circle cx="{X(k):.1f}" cy="{Y(v):.1f}" r="2.2" fill="#0b1226" stroke="{cols[i % 2]}" stroke-width="1.2"/>' for k, v in enumerate(pts))
        fechas = "".join(f'<text x="{X(k):.1f}" y="{yb + 8}" text-anchor="middle" class="rk">{dd} {abbr}</text>' for k, dd in enumerate([3, 10, 17, 24]))
        tr = " → ".join(niveles[v] for v in pts[-3:])
        return (f'<div class="rc"><div class="rc-h"><b style="color:{cols[i % 2]}">{e(subs[i])}</b></div>'
                f'<svg viewBox="0 0 {W} {H}" class="rsvg">{grid}<polygon points="{area}" fill="#13244a"/>'
                f'<polyline points="{poly}" fill="none" stroke="{cols[i % 2]}" stroke-width="1.6"/>{dots}{fechas}</svg>'
                f'<div class="rc-t" style="color:{cols[i % 2]}">{e(tr)}</div></div>')

    charts = "".join(chart(i) for i in range(min(2, len(subs))))
    multi = r.get("destrezas_label", "").lower().startswith("asignaturas")
    asig_txt = " · ".join(subs) if multi else (lista_asig(d["asignaturas"]) or " · ".join(subs))
    kpi_lab = "ASIGNATURAS" if multi else "BLOQUES"
    s1 = f'''<div class="scr dk">
  <img class="rs-logo" src="{LOGO_URI}">
  <div class="rs-pill">DOCUMENTO PRIVADO · INFORME MENSUAL</div>
  <div class="rs-t">Informe de seguimiento</div><div class="rs-m">{e(mes)}</div>
  <div class="rs-card"><div class="rs-n">{e(n)}</div>
    <div class="rs-g"><div><small>PROFESOR</small>{e(prof)}</div><div><small>ASIGNATURAS</small>{e(asig_txt)}</div>
    <div><small>PERIODO</small>{e(mes)}</div><div><small>SESIONES Y HORAS</small>{r["sesiones"]} sesiones · {e(r["horas"])}</div></div></div>
  <div class="rs-charts">{charts}</div>
</div>'''
    frases = [x.strip() for x in r["resumen"].replace(". ", ".|").split("|") if x.strip()]
    secc = f'<div class="rs-sec g"><small>EL MES EN GENERAL</small><p>{e(frases[0])}</p></div>'
    for i, sub in enumerate(subs[:2]):
        txt = frases[i + 1] if i + 1 < len(frases) else ""
        if txt:
            secc += f'<div class="rs-sec" style="border-color:{cols[i % 2]}"><small style="color:{cols[i % 2]}">{e(sub.upper())}</small><p>{e(txt)}</p></div>'
    s2 = f'''<div class="scr dk">
  <div class="rs-pill l">INFORME DE SEGUIMIENTO MENSUAL</div>
  <div class="rs-n l">{e(n)}</div><div class="rs-sub">{e(asig_txt)} · {e(mes)}</div>
  <div class="rs-k"><div><b>{r["sesiones"]}</b>SESIONES</div><div><b>{e(r["horas"])}</b>DEDICADAS</div><div><b>{len(subs)}</b>{kpi_lab}</div></div>
  <div class="rs-hl"><small>MAYOR PROGRESO DEL MES</small>{e(r["mayor_progreso"])}</div>
  <div class="rs-h2">Resumen del mes</div>{secc}
  <div class="rs-sec" style="border-color:#7d7f8a"><small style="color:#a49f8e">CONCLUSIÓN</small><p>{e(r["conclusion"])}</p></div>
</div>'''
    auto = [25, 55, 55, 90]
    barras = "".join(f'<div class="ra"><em>{v}%</em><i style="height:{v * 0.5:.0f}px"></i><span>{dd} {abbr}</span></div>'
                     for v, dd in zip(auto, [3, 10, 17, 24]))
    li = lambda xs: "".join(f"<div>— {e(x)}</div>" for x in xs)
    hsub = sum(h for _, h in r["temas"])
    s3 = f'''<div class="scr dk">
  <div class="rs-pill l">{e(r["asignatura"].upper())}</div>
  <div class="rs-n l">{e(r["asignatura"])}</div>
  <div class="rs-k"><div><b>{(f"{hsub:g}").replace(".", ",")}h</b>HORAS</div><div><b>4</b>SESIONES</div></div>
  <div class="rs-box"><b>Evolución de autonomía en el mes</b><div class="ras">{barras}</div></div>
  <div class="rs-b g"><small>PUNTOS FUERTES</small>{li(r["fuertes"])}</div>
  <div class="rs-b a"><small>A TENER EN CUENTA</small>{li(r["atencion"])}</div>
  <div class="rs-b b"><small>REFUERZO RECOMENDADO</small>{li(r["casa"])}</div>
</div>'''
    props = ""
    for i, sub in enumerate(subs[:2]):
        chip, txt = ("CONSOLIDAR", r["conclusion"]) if i == 0 else ("REFORZAR", r["atencion"][0])
        props += f'<div class="rs-pr"><b>{e(sub)}</b><span class="{"c" if i == 0 else "r"}">{chip}</span><p>{e(txt)}</p></div>'
    s4 = f'''<div class="scr dk">
  <div class="rs-pill l">DE CARA A {e(sig.upper())}</div>
  <div class="rs-n l sm">Qué tener en cuenta el mes que viene</div>
  <div class="rs-box"><b>Organización del mes</b><p>{e(r["horario"])}</p></div>
  <div class="rs-box"><b>Propuesta para {e(sig)}</b>{props}</div>
  <div class="rs-box"><b>Base científica de las recomendaciones</b><p>Las recomendaciones de refuerzo se apoyan en técnicas con evidencia sólida: práctica espaciada, autoevaluación y ejemplos resueltos.</p></div>
</div>'''
    caps = [("Portada del informe", "Comprensión de cada asignatura, sesión a sesión."),
            ("Resumen del mes", "Mayor progreso y resumen separado por asignatura."),
            ("Detalle por asignatura", "Autonomía por sesión, puntos fuertes y refuerzo."),
            ("Propuesta para el mes siguiente", "Organización y foco de cada asignatura.")]
    return "".join(f'<div class="ph-wrap"><div class="phone"><div class="notch"></div>{x}</div>'
                   f'<h5>{e(a)}</h5><p>{e(b)}</p></div>' for x, (a, b) in zip([s1, s2, s3, s4], caps))


def page_phones(d, t):
    return f'''<section class="page">
  <div class="hdr"><span class="hdr-l">LOS INFORMES</span></div><div class="rule"></div>
  <div class="pill gold">{e(t["p4_pill"])}</div>
  <h2>El informe, capturado desde el móvil</h2>
  <p class="lead">{e(t["p4_sub"])}</p>
  <div class="phones">{phones_real(d)}</div>
  {footer()}
</section>'''


def page_tarifas(d, t, mod):
    tf = TARIFAS[d["etapa"]]
    pr, base = tf["precios"][mod], tf["base"][mod]
    etiqueta = {"online": "ONLINE", "casa_profesor": "EN CASA DEL PROFESOR",
                "casa_alumno": "PRESENCIAL EN CASA DEL ALUMNO"}[mod]
    sub = tf["corto"] + (" · Online" if mod == "online" else "")
    cards = ""
    for h in (2, 4, 8, 12):
        precio = f'<div class="old">{eur(base*2)}</div><div class="price">{eur(pr[h])}</div><div class="new">★ Precio nuevos alumnos</div>' \
            if h == 2 else f'<div class="price solo">{eur(pr[h])}</div>'
        feats = "".join(f"<li>{e(f)}</li>" for f in FEATURES[h])
        top = '<div class="top">Más elegido</div>' if h == 12 else ""
        cards += f'<div class="tc{" feat" if h == 12 else ""}">{top}<div class="hh">{h}h</div><div class="hs">{e(sub)}</div>{precio}<ul class="checks sm">{feats}</ul></div>'
    return f'''<section class="page">
  <div class="hdr"><span class="hdr-l">TARIFAS · {etiqueta}</span></div><div class="rule"></div>
  <div class="pill blue">TARIFAS {e(tf["nombre"].upper())} · {etiqueta}</div>
  <h2>Bonos de horas. Sin permanencia.</h2>
  <p class="lead">{e(t["pagais"])}</p>
  <div class="tcards">{cards}</div>
  {footer("Nexo Académico · Guía " + tf["nombre"])}
</section>'''


def calc(d, h, mod):
    tf = TARIFAS[d["etapa"]]
    p, b = tf["precios"][mod][h], tf["base"][mod]
    ref = b * h
    return dict(precio=p, hora=p / h, base=b, ahorro=ref - p, pct=pct(ref - p, ref))


def precio_bloque(d, c, h):
    # Por defecto, total del bono en grande; con "destacar": "hora", el precio por hora
    if d.get("destacar") == "hora":
        return (f'<div class="rp hora">{eur(c["hora"])}<small>/hora</small></div>'
                f'<div class="rh">{eur(c["precio"], 0)} al mes · bono de {h}h</div>')
    return f'<div class="rp">{eur(c["precio"], 0)}</div><div class="rh">{eur(c["hora"])}/hora</div>'


def page_bono(d, t):
    n = d["nombre"] or d["curso"]
    anon = not d["nombre"]
    bonos, mods = d["bonos_recomendados"], d["modalidades_recomendadas"]
    hs = " u ".join(f"{b['horas']}h" for b in bonos) if len(bonos) > 1 else f"{bonos[0]['horas']}h"
    ms = " o ".join(mod_corto(m, t) for m in mods)
    title = f"Bono{'s' if len(bonos) > 1 else ''} de {hs}{',' if len(mods) > 1 else ''} {ms}"
    title = title[0].upper() + title[1:]
    verbo = "haces" if d["voz"] == "tu" else "hace"
    if not d["nombre"] and d["voz"] != "tu":
        verbo = "son"
    if len(bonos) == 1:
        frases = f"el bono de {bonos[0]['horas']}h al mes ({bonos[0]['frecuencia']})"
    else:
        frases = ", o ".join(f"el bono de {b['horas']}h al mes si {verbo} {b['frecuencia']}" if i == 0
                             else f"el de {b['horas']}h si {verbo} {b['frecuencia']}" for i, b in enumerate(bonos))
    ubic = f", {d['ubicacion']}" if d.get("ubicacion") else ""
    if len(mods) == 1:
        extra = f"con el profesor dando la clase {ms}{ubic}" if mods[0] != "online" else "con clases online"
        lead = f"{t['p8_para']} {frases}, {extra}."
    elif d["voz"] == "tu":
        lead = f"{t['p8_para']} {frases}. Puedes elegir entre clases {ms}{ubic}."
    else:
        lead = f"{t['p8_para']} {frases}. Podéis elegir entre clases {ms}{ubic}."
    if d.get("frase_bono"):
        lead += " " + d["frase_bono"]
    cards = ""
    for b in bonos:
        h = b["horas"]
        rows = ""
        for m in mods:
            c = calc(d, h, m)
            rows += f'''<div class="rrow"><div class="rm">{e(cap(mod_corto(m, t)))}</div>
  {precio_bloque(d, c, h)}
  <div class="rs">Ahorro de {eur(c["ahorro"], 0)} (−{c["pct"]}%) frente a la tarifa base de {eur(c["base"])}/h</div></div>'''
        if b.get("refuerzo"):
            rf = b["refuerzo"]
            precios = " · ".join(f"{eur(calc(d, rf['horas'], m)['precio'], 0)} {mod_corto(m, t)}" for m in mods)
            rows += (f'<div class="rref"><b>+ Refuerzo de {rf["horas"]}h {e(rf["cuando"])}</b>'
                     f'<span>{e(rf["motivo"])}</span><em>Bono de {rf["horas"]}h: {e(precios)}</em></div>')
        feats = "".join(f"<li>{e(f)}</li>" for f in FEATURES[h])
        cards += f'''<div class="rcard"><div class="rtop"><b>{h}h</b><span>al mes · {e(b["frecuencia"])}</span></div>
  {rows}<ul class="checks sm">{feats}</ul></div>'''
    return f'''<section class="page">
  <div class="hdr"><span class="hdr-l">PLAN PERSONALIZADO · {e(n.upper())}</span></div><div class="rule"></div>
  <div class="who"><div class="av">{e(n.split()[0] if anon else n[0])}</div><div><div class="wn">{e(n)}</div><div class="ws">{e(" · ".join(x for x in [None if anon else d["curso"], lista_asig(d["asignaturas"])] if x).upper())}</div></div></div>
  <div class="pill gold">{e(t["p8_pill"])}</div>
  <h2>{e(title)}</h2>
  <p class="lead">{e(lead)} Sin permanencia.</p>
  <div class="rwrap"><div class="rbadge">{e(d.get("badge_bono") or t["p8_badge"])}</div><div class="rgrid">{cards}</div></div>
  {f'<p class="nota-bono">{e(d["nota_bono"])}</p>' if d.get("nota_bono") else ""}
  {footer()}
</section>'''


def page_resumen(d, t):
    n = d["nombre"] or d["curso"]
    anon = not d["nombre"]
    rows = ""
    for b in d["bonos_recomendados"]:
        h = b["horas"]
        prices = "".join(f'<div class="sp"><small>{e(cap(mod_corto(m, t)))}</small><b>{eur(calc(d, h, m)["hora"])}<i>/h</i></b><em>{eur(calc(d, h, m)["precio"], 0)} al mes</em></div>'
                         if d.get("destacar") == "hora" else
                         f'<div class="sp"><small>{e(cap(mod_corto(m, t)))}</small><b>{eur(calc(d, h, m)["precio"], 0)}</b></div>'
                         for m in d["modalidades_recomendadas"])
        rows += f'''<div class="srow"><div class="av w">{e(n.split()[0] if anon else n[0])}</div>
  <div class="st"><b>{e(("" if anon else n + " — ") + f"Bono de {h}h")}</b><small>{e(" · ".join(x for x in [b["frecuencia"], lista_asig(d["asignaturas"]) or d["curso"]] if x))}</small></div>
  <div class="sps">{prices}</div></div>'''
        if b.get("refuerzo"):
            rf = b["refuerzo"]
            prices = "".join(f'<div class="sp"><small>{e(cap(mod_corto(m, t)))}</small><b>+{eur(calc(d, rf["horas"], m)["precio"], 0)}</b></div>'
                             for m in d["modalidades_recomendadas"])
            rows += f'''<div class="srow ref"><div class="av w">+</div>
  <div class="st"><b>Refuerzo de {rf["horas"]}h</b><small>{e(rf["cuando"])} · {e(rf["motivo"])}</small></div>
  <div class="sps">{prices}</div></div>'''
    ms = " o ".join(mod_corto(m, t) for m in d["modalidades_recomendadas"])
    ubic = f", {d['ubicacion']}" if d.get("ubicacion") else ""
    q_end = ("con el profesor en " + ("tu" if d["voz"] == "tu" else "su") + " propia casa") \
        if d["modalidades_recomendadas"] == ["casa_alumno"] else ms
    return f'''<section class="page">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">RESUMEN DEL PLAN</span></div><div class="rule"></div>
  <div class="pill gold">RESUMEN MENSUAL</div>
  <h2>Tu plan, de un vistazo</h2>
  <p class="lead">{e(t["p9_sub"])}</p>
  <div class="srows">{rows}</div>
  <ul class="dash"><li>{e(t["p9_l1"])}, {e(ms)}{e(ubic)}.</li><li>{e(t["p9_l2"])}</li></ul>
  <div class="quote"><span>"</span><em>{e(t["quote"])}, {e(q_end)}.</em></div>
  {footer()}
</section>'''


def page_cierre(d, t):
    return f'''<section class="page cover">
  <img class="logo-md" src="{LOGO_URI}">
  <div class="pill gold">PLAN VÁLIDO CURSO 2026–2027</div>
  <h2 class="c">¿Confirmamos el mes?</h2>
  <p class="cover-sub">{e(t["p10_sub"])}</p>
  <a class="wa" href="https://wa.me/34699529399">💬 Escríbenos por WhatsApp</a>
  <div class="contact"><span>🌐 nexoacademico.com</span><span>📞 699 52 93 99</span><span>✉️ nexoacademicopremium@gmail.com</span></div>
</section>'''


CSS = r"""
@page { size: 960px 904px; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'Liberation Sans', Arial, sans-serif; color: #fff; background: #0a1226; }
.page { width: 960px; height: 904px; overflow: hidden; position: relative; page-break-after: always; padding: 40px 64px 0;
  background:
    radial-gradient(rgba(255,255,255,0.045) 1px, transparent 1.2px) 0 0/22px 22px,
    radial-gradient(ellipse 60% 45% at 100% 100%, rgba(30,60,130,0.45), transparent 70%),
    linear-gradient(160deg, #0b0d18 0%, #0a1226 55%, #10214a 100%); }
.page.glow { background:
    radial-gradient(rgba(255,255,255,0.045) 1px, transparent 1.2px) 0 0/22px 22px,
    radial-gradient(ellipse 35% 30% at 18% 18%, rgba(90,75,45,0.22), transparent 70%),
    radial-gradient(ellipse 60% 45% at 100% 100%, rgba(30,60,130,0.45), transparent 70%),
    linear-gradient(160deg, #0b0d18 0%, #0a1226 55%, #10214a 100%); }
h1, h2, h4, h5, .num, .nm, .wn, .hh, .price, .old, b { font-family: 'Liberation Serif', 'Times New Roman', serif; }
.cover { display: flex; flex-direction: column; align-items: center; text-align: center; padding-top: 240px; }
.logo-lg { width: 230px; margin-bottom: 26px; }
.logo-md { width: 115px; margin: 36px 0 26px; }
.logo-sm { width: 95px; }
.pill { display: inline-block; border-radius: 999px; padding: 8px 16px 7px; font: 700 11.5px/1.1 'Liberation Sans', Arial; letter-spacing: 0.14em; }
.pill.gold { color: #e9d18f; border: 1px solid rgba(233,209,143,0.55); }
.pill.blue { color: #8fb8ec; border: 1px solid rgba(143,184,236,0.55); }
.cover-h { font-size: 45px; line-height: 1.2; margin: 30px 0 22px; font-weight: 700; }
.cover-h em { color: #e9d18f; font-style: italic; }
.cover-sub { color: #a49f8e; font-size: 16px; max-width: 560px; line-height: 1.3; }
.name-card { margin-top: 42px; border: 1px solid rgba(255,255,255,0.14); border-radius: 14px; padding: 22px 42px; background: rgba(10,16,34,0.55); }
.nm { color: #e9d18f; font-size: 22px; font-weight: 700; }
.cs { color: #8a8a93; font-size: 12px; letter-spacing: 0.1em; margin-top: 6px; }
.cover-foot { position: absolute; bottom: 30px; left: 0; right: 0; color: #6c6f7c; font-size: 11.5px; letter-spacing: 0.16em; }
.hdr { display: flex; align-items: center; justify-content: space-between; min-height: 30px; }
.hdr-l, .hdr-r { color: #cdb57a; font-size: 11.5px; font-weight: 700; letter-spacing: 0.16em; }
.rule { height: 1px; margin: 22px 0 36px; background: linear-gradient(90deg, transparent, rgba(233,209,143,0.35), transparent); }
h2 { font-size: 33px; font-weight: 700; margin: 24px 0 10px; }
h2.c { font-size: 34px; margin: 26px 0 18px; }
.lead { color: #a49f8e; font-size: 16px; line-height: 1.25; max-width: 700px; }
.steps { display: grid; grid-template-columns: repeat(3,1fr); border: 1px solid rgba(255,255,255,0.12); border-radius: 14px; margin-top: 34px; background: rgba(12,18,36,0.55); }
.steps > div { padding: 22px 23px 24px; border-left: 1px solid rgba(255,255,255,0.12); }
.steps > div:first-child { border-left: 0; }
.num { color: #e9d18f; font-size: 14px; }
.steps h4 { font-size: 16.5px; margin: 12px 0 10px; }
.steps p { color: #a49f8e; font-size: 13.5px; line-height: 1.17; }
.stats { display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; margin-top: 32px; }
.stats > div, .kpis > div { border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; padding: 16px 8px 14px; text-align: center; background: rgba(12,18,36,0.55); }
.stats b { display: block; color: #e9d18f; font-size: 21px; }
.stats span { display: block; color: #7d7f8a; font-size: 10.5px; letter-spacing: 0.06em; margin-top: 6px; }
.foot { margin-top: 42px; border-top: 1px solid rgba(255,255,255,0.12); padding-top: 14px; display: flex; justify-content: space-between; color: #6c6f7c; font-size: 12px; }
.checks { list-style: none; display: grid; grid-template-columns: 1fr 1fr; column-gap: 40px; row-gap: 20px; margin: 34px 0 30px; }
.checks li { color: #a49f8e; font-size: 14.5px; }
.checks li::before { content: "✓"; color: #e9d18f; margin-right: 10px; }
.checks.sm { grid-template-columns: 1fr; row-gap: 7px; margin: 16px 0 0; }
.checks.sm li { font-size: 13.5px; }
.panel { border: 1px solid rgba(255,255,255,0.14); border-radius: 14px; padding: 26px 30px 20px; background: rgba(14,18,32,0.6); }
.panel-h { display: flex; justify-content: space-between; align-items: center; }
.panel-h b { font-size: 18px; }
.panel-h span { color: #e9d18f; font-size: 12px; letter-spacing: 0.08em; }
.kpis { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin: 22px 0 18px; }
.kpis > div { text-align: left; padding: 12px 15px; }
.kpis b { display: block; color: #e9d18f; font-size: 20px; }
.kpis span { color: #7d7f8a; font-size: 9.5px; letter-spacing: 0.05em; }
.bar { display: grid; grid-template-columns: 170px 1fr 40px; align-items: center; margin: 7px 0; }
.bl { color: #c9c9cf; font-size: 13.5px; }
.bt { height: 6px; border-radius: 4px; background: rgba(40,60,110,0.5); overflow: hidden; }
.bt i { display: block; height: 100%; border-radius: 4px; background: linear-gradient(90deg, #8a6e33, #e9d18f); }
.bv { text-align: right; color: #e9d18f; font-weight: 700; font-size: 13px; }
.phones { display: grid; grid-template-columns: repeat(4,1fr); gap: 22px; margin-top: 44px; }
.ph-wrap { text-align: center; }
.ph-wrap h5 { font: 700 14.5px 'Liberation Sans', Arial; margin-top: 12px; }
.ph-wrap p { color: #8a8a93; font-size: 12.5px; line-height: 1.2; margin-top: 3px; }
.phone { position: relative; height: 415px; background: #f4f1e8; border: 1px solid #d9d4c4; border-radius: 26px; padding: 11px 10px 12px; }
.notch { position: absolute; top: 11px; left: 50%; transform: translateX(-50%); width: 64px; height: 6px; background: #f4f1e8; border-radius: 0 0 6px 6px; z-index: 2; }
.scr.dk { background: linear-gradient(170deg, #0d1222, #0b1530 60%, #10204a); color: #e7e7ea; padding: 14px 8px 8px; }
.rs-logo { display: block; width: 46px; margin: 4px auto 6px; }
.rs-pill { width: max-content; margin: 0 auto; border: 0.6px solid #c9a24b; color: #e9d18f; border-radius: 99px; padding: 1.5px 5px; font-size: 4.3px; font-weight: 700; letter-spacing: 0.05em; }
.rs-pill.l { margin: 0; }
.rs-t { text-align: center; font: 700 10.5px 'Liberation Serif', serif; margin-top: 6px; }
.rs-m { text-align: center; font: italic 9.5px 'Liberation Serif', serif; color: #e9d18f; }
.rs-card { margin-top: 7px; border: 0.6px solid #2a3350; border-radius: 6px; padding: 6px 7px; background: #0c1428; }
.rs-n { text-align: center; font: 700 9px 'Liberation Serif', serif; color: #e9d18f; padding-bottom: 4px; border-bottom: 0.6px solid #2a3350; }
.rs-n.l { text-align: left; color: #fff; font-size: 13px; border: 0; padding: 0; margin-top: 5px; }
.rs-n.sm { font-size: 11px; }
.rs-g { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 6px; margin-top: 4px; font-size: 5px; font-weight: 700; }
.rs-g small { display: block; font-size: 3.8px; color: #7d7f8a; letter-spacing: 0.06em; }
.rs-charts { display: grid; gap: 5px; margin-top: 6px; }
.rc { border: 0.6px solid #2a3350; border-radius: 6px; padding: 4px 5px 3px; background: #0c1428; }
.rc-h b { font: 700 7px 'Liberation Serif', serif; }
.rsvg { display: block; width: 100%; height: auto; }
.rsvg .rk { fill: #7d7f8a; font-size: 4px; font-family: 'Liberation Sans', Arial; }
.rc-t { text-align: center; font-size: 4.5px; font-weight: 700; }
.rs-sub { color: #a49f8e; font-size: 5.8px; margin-top: 1px; }
.rs-k { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3px; margin-top: 5px; }
.rs-k div { border: 0.6px solid #2a3350; border-radius: 4px; padding: 4px 5px; font-size: 4.3px; color: #7d7f8a; font-weight: 700; }
.rs-k b { display: block; font: 700 9.5px 'Liberation Serif', serif; color: #e9d18f; }
.rs-hl { margin-top: 6px; border-radius: 5px; padding: 6px 7px; background: linear-gradient(120deg, #13285a, #1d3d74); border: 0.6px solid #2e5596; font: 700 6.8px 'Liberation Serif', serif; line-height: 1.3; }
.rs-hl small { display: block; font: 700 3.8px 'Liberation Sans', Arial; color: #8fb8ec; letter-spacing: 0.06em; margin-bottom: 2px; }
.rs-h2 { font: 700 9.5px 'Liberation Serif', serif; margin: 8px 0 4px; }
.rs-sec { border-left: 1.2px solid #c9a24b; padding: 1px 0 1px 6px; margin: 5px 0 8px; }
.rs-sec small { display: block; font-size: 4.5px; font-weight: 700; color: #e9d18f; letter-spacing: 0.06em; margin-bottom: 1.5px; }
.rs-sec p { font-size: 6.2px; line-height: 1.5; color: #c9c9cf; }
.rs-box { margin-top: 7px; border: 0.6px solid #2a3350; border-radius: 5px; padding: 5px 6px; background: #0c1428; }
.rs-box b { font: 700 7.2px 'Liberation Serif', serif; }
.rs-box p { font-size: 6px; color: #c9c9cf; margin-top: 2px; line-height: 1.4; }
.ras { display: flex; gap: 4px; align-items: flex-end; height: 62px; margin-top: 3px; }
.ra { flex: 1; text-align: center; font-size: 3.8px; color: #7d7f8a; }
.ra em { display: block; font-style: normal; color: #e9d18f; font-weight: 700; font-size: 4.2px; }
.ra i { display: block; margin: 1px 0; border-radius: 1.5px; background: linear-gradient(180deg, #e9d18f, #9c8550); }
.rs-b { margin-top: 6px; border-left: 1.2px solid; border-radius: 3px; padding: 5px 6px; background: #0c1428; font-size: 5.8px; color: #c9c9cf; line-height: 1.4; }
.rs-b small { display: block; font-size: 4.5px; font-weight: 700; letter-spacing: 0.06em; margin-bottom: 1px; }
.rs-b.g { border-color: #7fcfa0; } .rs-b.g small { color: #7fcfa0; }
.rs-b.a { border-color: #e9d18f; } .rs-b.a small { color: #e9d18f; }
.rs-b.b { border-color: #8fb8ec; } .rs-b.b small { color: #8fb8ec; }
.rs-pr { margin-top: 4px; border: 0.6px solid #2a3350; border-radius: 4px; padding: 4px 5px; }
.rs-pr b { font: 700 6.6px 'Liberation Sans', Arial; }
.rs-pr span { margin-left: 3px; font-size: 3.6px; font-weight: 700; padding: 1px 3px; border-radius: 99px; border: 0.5px solid; }
.rs-pr span.c { color: #7fcfa0; } .rs-pr span.r { color: #e9d18f; }
.rs-pr p { font-size: 5.8px; color: #c9c9cf; margin-top: 2px; line-height: 1.4; }
.scr { background: #fff; color: #0a1226; height: 100%; border-radius: 16px; padding: 16px 10px 10px; font-size: 7px; line-height: 1.35; overflow: hidden; text-align: left; }
.s-eyebrow { text-align: center; color: #3565b8; font-size: 6.2px; letter-spacing: 0.06em; }
.s-name { text-align: center; font: 700 12.5px 'Liberation Serif', serif; margin-top: 5px; }
.s-name.l, .s-sub.b { text-align: left; }
.s-sub { text-align: center; color: #777; font-size: 6.5px; }
.s-sub.b { color: #3565b8; }
.s-kpis { display: grid; grid-template-columns: repeat(4,1fr); gap: 4px; margin: 9px 0; }
.s-kpis.m { grid-template-columns: repeat(3,1fr); }
.s-kpis > div { background: #eef1f7; border-radius: 4px; text-align: center; padding: 4px 1px; font-size: 4.8px; color: #888; }
.s-kpis b { display: block; color: #0a1226; font-size: 9px; }
.s-hl { background: linear-gradient(120deg,#0a1a44,#2a5fc0); color: #fff; border-radius: 6px; padding: 7px 8px; font-weight: 700; font-size: 7px; }
.s-hl small { display: block; font-weight: 400; font-size: 5.5px; opacity: .8; margin-bottom: 2px; }
.s-h { font: 700 8.5px 'Liberation Serif', serif; margin: 9px 0 4px; }
.s-h.sm { font: 700 6.5px 'Liberation Sans', Arial; }
.scr .s-p { color: #333; font-size: 6.6px; line-height: 1.55; }
.s-note { background: #f3efe4; border-radius: 6px; padding: 7px 8px; margin-top: 9px; font-size: 6.2px; color: #444; }
.s-note b { display: block; font: 700 6.2px 'Liberation Sans', Arial; color: #0a1226; margin-bottom: 3px; letter-spacing: .04em; }
.s-band { background: linear-gradient(120deg,#0a1a44,#2a5fc0); color: #fff; border-radius: 6px; padding: 9px 9px; margin-bottom: 8px; }
.s-band b { display: block; font-size: 10px; } .s-band small { font-size: 5.8px; opacity: .85; }
.s-t { display: flex; justify-content: space-between; font-size: 6.3px; margin-top: 4px; }
.s-tb { height: 3px; background: #e3e8f2; border-radius: 2px; } .s-tb i { display: block; height: 100%; background: #5b8ee0; border-radius: 2px; }
.s-sec { font-size: 5.8px; font-weight: 700; letter-spacing: .05em; margin: 9px 0 3px; }
.s-sec.g { color: #1f8a57; } .s-sec.a { color: #c77a1e; }
.s-li { font-size: 6px; color: #444; margin: 2px 0; }
.s-cols { display: flex; gap: 6px; align-items: flex-end; height: 64px; margin: 8px 0 4px; }
.s-col { flex: 1; text-align: center; font-size: 5.5px; color: #888; }
.s-col b { display: block; color: #0a1226; font-size: 6px; }
.s-col i { display: block; background: linear-gradient(180deg,#6fa0ea,#3d72cf); border-radius: 2px 2px 0 0; margin: 2px 0; }
.s-ev { margin: 6px 0; font-size: 6px; color: #555; }
.s-ev b { font: 700 6.4px 'Liberation Sans', Arial; color: #0a1226; } .s-ev span { color: #1f8a57; font-weight: 700; }
.s-cd { display: flex; gap: 8px; align-items: center; background: linear-gradient(90deg,#b8641e,#d9993e); color: #fff; border-radius: 6px; padding: 7px 8px; margin: 8px 0; }
.s-cd b { font-size: 10px; } .s-cd small { font-size: 5.5px; }
.s-cal { display: grid; grid-template-columns: repeat(7,1fr); gap: 2.5px; margin-top: 6px; }
.s-cal span { background: #eef1f7; border-radius: 2px; text-align: center; font-size: 5.3px; padding: 3.5px 0; color: #555; }
.s-cal span.h { background: none; font-weight: 700; }
.s-cal span.o { background: none; }
.s-cal span.s { background: #cfe0fa; color: #0a1226; }
.s-cal span.x { background: #c1502e; color: #fff; font-weight: 700; }
.s-leg { font-size: 5.3px; color: #777; margin-top: 6px; } .d1 { color: #7aa6ea; } .d2 { color: #c1502e; }
.s-aa { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 9px; font-size: 5.8px; color: #333; }
.s-aa small { display: block; font-style: italic; color: #888; margin-bottom: 2px; } .s-aa small.b { color: #3565b8; }
.tcards { display: grid; grid-template-columns: repeat(4,1fr); gap: 20px; margin-top: 34px; }
.tc { position: relative; height: 266px; border: 1px solid rgba(255,255,255,0.12); border-radius: 14px; padding: 26px 20px; text-align: center; background: rgba(10,22,52,0.8); }
.tc.feat { border-color: #3a7bd5; }
.tc .top { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #3a7bd5; color: #fff; font-size: 11.5px; font-weight: 700; padding: 5px 14px; border-radius: 999px; white-space: nowrap; }
.hh { color: #8fb8ec; font-size: 29px; font-weight: 700; }
.hs { color: #7d7f8a; font-size: 13px; margin-top: 2px; }
.old { color: #6c6f7c; font-size: 14px; text-decoration: line-through; margin-top: 16px; }
.price { font-size: 25px; font-weight: 700; }
.price.solo { margin-top: 36px; }
.new { color: #e9d18f; font-size: 12px; font-weight: 700; margin-top: 4px; }
.tc .checks.sm { text-align: left; margin-top: 18px; }
.tc .checks.sm li { display: flex; font-size: 13.5px; } .tc .checks.sm li::before { flex: none; }
.who { display: flex; align-items: center; gap: 16px; margin: -6px 0 24px; }
.av { width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg,#f0d68c,#c9a24b); color: #0a1226; display: flex; align-items: center; justify-content: center; font: 700 20px 'Liberation Serif', serif; }
.av.w { width: 40px; height: 40px; font-size: 15px; background: linear-gradient(135deg,#fff,#cfd3dc); }
.wn { font: 700 24px 'Liberation Serif', serif; }
.ws { color: #7d7f8a; font-size: 13px; letter-spacing: 0.08em; margin-top: 2px; }
.rwrap { position: relative; border: 1px solid #c9a24b; border-radius: 14px; padding: 30px 26px 24px; margin-top: 30px; background: rgba(18,22,36,0.6); }
.rbadge { position: absolute; top: -11px; left: 30px; background: #c9a24b; color: #0a1226; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; padding: 5px 14px; border-radius: 999px; }
.rgrid { display: grid; grid-template-columns: repeat(auto-fit, minmax(0,1fr)); gap: 24px; }
.rcard { border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 18px 20px; background: rgba(10,16,34,0.5); }
.rtop { display: flex; align-items: baseline; gap: 10px; margin-bottom: 8px; }
.rtop b { font-size: 34px; } .rtop span { color: #a49f8e; font-size: 13.5px; }
.rrow { display: grid; grid-template-columns: 1fr auto; column-gap: 10px; padding: 10px 0; border-top: 1px solid rgba(255,255,255,0.08); }
.rm { color: #e7e7ea; font-size: 14px; font-weight: 700; align-self: center; }
.rp { color: #e9d18f; font: 700 26px 'Liberation Serif', serif; text-align: right; grid-row: span 2; align-self: center; }
.rh { color: #a49f8e; font-size: 12.5px; }
.rref { border-top: 1px dashed rgba(233,209,143,0.4); padding: 10px 0 2px; }
.rref b { display: block; font: 700 14px 'Liberation Sans', Arial; color: #e9d18f; }
.rref span { display: block; color: #a49f8e; font-size: 12.5px; margin-top: 2px; }
.rref em { display: block; font-style: normal; color: #e7e7ea; font-size: 13px; margin-top: 4px; }
.srow.ref { border-style: dashed; border-color: rgba(233,209,143,0.4); }
.rp.hora { font-size: 30px; }
.rp.hora small { font: 400 13px 'Liberation Sans', Arial; color: #a49f8e; margin-left: 3px; }
.sp b i { font: 400 12px 'Liberation Sans', Arial; font-style: normal; color: #a49f8e; margin-left: 2px; }
.sp em { display: block; font-style: normal; color: #7d7f8a; font-size: 11.5px; margin-top: 2px; }
.nota-bono { color: #7d7f8a; font-size: 11.5px; margin-top: 12px; }
.rs { grid-column: 1 / -1; color: #7fcfa0; font-size: 12px; margin-top: 4px; }
.srow { display: flex; align-items: center; gap: 16px; border: 1px solid rgba(255,255,255,0.12); border-radius: 14px; padding: 16px 30px; margin-top: 16px; background: linear-gradient(90deg, rgba(8,12,26,0.8), rgba(16,33,74,0.8)); }
.srows { margin-top: 30px; }
.srows .srow:first-child { margin-top: 0; }
.st { flex: 1; } .st b { display: block; font-size: 19px; } .st small { color: #7d7f8a; font-size: 13px; }
.sps { display: flex; gap: 26px; }
.sp { text-align: right; } .sp small { display: block; color: #7d7f8a; font-size: 11.5px; } .sp b { color: #e9d18f; font-size: 26px; }
.dash { list-style: none; margin: 26px 0 14px; }
.dash li { color: #a49f8e; font-size: 14.5px; margin: 9px 0; }
.dash li::before { content: "—"; color: #e9d18f; margin-right: 10px; }
.quote { display: flex; gap: 16px; border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; padding: 24px 30px 30px; background: rgba(18,22,36,0.6); }
.quote span { color: #e9d18f; font: 700 26px 'Liberation Serif', serif; line-height: 1; }
.quote em { font: italic 16.5px 'Liberation Serif', serif; }
.wa { display: inline-block; margin-top: 36px; padding: 15px 36px; border-radius: 999px; background: linear-gradient(90deg,#e8cf8e,#c9a24b); color: #0a1226; font-weight: 700; font-size: 16px; text-decoration: none; }
.contact { display: flex; gap: 32px; margin-top: 30px; color: #a49f8e; font-size: 14px; }
.bigstats { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-top: 28px; }
.bigstats > div { border: 1px solid #5d5438; border-radius: 14px; padding: 16px 16px 14px; background: linear-gradient(160deg, #1c1e24, #0e1528); }
.bigstats b { display: block; color: #e9d18f; font-size: 34px; line-height: 1.05; }
.bigstats span { display: block; color: #a49f8e; font-size: 12.5px; line-height: 1.25; margin-top: 6px; }
.ruta .rule { margin: 18px 0 26px; }
.ruta h2 { margin-top: 16px; }
.ruta .bigstats { margin-top: 20px; }
.ruta .bigstats > div { padding: 12px 14px 11px; }
.ruta .bigstats b { font-size: 28px; }
.cal { margin-top: 18px; border: 1px solid rgba(255,255,255,0.12); border-radius: 14px; padding: 16px 18px 12px; background: rgba(12,18,36,0.6); }
.cal-h { display: flex; justify-content: space-between; align-items: center; }
.cal-h b { font-size: 16px; }
.leg { display: flex; gap: 14px; color: #a49f8e; font-size: 12px; }
.leg i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 5px; vertical-align: -1px; }
.grid { display: grid; column-gap: 5px; margin-top: 12px; align-items: end; }
.mes { border-top: 2px solid rgba(143,184,236,0.6); padding-top: 5px; margin: 0 2px 8px; align-self: start; }
.mes b { display: block; font: 700 11px 'Liberation Sans', Arial; letter-spacing: 0.1em; color: #8fb8ec; text-transform: uppercase; }
.mes span { color: #e9d18f; font-size: 11.5px; font-weight: 700; }
.wk { text-align: center; }
.wk small { display: block; color: #7d7f8a; font-size: 10px; margin-top: 5px; white-space: nowrap; }
.stack { display: flex; flex-direction: column-reverse; gap: 2px; height: 150px; justify-content: flex-start; }
.bdg { display: block; margin: 0 auto 4px; width: max-content; max-width: 100%; white-space: normal; line-height: 1.2; background: #c1502e; color: #fff; font: 700 9px 'Liberation Sans', Arial; letter-spacing: 0.06em; padding: 3px 6px; border-radius: 999px; }
.stack b small { display: block; font: 700 10px 'Liberation Sans', Arial; color: #e9d18f; }
.stack b { order: 99; font-size: 13px; color: #e7e7ea; margin-bottom: 3px; }
.wk.pico .stack b { color: #e9d18f; }
.stack i { display: block; border-radius: 3px; }
.c0 { background: linear-gradient(90deg,#e8cf8e,#c9a24b); }
.c1 { background: linear-gradient(90deg,#8fb8ec,#5b8ee0); }
.c2 { background: linear-gradient(90deg,#cfd8e8,#9fb0cc); }
.c3 { background: linear-gradient(90deg,#7fcfa0,#3f9e6f); }
.exbox { height: 150px; border-radius: 6px; background: repeating-linear-gradient(135deg, rgba(193,80,46,0.35) 0 6px, rgba(193,80,46,0.18) 6px 12px); border: 1px solid rgba(225,110,70,0.7); display: flex; align-items: center; justify-content: center; }
.exbox span { writing-mode: vertical-rl; transform: rotate(180deg); color: #ffd9c7; font-size: 11.5px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
.wk.ex small { color: #f0a283; font-weight: 700; }
.cal-n { color: #8a8a93; font-size: 12px; margin-top: 10px; line-height: 1.3; }
.bloques { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }
.blq { border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; padding: 12px 16px; background: rgba(12,18,36,0.6); }
.blq small { color: #8fb8ec; font-size: 10.5px; font-weight: 700; letter-spacing: 0.12em; }
.blq h4 { font-size: 15.5px; margin: 3px 0 4px; }
.blq p { color: #a49f8e; font-size: 12.5px; line-height: 1.3; }
.ruta .foot { margin-top: 18px; }
.calp .rule { margin: 18px 0 24px; }
.calp h2 { margin-top: 16px; }
.mgrid { display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; margin-top: 20px; }
.mc { border: 1px solid rgba(255,255,255,0.12); border-radius: 14px; padding: 12px 12px 10px; background: rgba(12,18,36,0.65); }
.mc-h { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; }
.mc-h b { font-size: 16px; } .mc-h span { color: #e9d18f; font-size: 11.5px; font-weight: 700; }
.mc-g { display: grid; grid-template-columns: repeat(7,1fr); gap: 3px; }
.dh { text-align: center; color: #6c6f7c; font-size: 9.5px; font-weight: 700; padding-bottom: 2px; }
.dd { height: 31px; border-radius: 6px; background: rgba(255,255,255,0.04); display: flex; flex-direction: column; align-items: center; justify-content: center; line-height: 1; }
.dd b { font: 400 11.5px 'Liberation Sans', Arial; color: #c9c9cf; }
.dd small { font-size: 7.5px; font-weight: 700; margin-top: 2px; letter-spacing: 0.02em; }
.dd.o { background: none; }
.dd.off { opacity: 0.3; }
.dd.fe { background: repeating-linear-gradient(135deg, rgba(255,255,255,0.10) 0 3px, transparent 3px 6px); }
.dd.fe b { color: #7d7f8a; }
.dd.sx { background: rgba(193,80,46,0.22); box-shadow: inset 0 0 0 1px rgba(225,110,70,0.55); }
.dd.se { background: linear-gradient(160deg,#6fa0ea,#3d72cf); }
.dd.se b, .dd.se small { color: #fff; }
.dd.in { background: linear-gradient(160deg,#f0d68c,#c9a24b); }
.dd.in b, .dd.in small { color: #0a1226; font-weight: 700; }
.dd.ex { background: #c1502e; box-shadow: 0 0 0 2px rgba(193,80,46,0.35); }
.dd.ex b, .dd.ex small { color: #fff; font-weight: 700; }
.dd.hoy { box-shadow: 0 0 0 2px #e9d18f; }
.dd.hoy small { color: #e9d18f; }
.mc-i { color: #8a8a93; font-size: 11px; margin-top: 8px; min-height: 13px; }
.mc.side { display: flex; flex-direction: column; }
.legend { display: grid; grid-template-columns: 1fr 1fr; gap: 7px 8px; }
.legend div { display: flex; align-items: center; gap: 7px; color: #a49f8e; font-size: 11px; }
.legend .dd { width: 18px; height: 18px; flex: none; border-radius: 4px; }
.rs-r { display: flex; align-items: baseline; gap: 8px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 7px; margin-top: 8px; }
.rs-r b { color: #e9d18f; font: 700 19px 'Liberation Serif', serif; min-width: 54px; }
.rs-r span { color: #a49f8e; font-size: 11.5px; line-height: 1.25; }
.legend + .rs-r { margin-top: 12px; }
.calp .foot { margin-top: 18px; }
.camino h2 { font-size: 36px; margin-top: 22px; }
.road { margin-top: 44px; }
.cfases { display: grid; gap: 8px; }
.cf { border-radius: 14px; padding: 14px 16px; min-height: 74px; border: 1px solid #2a3350; }
.cf small { display: block; font-size: 10.5px; font-weight: 700; letter-spacing: 0.14em; color: #8fb8ec; }
.cf b { display: block; font: 700 17px 'Liberation Serif', serif; margin-top: 6px; }
.f0 { background: linear-gradient(160deg, #15305e, #0f1c3a); }
.f1 { background: linear-gradient(160deg, #1a3360, #121f3e); }
.f2 { background: linear-gradient(160deg, #2c3140, #181f33); }
.f3 { background: linear-gradient(160deg, #5a4e30, #2c2a2a); border-color: #9c8550; }
.f3 small { color: #e9d18f; }
.track { position: relative; height: 92px; margin: 6px 0 0; }
.line { position: absolute; left: 0; right: 0; top: 30px; height: 6px; border-radius: 6px; background: linear-gradient(90deg, #3a7bd5 0%, #8fb8ec 45%, #e9d18f 85%, #c9a24b 100%); }
.hito { position: absolute; top: 20px; transform: translateX(-50%); text-align: center; width: 120px; }
.hito i { display: block; width: 26px; height: 26px; margin: 0 auto; border-radius: 50%; background: #0a1226; border: 4px solid #8fb8ec; }
.hito span { display: block; margin-top: 10px; font-size: 12.5px; font-weight: 700; color: #e7e7ea; }
.hito.meta { top: 12px; }
.hito.meta i { width: 44px; height: 44px; border: 6px solid #3d3826; background: linear-gradient(135deg, #f6e2a6, #c9a24b); }
.hito.meta span { color: #e9d18f; font: 700 16px 'Liberation Serif', serif; margin-top: 8px; }
.mlab { display: grid; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 10px; }
.mlab span { text-align: center; color: #7d7f8a; font-size: 11.5px; letter-spacing: 0.1em; text-transform: uppercase; }
.ccards { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-top: 40px; }
.cc { border-radius: 14px; padding: 18px 18px 20px; border: 1px solid #2a3350; }
.cc em { font: italic 700 14px 'Liberation Serif', serif; color: #e9d18f; }
.cc b { display: block; font: 700 17px 'Liberation Serif', serif; margin: 8px 0 6px; }
.cc p { color: #a49f8e; font-size: 13px; line-height: 1.35; }
.camino .foot { margin-top: 40px; }
.ciclos h2 { margin-top: 18px; }
.bigcal { margin-top: 22px; border: 1px solid #2a3350; border-radius: 16px; padding: 16px 18px 18px; background: #0c1428; }
.bc-h { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; }
.bc-h b { font: 700 24px 'Liberation Serif', serif; }
.bc-h span { color: #e9d18f; font-size: 13px; font-weight: 700; }
.bc-g { display: grid; grid-template-columns: repeat(7, minmax(0,1fr)); gap: 6px; }
.bh { text-align: center; color: #7d7f8a; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; padding-bottom: 2px; }
.bd { position: relative; height: 62px; border-radius: 10px; background: #121a30; border: 1px solid #1d2744; padding: 7px 9px; }
.bd b { font: 700 17px 'Liberation Serif', serif; color: #e7e7ea; }
.bd em { position: absolute; left: 8px; right: 6px; bottom: 6px; font-style: normal; font-size: 9px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; line-height: 1.15; }
.bd.k0 { background: linear-gradient(160deg, #1d3d74, #152c56); border-color: #2e5596; }
.bd.k1 { background: linear-gradient(160deg, #4d4128, #33301f); border-color: #7a6638; }
.bd.k2 { background: linear-gradient(160deg, #2b3c5c, #1f2c46); border-color: #3f5680; }
.bd.k0 em { color: #b9d2f5; } .bd.k1 em { color: #f1dca0; } .bd.k2 em { color: #c9d6ee; }
.bd.fuera { opacity: 0.35; }
.bd.fest { background: repeating-linear-gradient(135deg, #1a2238 0 5px, #141b2e 5px 10px); border-color: #2a3350; }
.bd.fest em { color: #a49f8e; }
.kleg { display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; margin-top: 18px; }
.kl { display: flex; gap: 12px; align-items: flex-start; border: 1px solid #2a3350; border-radius: 12px; padding: 12px 14px; background: #0e1629; }
.kl i { flex: none; width: 16px; height: 16px; border-radius: 5px; margin-top: 2px; }
.kl.k0 i { background: #2e5ea8; } .kl.k1 i { background: #b8964c; } .kl.k2 i { background: #56709e; }
.kl b { display: block; font: 700 15px 'Liberation Serif', serif; }
.kl span { color: #a49f8e; font-size: 12px; line-height: 1.3; }
.ciclos .foot { margin-top: 20px; }
.bd.s0 { background: linear-gradient(160deg, #5a4e30, #3a3322); border-color: #9c8550; } .bd.s0 em { color: #f1dca0; }
.bd.s1 { background: linear-gradient(160deg, #1d3d74, #152c56); border-color: #2e5596; } .bd.s1 em { color: #b9d2f5; }
.bd.s2 { background: linear-gradient(160deg, #3a4660, #283247); border-color: #5a6a8c; } .bd.s2 em { color: #dfe6f3; }
.bd.s3 { background: linear-gradient(160deg, #1f4a37, #163528); border-color: #3f8a64; } .bd.s3 em { color: #b5ecc9; }
.bd.s4 { background: linear-gradient(160deg, #e8cf8e, #c9a24b); border-color: #e9d18f; } .bd.s4 b, .bd.s4 em { color: #0a1226; }
.semp h2 { margin-top: 16px; }
.semp .rule { margin: 18px 0 24px; }
.sgrid { display: grid; grid-template-columns: 46px repeat(5, 1fr); gap: 8px; margin-top: 20px; }
.shs { position: relative; margin-top: 32px; }
.sh { position: absolute; right: 4px; transform: translateY(-50%); color: #7d7f8a; font-size: 11px; font-weight: 700; }
.sdh { height: 26px; margin-bottom: 6px; text-align: center; font: 700 14px 'Liberation Serif', serif; color: #e7e7ea; border-bottom: 2px solid #2a3350; }
.sdb { position: relative; border-radius: 10px; background: repeating-linear-gradient(180deg, #0e1629 0 57px, #172243 57px 58px); border: 1px solid #1d2744; }
.sb { position: absolute; left: 4px; right: 4px; border-radius: 9px; padding: 8px 10px; border: 1px solid; }
.sb b { display: block; font: 700 14px 'Liberation Serif', serif; }
.sb span { font-size: 11px; font-weight: 700; opacity: 0.85; }
.a0 { background: linear-gradient(160deg, #5a4e30, #3a3322); border-color: #9c8550; color: #f1dca0; }
.a1 { background: linear-gradient(160deg, #1d3d74, #152c56); border-color: #2e5596; color: #b9d2f5; }
.a2 { background: linear-gradient(160deg, #3a3060, #282046); border-color: #6a5aa8; color: #d6cdf5; }
.a3 { background: linear-gradient(160deg, #1f4a37, #163528); border-color: #3f8a64; color: #b5ecc9; }
.sb.mini { padding: 5px 9px; }
.sb.mini b { font-size: 12.5px; white-space: nowrap; }
.sb.mini span { font-size: 10px; }
.a4 { background: linear-gradient(160deg, #5c2f3c, #3e2029); border-color: #a85a70; color: #f5c9d5; }
.bx-ref { display: flex; justify-content: space-between; color: #7d7f8a; font-size: 13px; padding: 3px 0; }
.bx-ref s { color: #a49f8e; }
.dtp h2 { margin-top: 14px; }
.dtp .rule { margin: 18px 0 24px; }
.dts { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 26px; }
.dt { border: 1px solid #2a3350; border-radius: 18px; padding: 24px 24px 20px; background: #0e1629; }
.dt.std { border-color: #3a5a96; background: linear-gradient(160deg, #15264a, #0e1629); }
.dt.pre { border-color: #c9a24b; background: linear-gradient(160deg, #2a2618, #0e1629); }
.dt-n { font: 700 24px 'Liberation Serif', serif; }
.dt-s { color: #a49f8e; font-size: 13.5px; margin-top: 2px; }
.dt-d { margin-top: 18px; color: #7d7f8a; font-size: 12px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
.dt-h { font: 700 54px 'Liberation Serif', serif; line-height: 1; }
.dt.std .dt-h { color: #8fb8ec; } .dt.pre .dt-h { color: #e9d18f; }
.dt-h small { font: 400 15px 'Liberation Sans', Arial; color: #a49f8e; margin-left: 4px; }
.dt-l { list-style: none; margin-top: 18px; padding-top: 16px; border-top: 1px solid #1d2744; }
.dt-l li { font-size: 15px; color: #e7e7ea; margin: 9px 0; }
.dt-l li::before { margin-right: 10px; font-weight: 700; }
.dt-l li.si::before { content: "✓"; color: #7fcfa0; } .dt-l li.no::before { content: "✕"; color: #f0a283; }
.dt-l li.no { color: #a49f8e; }
.dt-q { margin-top: 14px; padding: 10px 14px; border-radius: 10px; background: #0b1326; color: #c9c9cf; font-size: 13.5px; }
.dt-next { margin-top: 18px; display: flex; gap: 12px; align-items: center; justify-content: center; color: #a49f8e; font-size: 14.5px; }
.dt-next i { font-style: normal; color: #e9d18f; font-weight: 700; }
.prp h2 { margin-top: 14px; }
.prp .rule { margin: 18px 0 24px; }
.prs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-top: 44px; }
.pr { position: relative; border: 1px solid #2a3350; border-radius: 18px; padding: 34px 20px 26px; text-align: center; background: #0e1629; }
.pr.rec { border-color: #c9a24b; background: linear-gradient(160deg, #2a2618, #0e1629); }
.pr-top { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #c9a24b; color: #0a1226; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; padding: 5px 14px; border-radius: 999px; white-space: nowrap; }
.pr-n { font: 700 18px 'Liberation Serif', serif; color: #e7e7ea; }
.pr-h { margin-top: 20px; font: 700 50px 'Liberation Serif', serif; color: #e9d18f; line-height: 1; }
.pr-h small { display: block; margin-top: 4px; font: 400 14px 'Liberation Sans', Arial; color: #a49f8e; }
.pr-s { margin: 24px 0 0; padding-top: 20px; border-top: 1px solid #1d2744; }
.pr-s b { display: block; font: 700 34px 'Liberation Serif', serif; color: #fff; line-height: 1; }
.pr-s span { color: #a49f8e; font-size: 14px; }
.pr-p { margin-top: 16px; color: #7d7f8a; font-size: 13px; }
.pr-foot { margin-top: 30px; text-align: center; color: #a49f8e; font-size: 14px; }
.ocp h2 { margin-top: 14px; }
.ocp .rule { margin: 18px 0 24px; }
.ocs { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 22px; }
.oc { border: 1px solid #2a3350; border-radius: 16px; padding: 20px 22px 18px; background: #0e1629; }
.oc.b { border-color: #3a5a96; background: linear-gradient(160deg, #15264a, #0e1629); }
.oc:not(.b) { border-color: #9c8550; background: linear-gradient(160deg, #2a2618, #0e1629); }
.oc-t { display: flex; gap: 12px; align-items: center; }
.oc-t span { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font: italic 700 18px 'Liberation Serif', serif; background: linear-gradient(135deg, #f6e2a6, #c9a24b); color: #0a1226; }
.oc.b .oc-t span { background: #3a7bd5; color: #fff; }
.oc-t b { display: block; font: 700 18px 'Liberation Serif', serif; }
.oc-t small { color: #a49f8e; font-size: 12.5px; }
.oc-h { margin: 14px 0 2px; font: 700 40px 'Liberation Serif', serif; color: #e9d18f; line-height: 1; }
.oc.b .oc-h { color: #8fb8ec; }
.oc-h small { font: 400 14px 'Liberation Sans', Arial; color: #a49f8e; margin-left: 4px; }
.oc-p { color: #a49f8e; font-size: 14px; padding-bottom: 12px; border-bottom: 1px solid #1d2744; }
.oc-p b { color: #fff; font: 700 20px 'Liberation Serif', serif; }
.oc-s { margin: 12px 0 5px; font-size: 10.5px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #7d7f8a; }
.oc-l { list-style: none; } .oc-l li { color: #c9c9cf; font-size: 13px; line-height: 1.35; margin: 3px 0; }
.oc-l li::before { content: "✓"; color: #7fcfa0; margin-right: 7px; }
.oc-e { color: #c9c9cf; font-size: 13px; line-height: 1.4; }
.oc-inc { margin-top: 14px; display: flex; gap: 10px; align-items: center; border: 1px solid #2a3350; border-radius: 12px; padding: 10px 16px; background: #0b1326; }
.oc-inc i { font-style: normal; color: #7fcfa0; font-weight: 700; } .oc-inc span { color: #c9c9cf; font-size: 13px; }
.oc-mas { margin-top: 10px; border: 1px dashed #9c8550; border-radius: 12px; padding: 10px 16px; background: #14161f; }
.oc-mas b { display: block; font: 700 14px 'Liberation Serif', serif; color: #e9d18f; } .oc-mas span { color: #a49f8e; font-size: 12.5px; }
.oc-mas.alt { border-color: #3a5a96; } .oc-mas.alt b { color: #8fb8ec; }
.rzs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 22px; }
.rz { border: 1px solid #2a3350; border-radius: 14px; padding: 16px 18px; background: #0e1629; }
.rz b { display: block; font-size: 10.5px; letter-spacing: 0.12em; text-transform: uppercase; color: #8fb8ec; }
.rz strong { display: block; margin: 6px 0 4px; font: 700 24px 'Liberation Serif', serif; color: #e9d18f; }
.rz span { color: #a49f8e; font-size: 12.5px; line-height: 1.35; }
.cmpx { margin-top: 16px; border: 1px solid #2a3350; border-radius: 14px; padding: 14px 20px 10px; background: #0e1629; }
.cx { display: grid; grid-template-columns: 150px 1fr 80px; gap: 12px; align-items: center; margin: 7px 0; }
.cx span { color: #e7e7ea; font-size: 13.5px; font-weight: 700; }
.cx div { height: 14px; border-radius: 8px; background: #141d35; overflow: hidden; } .cx i { display: block; height: 100%; border-radius: 8px; }
.cx i.bono { background: linear-gradient(90deg, #c9a24b, #e9d18f); } .cx i.base { background: #56709e; }
.cx em { font-style: normal; text-align: right; color: #e7e7ea; font-weight: 700; font-size: 13.5px; }
.cmpx p { color: #7fcfa0; font-size: 13px; font-weight: 700; margin-top: 6px; }
.rps2 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 14px; }
.rp2 { display: flex; gap: 10px; align-items: center; border: 1px solid #2a3350; border-radius: 12px; padding: 10px 14px; background: #0b1326; }
.rp2 em { flex: none; width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font: italic 700 14px 'Liberation Serif', serif; background: #1a2d52; color: #8fb8ec; }
.rp2 span { color: #c9c9cf; font-size: 12.5px; line-height: 1.3; }
.pasosp .who { margin-bottom: 10px; }
.pasosp h2 { margin-top: 10px; }
.paso1 { display: grid; grid-template-columns: 56px 1fr auto; gap: 18px; align-items: center; margin-top: 22px; border: 1px solid #c9a24b; border-radius: 16px; padding: 18px 24px; background: linear-gradient(160deg, #2a2618, #0e1629); }
.pnum { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font: italic 700 24px 'Liberation Serif', serif; background: linear-gradient(135deg, #f6e2a6, #c9a24b); color: #0a1226; }
.pnum.s { width: 40px; height: 40px; font-size: 20px; background: #1a2d52; color: #8fb8ec; }
.p1t small, .paso2h small { display: block; font-size: 10.5px; font-weight: 700; letter-spacing: 0.14em; color: #e9d18f; }
.p1t b { display: block; font: 700 22px 'Liberation Serif', serif; margin: 3px 0 4px; }
.p1t span { color: #a49f8e; font-size: 13px; line-height: 1.35; }
.p1p { text-align: right; }
.p1p s { display: block; color: #7d7f8a; font-size: 14px; }
.p1p b { display: block; font: 700 40px 'Liberation Serif', serif; color: #e9d18f; line-height: 1.05; }
.p1p span { color: #a49f8e; font-size: 12px; }
.paso2h { display: flex; gap: 14px; align-items: center; margin-top: 26px; }
.paso2h small { color: #8fb8ec; }
.paso2h b { font: 700 19px 'Liberation Serif', serif; }
.pasosp .bxs { margin-top: 22px; }
.extra-t { display: flex; gap: 12px; align-items: center; margin-top: 14px; border: 1px dashed #9c8550; border-radius: 12px; padding: 11px 16px; background: #14161f; }
.extra-t i { flex: none; width: 14px; height: 14px; border-radius: 50%; background: linear-gradient(135deg, #f6e2a6, #c9a24b); }
.extra-t b { display: block; font: 700 14.5px 'Liberation Serif', serif; color: #e9d18f; }
.extra-t span { color: #a49f8e; font-size: 12.5px; }
.rps { margin-top: 12px; display: grid; gap: 8px; }
.rpf { display: grid; grid-template-columns: 130px 1fr; align-items: center; gap: 10px; }
.rpf em { font-style: normal; color: #e7e7ea; font: 700 13px 'Liberation Sans', Arial; }
.rpb { display: flex; gap: 4px; }
.rpc { border-radius: 8px; padding: 6px 10px; border: 1px solid; display: flex; justify-content: space-between; align-items: center; min-width: 0; }
.rpc b { font: 700 12px 'Liberation Sans', Arial; white-space: nowrap; overflow: hidden; }
.rpc span { font-size: 12px; font-weight: 700; margin-left: 6px; }
.semp .foot { margin-top: 16px; }
.bxs { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin-top: 30px; }
.bx { position: relative; border: 1px solid #2a3350; border-radius: 16px; padding: 24px 24px 20px; background: #0e1629; }
.bx.star { border-color: #c9a24b; background: linear-gradient(160deg, #2a2618, #0e1629); }
.bx-top { position: absolute; top: -12px; left: 22px; background: #c9a24b; color: #0a1226; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; padding: 5px 12px; border-radius: 999px; }
.bx-h { display: flex; align-items: baseline; gap: 8px; }
.bx-h b { font: 700 40px 'Liberation Serif', serif; }
.bx-h span { color: #a49f8e; font-size: 14px; }
.bx-p { font: 700 30px 'Liberation Serif', serif; color: #e7e7ea; margin: 4px 0 14px; }
.bx-p small { font: 400 13px 'Liberation Sans', Arial; color: #a49f8e; margin-left: 4px; }
.bx-hora { display: grid; grid-template-columns: auto 1fr auto; align-items: baseline; gap: 10px; padding: 10px 0; border-top: 1px solid #1d2744; }
.bx-hora b { font: 700 32px 'Liberation Serif', serif; color: #e9d18f; }
.bx-hora.ex b { font-size: 22px; color: #8fb8ec; }
.bx-hora span { color: #a49f8e; font-size: 13px; }
.bx-hora em { font-style: normal; background: #1f4a37; color: #7fcfa0; font-weight: 700; font-size: 15px; padding: 4px 10px; border-radius: 999px; }
.bx-ah { margin-top: 8px; color: #a49f8e; font-size: 13px; } .bx-ah b { color: #7fcfa0; }
.base-l { margin-top: 14px; color: #7d7f8a; font-size: 12.5px; } .base-l b { color: #e7e7ea; }
.dash.ej { margin-top: 14px; } .dash.ej li { font-size: 14px; } .dash.ej b { color: #e9d18f; }
.cmpbox { margin-top: 18px; border: 1px solid #2a3350; border-radius: 14px; padding: 14px 20px 12px; background: #0e1629; }
.cmp-h { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px; }
.cmp-h b { font: 700 16px 'Liberation Serif', serif; } .cmp-h span { color: #7d7f8a; font-size: 12px; }
.cr { display: grid; grid-template-columns: 1fr 1fr 1fr; padding: 4px 0; border-top: 1px solid #1d2744; font-size: 13px; }
.cr span { color: #a49f8e; font-weight: 700; }
.cr em { font-style: normal; text-align: center; color: #7d7f8a; }
.cr em.w { color: #7fcfa0; font-weight: 700; }
.cr.hd { border-top: 0; } .cr.hd em { color: #8fb8ec; font-weight: 700; font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; }
.cmpbox p { color: #7d7f8a; font-size: 11.5px; margin-top: 6px; }
.tray h2 { margin-top: 16px; }
.tray .rule { margin: 18px 0 24px; }
.tbox { margin-top: 18px; border: 1px solid #2a3350; border-radius: 16px; padding: 14px 0 12px; background: #0b1326; }
.tsvg { display: block; margin: 0 auto; overflow: visible; }
.tsvg .ax { fill: #56607a; font: 700 10px 'Liberation Sans', Arial; letter-spacing: 0.14em; }
.tsvg .th2 { fill: #e7e7ea; font: 700 12px 'Liberation Sans', Arial; }
.tsvg .tm { fill: #e9d18f; font: 700 20px 'Liberation Serif', serif; }
.tbands { display: grid; gap: 6px; padding: 8px 16px 0; }
.tb { border: 1px solid; border-radius: 10px; padding: 7px 7px; display: flex; align-items: baseline; gap: 5px; min-width: 0; }
.tb em { font: italic 700 16px 'Liberation Serif', serif; }
.tb b { font: 700 11px 'Liberation Sans', Arial; color: #e7e7ea; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tbox .mlab { margin: 8px 16px 0; }
.tcards { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-top: 16px; }
.tcd { border: 1px solid #2a3350; border-radius: 12px; padding: 12px 14px; background: #0e1629; }
.tcd em { font: italic 700 22px 'Liberation Serif', serif; }
.tcd b { display: block; font: 700 14.5px 'Liberation Serif', serif; margin: 4px 0 3px; }
.tcd p { color: #a49f8e; font-size: 12px; line-height: 1.3; }
.tray .foot { margin-top: 18px; }
.bd em .hh2 { text-transform: none; font-size: 10px; }
.mleg { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 16px; }
.ml { display: flex; align-items: center; gap: 8px; border: 1px solid #2a3350; border-radius: 12px; padding: 10px 12px; background: #0e1629; }
.ml i { flex: none; width: 14px; height: 14px; border-radius: 4px; }
.ml i.s0 { background: #b8964c; } .ml i.s1 { background: #2e5ea8; } .ml i.s2 { background: #6a7a9c; } .ml i.s3 { background: #3f8a64; } .ml i.s4 { background: #e9d18f; }
.ml b { font: 700 13.5px 'Liberation Serif', serif; flex: 1; }
.ml span { color: #e9d18f; font-size: 12.5px; font-weight: 700; }
.rwrap.q { padding: 34px 30px 26px; }
.qhero { display: grid; grid-template-columns: 1.1fr 1fr 1fr; gap: 16px; }
.qhero > div { border: 1px solid #2a3350; border-radius: 12px; padding: 16px 18px; background: #0e1629; }
.qhero b { display: block; font: 700 34px 'Liberation Serif', serif; color: #e9d18f; }
.qhero b small { font: 400 14px 'Liberation Sans', Arial; color: #a49f8e; margin-left: 3px; }
.qhero span { color: #a49f8e; font-size: 13px; }
.cmps { margin-top: 24px; }
.cmp { display: grid; grid-template-columns: 170px 1fr 92px 50px; align-items: center; gap: 12px; margin: 10px 0; }
.cl { color: #e7e7ea; font-size: 14px; font-weight: 700; }
.ct { height: 14px; border-radius: 8px; background: #141d35; overflow: hidden; }
.ct i { display: block; height: 100%; border-radius: 8px; }
.ct i.base { background: #56607a; } .ct i.bono { background: linear-gradient(90deg, #c9a24b, #e9d18f); } .ct i.extra { background: linear-gradient(90deg, #5b8ee0, #8fb8ec); }
.cv { text-align: right; color: #e7e7ea; font-size: 14px; font-weight: 700; }
.dto { color: #7fcfa0; font-size: 13px; font-weight: 700; }
.ejemplo { margin-top: 18px; border-top: 1px dashed #5d5438; padding-top: 14px; color: #a49f8e; font-size: 14px; }
.ejemplo b { color: #e9d18f; }
.escs { margin-top: 26px; display: grid; gap: 14px; }
.esc { display: grid; grid-template-columns: 110px 1fr 200px; gap: 20px; align-items: center; border: 1px solid #2a3350; border-radius: 14px; padding: 16px 20px; background: #0e1629; }
.esc.top { border-color: #9c8550; background: linear-gradient(160deg, #2a2618, #0e1629); }
.eh b { display: block; font: 700 30px 'Liberation Serif', serif; }
.eh span { color: #a49f8e; font-size: 12.5px; }
.ebr { display: grid; grid-template-columns: 96px 1fr 60px; gap: 10px; align-items: center; margin: 5px 0; }
.ebr span { color: #a49f8e; font-size: 12.5px; }
.ebr div { height: 12px; border-radius: 7px; background: #141d35; overflow: hidden; }
.ebr i { display: block; height: 100%; border-radius: 7px; }
.ebr i.base { background: #56607a; } .ebr i.bono { background: linear-gradient(90deg, #c9a24b, #e9d18f); }
.ebr em { font-style: normal; text-align: right; color: #e7e7ea; font-size: 13px; font-weight: 700; }
.ea { text-align: right; }
.ea b { display: block; font: 700 30px 'Liberation Serif', serif; color: #7fcfa0; }
.esc.top .ea b { font-size: 36px; }
.ea span { display: block; color: #e7e7ea; font-size: 13px; font-weight: 700; }
.ea small { display: block; color: #7d7f8a; font-size: 11.5px; margin-top: 2px; }
"""


def main():
    global LOGO_URI
    src = Path(sys.argv[1])
    d = json.loads(src.read_text(encoding="utf-8"))
    LOGO_URI = "data:image/png;base64," + base64.b64encode(LOGO.read_bytes()).decode()
    t = textos(d)
    t.update(d.get("textos", {}))  # ajustes de texto específicos del lead
    tf = TARIFAS[d["etapa"]]
    for m in d["modalidades_recomendadas"]:
        assert m in tf["precios"], f"La etapa {d['etapa']} no tiene modalidad {m}"
    pages = [page_cover(d, t)] + ([page_semana(d, t)] if d.get("semana") else []) \
        + ([page_trayectoria(d, t)] if d.get("trayectoria") else []) \
        + ([page_mes(d, t)] if d.get("mes_ejemplo") else []) \
        + ([page_ciclos(d, t)] if d.get("ciclos") else []) \
        + ([page_camino(d, t)] if d.get("camino") else []) \
        + ([page_calendario(d, t)] if d.get("calendario") else []) \
        + ([page_ruta(d, t)] if d.get("ruta") else []) \
        + ([] if d.get("omitir_proceso") else [page_proceso(d, t)]) \
        + ([] if d.get("omitir_informe") else [page_informe(d, t)]) + [page_phones(d, t)]
    for m in ([] if (d.get("opciones_comp") or d.get("precios_comp") or d.get("dos_tarifas")) else (d.get("tarifas_mostrar") or ("online", "casa_profesor", "casa_alumno"))):
        if m in tf["precios"]:
            pages.append(page_tarifas(d, t, m))
    if d.get("dos_tarifas"):
        pages += [page_dos_tarifas(d, t), page_cierre(d, t)]
    elif d.get("precios_comp"):
        pages += [page_precios(d, t), page_cierre(d, t)]
    elif d.get("opciones_comp"):
        pages += [page_opciones(d, t), page_recomendacion(d, t), page_cierre(d, t)]
    elif d.get("pasos"):
        pages += [page_pasos(d, t), page_resumen_pasos(d, t), page_cierre(d, t)]
    elif d.get("bonos_especiales"):
        pages += [page_bonos_esp(d, t), page_ahorro_esp(d, t), page_resumen_esp2(d, t), page_cierre(d, t)]
    elif d.get("bono_especial"):
        pages += [page_quincenal(d, t), page_ahorro(d, t), page_resumen_esp(d, t), page_cierre(d, t)]
    else:
        pages += [page_bono(d, t), page_resumen(d, t), page_cierre(d, t)]
    doc = f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Plan NEXO — {e(d["nombre"] or d["curso"])}</title><style>{CSS}</style></head><body>{"".join(pages)}</body></html>'
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    # Nombre de archivo: Plan_NEXO_<Nombre>_<Curso>_<Asignaturas> (sin curso, la etapa)
    partes = [d.get("nombre_completo") or d["nombre"], d["curso"] or tf["nombre"]] + d["asignaturas"]
    base = out / ("Plan_NEXO_" + "_".join(re.sub(r"[^\wº]+", "_", x).strip("_") for x in partes if x))
    base.with_suffix(".html").write_text(doc, encoding="utf-8")
    subprocess.run(["node", str(ROOT / "render_pdf.js"), str(base.with_suffix(".html")), str(base.with_suffix(".pdf"))], check=True)
    print(base.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
