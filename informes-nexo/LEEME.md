# Informes mensuales Nexo

    python3 generar_informe.py datos_alumno.json "Informe Nombre - mes.pdf"

- `datos_ejemplo_juan.json`: formato de datos (copiar y rellenar por alumno).
- `estilo.css`: estética de los Planes NEXO. `assets/logo_nexo.png`: logo (extraído del plan).
- Estructura del informe: la del Word de ejemplo. Requiere Chromium (`/opt/pw-browsers`).
- Si hay mes anterior: `hay_mes_anterior: true` y usar `evolucion_intro`/`evolucion` para comparar.

## Ejemplo ficticio (Héctor, 1º Bachillerato)
`ejemplos/crear_ejemplo_hector.py` genera una tabla de sesiones inventada sobre el horario real del plan
(L-V 9-13 h, bono 20 h) y calcula horas, sesiones y medias; después:

    python3 ejemplos/crear_ejemplo_hector.py
    python3 generar_informe.py ejemplos/hector_ejemplo_2026-09.json "ejemplos/Informe EJEMPLO Hector - septiembre 2026.pdf"

`"ejemplo": true` en el JSON marca el PDF como «datos ficticios». Datos reales de alumnos: carpeta `alumnos/` (ignorada por git).
