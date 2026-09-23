#!/usr/bin/env python3
"""Genera el plan personalizado de NEXO Académico para un lead.

Uso:  python3 planes/generar_plan.py planes/leads/<lead>.json
Salida: planes/output/Plan_NEXO_<Nombre>.html y .pdf
"""
import base64
import calendar
import html
import json
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
    return a[0] if len(a) == 1 else ", ".join(a[:-1]) + " y " + a[-1]


def textos(d):
    n, asig = d["nombre"], lista_asig(d["asignaturas"])
    una = len(d["asignaturas"]) == 1
    if d["voz"] == "tu":
        return dict(
            cover_sub=f"Un acompañamiento diseñado específicamente para ti, {n}, con clases de {asig}.",
            cover_foot="CURSO 2026–2027 — CONDICIONES VÁLIDAS PARA ESTE PLAN",
            p2_title=f"Así te acompañamos cada mes, {n}",
            p2_sub=f"Un profesor especializado en {asig}, con sesiones centradas en {'tu asignatura' if una else 'tus asignaturas'} y ajuste continuo según lo que necesites reforzar.",
            c1=f"Tienes tu profesor de referencia asignado, especializado en {asig}, con horario fijo cada semana.",
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
            su_casa="en tu casa",
            p8_badge=f"BONOS RECOMENDADOS PARA {n.upper()}",
            p9_sub="Tus bonos recomendados, de un vistazo.",
            p9_l1=f"El bono cubre tus clases mensuales de {asig}",
            p9_l2="Sin permanencia: si un mes necesitas menos horas, se ajusta el bono contratado.",
            quote=f"Un plan a medida para acompañarte en {asig}",
            p10_sub="Escríbenos para confirmar tu bono de cada mes o cualquier ajuste de horas.",
        )
    return dict(
        cover_sub=f"Un acompañamiento diseñado específicamente para {n}, con clases de {asig}.",
        cover_foot="CURSO 2026–2027 — CONDICIONES VÁLIDAS PARA ESTA FAMILIA",
        p2_title=f"Así acompañamos a {n} cada mes",
        p2_sub=f"Un profesor especializado en {asig}, con sesiones centradas en {'su asignatura' if una else 'sus asignaturas'} y ajuste continuo según lo que necesite reforzar.",
        c1=f"{n} tiene su profesor de referencia asignado, especializado en {asig}, con horario fijo cada semana.",
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
        su_casa="en su casa",
        p8_badge=f"BONOS RECOMENDADOS DE {n.upper()}",
        p9_sub=f"Los bonos recomendados de {n}, de un vistazo.",
        p9_l1=f"El bono cubre las clases mensuales de {n} de {asig}",
        p9_l2="Sin permanencia: si un mes necesita menos horas, se ajusta el bono contratado.",
        quote=f"Un plan a medida para acompañar a {n} en {asig}",
        p10_sub=f"Escríbenos para confirmar el bono de cada mes o cualquier ajuste de horas de {n}.",
    )


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
  <div class="pill gold">DOCUMENTO PRIVADO · PLAN PERSONALIZADO</div>
  <h1 class="cover-h">Tu plan a medida en<br><em>NEXO Académico</em></h1>
  <p class="cover-sub">{e(t["cover_sub"])}</p>
  <div class="name-card"><div class="nm">{e(d["nombre"])}</div><div class="cs">{e(sub.upper())}</div></div>
  <div class="cover-foot">{e(t["cover_foot"])}</div>
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
  <h2>Un informe real para {e(d["nombre"])}</h2>
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
    r, n = d["informe_ejemplo"], d["nombre"]
    asig = lista_asig(d["asignaturas"])
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
  <div class="s-name l">Comparado con octubre</div><div class="s-sub b">{e(n)} · {e(asig)} — Evolución nota estimada, 4 semanas</div>
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


