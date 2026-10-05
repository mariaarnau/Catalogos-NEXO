#!/usr/bin/env python3
"""Genera el informe mensual de un alumno de Nexo Académico en PDF.

Uso:  python3 generar_informe.py datos.json [salida.pdf]

Estructura: la del informe de ejemplo (resumen, bloque por asignatura,
conclusiones, evolución, próximo mes, propuesta).
Estética: la de los Planes NEXO (fondo azul marino, dorado, titulares serif).
"""
import base64, calendar, datetime as dt, html, json, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).parent
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
MESES = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
TENDENCIA = {"sube": ("▲", "#7fcfa0"), "baja": ("▼", "#e58a7b"),
             "estable": ("■", "#8fb8ec"), "irregular": ("●", "#e9d18f"), "inicial": ("◆", "#8fb8ec")}
ACCION = {"MANTENER": "#8fb8ec", "CONSOLIDAR": "#7fcfa0", "REFORZAR": "#e9d18f",
          "AUMENTAR": "#e9d18f", "REDUCIR": "#a49f8e", "AÑADIR": "#c3a6ec", "AVANZAR": "#7fcfa0", "ORGANIZAR": "#c3a6ec"}
EJEMPLO = False

e = lambda s: html.escape(str(s))


def horas(h):
    h = float(h)
    return f"{int(h)}h" if h == int(h) else f"{h:g}h".replace(".", ",")


def hm(h):
    m = int(float(h) * 60 + 0.5)
    if m < 60:
        return f"{m} min"
    return f"{m // 60}h {m % 60:02d}m" if m % 60 else f"{m // 60}h"


def fecha_larga(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.day} de {MESES[d.month]} de {d.year}"


def kpi(valor, etiqueta):
    return f'<div class="kpi"><b>{e(valor)}</b><span>{e(etiqueta)}</span></div>'


def lista(items, marca="—"):
    return "".join(f'<li><i>{marca}</i><span>{e(t)}</span></li>' for t in items)


def bloque(titulo, items, cls, numerar=False):
    if not items:
        return ""
    lis = "".join(
        f'<li><i>{n if numerar else "—"}</i><span>{e(t)}</span></li>'
        for n, t in enumerate(items, 1))
    return f'<div class="bl {cls}"><h4>{titulo}</h4><ul>{lis}</ul></div>'


def pag(cuerpo, cabecera=None, logo=""):
    cab = cabecera or ("INFORME DE SEGUIMIENTO · EJEMPLO" if EJEMPLO else "INFORME DE SEGUIMIENTO")
    pie = "Nexo Académico · Informe de ejemplo · Datos ficticios" if EJEMPLO else "Nexo Académico · Informe personalizado"
    return f"""<section class="page"><header><img src="{logo}"><em>{cab}</em></header>
<div class="rule"></div>{cuerpo}
<footer><span>{pie}</span><span>nexoacademico.com</span></footer></section>"""


def calendario(anio, mes, sesiones, examenes, hoy, extra=(), festivos=()):
    ses = {dt.date.fromisoformat(s) for s in sesiones}
    exa = {dt.date.fromisoformat(x["fecha"]) for x in examenes}
    ext = {dt.date.fromisoformat(x) for x in extra}
    fes = {dt.date.fromisoformat(x) for x in festivos}
    filas = "".join(f"<th>{d}</th>" for d in "LMXJVSD")
    celdas = ""
    for sem in calendar.Calendar(0).monthdatescalendar(anio, mes):
        celdas += "<tr>"
        for d in sem:
            if d.month != mes:
                celdas += "<td></td>"
                continue
            c = "exa" if d in exa else "ext" if d in ext else "fes" if d in fes else "ses" if d in ses else "hoy" if d == hoy else ""
            celdas += f'<td class="{c}">{d.day}</td>'
        celdas += "</tr>"
    return (f'<table class="cal"><tr>{filas}</tr>{celdas}</table>'
            '<p class="leyenda"><b class="l1"></b> Sesión &nbsp; '
            + ('<b class="l4"></b> Sesión extra de tarde &nbsp; ' if ext else '')
            + '<b class="l2"></b> Examen &nbsp; '
            + ('<b class="l5"></b> Festivo &nbsp; ' if fes else '')
            + '<b class="l3"></b> Fecha de este informe</p>')


