#!/usr/bin/env python3
"""Genera autofacturas NEXO en PDF (A4 vertical) a partir del CSV de clases.
Uso: python3 generar.py [COD_PROFESOR ...]   (sin argumentos: todos)"""
import csv, sys, subprocess, base64, html, collections
from decimal import Decimal as D
from pathlib import Path

AQUI = Path(__file__).parent
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
RET_PCT = 15
PERIODO, ANIO, MES = "septiembre 2026", 2026, 9
FECHA_EMISION = "30/09/2026"        # PENDIENTE DE CONFIRMAR
FORMA_PAGO = "Transferencia"        # PENDIENTE DE CONFIRMAR

# nombre, DNI, domicilio (None = pendiente)
PROFES = {
 "PRO_26_004": ("SOFIA LORENTE JUSTO", None, None),
 "PRO_26_007": ("SANTIAGO MIGUEL PITA", None, None),
 "PRO_26_011": ("NICOLAS SANCHEZ FUENTES", None, None),
 "PRO_26_014": ("PABLO GUTIERREZ VIDAL", None, None),
 "PRO_26_016": ("CARLOS PALENCIA MARTINEZ", None, None),
 "PRO_26_017": ("LAURA GONZALEZ BERNAL", None, None),
 "PRO_26_019": ("JOSSELYN GUAÑO COLCHA", None, None),
 "PRO_26_020": ("ESTHER ANGONO SANCHEZ AKUM", None, None),
 "PRO_26_024": ("LIANYS ORTEGA VIERA", None, None),
}

def eur(c):  # c en céntimos
    s = f"{abs(c)/100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if c < 0 else "") + s + " €"
def horas(h):
    return (f"{h:g}").replace(".", ",")

def cargar():
    d = collections.defaultdict(list)
    for r in csv.DictReader(open(AQUI / "clases_septiembre_2026.csv")):
        h = D(r["horas"]); t = D(r["tarifa"])
        d[r["cod_profesor"]].append(dict(fecha=r["fecha"], curso=r["curso"], mod=r["modalidad"],
                                         h=h, t=t, imp=int(h * t * 100)))
    return d

def pendiente(txt): return f'<span class="pend">{txt}</span>'

