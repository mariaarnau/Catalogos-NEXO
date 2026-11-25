# Planes personalizados NEXO — Instrucciones

Cómo se hace cada plan personalizado (PDF) y el mensaje de WhatsApp que lo acompaña.

---

## 1. Qué hay en esta carpeta

| Archivo | Para qué sirve |
|---|---|
| `plantilla_plan_nexo.html` | Plantilla visual ya generada, con marcadores `[NOMBRE]`, `[ZONA]`… Se abre en el navegador. Sirve para ver la estructura o para retocar a mano un plan puntual. |
| `plantilla_plan_nexo_vista_previa.pdf` | La misma plantilla en PDF (10 páginas). |
| `generador/generar_plan.py` | **El motor real.** Lee un JSON del lead y genera el HTML y el PDF. |
| `generador/tema_claro.py` | Aplica el tema claro: fondo blanco, logo azul, portada y cierre en azul marino con logo blanco. |
| `generador/render_pdf.js` | Convierte el HTML a PDF con Playwright (páginas de 960 × 904 px). |
| `generador/plantilla_lead.json` | JSON de partida con todos los campos habituales. |
| `generador/leads_ejemplo/*.json` | Leads reales ya hechos, para copiar el que más se parezca. |
| `generador/logos/` | Logos blanco y azul. |

> La "plantilla" de verdad es `generar_plan.py`. El HTML sale de él, con el CSS, el logo y los gráficos incrustados. Editar el HTML a mano vale para un caso suelto. Para el día a día, se rellena un JSON y se genera.

---

## 2. Cómo generar un plan

**Requisitos, una sola vez:**

```bash
pip install pillow            # solo si quieres hacer miniaturas de revisión
npm install -g playwright
npx playwright install chromium
```

**Generar:**

```bash
cd generador
python generar_plan.py leads/<lead>.json
```

Salida: `generador/output/<archivo>.html` y `<archivo>.pdf`.

**Flujo:**

1. Copiar `plantilla_lead.json`, o el ejemplo más parecido de `leads_ejemplo/`, con el nombre del alumno.
2. Rellenar los datos del chat: nombre, curso, asignaturas, zona, modalidad, días y horas.
3. Generar el plan.
4. Revisar el PDF página a página:
   - textos de otro alumno que se hayan quedado al copiar
   - gráficos que se salgan de su caja
   - precios
5. Enviar el PDF y el mensaje de WhatsApp.

---

## 3. Reglas de negocio

### Tarifas 2026/27

Bonos de horas, sin permanencia. Las de casa del profesor son las mismas que las online.

| Etapa | Modalidad | 2h (prueba) | 4h | 8h | 12h | €/h con 12h | Base €/h |
|---|---|---|---|---|---|---|---|
| Primaria | Presencial | 40 (tachado 44) | 86 | 170 | 250 | 20,83 | 22 |
| Primaria | Online (solo si se pide) | 36 | 77,40 | 153 | 225 | 18,75 | — |
| ESO | Online | 40 (tachado 44) | 86 | 170 | 250 | 20,83 | 22 |
| ESO | Presencial | 44 (tachado 48) | 94 | 185 | 270 | 22,50 | 24 |
| Bachillerato | Online | 44 (tachado 48) | 94 | 185 | 270 | 22,50 | 24 |
| Bachillerato | Presencial | 46 (tachado 50) | 98 | 195 | 285 | 23,75 | 25 |
| Universidad | Online | 46 (tachado 50) | 98 | 195 | 285 | 23,75 | 25 |
| Universidad | Presencial | 54 (tachado 56) | 111 | 220 | 327 | 27,25 | 28 |

Equivalencias rápidas:
- ESO online = Primaria presencial.
- Bachillerato online = ESO presencial.
- Universidad online = Bachillerato presencial.

Las tarifas están en el diccionario `TARIFAS`, al principio de `generar_plan.py`. Si cambia un precio, se cambia ahí.

