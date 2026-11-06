#!/usr/bin/env python3
"""Lee el registro mensual de clases de Nexo (formato «INFORME DE CLASES», todos los alumnos) y lo vuelca a JSON."""
import json, re, sys

MESES = {m: i for i, m in enumerate(["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
                                      "agosto", "septiembre", "octubre", "noviembre", "diciembre"])}


def horas(txt):
    txt = txt.strip()
    m = re.match(r"(?:(\d+(?:[.,]\d+)?)\s*h)?\s*(?:(\d+)\s*min)?", txt)
    h = float(m.group(1).replace(",", ".")) if m and m.group(1) else 0
    return h + (int(m.group(2)) / 60 if m and m.group(2) else 0)


def leer(ruta, anio=2026):
    alumnos, al, clase, bloque = [], None, None, None
    for raw in open(ruta, encoding="utf-8-sig"):
        l = raw.rstrip("\n")
        s = l.strip()
        if s.startswith("ALUMNO:"):
            al = {"alumno": s[7:].strip(), "clases": []}; alumnos.append(al); clase = bloque = None
        elif al is None or not s or set(s) == {"━"}:
            continue
        elif s.startswith("Periodo:"):
            al["periodo"] = s[8:].strip()
        elif s.startswith("Clases:"):
            m = re.match(r"Clases:\s*(\d+)\s*·\s*Horas:\s*(.+)", s); al["n_clases"] = int(m.group(1)); al["horas"] = horas(m.group(2))
        elif s.startswith("Por asignatura:"):
            al["por_asignatura"] = {k.strip(): horas(v) for k, v in (re.match(r"(.+?)\s+([\d.,]+\s*h.*|\d+\s*min)$", p.strip()).groups() for p in s[15:].split("·"))}
        elif s.startswith("CLASE "):
            m = re.match(r"CLASE (\d+) · (\w+), (\d+) de (\w+) · ([\d:]+) · (.+)", s)
            clase = {"n": int(m.group(1)), "dia_semana": m.group(2), "fecha": f"{anio}-{MESES[m.group(4)]:02d}-{int(m.group(3)):02d}",
                     "hora": m.group(5), "duracion_h": horas(m.group(6)), "bloques": [], "examenes": []}
            al["clases"].append(clase); bloque = None
        elif s.startswith("Profesor:"):
            prof, _, estado = s[9:].partition("·"); clase["profesor"] = prof.strip(); clase["estado"] = estado.strip()
        elif s.startswith("▸"):
            m = re.match(r"▸ (.+?) — (.+?)(?: \(([^()]*)\))?$", s)
            extra = m.group(3) or ""
            mins = re.search(r"(\d+)\s*min", extra); nota = re.search(r"Nota\s*([\d.,]+)\s*/\s*([\d.,]+)", extra)
            bloque = {"asignatura": m.group(1).strip(), "tema": m.group(2).strip(), "min": int(mins.group(1)) if mins else None,
                      "nota": f"{nota.group(1)}/{nota.group(2)}" if nota else None, "respuestas": {}, "comentario": None}
            clase["bloques"].append(bloque)
        elif s.startswith("•"):
            p, _, r = s[1:].partition("→"); bloque["respuestas"][p.strip()] = r.strip()
        elif s.startswith("Comentario:"):
            bloque["comentario"] = s[11:].strip()
        elif s.startswith("Examen próximo:"):
            m = re.match(r"Examen próximo:\s*(\d+)/(\d+)/(\d+)\s*·\s*(.+)", s)
            clase["examenes"].append({"fecha": f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}", "texto": m.group(4).strip()})
        elif s.startswith("Generado el"):
            continue
        elif bloque is not None and bloque.get("comentario") is not None:
            bloque["comentario"] += " " + s
        elif bloque is not None and bloque["comentario"] is None and not bloque["respuestas"]:
            bloque["tema_detalle"] = (bloque.get("tema_detalle", "") + " · " + s).strip(" ·")
        else:
            print("LÍNEA NO RECONOCIDA:", al["alumno"], repr(s), file=sys.stderr)
    return alumnos


if __name__ == "__main__":
    datos = leer(sys.argv[1])
    json.dump(datos, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
    for a in datos:
        suma = sum(c["duracion_h"] for c in a["clases"])
        ok = "OK" if len(a["clases"]) == a["n_clases"] and abs(suma - a["horas"]) < 0.01 else "DESCUADRE"
        print(f'{a["alumno"]:32} {len(a["clases"]):>2} clases {a["horas"]:>5.2f} h  {ok}')
