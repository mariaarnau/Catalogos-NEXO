# Instrucciones de la ficha del profesor

Nexo Académico · Equipo docente

## 1. Qué es y cómo se usa

La **ficha del profesor** es un PDF de una sola hoja A4 que la familia recibe cuando paga, para conocer a su profe antes de la primera clase. Se genera también como imagen PNG, que se ve bien en WhatsApp. Su trabajo es dar confianza: quién es el profe, qué ha estudiado, qué ha hecho dando clase y cómo trabaja, con datos comprobables y sin adornos.

El circuito completo es este:

1. Se parte del **CV del profe** (PDF, Word o foto) y de su **foto carnet**.
2. Una IA lee el CV con el prompt de `extraer_del_cv.md` y devuelve **solo un JSON** con el formato de `esquema_ficha.json`.
3. Se **valida** el JSON: `python generar_ficha.py --validar ficha.json`.
4. Se **genera** el PDF y el PNG con `generador/generar_ficha.py`.
5. Una persona **revisa** el resultado con la lista del apartado 9.
6. Se envía a la familia por WhatsApp. El teléfono del profe se pasa aparte, nunca va en la ficha.

## 2. Qué hay en esta carpeta

| Archivo | Para qué sirve |
|---|---|
| `INSTRUCCIONES_FICHAS_PROFE.md` y `.html` | Este documento. La copia `.html` es la misma, para leerla cómodamente. |
| `extraer_del_cv.md` | El prompt exacto que usa la IA para pasar de un CV al JSON. |
| `esquema_ficha.json` | El formato de los datos, campo por campo, con obligatoriedad y largos máximos. Lo lee también el validador. |
| `plantilla_ficha_profe.html` | La plantilla visual, con huecos para los datos y la foto. |
| `ficha_ejemplo.json` | Un ejemplo completo y realista, con todos los campos. |
| `cv_ejemplo.txt` y `cv_ejemplo_resultado.json` | Un CV inventado (con datos sensibles incluidos a propósito) y el JSON que debe salir de él. |
| `generador/generar_ficha.py` | Genera el PDF y el PNG. Valida los datos antes. |
| `generador/probar_generador.py` | Pruebas automáticas del generador. |
| `generador/prueba_limites.json` | Ficha con todos los campos en su largo máximo, para comprobar que cabe en una hoja. |
| `ejemplo/` | El PDF y el PNG de ejemplo ya generados. |
| `salida/` | Aquí se guardan los PDF y PNG que se generen. No se sube a git. |
| `assets/logo_nexo.png` | Logotipo de Nexo para la cabecera. |

## 3. Apartados de la ficha, de arriba abajo

Paleta Nexo: azul noche `#0a1226`, azul `#154CA9`, crema `#F4F1E8` y dorado `#a8802a`. La ficha es sobria, de nivel profesional, y siempre ocupa una sola hoja A4.

| Orden | Apartado | Campo | Qué va | Obligatorio |
|---|---|---|---|---|
| 1 | Cabecera | `foto` | Foto carnet en un círculo. Sin foto, un círculo con las iniciales. | No |
| 1 | Cabecera | `nombre` | Nombre y primer apellido. | Sí |
| 1 | Cabecera | `titular` | Una línea que resume al profe. | Sí |
| 1 | Cabecera | `edad`, `modalidad` | Debajo del titular, en una línea: «27 años · Online y presencial en Valencia». | No |
| 2 | Presentación | `presentacion` | De 2 a 4 frases en tercera persona. | Sí |
| 3 | Qué enseña | `asignaturas` | Cada asignatura con sus niveles. | Sí |
| 4 | Formación | `formacion` | Estudios, del más reciente al más antiguo. | Sí |
| 4 | Idiomas | `idiomas` | Idioma, nivel y certificado. Va al lado de Formación. | No |
| 5 | Experiencia dando clase | `experiencia` | Solo experiencia relacionada con la docencia. | No (ver nota) |
| 6 | Puntos fuertes | `puntos_fuertes` | Frases cortas y concretas. | No (ver nota) |
| Pie | Pie de página | (fijo) | «Nexo Académico · Equipo docente» y nexoacademico.com. | No se rellena |