### Reglas fijas

- **Formación Profesional (Grado Medio y Superior) se cobra con la tarifa de Universidad.** Se usa `"etapa": "universidad"` con `"tarifa_nombre": "FP Grado Medio"` y `"tarifa_corto": "FP"`.
- **Siempre se muestran también las tarifas online**, aunque pidan presencial: `"tarifas_mostrar": ["online", "casa_alumno"]` y la comparativa `dos_opciones`, con la presencial destacada si la han pedido.
- **Presencial = en casa del alumno.** Nunca en casa del profesor, salvo que se pida expresamente. Si la clase es en otro sitio (por ejemplo, una biblioteca), se cobra precio presencial y se cambia la etiqueta con `etiqueta_tarifas`.
- **Nunca "al mes" ni "/mes" en los bonos.** Las familias solo pagan las horas que se dan. Usar `"sin_mes": true` en `pasos`.
- **Recomendación por defecto:**
  1. Primero el bono de prueba de 2 h. **Sin precio tachado, sin "precio nuevos alumnos" y sin €/h** (es el comportamiento por defecto del generador; `"nuevos_alumnos": true` lo vuelve a mostrar).
  2. Después el bono de 12 h, destacando el €/h en dorado.
  3. Frase: "el mejor precio por hora del curso".
- **Plan Ahorro:** de momento **NO se vende**. No usar `tarifa_doble` hasta nueva orden. Solo bonos.
- **Hermanos en cursos distintos:** 10 % de descuento al que haga menos horas.
- **Dos alumnos en la misma clase:** −30 % en cada bono para cada uno, con `"descuento_grupo": true`. No se llama "Premium" y no lleva Plan Ahorro.
- **Sustitución garantizada:** sin dar número de horas, salvo que se pida.
- **Horarios:** siempre orientativos. Los cierra el profesor con la familia.
- **Tema claro por defecto.** `"tema": "oscuro"` solo si se pide.
- **Privacidad:** nunca usar informes reales de otros alumnos como ejemplo. El informe de ejemplo se inventa en el JSON (`informe_ejemplo`).

---

## 4. Campos del JSON del lead

### Básicos

| Campo | Ejemplo | Notas |
|---|---|---|
| `nombre` | `"Marina"` | `""` si no lo sabemos: el plan dice "Tu plan" o "vuestro hijo o hija". |
| `nombre_completo` | `"Marina Cubas Escobar"` | Va en la portada. |
| `etapa` | `primaria` / `eso` / `bachillerato` / `universidad` | Decide las tarifas. |
| `curso` | `"4º ESO"` | |
| `asignaturas` | `["Matemáticas"]` | |
| `voz` | `familia` / `tu` | `familia` cuando escribe la madre o el padre ("vosotros"); `tu` cuando escribe el alumno. |
| `archivo` | `"Plan_NEXO_Marina_Cubas_4ESO_Matematicas_Paterna"` | Nombre del PDF. |
| `cover_card_sub` | `"4º ESO · Matemáticas · Presencial en Paterna"` | Línea bajo el nombre, en la portada. |
| `presencial_label` | `"en vuestra casa"` | |
| `tarifas_mostrar` | `["casa_alumno"]`, `["online"]`, `["online","casa_alumno"]`, `["casa_alumno","casa_profesor"]` | Páginas de tarifas que salen. |
| `modalidades_recomendadas` | igual que el anterior | |
| `bonos_recomendados` | `[{"horas":12,"frecuencia":""}]` | |
| `textos` | `{cover_sub, p2_title, c1, c2t, c2, c3, informe_h2, p4_sub, p10_sub…}` | Cambia cualquier texto por defecto. |

### Páginas opcionales (salen si el campo existe)

- **`semana`:** horario semanal orientativo.
  - `bloques`: `[día, hora_inicio, hora_fin, índice_asignatura]`. Día 0 = lunes.
  - `dias`: para añadir el sábado.
  - `repartos`: horas por asignatura.
