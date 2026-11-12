"""Tema claro para los planes: fondo blanco en páginas de contenido; portada y cierre en azul con el logo blanco."""
import base64, re
from pathlib import Path

LOGO_AZUL = "data:image/png;base64," + base64.b64encode((Path(__file__).parent / "logos" / "Logo_NEXO_azul.png").read_bytes()).decode()
NAVY = "#0B1B3A"
BG = {"#0a1226": "#ffffff", "#0b0d18": "#ffffff", "#10214a": "#ffffff", "#0e1629": "#f6f8fc", "#0b1428": "#f1f4fa",
      "#12234a": "#e8eefb", "#16284a": "#eaf0fb", "#13302a": "#e6f4ec", "#3a3322": "#fbf3dc", "#3a2a1c": "#fbeedf",
      "#1d2744": "#e3e8f1", "#2a3350": "#d6dce8", "#172243": "#e6ebf4", "#2a2618": "#fff8e6", "#1a2d52": "#e3ebf8",
      "#1f4a37": "#dff3e8", "#163528": "#e6f4ec", "#5c2f3c": "#fbe6ec", "#3e2029": "#fbe6ec", "#15294f": "#eef3fb",
      "#0c1428": "#ffffff", "#3a3a2c": "#e9dcb4", "#1e3a6e": "#e3ebf8", "#0f1a33": "#f1f4fa", "#2c3d63": "#d6dce8",
      "#0d1b4b": "#e8eefb", "#0b1326": "#f6f8fc", "#14161f": "#fff8e6", "#0a1430": "#f6f8fc", "#e7e7ea": "#1c2433"}
TX = {"#fff": NAVY, "#ffffff": NAVY, "#e7e7ea": "#1c2433", "#a49f8e": "#5b6578", "#c9c6ba": "#3a4558", "#a9b4d0": "#3a4558",
      "#cdd6e6": "#3a4558", "#e9d18f": "#9a7420", "#8fb8ec": "#2a5bb0", "#7fcfa0": "#1f7a4f", "#b5ecc9": "#1f7a4f",
      "#f5c9d5": "#8a2a44", "#6c6f7c": "#8a90a0", "#7d7f8a": "#7d8596", "#cdb57a": "#9a7420", "#c9c9cf": "#3a4558", "#d8d8de": "#3a4558"}

def _rgba_bg(m):
    r, g, b = (int(x) for x in m.group(1, 2, 3))
    if r < 90 and g < 90 and b < 140:
        return "rgba(240,244,250,1)"
    if r > 200 and g > 200 and b > 200:
        return "rgba(11,27,58,0.10)"
    return m.group(0)

def _claro(h):
    h = h.lower()
    if len(h) != 7:
        return None
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    if (r + g + b) / 3 >= 70:
        return None
    k = 0.9
    return "#%02x%02x%02x" % tuple(int(x + (255 - x) * k) for x in (r, g, b))


def _map(val, table, rgba=False):
    val = re.sub(r"#[0-9a-fA-F]{3,6}\b", lambda m: table.get(m.group(0).lower()) or ((_claro(m.group(0)) or m.group(0)) if table is BG else m.group(0)), val)
    if rgba:
        val = re.sub(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)", _rgba_bg, val)
    return val

def _decl(m):
    prop, val = m.group(1), m.group(2)
    p = prop.strip().lower()
    if p == "color":
        val = _map(val, TX)
    elif p in ("fill", "stroke"):
        val = re.sub(r"#[0-9a-fA-F]{3,6}\b", lambda m: TX.get(m.group(0).lower()) or BG.get(m.group(0).lower()) or _claro(m.group(0)) or m.group(0), val)
    elif p.startswith(("background", "border", "box-shadow", "outline")):
        val = _map(val, BG, rgba=True)
    return f"{prop}:{val}"

COVER = """
.page { background: #ffffff !important; }
.page.cover { background: radial-gradient(ellipse 35% 30% at 18% 18%, rgba(90,75,45,0.22), transparent 70%), linear-gradient(160deg, #0b0d18 0%, #0a1226 55%, #10214a 100%) !important; color: #fff; }
.page.cover h1, .page.cover h2, .page.cover .nm { color: #fff; }
.page.cover em, .page.cover h1 em { color: #e9d18f; }
.page.cover .pill.gold { color: #e9d18f; border-color: rgba(233,209,143,0.55); }
.page.cover .cover-sub, .page.cover .contact, .page.cover .cover-foot { color: #a49f8e; }
.page.cover .name-card { background: #0e1629; border-color: #2a3350; }
.page.cover .name-card .nm { color: #e9d18f; } .page.cover .name-card .cs { color: #a49f8e; }
.rule { background: linear-gradient(90deg, transparent, #c9a24b, transparent) !important; opacity: .55; }
.scr, .scr * { }
"""

def aplicar(doc, logo_blanco_uri):
    head, sep, body = doc.partition("</style>")
    css_start = head.index("<style>") + 7
    css = head[css_start:]
    css = re.sub(r"([a-zA-Z-]+)\s*:\s*([^;{}]+)", _decl, css)
    head = head[:css_start] + css + COVER
    # estilos en línea y atributos SVG del cuerpo
    body = re.sub(r'style="([^"]*)"', lambda m: 'style="' + re.sub(r"([a-zA-Z-]+)\s*:\s*([^;]+)", _decl, m.group(1)) + '"', body)
    def _attr(m):
        a, v = m.group(1), m.group(2).lower()
        if a == "fill" and v in TX:
            return f'{a}="{TX[v]}"'
        return f'{a}="{BG.get(v) or _claro(v) or m.group(2)}"'
    body = re.sub(r'(fill|stroke|stop-color)="(#[0-9a-fA-F]{3,6})"', _attr, body)
    body = body.replace(f'class="logo-sm" src="{logo_blanco_uri}"', f'class="logo-sm" src="{LOGO_AZUL}"')
    body = body.replace(f'class="rs-logo" src="{logo_blanco_uri}"', f'class="rs-logo" src="{LOGO_AZUL}"')
    return head + sep + body
