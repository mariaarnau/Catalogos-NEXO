"""Generador de la FICHA DEL PROFESOR de Nexo Académico.

Solo usa la librería estándar y Playwright (Python).

Desde otro programa:

    from generar_ficha import generar, generar_imagen, validar

    pdf = generar(datos, foto)            # bytes del PDF (una hoja A4)
    png = generar_imagen(datos, foto)     # bytes del PNG, para enviarlo por WhatsApp
    errores, avisos = validar(datos)      # sin generar nada

    # datos: dict con el formato de esquema_ficha.json
    # foto:  bytes de un JPG, PNG o WEBP, o None (entonces sale un círculo con las iniciales)

Desde la línea de comandos:

    python generar_ficha.py ficha_ejemplo.json [foto.jpg]
    python generar_ficha.py --validar ficha.json

Crea Nombre_Apellido_AAAA.pdf y .png en docs/fichas_profe/salida/. Si no se indica foto, usa el
campo «foto» del JSON (ruta relativa a la carpeta del JSON), y si tampoco hay, las iniciales.

Navegador: por defecto, el Chromium de Playwright. En el ordenador de Nexo, para usar Edge:
    set NEXO_CANAL=msedge        (Windows)    o    export NEXO_CANAL=msedge
Si hay que indicar un ejecutable concreto: NEXO_NAVEGADOR=ruta/al/ejecutable
"""
from __future__ import annotations

import argparse
import base64
import datetime
import html
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

CARPETA = Path(__file__).resolve().parent.parent          # docs/fichas_profe
PLANTILLA = CARPETA / "plantilla_ficha_profe.html"
ESQUEMA = CARPETA / "esquema_ficha.json"
LOGO = CARPETA / "assets" / "logo_nexo.png"
SALIDA = CARPETA / "salida"

ESCALA_MINIMA_AVISO = 0.85   # por debajo, la letra queda pequeña y se avisa para recortar textos
FOTO_MAX_BYTES = 8 * 1024 * 1024

# --------------------------------------------------------------------------------------
# Validación
# --------------------------------------------------------------------------------------

_SENSIBLES = [
    (re.compile(r"\S+@\S+"), "parece un email"),
    (re.compile(r"(?<![\d\w])(?:\+?34[\s.\-]?)?[6789]\d{2}[\s.\-]?\d{3}[\s.\-]?\d{3}(?![\d\w])"), "parece un teléfono"),
    (re.compile(r"(?<![\d\w])(?:\+?34[\s.\-]?)?[6789]\d{2}[\s.\-]\d{2}[\s.\-]\d{2}[\s.\-]\d{2}(?![\d\w])"), "parece un teléfono"),
    (re.compile(r"\b\d{8}[A-Za-z]\b|\b[XYZxyz]\d{7}[A-Za-z]\b"), "parece un DNI o NIE"),
    (re.compile(r"(?<!\d)\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}(?!\d)"), "parece una fecha completa (¿de nacimiento?)"),
    (re.compile(r"https?://|www\.|linkedin|instagram|facebook", re.I), "parece un enlace o una red social"),
    (re.compile(r"\b(DNI|NIE|NIF|pasaporte|nacimiento|nació|nacid[oa]|estado civil|soltero|soltera|casado|casada)\b|\bdomicilio\s*:", re.I),
     "nombra un dato personal sensible"),
    (re.compile(r"\b(calle|c/|avda\.?|avenida|carrer|paseo)\s+\S", re.I), "parece una dirección"),
]
_RAYAS = re.compile("[—–]")
_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]")
_FRASES_HECHAS = [
    "apasionad", "comprometid", "excelencia", "dinámic", "proactiv", "alto nivel", "gran capacidad",
    "excelentes habilidades", "orientad", "amplia experiencia", "sólida trayectoria", "perfil",
    "polifacétic", "mundo de la", "vocación de servicio", "motivad", "trabajo en equipo", "multidisciplinar",
]