**Nota.** Hace falta contenido en `experiencia` o en `puntos_fuertes`; al menos uno de los dos. Si el profe no ha dado clase nunca, la ficha se apoya en los puntos fuertes (aptitudes que consten en el CV).

Los campos opcionales que no se conozcan se dejan vacíos (`""`, `[]` o `null`) y la ficha **no muestra** ni el apartado ni su título. Quitar cualquier opcional no rompe el diseño.

Campos que no se ven en la ficha: `foto_encuadre` (ajusta el recorte de la foto) y `notas_revision` (avisos para quien revisa).

## 4. Límites y tono de cada texto

Los largos cuentan **caracteres, espacios incluidos**. El validador rechaza lo que se pase. Si un texto no cabe, se reescribe más corto; nunca se corta a mitad de frase.

| Campo | Máx. caracteres | Elementos máx. | Tono y contenido |
|---|---|---|---|
| `nombre` | 40 | | Tal como figura en el CV. Nombre y primer apellido. |
| `titular` | 70 | | Seco y informativo. Dos datos separados por « · »: situación y años dando clase. |
| `edad` | 16 a 99 (número) | | Solo si el CV da la edad o la fecha de nacimiento. |
| `modalidad` | 60 | | Neutro. «Online», «Presencial en Valencia» u «Online y presencial en Valencia». |
| `presentacion` | 90 a 480 | | Cálido y concreto. Tercera persona. De 2 a 4 frases. |
| `asignaturas` | | 5 | Una entrada por asignatura. |
| `asignaturas.nombre` | 28 | | La asignatura concreta (Estadística, no «Ciencias»). |
| `asignaturas.niveles` | 40 | | «ESO y Bachillerato», «Nivel universitario». |
| `formacion` | | 3 | Del más reciente al más antiguo. |
| `formacion.titulo` | 64 | | Título completo, sin abreviar. |
| `formacion.centro` | 48 | | Universidad o centro. |
| `formacion.periodo` | 24 | | «2022-2026» o «2023-actualidad». |
| `experiencia` | | 3 | Del más reciente al más antiguo. |
| `experiencia.puesto` | 60 | | Qué hacía, en una expresión corta. |
| `experiencia.lugar` | 48 | | Centro o entidad, si lo hay. |
| `experiencia.periodo` | 24 | | «2022-actualidad». |
| `experiencia.detalle` | 120 | | Una frase con qué hacía y con quién. |
| `puntos_fuertes` | | 5 | Frases cortas, todas respaldadas por el CV. |
| `puntos_fuertes` (cada uno) | 40 | | Empiezan por un verbo o por un hecho. Sin adjetivos vacíos. |
| `idiomas` | | 3 | Solo los que figuran en el CV. |
| `idiomas.idioma` | 20 | | «Inglés». |
| `idiomas.nivel` | 20 | | «B2», «Nativo», «Avanzado». |
| `idiomas.certificado` | 36 | | Solo si el CV nombra el título. |
| `notas_revision` | | 8 | Avisos internos, no se muestran. |
| `notas_revision` (cada una) | 200 | | Claras y breves, para la persona que revisa. |

Con todos los campos al máximo a la vez, la ficha se reduce hasta el 75 % para seguir cabiendo en una hoja. Con datos normales (como `ficha_ejemplo.json`) no se reduce nada. Si el generador avisa de que ha tenido que reducirla, conviene acortar algún texto.

## 5. Cómo se saca cada dato del CV

**`nombre`.** El nombre propio y el primer apellido que aparecen en el CV. Si el CV trae dos apellidos, se deja el primero. Si el profe usa un nombre distinto del legal (por ejemplo, «Pau» por «Paulina»), se respeta el que escribe en el CV.

**`foto`.** No se saca del CV: es la foto carnet que se entrega aparte. El campo puede llevar el nombre del archivo (`irene_soler.jpg`) para la línea de comandos, o ir vacío. Si el profe no tiene foto, la ficha muestra un círculo con sus iniciales.