- **`trayectoria`:** hoja de ruta con curva.
  - `meses`
  - `tramos`: en índice de mes, de 0 a nº de meses − 1. Si se pasa de ahí, la curva se sale.
  - `bloques`: con `span`, y la suma de los `span` debe ser el nº de meses.
  - `hitos`: con `pos`, y `meta: true` en el último.
- **`camino`:** hoja de ruta por trimestres, con `fases` e `hitos`. Buena para 2º de Bachillerato y la PAU.
- **`calendario`:** calendario de sesiones.
- **`informe_ejemplo`:** datos ficticios del informe mensual.
- **Para quitar páginas:** `omitir_proceso`, `omitir_informe`, `omitir_phones`.

### Bloque de precios: elegir UNO

- **`pasos`** (el habitual): "Su plan, en dos pasos".
  - `prueba`: horas, precio, tachado, texto, y `alt` opcional.
  - `opciones`: 12 h con `destacado` y `alt`. Usar `alt.oro` para el €/h grande.
  - `resumen` y `quote`.
  - `sin_mes: true`.
  - `solo_bono` quita la prueba. `extra` añade una hora suelta. `nivel` añade un paso de evaluación inicial.
- **`dos_opciones`:** compara dos modalidades en columnas, por ejemplo presencial frente a online, o en casa frente a casa del profesor. Cada opción lleva `prueba` y `bono` con `base`. No lleva `pasos`.
- `tarifa_doble`: Premium + Plan Ahorro. **Desactivado por ahora.**

### Otros

- **`descuento_grupo: true`:** −30 % por alumno en las tarjetas de tarifas.
- **`tarifas_override`:** precios propios para un lead concreto.
- **`etiqueta_tarifas`:** cambia la cabecera de la página de tarifas. Ejemplo: `{"casa_alumno": "PRESENCIAL EN BENICALAP"}`.

---

## 5. Qué ejemplo copiar según el caso

| Caso | Ejemplo |
|---|---|
| ESO o Primaria presencial, un día a la semana, solo bonos | `marina_cubas.json` |
| Primaria / niños pequeños | `joel.json` |
| 2º Bachillerato, PAU, presencial + online | `candela.json` |
| Solo online, varias asignaturas | `saul.json` |
| Universidad, online + presencial puntual | `gonzalo.json` |
| En su casa o en casa del profesor | `pau.json` |
| Dos hermanos en la misma clase (−30 %) | `eric_elsa.json` |

---

## 6. Mensaje de WhatsApp que acompaña al PDF

**Estilo:**
- natural, esquemático, con emojis
- frases cortas
- tú o vosotros, según quién escriba

**Estructura:**

1. Saludo con el nombre de la madre, el padre o el alumno, más "te envío el plan que he preparado para [alumno]".
2. 🎯 **Enfoque:** qué se va a trabajar, a partir de lo que contaron en el chat.
3. 🏠 / 💻 **Modalidad:** días y horas, como orientativos.
4. 💶 **Precios:**
   - bono de prueba de 2 h
   - bono de 12 h, con el €/h ("el mejor precio por hora del curso")
   - ✨ "Sin permanencia: solo pagáis las horas de clase que se dan"
5. ✅ **Lo que tenéis con nosotros:**
   - 👩‍🏫 Profesores filtrados y verificados
   - 🔄 Sustitución: si el profesor no puede o no encaja, os ponemos otro del equipo
   - 📱 La app, con material, tareas y ejercicios
   - 📊 Informe mensual de evolución
6. 📎 Cierre: "Te adjunto el plan en PDF". Preguntar lo que falte (días, nombre, modalidad) y decir "os asigno profesor".

**Antes de enviar, comprobar:**
- que hay profesor disponible en la zona
- que los precios del mensaje coinciden con los del PDF
- que no queda texto de otro alumno