def cargar_esquema() -> dict:
    return json.loads(ESQUEMA.read_text(encoding="utf-8"))


def _vacio(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, (list, dict)) and not v)


def _limpiar_texto(v) -> str:
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def _comprobar_texto(valor: str, ruta: str, errores: list, mostrado: bool = True) -> None:
    for patron, motivo in _SENSIBLES:
        if patron.search(valor):
            errores.append(f"{ruta}: {motivo}. Nunca se incluyen datos sensibles. Texto: «{valor[:60]}»")
            break
    if "{{" in valor or "}}" in valor or "<!--" in valor:
        errores.append(f"{ruta}: contiene caracteres reservados de la plantilla.")
    if mostrado:
        if _RAYAS.search(valor):
            errores.append(f"{ruta}: contiene un guion largo (— o –). Usa guion corto (2022-2024) o reescribe la frase.")
        if _EMOJI.search(valor):
            errores.append(f"{ruta}: contiene un emoji.")


def _validar_campo(nombre: str, regla: dict, valor, errores: list, avisos: list, ruta: str, mostrado: bool) -> None:
    tipo = regla["tipo"]
    if tipo == "texto":
        if _vacio(valor):
            if regla.get("obligatorio"):
                errores.append(f"{ruta}: es obligatorio y está vacío.")
            return
        if not isinstance(valor, str):
            errores.append(f"{ruta}: debe ser texto.")
            return
        t = _limpiar_texto(valor)
        if len(t) > regla.get("max", 10**6):
            errores.append(f"{ruta}: {len(t)} caracteres; el máximo es {regla['max']}.")
        if len(t) < regla.get("min", 0):
            errores.append(f"{ruta}: {len(t)} caracteres; el mínimo es {regla['min']}.")
        if "formato" in regla and not re.match(regla["formato"], t):
            errores.append(f"{ruta}: formato no válido («{t}»).")
        _comprobar_texto(t, ruta, errores, mostrado)
    elif tipo == "entero":
        if valor is None or valor == "":
            if regla.get("obligatorio"):
                errores.append(f"{ruta}: es obligatorio.")
            return
        if isinstance(valor, bool) or not isinstance(valor, int):
            errores.append(f"{ruta}: debe ser un número entero o null.")
        elif not regla.get("min", 0) <= valor <= regla.get("max", 10**6):
            errores.append(f"{ruta}: {valor} fuera del rango {regla.get('min')}-{regla.get('max')}.")
    elif tipo == "lista_de_texto":
        if _vacio(valor):
            if regla.get("obligatorio"):
                errores.append(f"{ruta}: es obligatorio y está vacío.")
            return
        if not isinstance(valor, list):
            errores.append(f"{ruta}: debe ser una lista.")
            return
        elementos = [e for e in valor if not _vacio(e)]
        if len(elementos) > regla.get("max_elementos", 10**6):
            errores.append(f"{ruta}: {len(elementos)} elementos; el máximo es {regla['max_elementos']}.")
        for i, e in enumerate(elementos, 1):
            if not isinstance(e, str):
                errores.append(f"{ruta}[{i}]: debe ser texto.")
                continue
            t = _limpiar_texto(e)
            if len(t) > regla.get("max", 10**6):
                errores.append(f"{ruta}[{i}]: {len(t)} caracteres; el máximo es {regla['max']}.")
            _comprobar_texto(t, f"{ruta}[{i}]", errores, mostrado)
    elif tipo == "lista_de_objetos":
        if _vacio(valor):
            if regla.get("obligatorio"):
                errores.append(f"{ruta}: es obligatorio y está vacío.")
            return
        if not isinstance(valor, list):
            errores.append(f"{ruta}: debe ser una lista.")
            return
        elementos = [e for e in valor if not _vacio(e)]
        if len(elementos) < regla.get("min_elementos", 0):
            errores.append(f"{ruta}: necesita al menos {regla['min_elementos']} elemento(s).")
        if len(elementos) > regla.get("max_elementos", 10**6):
            errores.append(f"{ruta}: {len(elementos)} elementos; el máximo es {regla['max_elementos']}.")
        for i, e in enumerate(elementos, 1):
            if not isinstance(e, dict):
                errores.append(f"{ruta}[{i}]: debe ser un objeto.")
                continue
            for sub, sregla in regla["elementos"].items():
                _validar_campo(sub, sregla, e.get(sub), errores, avisos, f"{ruta}[{i}].{sub}", mostrado)
            for extra in set(e) - set(regla["elementos"]):
                errores.append(f"{ruta}[{i}]: campo desconocido «{extra}».")