**`titular`.** Combina la situación académica o profesional con los años dando clase, separados por « · ».
- Situación: «Estudiante de 4.º de Matemáticas», «Graduado en Física», «Ingeniera industrial», «Maestra de Educación Infantil».
- Años dando clase: se calculan con la fecha de hoy a partir del inicio de la primera experiencia docente que figure en el CV, y se redondean hacia abajo. Si el CV no da fechas, no se pone cifra: «Estudiante de 4.º de Matemáticas».
- Ejemplos: «Estudiante de 4.º de Matemáticas · 4 años dando clase»; «Graduado en Física · 6 años dando clase».

**`edad`.** Solo si el CV da la edad o la fecha de nacimiento; en ese caso se calcula con la fecha de hoy. **La fecha de nacimiento no se escribe nunca**, ni en este campo, ni en la presentación, ni en las notas. Si el profe es menor de edad, se deja vacío y se avisa en `notas_revision`.

**`modalidad`.** Se toma del CV («clases online y a domicilio») o de las notas de Nexo. Si ninguno lo dice, se deja vacío.

**`presentacion`.** Se redacta con datos del CV, sin añadir ninguno. Estructura recomendada:
1. Quién es y qué estudia o ha estudiado, con el nombre de pila.
2. A quién da clase y desde cuándo, con las cifras que dé el CV (alumnos, años, niveles).
3. Cómo trabaja, **solo si el CV lo cuenta**: un método, una costumbre de trabajo, un tipo de ejercicio. Si el CV no dice nada de cómo da clase, esta frase se sustituye por un dato de experiencia (una academia, unas prácticas, un grupo reducido).

**`asignaturas`.** Las que el CV dice que imparte. Si el CV solo da «matemáticas», se pone «Matemáticas». Las asignaturas o niveles que Nexo comunica aparte (por ejemplo, «va a dar Estadística universitaria») se aceptan como dato verificado, aunque no estén en el CV, y se anota en `notas_revision` que proceden de las notas de Nexo.

**`formacion`.** De más a menos reciente. Entran los grados, másteres y, si el profe es joven y no tiene más, el Bachillerato. No entran la ESO, la formación obligatoria ni los cursos sueltos que no tengan que ver con enseñar. Se respeta el estado: «(4.º curso)», «(en curso)».

**`experiencia`.** Solo lo relacionado con dar clase: clases particulares, academias, colegios, prácticas docentes, monitorías de refuerzo, voluntariado educativo. **Se descartan** los trabajos de camarero, dependiente, repartidor, azafata, cajero y similares, aunque ocupen media página del CV. Las clases particulares que el CV mencione sin fechas se incluyen sin periodo.

**`puntos_fuertes`.** Hechos del CV convertidos en frases cortas: un método, un tipo de alumno, una cifra, una circunstancia («Ha dado clase uno a uno y en grupo»). Si no hay experiencia docente, aquí van las aptitudes que consten en el CV (paciencia, organización, facilidad para explicar), sin adornarlas.

**`idiomas`.** Los que figuran en el CV con nivel o certificado. Si el CV pone «inglés» sin más, se pone «Inglés» sin nivel. El idioma materno solo se incluye si el CV lo menciona.

**`notas_revision`.** Todo lo que la persona que revisa debería saber: datos que faltan, asignaturas que no salen del CV, fechas ambiguas, discrepancias dentro del CV, disponibilidad que se ha omitido. Nunca incluyen datos sensibles. Ejemplo: «El CV no indica qué asignaturas imparte; se han tomado de las notas de Nexo.»

## 6. Reglas de contenido

### 6.1 No inventar nada

Cada dato de la ficha sale del CV o de las notas de Nexo. Si falta, el campo queda vacío y no se muestra. Eso incluye cifras, centros, métodos, resultados, cualidades y nombres. Está prohibido deducir lo que «probablemente» sabe el profe.

### 6.2 Datos que no aparecen NUNCA