def pagina(cod, lineas):
    nombre, dni, dom = PROFES[cod]
    lineas = sorted(lineas, key=lambda l: l["fecha"])
    base = sum(l["imp"] for l in lineas)
    ret = (base * RET_PCT + 50) // 100          # redondeo half-up a céntimo
    neto = base - ret
    filas = ""
    for l in lineas:
        y, m, dd = l["fecha"].split("-")
        desc = f"Clase de {l['curso']}" + (" (online)" if l["mod"] == "Online" else "")
        filas += (f"<tr><td class='f'>{dd}/{m}/{y}</td><td>{desc}</td><td class='n'>{horas(l['h'])}</td>"
                  f"<td class='n'>{eur(int(l['t']*100))}</td><td class='n imp'>{eur(l['imp'])}</td></tr>")
    nfac = f"AF-{ANIO}-{MES:02d}-{cod[-3:]}"
    logo = base64.b64encode((AQUI / "logo_nexo_blanco.png").read_bytes()).decode()
    nh = sum(l["h"] for l in lineas)
    doc = f"""<!doctype html><html lang="es"><meta charset="utf-8"><title>{nfac}</title><style>
@page{{size:A4;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:210mm;height:297mm}}
body{{font-family:'Liberation Sans',Arial,sans-serif;color:#f9f9f9;font-size:10.5px;
 background:radial-gradient(ellipse 90% 70% at 100% 100%,#162c62 0%,rgba(22,44,98,0) 70%),
 linear-gradient(160deg,#0b0d18 0%,#0a101f 55%,#0c1833 100%);
 -webkit-print-color-adjust:exact;print-color-adjust:exact;padding:15mm 15mm 12mm;position:relative}}
.serif{{font-family:'Liberation Serif',Georgia,serif}}
.top{{display:flex;justify-content:space-between;align-items:center;padding-bottom:12px;
 border-bottom:1px solid transparent;border-image:linear-gradient(90deg,rgba(231,207,142,0),#a99669,rgba(231,207,142,0)) 1}}
.top img{{width:118px}}
.tag{{font-weight:700;letter-spacing:.17em;font-size:10px;color:#cbb379;text-transform:uppercase}}
.pill{{display:inline-block;border:1px solid #a99669;border-radius:20px;padding:6px 14px;font-weight:700;
 font-size:9px;letter-spacing:.15em;color:#e7cf8e;text-transform:uppercase}}
h1{{font-family:'Liberation Serif',serif;font-size:31px;margin:16px 0 4px;font-weight:700}}
h1 i{{color:#e7cf8e}}
.sub{{color:#9d9da1;font-size:11.5px}}
.cards{{display:flex;gap:14px;margin-top:18px}}
.card{{flex:1;border:1px solid #32435f;border-radius:14px;padding:13px 15px;background:rgba(11,17,35,.55)}}
.lab{{font-weight:700;letter-spacing:.15em;font-size:8.5px;color:#8db5e9;text-transform:uppercase;margin-bottom:7px}}
.card .nm{{font-family:'Liberation Serif',serif;font-weight:700;font-size:15px;color:#e7cf8e;margin-bottom:5px}}
.card p{{color:#a09b8b;line-height:1.55}}
.pend{{color:#6f6e74;font-style:italic}}
.meta{{display:flex;gap:10px;margin-top:14px}}
.meta div{{flex:1;border:1px solid #32435f;border-radius:12px;padding:9px 12px;text-align:center}}
.meta b{{display:block;font-size:12.5px;font-family:'Liberation Serif',serif;color:#e7cf8e;margin-top:3px}}
.meta span{{font-size:8px;letter-spacing:.15em;color:#8db5e9;font-weight:700;text-transform:uppercase}}
table{{width:100%;border-collapse:collapse;margin-top:16px;border:1px solid #32435f;border-radius:14px;overflow:hidden}}
th{{background:rgba(141,181,233,.10);color:#8db5e9;font-size:8.5px;letter-spacing:.15em;text-transform:uppercase;
 padding:9px 12px;text-align:left}}
th.n,td.n{{text-align:right}}
td{{padding:6.5px 12px;border-top:1px solid rgba(50,67,95,.55);color:#d6d4cf}}
td.f{{color:#a09b8b;width:78px}} td.imp{{color:#fff;font-weight:700}}
.tot{{display:flex;gap:10px;margin-top:14px}}
.tot div{{flex:1;border:1px solid #32435f;border-radius:12px;padding:10px 12px}}
.tot span{{display:block;font-size:8px;letter-spacing:.14em;color:#8db5e9;font-weight:700;text-transform:uppercase;margin-bottom:5px}}
.tot b{{font-family:'Liberation Serif',serif;font-size:15px}}
.tot .big{{border-color:#a99669;background:rgba(231,207,142,.07)}} .tot .big b{{color:#e7cf8e;font-size:18px}}
.foot{{position:absolute;left:15mm;right:15mm;bottom:12mm;border-top:1px solid #2a3350;padding-top:9px;
 display:flex;justify-content:space-between;color:#7b7d86;font-size:10px}}
</style><body>
<div class="top"><img src="data:image/png;base64,{logo}"><div class="tag">Justificante mensual</div></div>
<h1>Autofactura <i>{PERIODO}</i></h1>
<div class="sub">Servicios de docencia prestados a NEXO Académico durante el periodo indicado.</div>
<div class="cards">
 <div class="card"><div class="lab">De · Profesor/a</div><div class="nm">{html.escape(nombre.title())}</div>
  <p>DNI: {dni or pendiente('pendiente')}<br>{dom or pendiente('Domicilio pendiente')}</p></div>
 <div class="card"><div class="lab">Para · Empresa</div><div class="nm">NEXO Académico</div>
  <p>{pendiente('Razón social, CIF y domicilio pendientes')}</p></div>
</div>
<div class="meta">
 <div><span>Emisor</span><b>{cod}</b></div><div><span>Nº Autofactura</span><b>{nfac}</b></div>
 <div><span>Fecha</span><b>{FECHA_EMISION}</b></div><div><span>Forma de pago</span><b>{FORMA_PAGO}</b></div></div>
<table><thead><tr><th>Fecha</th><th>Descripción</th><th class="n">Horas</th><th class="n">Tarifa/h</th><th class="n">Importe</th></tr></thead>
<tbody>{filas}</tbody></table>
<div class="tot">
 <div><span>Horas totales</span><b>{horas(nh)} h</b></div>
 <div><span>Base retención</span><b>{eur(base)}</b></div>
 <div><span>Retención {RET_PCT}%</span><b>{eur(-ret)}</b></div>
 <div><span>IVA</span><b>—</b></div>
 <div class="big"><span>Total a percibir</span><b>{eur(neto)}</b></div></div>
<div class="foot"><span>Nexo Académico · Autofactura {nfac}</span><span>nexoacademico.com</span></div>
</body></html>"""
    return nfac, base, ret, neto, doc

def main():
    datos = cargar()
    sel = sys.argv[1:] or sorted(datos)
    for cod in sel:
        nfac, base, ret, neto, doc = pagina(cod, datos[cod])
        h = AQUI / f"{nfac}.html"; h.write_text(doc, encoding="utf-8")
        pdf = AQUI / f"{nfac}_{PROFES[cod][0].replace(' ', '_')}.pdf"
        subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", h.as_uri()], check=True, capture_output=True)
        h.unlink()
        print(f"{nfac} {PROFES[cod][0]:30s} base {base/100:8.2f} ret {ret/100:6.2f} neto {neto/100:8.2f} -> {pdf.name}")
main()