NIVELES = ["No entendido", "Con dificultad", "Bien", "Con soltura"]
COLORES = {"blue": "#8fb8ec", "green": "#7fcfa0", "gold": "#e9d18f", "purple": "#c3a6ec"}


def curva(pts, ymin, ymax):
    """Curva suave (Catmull-Rom a Bézier) por los puntos, sin salirse del rango vertical."""
    if len(pts) < 2:
        return ""
    r = lambda v: min(max(v, ymin), ymax)
    t = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[i - 1] if i else pts[i], pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else pts[i + 1]
        t += (f" C{p1[0]+(p2[0]-p0[0])/6:.1f},{r(p1[1]+(p2[1]-p0[1])/6):.1f}"
              f" {p2[0]-(p3[0]-p1[0])/6:.1f},{r(p2[1]-(p3[1]-p1[1])/6):.1f} {p2[0]:.1f},{p2[1]:.1f}")
    return t


def grafica_comprension(items, color, uid, w=330, h=262):
    L, R, T, B = 88, 14, 48, 34
    ancho, n = w - L - R, len(items)
    k = 0
    while k < n and items[k]["v"] is None:
        k += 1
    T = 48 if k else 30
    x = lambda i: L + ancho * (i + 0.5) / n
    y = lambda v: T + (h - T - B) * (1 - v / 3)
    o = [f'<defs><linearGradient id="a{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{color}" stop-opacity=".38"/>'
         f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>'
         f'<pattern id="h{uid}" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         f'<line x1="0" y1="0" x2="0" y2="6" stroke="rgba(255,255,255,.16)" stroke-width="2"/></pattern></defs>']
    k = 0
    while k < n and items[k]["v"] is None:
        k += 1
    if k:
        o.append(f'<rect x="{L}" y="{T-30}" width="{ancho*k/n:.1f}" height="{h-T-B+30}" rx="4" fill="url(#h{uid})" stroke="rgba(255,255,255,.18)" stroke-dasharray="3 3"/>'
                 f'<text x="{L+ancho*k/n/2:.1f}" y="{T-13}" text-anchor="middle" class="ax">{"Iniciación · sin valorar" if k >= 3 else "Sin valorar"}</text>')
    for v, nom in enumerate(NIVELES):
        o.append(f'<line x1="{L}" x2="{w-R}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="gl"/>'
                 f'<text x="{L-8}" y="{y(v)+3:.1f}" text-anchor="end" class="ax">{nom}</text>')
    pts = [(x(i), y(it["v"])) for i, it in enumerate(items) if it["v"] is not None]
    c = curva(pts, y(3), y(0))
    if c:
        o.append(f'<path d="{c} L{pts[-1][0]:.1f},{y(0):.1f} L{pts[0][0]:.1f},{y(0):.1f} Z" fill="url(#a{uid})"/>'
                 f'<path d="{c}" fill="none" stroke="{color}" stroke-width="9" stroke-opacity=".14" stroke-linecap="round"/>'
                 f'<path d="{c}" fill="none" stroke="{color}" stroke-width="2.6" stroke-linecap="round"/>')
    for px, py in pts:
        o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.5" fill="#0a1226" stroke="{color}" stroke-width="2.5"/>')
    for i, it in enumerate(items):
        o.append(f'<text x="{x(i):.1f}" y="{h-B+17}" text-anchor="middle" class="ax">{e(it["e"])}</text>')
    return f'<svg viewBox="0 0 {w} {h}" width="100%">{"".join(o)}</svg>'


def portada(d, logo, mes_txt, tot_ses, tot_h):
    profes = [d["profesor_completo"]] if d.get("profesor_completo") else list(dict.fromkeys(a.get("profesor_completo", a["profesor"]) for a in d["asignaturas"]))
    curso = f'<p class="ccurso">{e(d["curso"])}</p>' if d.get("curso") else ""
    tarjetas = ""
    alto = 262 if len(d["asignaturas"]) <= 2 else (176 if len(d["asignaturas"]) == 4 else 190)
    for n, a in enumerate(d["asignaturas"]):
        items = a.get("comprension_por_sesion")
        if not items:
            continue
        col = COLORES.get(a.get("color", "blue"), "#8fb8ec")
        val = [i["v"] for i in items if i["v"] is not None]
        lectura = a.get("lectura_portada") or (" → ".join(NIVELES[v] for v in val) if len(val) <= 4
                   else f"«Bien» o mejor en {sum(v >= 2 for v in val)} de {len(val)} sesiones")
        ancha = len(d["asignaturas"]) % 2 == 1 and len(d["asignaturas"]) > 1 and n == len(d["asignaturas"]) - 1
        tarjetas += (f'<div class="cc{" wide" if ancha else ""}"><div class="cch"><b style="color:{col}">{e(a["nombre"])}</b>'
                     f'<span>{horas(a["horas"])} · {a["sesiones"]} sesiones</span></div>'
                     f'<p class="ccs">{e(d.get("comprension_sub", "Comprensión del tema, sesión a sesión"))}</p>'
                     f'{grafica_comprension(items, col, n, w=680 if ancha else 330, h=alto)}<p class="ccl" style="color:{col}">{e(lectura)}</p></div>')
    return f"""<section class="page cover{' c4' if len(d['asignaturas']) > 2 else ''}"><img class="clogo" src="{logo}">
<div class="pill">{"INFORME DE EJEMPLO · DATOS FICTICIOS" if d.get("ejemplo") else "DOCUMENTO PRIVADO · INFORME MENSUAL"}</div>
<h1 class="ct">Informe de seguimiento<br><i>{e(mes_txt)}</i></h1>
<div class="ficha"><h2 class="fnom">{e(d['alumno'])}</h2>{curso}
<div class="fgrid">
<div><small>PROFESOR</small><b>{e(' · '.join(profes))}</b></div>
<div><small>ASIGNATURAS</small><b>{e(' · '.join(a['nombre'] for a in d['asignaturas']))}</b></div>
<div><small>PERIODO</small><b>{e(mes_txt)}</b></div>
<div><small>SESIONES Y HORAS</small><b>{tot_ses} sesiones · {horas(tot_h)}</b></div></div></div>
<div class="cgraf">{tarjetas}</div>
<p class="cpie">NEXO ACADÉMICO · INFORME GENERADO EL {e(fecha_larga(d['fecha_informe']).upper())}</p></section>"""


def construir(d):
    global EJEMPLO
    EJEMPLO = bool(d.get("ejemplo"))
    logo = "data:image/png;base64," + base64.b64encode((AQUI / "assets/logo_nexo.png").read_bytes()).decode()
    mes, anio = d["mes"], d["anio"]
    mes_txt = f"{MESES[mes].capitalize()} {anio}"
    sig_mes, sig_anio = (mes % 12) + 1, anio + (mes == 12)
    sig_txt = MESES[sig_mes]
    informe = dt.date.fromisoformat(d["fecha_informe"])
    asigs = d["asignaturas"]
    nombres = " · ".join(a["nombre"] for a in asigs)
    tot_ses = d.get("sesiones_totales") or sum(a["sesiones"] for a in asigs)
    tot_prev = sum(a.get("sesiones_previstas", a["sesiones"]) for a in asigs)
    tot_h = sum(a["horas"] for a in asigs)
    auto = [(x["v"] if isinstance(x, dict) else x) for a in asigs for x in a.get("autonomia_por_sesion", [])]
    auto = [v for v in auto if v is not None]
    paginas = []
    kp = d.get("kpis_portada")
    kp_portada = "".join(kpi(v, l) for v, l in kp) if kp else (
        kpi(tot_ses, 'SESIONES') + kpi(horas(tot_h), 'DEDICADAS')
        + kpi(len(asigs), 'ASIGNATURA' + ('S' if len(asigs) > 1 else ''))
        + kpi(f'{tot_ses}/{tot_prev}', 'ASISTENCIA') + kpi(hm(tot_h/tot_ses), 'DURACIÓN MEDIA'))

    paginas.append(portada(d, logo, mes_txt, tot_ses, tot_h))

    # 1 · Resumen
    def grupo(g):
        return (f'<div class="rs" style="--c:{COLORES.get(g.get("color", "gold"))}"><h4>{e(g["titulo"]).upper()}</h4>'
                + "".join(f"<p>{e(t)}</p>" for t in g["parrafos"]) + "</div>")
    grupos = d.get("resumen_parrafos")
    dos_paginas = bool(grupos) and bool(d.get("resumen_dos_paginas")) and len(grupos) > 1
    if grupos:
        a_pag1 = grupos[:1] if dos_paginas else grupos
        resumen_html = '<div class="rsw%s">' % (" cmp" if len(grupos) > 4 and not dos_paginas else "") + "".join(grupo(g) for g in a_pag1) + "</div>"
    else:
        resumen_html = f'<p class="txt">{e(d["resumen"])}</p>'
    paginas.append(pag(f"""
<div class="pill">INFORME DE SEGUIMIENTO MENSUAL</div>
<h1>{e(d['alumno'])}</h1>
<p class="sub">{e(nombres)} · {mes_txt}</p>
<div class="kpis">{kp_portada}</div>
<div class="card destaque"><small>{e(d.get("etiqueta_progreso", "MAYOR PROGRESO DEL MES"))}</small><p>{e(d['progreso_destacado'])}</p></div>
<h2>Resumen del mes</h2>{resumen_html}""", logo=logo))
    if dos_paginas:
        paginas.append(pag(f"""
<div class="pill">RESUMEN DEL MES</div>
<h1>Asignatura por asignatura</h1>
<div class="rsw" style="margin-top:14px">{"".join(grupo(g) for g in grupos[1:])}</div>""", logo=logo))

    # 2 · Una página por asignatura
    for a in asigs:
        maxh = max(t["horas"] for t in a["temas"])
        temas = "".join(
            f'<div class="tema"><span>{e(t["nombre"])}</span><div class="barra"><i style="width:{t["horas"]/maxh*100:.0f}%"></i></div><b>{horas(t["horas"])}</b></div>'
            for t in a["temas"])
        graf = ""
        if a.get("autonomia_por_sesion"):
            def barra(n, x):
                v, et = (x["v"], x.get("e", f"S{n}")) if isinstance(x, dict) else (x, f"S{n}")
                txt = x.get("t", f"{v}%") if isinstance(x, dict) else f"{v}%"
                if v is None:
                    return f'<div class="col"><b>—</b><div class="hb"><i class="x" style="height:100%"></i></div><span>{e(et)}</span></div>'
                return f'<div class="col"><b>{e(txt)}</b><div class="hb"><i style="height:{v}%;opacity:{0.35+0.65*v/100:.2f}"></i></div><span>{e(et)}</span></div>'
            barras = "".join(barra(n, x) for n, x in enumerate(a["autonomia_por_sesion"], 1))
            sub = a.get("autonomia_sub", "% resuelto solo por sesión")
            nota_g = a.get("autonomia_nota", "Dorado más intenso = mayor autonomía · % = ejercicios resueltos sin ayuda")
            graf = f'<div class="card"><h3>Evolución de autonomía en el mes <small>({e(sub)})</small></h3><div class="cols">{barras}</div><p class="nota">{e(nota_g)}</p></div>'
        ref = ""
        if a.get("refuerzo"):
            ref = f'<div class="bl ref"><h4>REFUERZO RECOMENDADO</h4><p class="nota">El profesor irá marcando las tareas necesarias en cada sesión.</p><ul>{lista(a["refuerzo"], "›")}</ul></div>'
        fila = (f'<div class="dos"><div class="card temas">{temas}</div>{graf}</div>' if graf
                else f'<div class="card temas">{temas}</div>')
        paginas.append(pag(f"""
<div class="pill">{e(a['nombre']).upper()}</div>
<h1>{e(a['nombre'])}</h1><p class="sub">{e(a['profesor'])} · {e(a['horario'])}</p>
<div class="kpis k3">{kpi(horas(a['horas']),'HORAS DEDICADAS')}{kpi(a['sesiones'],'SESIONES TRABAJADAS')}{kpi(hm(a['horas']/a['sesiones']),'MEDIA POR SESIÓN')}</div>
{fila}
<div class="dos">{bloque('PUNTOS FUERTES', a.get('puntos_fuertes'), 'ok')}{bloque('A TENER EN CUENTA', a.get('a_tener_en_cuenta'), 'aten')}</div>
{bloque('PUNTOS A MEJORAR', a.get('puntos_a_mejorar'), 'mej', True)}{ref}""", logo=logo))

    # 3 · Conclusiones + evolución
    kc = kpi(f"{round(sum(auto)/len(auto))}%", "AUTONOMÍA MEDIA") if auto else ""
    n_temas = d.get("temas_trabajados") or sum(len(a["temas"]) for a in asigs)
    kc2 = d.get("kpis_conclusion")
    kp_concl = "".join(kpi(v, l) for v, l in kc2) if kc2 else (
        kc + kpi(horas(tot_h), 'TOTAL DEDICADAS') + kpi(f'{tot_ses}/{tot_prev}', 'SESIONES SIN FALTAR')
        + kpi(n_temas, 'TEMAS TRABAJADOS'))
    evo = ""
    for x in d["evolucion"]:
        s, col = TENDENCIA[x["tendencia"]]
        evo += f'<div class="card ev"><h3>{e(x["titulo"])}</h3><p class="est">{e(x["etiqueta"])} <b style="color:{col}">{s} {e(x["estado"])}</b></p><p class="txt">{e(x["texto"])}</p></div>'
    paginas.append(pag(f"""
<div class="pill">CONCLUSIONES · {mes_txt.upper()}</div>
<h1>Cómo ha ido {MESES[mes]}</h1>
<div class="kpis">{kp_concl}</div>
<p class="txt">{e(d['conclusion'])}</p>
<div class="pill" style="margin-top:22px">EVOLUCIÓN DENTRO DEL MES</div>
<h2>Cómo ha evolucionado a lo largo de {MESES[mes]}</h2>
<p class="nota">{e(d['evolucion_intro'])}</p><div class="evg{' dosc' if len(d['evolucion'])>2 else ''}">{evo}</div>""", logo=logo))

    # 4 · Próximo mes + propuesta
    ex = d["examenes"]
    bloque_ex, dias = "", None
    if ex:
        x = ex[0]
        fx = dt.date.fromisoformat(x["fecha"])
        dias = (fx - informe).days
        if dias >= 0:
            plan = ""
            if d.get("plan_examen"):
                plan = '<h3 style="margin-top:12px">Plan de preparación</h3><div class="pe">' + "".join(
                    f"<div><b>{e(c)}</b><span>{e(t)}</span></div>" for c, t in d["plan_examen"]) + "</div>"
            bloque_ex = f"""<div class="card"><p class="txt"><b>Examen de {e(x['asignatura'])} ({e(x['tema'])}) el {fx.day} de {MESES[fx.month]}</b> — indicado por {e(x['fuente'])}.</p>
<p class="dias"><b>{dias} días</b> desde la fecha de este informe hasta el examen</p>
<h3>Calendario de preparación — {sig_txt} {sig_anio}</h3>
{calendario(sig_anio, sig_mes, d['sesiones_proximo_mes'], ex, informe, d.get('sesiones_extra', []), d.get('festivos', []))}<p class="txt">{e(d['texto_examen'])}</p>{plan}</div>"""
        else:
            bloque_ex = f'<div class="card"><p class="txt"><b>Examen de {e(x["asignatura"])} ({e(x["tema"])}) — {fx.day} de {MESES[fx.month]}</b></p><p class="txt">{e(d["texto_examen"])}</p></div>'
    if not ex and d.get("nota_proximo_mes"):
        bloque_ex = f'<div class="card"><p class="txt">{e(d["nota_proximo_mes"])}</p></div>'
    bc = d.get("base_cientifica")
    base = (f'<div class="card refc"><h3>Base científica de las recomendaciones</h3><p class="nota">{e(bc["texto"])}</p>'
            f'<ol>{"".join(f"<li>{e(r)}</li>" for r in bc["referencias"])}</ol></div>') if bc else ""
    prop = "".join(
        f'<div class="pr"><h4>{e(p["asignatura"])} <em style="color:{ACCION.get(p["accion"], "#e9d18f")};border-color:{ACCION.get(p["accion"], "#e9d18f")}">{e(p["accion"])}</em></h4><p>{e(p["texto"])}</p></div>'
        for p in d["propuesta"] if p["accion"] != "ORGANIZAR")
    extra_org = "".join(
        f'<div class="card"><h3>{e(p["asignatura"])}</h3><p class="txt">{e(p["texto"])}</p></div>'
        for p in d["propuesta"] if p["accion"] == "ORGANIZAR")
    semana = ""
    if d.get("semana_tipo"):
        cols = "".join(
            f'<div class="sd"><h5>{e(dia)}</h5>' + "".join(
                f'<div class="sb" style="--c:{COLORES.get(c, "#e9d18f")}"><b>{e(a)}</b><span>{e(hh)}</span></div>' for a, hh, c in bl) + "</div>"
            for dia, bl in d["semana_tipo"].items())
        semana = f'<div class="card"><h3>Semana tipo</h3><div class="sem">{cols}</div></div>'
    org = f"""<div class="dos"><div><div class="card"><h3>Organización de {MESES[mes]}</h3>{''.join(f'<p class="txt">{e(o)}</p>' for o in d['organizacion_actual'])}</div>{extra_org}</div>
<div class="card"><h3>Propuesta para {sig_txt}</h3>{prop}</div></div>"""
    cierre = f'<p class="nota" style="margin-top:14px">Nexo Académico · Informe generado el {fecha_larga(d["fecha_informe"])}</p>'
    if dias is not None and dias >= 0:
        paginas.append(pag(f"""
<div class="pill">DE CARA A {sig_txt.upper()}</div>
<h1>Qué tener en cuenta el mes que viene</h1>{bloque_ex}{semana}""", logo=logo))
        paginas.append(pag(f"""
<div class="pill">PROPUESTA DE ORGANIZACIÓN</div>
<h1>Cómo organizamos {sig_txt}</h1>{org}{base}{cierre}""", logo=logo))
    else:
        paginas.append(pag(f"""
<div class="pill">DE CARA A {sig_txt.upper()}</div>
<h1>Qué tener en cuenta el mes que viene</h1>{bloque_ex}
<div class="pill" style="margin-top:20px">PROPUESTA DE ORGANIZACIÓN</div>
{org}{semana}{base}{cierre}""", logo=logo))

    css = (AQUI / "estilo.css").read_text()
    return f"<!doctype html><html lang='es'><meta charset='utf-8'><style>{css}</style><body>{''.join(paginas)}</body></html>"


if __name__ == "__main__":
    datos = json.loads(Path(sys.argv[1]).read_text())
    salida = Path(sys.argv[2] if len(sys.argv) > 2 else
                  f"Informe {datos['alumno']} - {MESES[datos['mes']]} {datos['anio']}.pdf")
    h = salida.with_suffix(".html")
    contenido = construir(datos)
    esperadas = contenido.count('<section class="page')
    h.write_text(contenido)
    medir = h.with_name(h.stem + "_medir.html")
    medir.write_text(contenido + """<script>addEventListener('load',()=>{const o=[];
document.querySelectorAll('.page').forEach((p,i)=>{const f=p.querySelector('footer,.cpie');const top=f.getBoundingClientRect().top;let m=0;
[...p.children].forEach(c=>{if(c!==f&&c.tagName!=='HEADER')m=Math.max(m,c.getBoundingClientRect().bottom)});if(m>top-2)o.push(i+1)});
document.body.setAttribute('data-over',o.join(','))})</script>""")
    try:
        dom = subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--virtual-time-budget=3000",
                              "--dump-dom", medir.resolve().as_uri()], capture_output=True, text=True).stdout
        import re
        m = re.search(r'data-over="([0-9,]*)"', dom)
        desbordadas = [x for x in (m.group(1).split(",") if m else []) if x]
    finally:
        medir.unlink()
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={salida}", h.resolve().as_uri()], check=True, capture_output=True)
    h.unlink()
    print("PDF generado:", salida)
    if desbordadas:
        print("AVISO: contenido que invade el pie en las páginas:", ", ".join(desbordadas), "→ revisar o acortar texto")
    try:
        import pymupdf
        n = len(pymupdf.open(salida))
        if n != esperadas:
            print(f"AVISO: {n} páginas en vez de {esperadas}: hay contenido desbordado. Revisar el PDF.")
    except ImportError:
        pass