- DNI, NIE, pasaporte, número de la Seguridad Social, SIP.
- Dirección o domicilio, ni siquiera el barrio o la calle.
- Fecha de nacimiento.
- Teléfono y email del profe. Los pasa Nexo a la familia aparte.
- Redes sociales, LinkedIn y enlaces.
- Estado civil, nacionalidad, situación administrativa, religión, salud.
- Datos económicos o laborales no docentes.

El validador rechaza lo que parezca un email, un teléfono, un DNI o NIE, una fecha completa, un enlace, una dirección o una de esas palabras. Es una red de seguridad: la responsabilidad es de quien redacta.

### 6.3 Tono

- **Tercera persona**, con respeto y cercanía: «Irene da clase desde 2022», no «yo» ni «usted».
- **Cálido y concreto.** Cada frase debe contener un dato que la familia pueda imaginarse: un número, un nivel, un método, un lugar.
- **Vocabulario amplio y preciso.** Verbos concretos (explica, corrige, repasa, prepara, acompaña, resuelve) en lugar de «ayuda», «hace» o «trabaja con».
- **Voz humana**, como la escribiría una persona de la academia que ha leído el CV con atención. Nada de aire corporativo.
- **Sin frases hechas.** Se evitan, entre otras: «apasionado por la enseñanza», «comprometido con la excelencia», «dinámico y proactivo», «amplia experiencia», «gran capacidad», «perfil», «alto nivel», «orientado a resultados», «excelentes habilidades», «trabajo en equipo» (como adjetivo suelto), «motivado».
- **Sin superlativos ni promesas.** No se promete aprobar ni subir nota. Se describe cómo trabaja el profe.
- **Sin guiones largos** (— o –), sin puntos suspensivos de relleno y **sin emojis**.

### 6.4 Ortografía y formato

- Sin faltas de ortografía ni de puntuación. Con tildes, incluidas las de las mayúsculas.
- Ordinales con punto y ordinal volado: «4.º de ESO», «1.º de Bachillerato», «3.er curso».
- Nombres propios con su ortografía oficial: «Universitat de València», «Universitat Politècnica de València», «Bachillerato», «ESO».
- Periodos con guion corto y sin espacios: «2022-2024», «2023-actualidad».
- En el texto corrido, los números del uno al nueve van con letra («cuatro años», «cinco alumnos») y del 10 en adelante con cifra. En el titular y en los datos cortos se usa la cifra: «4 años dando clase».
- Si necesitas comillas dentro de un texto, usa las españolas: «así».

### 6.5 Género

Se escribe en masculino o en femenino solo cuando el CV lo deja claro («graduada», «monitora», «Sra.»). Si no lo deja claro, se usan construcciones neutras: «Titulación en Matemáticas», «Estudia cuarto», «da clase desde 2022». Nunca se deduce el género a partir del nombre de pila.

### 6.6 Cifras y fechas

Los años dando clase, los alumnos y los cursos se calculan solo con lo que dice el CV y con la fecha de hoy. Si el CV dice «2021-2026», se entiende que la actividad llega hasta la actualidad y se avisa en `notas_revision` si hay duda.

## 7. Ejemplos de redacción

**Presentación**

Mal, por vaga y llena de frases hechas:
> Irene es una estudiante muy comprometida y apasionada por la enseñanza, con amplia experiencia y gran capacidad para conectar con los alumnos.

Bien, concreta y verificable en el CV:
> Irene cursa cuarto de Matemáticas en la Universitat de València y da clases particulares desde septiembre de 2022, con unos doce alumnos de ESO y Bachillerato. Siempre empieza pidiendo al alumno que cuente con sus palabras qué entiende del enunciado, y desde ahí corrige el rumbo sin darle el resultado hecho.

**Puntos fuertes**

Mal: «Paciente», «Responsable», «Buena comunicadora».
Bien: «Parte de lo que el alumno ya entiende», «Ha dado clase uno a uno y en grupo», «Cuatro años seguidos dando clase».

**Titular**