def page_phones(d, t):
    return f'''<section class="page">
  <div class="hdr"><span class="hdr-l">LOS INFORMES</span></div><div class="rule"></div>
  <div class="pill gold">{e(t["p4_pill"])}</div>
  <h2>El informe, capturado desde el móvil</h2>
  <p class="lead">{e(t["p4_sub"])}</p>
  <div class="phones">{phones(d)}</div>
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


def page_bono(d, t):
    n = d["nombre"]
    bonos, mods = d["bonos_recomendados"], d["modalidades_recomendadas"]
    hs = " u ".join(f"{b['horas']}h" for b in bonos) if len(bonos) > 1 else f"{bonos[0]['horas']}h"
    ms = " o ".join(mod_corto(m, t) for m in mods)
    title = f"Bono{'s' if len(bonos) > 1 else ''} de {hs}, {ms}"
    title = title[0].upper() + title[1:]
    verbo = "haces" if d["voz"] == "tu" else "hace"
    frases = ", o ".join(f"el bono de {b['horas']}h al mes si {verbo} {b['frecuencia']}" if i == 0
                         else f"el de {b['horas']}h si {verbo} {b['frecuencia']}" for i, b in enumerate(bonos))
    lead = f"{t['p8_para']} {frases}. Puedes elegir entre clases {ms}." if d["voz"] == "tu" \
        else f"{t['p8_para']} {frases}. Podéis elegir entre clases {ms}."
    cards = ""
    for b in bonos:
        h = b["horas"]
        rows = ""
        for m in mods:
            c = calc(d, h, m)
            rows += f'''<div class="rrow"><div class="rm">{e(mod_corto(m, t).capitalize())}</div>
  <div class="rp">{eur(c["precio"], 0)}</div>
  <div class="rh">{eur(c["hora"])}/hora</div>
  <div class="rs">Ahorro de {eur(c["ahorro"], 0)} (−{c["pct"]}%) frente a la tarifa base de {eur(c["base"])}/h</div></div>'''
        feats = "".join(f"<li>{e(f)}</li>" for f in FEATURES[h])
        cards += f'''<div class="rcard"><div class="rtop"><b>{h}h</b><span>al mes · {e(b["frecuencia"])}</span></div>
  {rows}<ul class="checks sm">{feats}</ul></div>'''
    return f'''<section class="page">
  <div class="hdr"><span class="hdr-l">PLAN PERSONALIZADO · {e(n.upper())}</span></div><div class="rule"></div>
  <div class="who"><div class="av">{e(n[0])}</div><div><div class="wn">{e(n)}</div><div class="ws">{e((d["curso"] + " · " if d["curso"] else "") + lista_asig(d["asignaturas"]).upper())}</div></div></div>
  <div class="pill gold">{e(t["p8_pill"])}</div>
  <h2>{e(title)}</h2>
  <p class="lead">{e(lead)} Sin permanencia.</p>
  <div class="rwrap"><div class="rbadge">{e(t["p8_badge"])}</div><div class="rgrid">{cards}</div></div>
  {footer()}
</section>'''


def page_resumen(d, t):
    n = d["nombre"]
    rows = ""
    for b in d["bonos_recomendados"]:
        h = b["horas"]
        prices = "".join(f'<div class="sp"><small>{e(mod_corto(m, t).capitalize())}</small><b>{eur(calc(d, h, m)["precio"], 0)}</b></div>'
                         for m in d["modalidades_recomendadas"])
        rows += f'''<div class="srow"><div class="av w">{e(n[0])}</div>
  <div class="st"><b>{e(n)} — Bono de {h}h</b><small>{e(b["frecuencia"])} · {e(lista_asig(d["asignaturas"]))}</small></div>
  <div class="sps">{prices}</div></div>'''
    ms = " o ".join(mod_corto(m, t) for m in d["modalidades_recomendadas"])
    return f'''<section class="page">
  <div class="hdr"><img class="logo-sm" src="{LOGO_URI}"><span class="hdr-r">RESUMEN DEL PLAN</span></div><div class="rule"></div>
  <div class="pill gold">RESUMEN MENSUAL</div>
  <h2>Tu plan, de un vistazo</h2>
  <p class="lead">{e(t["p9_sub"])}</p>
  <div class="srows">{rows}</div>
  <ul class="dash"><li>{e(t["p9_l1"])}, {e(ms)}.</li><li>{e(t["p9_l2"])}</li></ul>
  <div class="quote"><span>"</span><em>{e(t["quote"])}, {e(ms)}.</em></div>
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
.phone { position: relative; height: 415px; background: #1d2747; border-radius: 26px; padding: 11px 10px 12px; }
.notch { position: absolute; top: 11px; left: 50%; transform: translateX(-50%); width: 64px; height: 6px; background: #1d2747; border-radius: 0 0 6px 6px; z-index: 2; }
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
"""


def main():
    global LOGO_URI
    src = Path(sys.argv[1])
    d = json.loads(src.read_text(encoding="utf-8"))
    LOGO_URI = "data:image/png;base64," + base64.b64encode(LOGO.read_bytes()).decode()
    t = textos(d)
    tf = TARIFAS[d["etapa"]]
    for m in d["modalidades_recomendadas"]:
        assert m in tf["precios"], f"La etapa {d['etapa']} no tiene modalidad {m}"
    pages = [page_cover(d, t), page_proceso(d, t), page_informe(d, t), page_phones(d, t)]
    for m in ("online", "casa_profesor", "casa_alumno"):
        if m in tf["precios"]:
            pages.append(page_tarifas(d, t, m))
    pages += [page_bono(d, t), page_resumen(d, t), page_cierre(d, t)]
    doc = f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Plan NEXO — {e(d["nombre"])}</title><style>{CSS}</style></head><body>{"".join(pages)}</body></html>'
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    base = out / f"Plan_NEXO_{d['nombre'].replace(' ', '_')}"
    base.with_suffix(".html").write_text(doc, encoding="utf-8")
    subprocess.run(["node", str(ROOT / "render_pdf.js"), str(base.with_suffix(".html")), str(base.with_suffix(".pdf"))], check=True)
    print(base.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
