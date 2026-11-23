"""Pruebas del generador de fichas. Solo librería estándar y Playwright.

    python probar_generador.py

Comprueba que los ejemplos son válidos, que los datos sensibles se rechazan, que cualquier campo
opcional se puede quitar sin romper el diseño, que la foto y las iniciales funcionan y que el PDF
sale en una sola hoja A4 y el PNG con el tamaño esperado.
"""
from __future__ import annotations

import copy
import json
import re
import struct
import sys
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generar_ficha as g  # noqa: E402

CARPETA = g.CARPETA


def cargar(nombre: str) -> dict:
    return json.loads((CARPETA / nombre).read_text(encoding="utf-8"))


def png_minimo() -> bytes:
    """PNG válido de 2x2 píxeles, hecho a mano para no depender de librerías de imagen."""
    def trozo(tipo, datos):
        c = struct.pack(">I", len(datos)) + tipo + datos
        return c + struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF)
    filas = b"".join(b"\x00" + b"\x80\x40\x20" * 2 for _ in range(2))
    return (b"\x89PNG\r\n\x1a\n" + trozo(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
            + trozo(b"IDAT", zlib.compress(filas)) + trozo(b"IEND", b""))


def paginas_pdf(pdf: bytes) -> int:
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", pdf))


class Validacion(unittest.TestCase):
    def test_ejemplos_validos(self):
        for nombre in ("ficha_ejemplo.json", "cv_ejemplo_resultado.json", "generador/prueba_limites.json"):
            errores, _ = g.validar(cargar(nombre))
            self.assertEqual(errores, [], f"{nombre}: {errores}")

    def test_ejemplos_sin_avisos_de_estilo(self):
        for nombre in ("ficha_ejemplo.json", "cv_ejemplo_resultado.json"):
            _, avisos = g.validar(cargar(nombre))
            self.assertEqual(avisos, [], f"{nombre}: {avisos}")

    def test_datos_sensibles_rechazados(self):
        casos = {
            "email": "Escribe a ana.lopez@gmail.com para más datos.",
            "telefono": "Su número es 654 32 10 98 para cualquier duda.",
            "telefono_con_prefijo": "Llama al +34 654321098 por la tarde.",
            "dni": "Documento 20487315K en regla.",
            "fecha": "Nacida el 14/03/2004 en Valencia.",
            "enlace": "Su perfil está en linkedin.com/in/ana",
            "direccion": "Vive en Calle del Pintor Sorolla 18.",
            "estado_civil": "Su estado civil es soltera.",
        }
        for nombre, texto in casos.items():
            d = cargar("ficha_ejemplo.json")
            d["presentacion"] = texto + " " + d["presentacion"]
            errores, _ = g.validar(d)
            self.assertTrue(any(e.startswith("presentacion") for e in errores), f"No rechaza: {nombre}")

    def test_periodos_y_a_domicilio_no_dan_falsos_positivos(self):
        d = cargar("ficha_ejemplo.json")
        d["experiencia"][0]["periodo"] = "06/2023-09/2024"
        d["experiencia"][0]["detalle"] = "Clases a domicilio en 2023-2024, de lunes a jueves."
        errores, _ = g.validar(d)
        self.assertEqual(errores, [])

    def test_rayas_y_emojis(self):
        d = cargar("ficha_ejemplo.json")
        d["titular"] = "Graduado en Física — 6 años dando clase"
        d["puntos_fuertes"][0] = "Explica con calma \U0001F600"
        errores, _ = g.validar(d)
        self.assertTrue(any(e.startswith("titular") for e in errores))
        self.assertTrue(any(e.startswith("puntos_fuertes[1]") for e in errores))

    def test_largos_y_obligatorios(self):
        d = cargar("ficha_ejemplo.json")
        d["nombre"] = "x" * 41
        d["presentacion"] = ""
        del d["asignaturas"]
        errores, _ = g.validar(d)
        texto = "\n".join(errores)
        self.assertIn("nombre: 41 caracteres", texto)
        self.assertIn("presentacion: es obligatorio", texto)
        self.assertIn("asignaturas: es obligatorio", texto)

    def test_hace_falta_experiencia_o_puntos(self):
        d = cargar("ficha_ejemplo.json")
        d["experiencia"], d["puntos_fuertes"] = [], []
        errores, _ = g.validar(d)
        self.assertTrue(any("experiencia" in e and "puntos_fuertes" in e for e in errores))

    def test_campo_desconocido(self):
        d = cargar("ficha_ejemplo.json")
        d["telefono"] = "654321098"
        errores, _ = g.validar(d)
        self.assertTrue(any("telefono" in e for e in errores))

    def test_nombre_archivo(self):
        self.assertEqual(g.nombre_archivo({"nombre": "Ángela Pastor"}, 2026), "Angela_Pastor_2026")
        self.assertEqual(g.nombre_archivo({"nombre": "Joaquín  López"}, 2026), "Joaquin_Lopez_2026")


class Plantilla(unittest.TestCase):
    def test_sin_restos_de_plantilla_al_quitar_cada_opcional(self):
        base = cargar("ficha_ejemplo.json")
        vacios = {"foto_encuadre": "", "edad": None, "modalidad": "", "experiencia": [], "idiomas": [],
                  "puntos_fuertes": [], "notas_revision": []}
        for campo, vacio in vacios.items():
            d = copy.deepcopy(base)
            d[campo] = vacio
            if campo == "experiencia":
                pass  # quedan los puntos fuertes
            html = g.construir_html(d, None)
            for resto in ("{{", "}}", "<!--SI", "<!--PARA", "None", "undefined"):
                self.assertNotIn(resto, html, f"Al quitar «{campo}» queda «{resto}»")

    def test_opcionales_internos_vacios(self):
        d = cargar("ficha_ejemplo.json")
        for e in d["formacion"]:
            e["centro"], e["periodo"] = "", ""
        for e in d["experiencia"]:
            e["lugar"], e["periodo"], e["detalle"] = "", "", ""
        for e in d["idiomas"]:
            e["nivel"], e["certificado"] = "", ""
        for e in d["asignaturas"]:
            e["niveles"] = ""
        html = g.construir_html(d, None)
        for resto in ("{{", "<!--SI", "<!--PARA", "None"):
            self.assertNotIn(resto, html)
        self.assertNotIn('class="fecha"', html)
        self.assertNotIn('class="idi-c"', html)

    def test_foto_o_iniciales(self):
        d = cargar("ficha_ejemplo.json")
        con = g.construir_html(d, png_minimo())
        sin = g.construir_html(d, None)
        self.assertIn('<img class="foto"', con)
        self.assertNotIn('class="foto ini"', con)
        self.assertIn('class="foto ini">DF<', sin)
        with self.assertRaises(ValueError):
            g.construir_html(d, b"esto no es una imagen")

    def test_el_html_escapa_el_texto(self):
        d = cargar("ficha_ejemplo.json")
        d["titular"] = "Graduado en <b>Física</b> & más"
        html = g.construir_html(d, None)
        self.assertIn("&lt;b&gt;Física&lt;/b&gt; &amp; más", html)

    def test_minimo_obligatorio(self):
        d = {
            "nombre": "Ana Gil", "titular": "Estudiante de 2.º de Química",
            "presentacion": "Ana estudia segundo de Química y ayuda con los deberes a su primo de 1.º de ESO. Explica con paciencia y repite cada paso.",
            "asignaturas": [{"nombre": "Química", "niveles": ""}],
            "formacion": [{"titulo": "Grado en Química", "centro": "", "periodo": ""}],
            "puntos_fuertes": ["Repite cada paso con calma"],
        }
        self.assertEqual(g.validar(d)[0], [])
        html = g.construir_html(d, None)
        self.assertNotIn("{{", html)


class Documentos(unittest.TestCase):
    """Los documentos escritos a mano no pueden desfasarse del esquema."""

    @staticmethod
    def _campos(esquema: dict):
        for nombre, regla in esquema["campos"].items():
            yield nombre, regla
            for sub, sregla in regla.get("elementos", {}).items():
                yield f"{nombre}.{sub}", sregla

    def test_documentos_coinciden_con_el_esquema(self):
        extraer = (CARPETA / "extraer_del_cv.md").read_text(encoding="utf-8").splitlines()
        instrucciones = (CARPETA / "INSTRUCCIONES_FICHAS_PROFE.md").read_text(encoding="utf-8").splitlines()
        for ruta, regla in self._campos(g.cargar_esquema()):
            numeros = [regla[k] for k in ("min", "max", "min_elementos", "max_elementos") if k in regla]
            lineas = [l for l in extraer if l.startswith(f"{ruta} (")]
            self.assertTrue(lineas, f"extraer_del_cv.md no describe «{ruta}»")
            for n in numeros:
                self.assertTrue(any(re.search(rf"\b{n}\b", l) for l in lineas), f"extraer_del_cv.md: «{ruta}» no menciona {n}")
            if ruta in ("foto", "foto_encuadre"):
                continue  # no aparecen en la tabla de límites: no se ven en la ficha
            lineas = [l for l in instrucciones if f"`{ruta}`" in l and l.startswith("|")]
            self.assertTrue(lineas, f"INSTRUCCIONES: falta «{ruta}» en la tabla de límites")
            for n in [regla[k] for k in ("min", "max", "max_elementos") if k in regla]:
                self.assertTrue(any(re.search(rf"\b{n}\b", l) for l in lineas), f"INSTRUCCIONES: «{ruta}» no menciona {n}")

    def test_el_ejemplo_de_cv_no_arrastra_datos_ajenos(self):
        resultado = json.dumps(cargar("cv_ejemplo_resultado.json"), ensure_ascii=False).lower()
        for prohibido in ("20487315", "14/03/2004", "2004", "soltera", "pintor sorolla", "654 32 10 98", "654321098",
                          "irene.soler", "gmail", "linkedin", "camarera", "dependienta", "banco de alimentos",
                          "chiringuito", "pastelería", "escalada", "ajedrez", "latex", "excel", "campos"):
            self.assertNotIn(prohibido, resultado, f"El resultado del CV de ejemplo contiene «{prohibido}»")
        self.assertEqual(g.validar(cargar("cv_ejemplo_resultado.json"))[0], [])

    def test_sin_guiones_largos_ni_emojis_en_los_ejemplos(self):
        for nombre in ("ficha_ejemplo.json", "cv_ejemplo_resultado.json"):
            texto = (CARPETA / nombre).read_text(encoding="utf-8")
            self.assertIsNone(re.search("[\u2014\u2013]", texto), nombre)
            self.assertIsNone(re.search("[\U0001F000-\U0001FAFF]", texto), nombre)


class Archivos(unittest.TestCase):
    """Estas pruebas abren el navegador."""

    @classmethod
    def setUpClass(cls):
        cls.datos = cargar("ficha_ejemplo.json")

    def test_pdf_una_hoja_a4(self):
        pdf = g.generar(self.datos, None)
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertEqual(paginas_pdf(pdf), 1)
        medida = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]", pdf)
        self.assertIsNotNone(medida)
        self.assertAlmostEqual(float(medida.group(1)), 595, delta=2)
        self.assertAlmostEqual(float(medida.group(2)), 842, delta=2)

    def test_png_con_el_tamano_esperado(self):
        png = g.generar_imagen(self.datos, None)
        self.assertTrue(png.startswith(b"\x89PNG"))
        ancho, alto = struct.unpack(">II", png[16:24])
        self.assertAlmostEqual(ancho, 1588, delta=4)
        self.assertAlmostEqual(alto, 2246, delta=4)

    def test_con_foto_y_en_el_limite_cabe_en_una_hoja(self):
        r = g.generar_todo(cargar("generador/prueba_limites.json"), png_minimo())
        self.assertEqual(paginas_pdf(r["pdf"]), 1)
        self.assertGreaterEqual(r["escala"], 0.7, "Incluso con todo al máximo la letra no debe bajar del 70 %.")

    def test_ejemplos_reales_sin_reducir_la_letra(self):
        for nombre in ("ficha_ejemplo.json", "cv_ejemplo_resultado.json"):
            r = g.generar_todo(cargar(nombre), None)
            self.assertGreaterEqual(r["escala"], g.ESCALA_MINIMA_AVISO, nombre)
            self.assertEqual(r["avisos"], [], nombre)

    def test_cada_opcional_quitado_sigue_en_una_hoja(self):
        base = cargar("ficha_ejemplo.json")
        for campo, vacio in {"idiomas": [], "modalidad": "", "edad": None, "experiencia": []}.items():
            d = copy.deepcopy(base)
            d[campo] = vacio
            self.assertEqual(paginas_pdf(g.generar(d, None)), 1, campo)


if __name__ == "__main__":
    unittest.main(verbosity=2)