Mal: «Profesora muy preparada y entusiasta».
Bien: «Estudiante de 4.º de Matemáticas · 4 años dando clase».

**Experiencia**

Mal: puesto «Camarera de eventos» (no tiene que ver con dar clase).
Bien: puesto «Monitora de refuerzo», lugar «Academia Vèrtex», detalle «Grupos de cinco alumnos de 3.º y 4.º de ESO, dos tardes por semana».

## 8. Generar la ficha

Requisitos: Python 3 y Playwright (`pip install playwright` y, una vez, `playwright install chromium`). Sin más dependencias.

**Por línea de comandos**

```
python generar_ficha.py ficha_ejemplo.json            (sin foto: sale el círculo con iniciales)
python generar_ficha.py ficha_ejemplo.json foto.jpg   (con foto carnet)
python generar_ficha.py --validar ficha.json          (solo comprueba el JSON)
```

Crea `Nombre_Apellido_AAAA.pdf` y `.png` en `docs/fichas_profe/salida/` (por ejemplo, `Irene_Soler_2026.pdf`). Opciones: `--salida CARPETA` y `--anio AAAA`. Si no se indica foto, usa el campo `foto` del JSON (ruta relativa al JSON).

**Códigos de salida:** 0 si todo va bien; 2 si el JSON no es válido (los errores salen por la salida de errores, uno por línea, para que la IA pueda corregirlos y repetir); 3 si el navegador no se puede abrir (Playwright o el navegador no están instalados).

**Desde otro programa**

```python
from generar_ficha import generar, generar_imagen, validar

errores, avisos = validar(datos)           # sin abrir el navegador
pdf = generar(datos, foto_en_bytes)        # bytes del PDF
png = generar_imagen(datos, foto_en_bytes) # bytes del PNG
```

`foto_en_bytes` es el contenido de un JPG, PNG o WEBP (hasta 8 MB), o `None`. Si los datos no son válidos, `generar` lanza `ValueError` con todos los errores.

**Navegador.** Por defecto usa el Chromium de Playwright. Para usar Edge en el ordenador de Nexo, define la variable de entorno `NEXO_CANAL=msedge` (en Windows: `set NEXO_CANAL=msedge`). Para un ejecutable concreto, `NEXO_NAVEGADOR=ruta`. No hay que tocar el código.

**Pruebas.** `python probar_generador.py` comprueba el validador, la plantilla, el PDF de una hoja A4 y el PNG. Conviene pasarlas después de cualquier cambio.

## 9. Lista de comprobación antes de enviar

1. ¿Está el nombre bien escrito, con tildes?
2. ¿La foto es del profe correcto y se ve la cara completa en el círculo? Si sale cortada, se ajusta `foto_encuadre` (por ejemplo, `50% 45%`).
3. ¿Cada dato está en el CV o en las notas de Nexo? Se leen las `notas_revision`.
4. ¿Hay algún teléfono, email, dirección, DNI o fecha de nacimiento? No debe haberlo.
5. ¿La presentación suena a una persona y no a un folleto? ¿Tiene datos concretos y ninguna frase hecha?
6. ¿Las asignaturas son concretas y los niveles correctos (sobre todo si Nexo los comunicó aparte)?
7. ¿La experiencia es solo de dar clase?
8. ¿Cabe en una hoja sin que la letra se vea pequeña? El generador avisa si se ha reducido.
9. ¿Hay faltas de ortografía? Se lee entero, una vez, en voz alta.
10. ¿Va a la familia correcta? El nombre del archivo lleva el del profe.

## 10. Cambios de diseño

- **Textos fijos y colores:** `plantilla_ficha_profe.html` (la paleta está al principio, en variables CSS).
- **Campos y largos máximos:** `esquema_ficha.json`. El validador lo lee, así que basta con cambiarlo ahí; después hay que actualizar la tabla del apartado 4 y `extraer_del_cv.md`. La prueba `test_documentos_coinciden_con_el_esquema` avisa si algún número se desfasa.
- **Logotipo:** `assets/logo_nexo.png`.