def validar(datos: dict) -> tuple[list[str], list[str]]:
    """Devuelve (errores, avisos). Con errores no se debe generar la ficha."""
    esquema = cargar_esquema()["campos"]
    errores: list[str] = []
    avisos: list[str] = []
    if not isinstance(datos, dict):
        return ["Los datos deben ser un objeto JSON."], []
    for extra in set(datos) - set(esquema):
        errores.append(f"Campo desconocido «{extra}». Campos válidos: {', '.join(esquema)}.")
    for nombre, regla in esquema.items():
        mostrado = nombre not in ("notas_revision", "foto")
        _validar_campo(nombre, regla, datos.get(nombre), errores, avisos, nombre, mostrado)
    if _vacio(datos.get("experiencia")) and _vacio(datos.get("puntos_fuertes")):
        errores.append("Hace falta contenido en «experiencia» o en «puntos_fuertes» (al menos uno de los dos).")
    pres = _limpiar_texto(datos.get("presentacion"))
    if pres:
        frases = [f for f in re.split(r"(?<=[.!?])\s+", pres) if f]
        if not 2 <= len(frases) <= 4:
            avisos.append(f"presentacion: tiene {len(frases)} frase(s); lo previsto son entre 2 y 4.")
    nombre = _limpiar_texto(datos.get("nombre"))
    if nombre and len(nombre.split()) < 2:
        avisos.append("nombre: debería llevar nombre y primer apellido.")
    mostrados = json.dumps({k: v for k, v in datos.items() if k not in ("notas_revision", "foto")}, ensure_ascii=False).lower()
    for frase in _FRASES_HECHAS:
        if frase in mostrados:
            avisos.append(f"Posible frase hecha o vaga: contiene «{frase}». Revisa que el texto sea concreto.")
    return errores, avisos


def comprobar(datos: dict) -> list[str]:
    """Lanza ValueError con todos los errores; devuelve los avisos."""
    errores, avisos = validar(datos)
    if errores:
        raise ValueError("La ficha no es válida:\n- " + "\n- ".join(errores))
    return avisos


# --------------------------------------------------------------------------------------
# Plantilla
# --------------------------------------------------------------------------------------

_RE_PARA = re.compile(r"<!--PARA (\w+)-->(.*?)<!--/PARA-->", re.S)
_RE_SI = re.compile(r"<!--SI (\w+)-->((?:(?!<!--SI ).)*?)<!--/SI-->", re.S)
_RE_HUECO = re.compile(r"\{\{(\.|\w+)\}\}")


def _esc(v) -> str:
    return html.escape("" if v is None else str(v), quote=True)


def _render(tpl: str, ctx: dict) -> str:
    def para(m):
        elementos = ctx.get(m.group(1)) or []
        salida = []
        for e in elementos:
            sub = {**ctx, **e} if isinstance(e, dict) else {**ctx, ".": e}
            salida.append(_render(m.group(2), sub))
        return "".join(salida)

    tpl = _RE_PARA.sub(para, tpl)
    previo = None
    while previo != tpl:
        previo = tpl
        tpl = _RE_SI.sub(lambda m: m.group(2) if ctx.get(m.group(1)) else "", tpl)
    return _RE_HUECO.sub(lambda m: _esc(ctx.get(m.group(1))), tpl)


