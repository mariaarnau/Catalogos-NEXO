# Informes mensuales Nexo

    python3 generar_informe.py datos_alumno.json "Informe Nombre - mes.pdf"

- `datos_ejemplo_juan.json`: formato de datos (copiar y rellenar por alumno).
- `estilo.css`: estética de los Planes NEXO. `assets/logo_nexo.png`: logo (extraído del plan).
- Estructura del informe: la del Word de ejemplo. Requiere Chromium (`/opt/pw-browsers`).
- Si hay mes anterior: `hay_mes_anterior: true` y usar `evolucion_intro`/`evolucion` para comparar.