def _data_uri(contenido: bytes, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(contenido).decode()}"


def _mime_foto(foto: bytes) -> str:
    if foto[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if foto[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if foto[:4] == b"RIFF" and foto[8:12] == b"WEBP":
        return "image/webp"
    raise ValueError("La foto debe ser un JPG, un PNG o un WEBP.")


def _iniciales(nombre: str) -> str:
    palabras = [p for p in re.split(r"\s+", nombre.strip()) if p]
    return "".join(p[0] for p in palabras[:2]).upper()


def _contexto(datos: dict, foto: bytes | None) -> dict:
    def lista(clave, campos):
        salida = []
        for e in datos.get(clave) or []:
            if _vacio(e):
                continue
            salida.append({c: _limpiar_texto(e.get(c)) for c in campos})
        return salida

    nombre = _limpiar_texto(datos.get("nombre"))
    edad = datos.get("edad")
    meta = " · ".join(x for x in [f"{edad} años" if edad else "", _limpiar_texto(datos.get("modalidad"))] if x)
    ctx = {
        "logo_uri": _data_uri(LOGO.read_bytes(), "image/png"),
        "nombre": nombre,
        "titular": _limpiar_texto(datos.get("titular")),
        "meta": meta,
        "presentacion": _limpiar_texto(datos.get("presentacion")),
        "asignaturas": lista("asignaturas", ["nombre", "niveles"]),
        "formacion": lista("formacion", ["titulo", "centro", "periodo"]),
        "experiencia": lista("experiencia", ["puesto", "lugar", "periodo", "detalle"]),
        "idiomas": lista("idiomas", ["idioma", "nivel", "certificado"]),
        "puntos_fuertes": [_limpiar_texto(p) for p in datos.get("puntos_fuertes") or [] if not _vacio(p)],
        "iniciales": _iniciales(nombre),
        "foto_encuadre": _limpiar_texto(datos.get("foto_encuadre")) or "50% 30%",
        "foto_uri": "",
        "sin_foto": True,
    }
    if foto:
        if len(foto) > FOTO_MAX_BYTES:
            raise ValueError("La foto pesa más de 8 MB; reduce su tamaño.")
        ctx["foto_uri"] = _data_uri(foto, _mime_foto(foto))
        ctx["sin_foto"] = False
    return ctx


def construir_html(datos: dict, foto: bytes | None = None) -> str:
    comprobar(datos)
    return _render(PLANTILLA.read_text(encoding="utf-8"), _contexto(datos, foto))


# --------------------------------------------------------------------------------------
# Navegador
# --------------------------------------------------------------------------------------

def _lanzar(p):
    canal = os.environ.get("NEXO_CANAL")
    ejecutable = os.environ.get("NEXO_NAVEGADOR")
    if canal:
        return p.chromium.launch(channel=canal)
    if ejecutable:
        return p.chromium.launch(executable_path=ejecutable)
    try:
        return p.chromium.launch()
    except Exception:
        for ruta in ("/opt/pw-browsers/chromium",):   # entorno de pruebas en la nube
            if Path(ruta).exists():
                return p.chromium.launch(executable_path=ruta)
        raise


def _producir(datos: dict, foto: bytes | None, pdf: bool, png: bool) -> dict:
    from playwright.sync_api import sync_playwright   # import tardío: validar() no lo necesita

    pagina_html = construir_html(datos, foto)
    resultado: dict = {}
    with sync_playwright() as p:
        navegador = _lanzar(p)
        try:
            pagina = navegador.new_page(viewport={"width": 900, "height": 1200}, device_scale_factor=2)
            pagina.set_content(pagina_html, wait_until="load")
            resultado["escala"] = pagina.evaluate("window.__escala")
            if pdf:
                resultado["pdf"] = pagina.pdf(format="A4", print_background=True, prefer_css_page_size=True)
            if png:
                resultado["png"] = pagina.locator(".ficha").screenshot(type="png")
        finally:
            navegador.close()
    return resultado


def generar(datos: dict, foto: bytes | None = None) -> bytes:
    """PDF de la ficha (una hoja A4) en bytes."""
    return _producir(datos, foto, pdf=True, png=False)["pdf"]


def generar_imagen(datos: dict, foto: bytes | None = None) -> bytes:
    """PNG de la ficha, a doble resolución, para verla bien en WhatsApp."""
    return _producir(datos, foto, pdf=False, png=True)["png"]


def generar_todo(datos: dict, foto: bytes | None = None) -> dict:
    """Devuelve {'pdf': bytes, 'png': bytes, 'escala': float, 'avisos': [str]} con un solo arranque del navegador."""
    avisos = comprobar(datos)
    r = _producir(datos, foto, pdf=True, png=True)
    if r["escala"] < ESCALA_MINIMA_AVISO:
        avisos.append(f"La ficha ha tenido que reducirse al {round(r['escala'] * 100)} % para caber en una hoja: "
                      "acorta algún texto o quita algún elemento para que la letra no quede pequeña.")
    r["avisos"] = avisos
    return r


def nombre_archivo(datos: dict, anio: int | None = None) -> str:
    """Nombre_Apellido_AAAA, sin tildes ni espacios."""
    ascii_ = unicodedata.normalize("NFKD", _limpiar_texto(datos.get("nombre"))).encode("ascii", "ignore").decode()
    palabras = re.findall(r"[A-Za-z0-9]+", ascii_)
    return "_".join([p.capitalize() for p in palabras] + [str(anio or datetime.date.today().year)])


# --------------------------------------------------------------------------------------
# Línea de comandos
# --------------------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Genera la ficha del profesor (PDF y PNG).")
    ap.add_argument("json", help="Archivo JSON con los datos de la ficha.")
    ap.add_argument("foto", nargs="?", help="Foto carnet (JPG, PNG o WEBP). Opcional.")
    ap.add_argument("--validar", action="store_true", help="Solo comprobar el JSON, sin generar nada.")
    ap.add_argument("--salida", default=str(SALIDA), help="Carpeta de salida (por defecto docs/fichas_profe/salida/).")
    ap.add_argument("--anio", type=int, help="Año para el nombre del archivo (por defecto, el actual).")
    args = ap.parse_args(argv)

    ruta_json = Path(args.json).resolve()
    try:
        datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"No se puede leer el JSON: {e}", file=sys.stderr)
        return 2

    errores, avisos = validar(datos)
    for a in avisos:
        print(f"AVISO: {a}", file=sys.stderr)
    if errores:
        print("ERRORES:\n- " + "\n- ".join(errores), file=sys.stderr)
        return 2
    if args.validar:
        print("JSON válido.")
        return 0

    ruta_foto = Path(args.foto) if args.foto else (ruta_json.parent / datos["foto"] if datos.get("foto") else None)
    foto = None
    if ruta_foto:
        try:
            foto = ruta_foto.read_bytes()
        except OSError as e:
            print(f"No se puede leer la foto ({e}); se generará con iniciales.", file=sys.stderr)

    try:
        r = generar_todo(datos, foto)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    except Exception as e:   # navegador no instalado o que no arranca
        print(f"No se ha podido abrir el navegador para generar la ficha: {str(e).splitlines()[0]}\n"
              "Comprueba que Playwright y el navegador están instalados (playwright install chromium) "
              "o, para Edge, la variable NEXO_CANAL=msedge.", file=sys.stderr)
        return 3
    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    base = nombre_archivo(datos, args.anio)
    (salida / f"{base}.pdf").write_bytes(r["pdf"])
    (salida / f"{base}.png").write_bytes(r["png"])
    for a in r["avisos"]:
        if a not in avisos:
            print(f"AVISO: {a}", file=sys.stderr)
    print(f"{salida / (base + '.pdf')}\n{salida / (base + '.png')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
