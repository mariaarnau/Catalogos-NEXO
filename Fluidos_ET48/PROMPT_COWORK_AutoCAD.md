# PROMPT PARA CLAUDE COWORK — Dibujar la instalación de AF y ACS del hotel en AutoCAD (Equipo 48)

## 0. Tu papel y reglas
Eres un delineante-proyectista de instalaciones de fontanería. Vas a dibujar en AutoCAD, sobre el DWG de arquitectura de un hotel, la instalación de **agua fría (AF) y agua caliente sanitaria (ACS)** que ya está calculada. **No tienes que calcular nada:** diámetros, trazados y equipos están definidos abajo y en el Excel `ET48_AF_ACS_calculo_v2.xlsx`, hoja `Tramos`.

Reglas obligatorias:
1. **No modifiques ni borres nada de la arquitectura.** Trabaja sobre una copia: `HOTEL_ET48_FONTANERIA.dwg`.
2. Dibuja todo en espacio modelo, en **metros** (1 unidad = 1 m), con las mismas coordenadas del DWG original. No muevas ni escales el dibujo existente.
3. Crea las capas del apartado 2 y dibuja cada cosa en su capa.
4. Guarda periódicamente. Al final guarda en formato **AutoCAD 2013/2016 DWG** (requisito del enunciado: versión 2016 o inferior).
5. Si una coordenada que te doy choca con un muro, pilar, puerta o ascensor, **desplaza el trazado lo mínimo** para no interferir, y apúntalo en el informe final (apartado 9).
6. Antes de cualquier acción destructiva o dudosa (borrar, purgar, explotar bloques del original), **pregunta**.

## 1. Cómo está organizado el DWG
Las plantas están dibujadas una encima de otra en espacio modelo, con la **misma X** y distinta Y. Coordenadas en metros; el edificio va de X ≈ 2,0 (fachada Oeste) a X ≈ 51,5 (fachada Este) y el Norte está arriba.

| Dibujo | Rango Y aprox. | Notas |
|---|---|---|
| Planta sobre cubierta | 148 – 163 | |
| Planta cubierta | 125,7 – 141,2 | (Y planta tipo + 25,71) |
| **Planta tipo** (P1-P11) | 100,0 – 115,1 | Pasillo central Y 107,0 – 108,5 |
| **Planta baja** | 56,3 – 72,0 | (Y planta tipo − 43,49) |
| **Planta sótano** (garaje) | 13,5 – 29,0 | (Y planta baja − 42,89) |
| Esquema vertical | −23,6 – −4 | X −20 … 31 |
| Leyenda arquitectura | X 82–90, Y 52–77 | |

Cotas (de solera): calzada 0,00 · sótano −2,20 · PB +0,30 · P1 +4,40 · Pn = 4,40 + 3,30·(n−1) · P11 +37,40. Los aparatos se conectan a +0,60 sobre solera.

**Patinillos** (rectángulos rojos con aspa, existentes):
- **Patinillo O** (montantes Oeste), dos huecos de 0,60 × 0,35 m. Planta tipo: P1 X 2,31–2,91 y P2 X 3,01–3,61, ambos en Y 108,66–109,01. Planta baja: mismas X, Y 65,17–65,52. En el sótano no está dibujado: los montantes arrancan del techo del sótano en X 2,3–3,6, Y ≈ 22,3–22,6.
- **Patinillo E** (montantes Este), 1,34 × 0,41 m. Planta tipo: X 49,41–50,75, Y 106,45–106,86. Planta baja: Y 62,97–63,37. Sótano (arranque en techo): Y ≈ 20,1–20,5.
- **Patinillo grande P4** (detrás de los ascensores), X 5,26–8,56. Planta tipo Y 113,98–115,06, sótano Y 27,61–28,69, cubierta Y 139,69–140,77. Úsalo **solo** para las tuberías del circuito de las bombas de calor (cubierta ↔ cuarto ACS).

## 2. Capas
| Capa | Color | Tipo de línea | Contenido |
|---|---|---|---|
| F-AF | 5 (azul) | Continuous | Tuberías de agua fría |
| F-ACS | 1 (rojo) | Continuous | Tuberías de ACS (ida) |
| F-ACS-RET | 6 (magenta) | DASHED | Retorno de ACS |
| F-EQUIPOS | 30 (naranja) | Continuous | Aljibes, bombas, calderín, acumuladores, BdC, caldera |
| F-VALV | 7 | Continuous | Llaves, retenciones, filtro, contador, reductora |
| F-TEXTO | 7 | — | Rótulos (ID tramo + diámetro) |
| F-COTAS | 8 | — | Medidas de cuartos |
| F-CAJETIN | 7 | — | Marco, cajetín y leyenda |
| F-OCULTO | 5 / 1 | DASHED | Tubería colgada bajo forjado vista desde la planta superior, o enterrada |

## 3. Planta SÓTANO (Y 13,5 – 29,0)
**Cuarto AF** (nuevo, cerrar con tabique de 10 cm): X 8,75–15,20, Y 24,30–29,00, entre pilares, junto al muro Norte. Puerta de **dos hojas de 0,90 + 0,90 m** al garaje en la cara Sur. Dentro dibuja:
- **2 aljibes** de 4.000 l, Ø 2,12 m y H 1,465 m, en paralelo. Cada uno con su válvula de flotador y sus llaves de aislamiento de entrada y salida (ver esquema "Cuestiones" del profesor).
- **Grupo de presión de velocidad variable: 3 bombas** (2 en servicio + 1 de reserva). Bancada de 0,4 × 0,8 m por bomba. Cada bomba con llaves de aislamiento en aspiración e impulsión y retención en la impulsión.
- **Calderín de 150 l**, Ø ≈ 0,55 m.
- **Conjunto filtro DN100** con llaves de aislamiento: 0,4 × 1,2 m.
- **Colector de directo** con llave de aislamiento.
- **Sumidero** sifónico en el suelo.
- Acota el cuarto.

**Cuarto ACS** (nuevo): X 15,20–21,70, Y 24,30–29,00, puerta doble de 1,80 m. Dentro dibuja:
- **4 acumuladores** de unos 2.500 l, Ø ≈ 1,40 m.
- **Caldera de gas** de apoyo de unos 87 kW.
- **Bomba de recirculación de ACS** (doble).
- **Válvula reductora de presión** en la salida de ACS baja (tarado 38 mca), con manómetros y llaves.
- Antirretorno en la entrada de AF a la producción.
- Sumidero.
- Acota el cuarto.

**Acometida y alimentación** (techo del sótano, tubería colgada):
- **Acometida G1:** PE 125x11.4. Va desde la red general de abastecimiento (línea "red abastecimiento" por la calle Oeste, X ≈ −10,9 en el marco de PB) hasta la **hornacina del contador en la fachada Oeste, en PB (X 2,0 ; Y 62,0)**. Dibújala en la planta baja, con la llave de toma en carga y la llave de registro en acera.
- **En la hornacina:** llave de aislamiento, **contador general DN100**, grifo de prueba, **válvula de retención general DN100** y llave de aislamiento (orden del esquema del profesor).
- **Tubo de alimentación G2:** PE 125x11.4. Entra al sótano por (2,2 ; 19,1), sigue hacia el Este por Y 19,1 hasta X 9,5 y sube hasta el cuarto AF (9,5 ; 24,3). Pon una llave de corte general justo a la entrada del edificio. Longitud total ≈ 14 m.

**Distribución en el sótano** (colgada del techo; dibuja las líneas paralelas separadas 0,15 m):
| ID | Tramo | Diámetro | Recorrido |
|---|---|---|---|
| D0 | Colector directo | MC 90x6 | dentro del cuarto AF |
| DL1 | Directo → patinillo O | MC 90x6 | cuarto AF → Oeste por Y 21,8 → X 3,3 → norte a (3,3 ; 22,3). ≈12 m |
| DR1 | Directo → patinillo E | MC 90x6 | cuarto AF → Este por Y 21,0 → X 50,1 → (50,1 ; 20,1). ≈48 m |
| BV0 | Impulsión grupo | MC 90x6 | colector del grupo |
| BL1 | Bombeo → patinillo O | MC 90x6 | paralelo a DL1 |
| BR1 | Bombeo → patinillo E | MC 90x6 | paralelo a DR1 |
| BC1 | Grupo → producción ACS | MC 90x6 | cuarto AF → cuarto ACS, ≈8 m |
| CAL1 / CAR1 | ACS alta → patinillos O / E | MC 75x5 / MC 75x5 | desde el cuarto ACS, paralelo a los anteriores |
| CB0, CBL1 / CBR1 | ACS baja (tras reductora) → patinillos O / E | MC 90x6 / MC 90x6 | ídem |
| Retornos | ACS alta y baja | MC 32x3 | paralelos, a los acumuladores |
| PB (AF) | Ramal colgado que alimenta la planta baja | ver tabla | ver apartado 4 |

En la base de **cada montante** pon una llave de corte, una válvula de retención y un grifo de vaciado.

## 4. PLANTA BAJA (Y 56,3 – 72,0)
La PB se alimenta **desde el techo del sótano**: las tuberías suben atravesando el forjado bajo cada local. En el plano de PB dibuja esos ramales con **trazo discontinuo** (van colgados bajo el forjado de la planta dibujada), con su subida a cada local. Ramales AF / ACS:

| ID | Tramo | AF | ACS (ID+C) |
|---|---|---|---|
| PBW | Cuarto → aseos públicos (X 3–9) | MC 40x3.5 | MC 26x3 |
| PBE1 | Cuarto → barra (X ≈ 16,6) | MC 63x4.5 | MC 50x4 |
| PBE2 | Barra → vestuarios (X ≈ 25) | MC 63x4.5 | MC 50x4 |
| PBE3 | Vestuarios → cocina/c. frío/basuras (X ≈ 34) | MC 63x4.5 | MC 50x4 |
| PBE4 | Cocina → oficio PB (X ≈ 39) | MC 50x4 | MC 50x4 |
| PBE5 | Oficio → habitaciones PB (X ≈ 44,5) | MC 50x4 | MC 50x4 |
| PBE6 | Derivación a cada habitación | MC 32x3 | MC 26x3 |

Habitaciones de PB: 010, 008, 006, 004 y 002 (fila Norte) y 003, 001 (fila Sur), X 37–51. **004 y 006 son adaptadas** (ducha). En PB dibuja también la **hornacina del contador** y la **acometida** (apartado 3), y los dos patinillos con sus montantes en círculo.

## 5. PLANTA TIPO (Y 100,0 – 115,1) — vale para P1 a P11
26 habitaciones por planta: 24 estándar (lavabo, bañera, bidé, inodoro) y 2 adaptadas (lavabo, ducha, inodoro). Además hay un **oficio** con fregadero y vertedero en la fila Sur, X ≈ 38,3–41.

**Montantes**: dibújalos como círculos en los patinillos y rotúlalos.
- Patinillo O: AF directo, AF bombeo, ACS alta, ACS baja, retorno ACS alta y retorno ACS baja.
- Patinillo E: los mismos seis.

**Plantas 1 a 7: suministro en DIRECTO.**
- La AF sale del montante de directo.
- La ACS sale del montante de ACS baja.
- Los montantes de bombeo y de ACS alta pasan de largo sin derivar.

**Plantas 8 a 11: suministro con BOMBEO.**
- La AF sale del montante de bombeo.
- La ACS sale del montante de ACS alta.

En el plano de planta tipo incluye una **tabla de diámetros de montante por planta**:

| Planta (tramo hasta) | AF directo O / E | ACS baja O / E | AF bombeo O / E | ACS alta O / E |
|---|---|---|---|---|
| P1 | 90x6 / 90x6 | 90x6 / 90x6 | 90x6 / 90x6 | 75x5 / 75x5 |
| P2 | 90x6 / 90x6 | 75x5 / 75x5 | 90x6 / 90x6 | 75x5 / 75x5 |
| P3 | 90x6 / 90x6 | 75x5 / 75x5 | 90x6 / 90x6 | 75x5 / 75x5 |
| P4 | 90x6 / 90x6 | 75x5 / 75x5 | 90x6 / 90x6 | 75x5 / 75x5 |
| P5 | 75x5 / 75x5 | 75x5 / 75x5 | 90x6 / 90x6 | 75x5 / 75x5 |
| P6 | 75x5 / 75x5 | 63x4.5 / 63x4.5 | 90x6 / 90x6 | 75x5 / 75x5 |
| P7 | 63x4.5 / 63x4.5 | 50x4 / 50x4 | 90x6 / 90x6 | 75x5 / 75x5 |
| P8 | — | — | 90x6 / 90x6 | 75x5 / 75x5 |
| P9 | — | — | 75x5 / 75x5 | 75x5 / 75x5 |
| P10 | — | — | 75x5 / 75x5 | 63x4.5 / 63x4.5 |
| P11 | — | — | 63x4.5 / 63x4.5 | 50x4 / 50x4 |

Todo en multicapa (MC).

**Ramal de planta** por el falso techo del pasillo:
- AF en Y 107,85, ACS en Y 107,65 y retorno ACS en Y 107,45.
- Del patinillo O al pasillo baja por X 3,0. Del patinillo E sube por X 50,1.

*Ramal Oeste* (sirve a las habitaciones con baño entre X 3 y X 27). Nudos en X 3,0 → 6,0 → 12,4 → 18,5 → 25,0:

| ID | Tramo | AF | ACS |
|---|---|---|---|
| RL1 | Patinillo → nudo X 6,0 (pareja Sur B1) | MC 63x4.5 | MC 50x4 |
| RL2 | X 6,0 → X 12,4 (parejas T1 Norte y B2 Sur, con habitación adaptada) | MC 63x4.5 | MC 50x4 |
| RL3 | X 12,4 → X 18,5 | MC 63x4.5 | MC 50x4 |
| RL4 | X 18,5 → X 25,0 | MC 50x4 | MC 40x3.5 |
| RL5 | Derivación a cada habitación (hasta el muro del baño) | MC 32x3 | MC 26x3 |

*Ramal Este* (habitaciones con baño entre X 29 y X 51, más el oficio). Nudos en X 50,1 → 50,0 → 44,5 → 39,6 (oficio) → 38,0 → 31,5:

| ID | Tramo | AF | ACS |
|---|---|---|---|
| RR1 | Patinillo → X 50,0 (T7) | MC 63x4.5 | MC 50x4 |
| RR2 | → X 44,5 | MC 63x4.5 | MC 50x4 |
| RR3 | → X 39,6 (oficio) | MC 63x4.5 | MC 50x4 |
| RR4 | → X 38,0 | MC 50x4 | MC 50x4 |
| RR5 | → X 31,5 | MC 50x4 | MC 40x3.5 |
| RR6 | Derivación a cada habitación | MC 32x3 | MC 26x3 |

**Derivaciones a las habitaciones:**
- En cada nudo, derivación a cada baño a X = nudo ± 0,9 m.
- Fila Norte: baños con muro al pasillo en Y 108,5. Fila Sur: muro en Y 107,0.
- **Llave de corte de AF y de ACS en la entrada de cada habitación.**

**Interior del baño estándar** (dibújalo al menos en una habitación de cada fila; en las demás basta la derivación con su llave):

| ID | Tramo | AF | ACS (ID) |
|---|---|---|---|
| H1 | Entrada → derivación bañera | MC 40x3.5 | MC 32x3 (HC1) |
| H2 | → derivación inodoro | MC 32x3 | — |
| H3 | → derivación bidé | MC 32x3 | MC 26x3 (HC2) |
| H4 | → lavabo | MC 20x2 | MC 16x2 (HC3) |
| H5 | Bañera | MC 32x3 | MC 32x3 (HC4) |

Cada aparato lleva su **llave de escuadra**. El retorno de ACS llega hasta la entrada de cada cuarto húmedo, y nunca a más de 5 m de cualquier punto de consumo.

## 6. PLANTA CUBIERTA (Y 125,7 – 141,2)
- **Bombas de calor (aerotermia)** de unos 87 kW en total (por ejemplo 2 × 45 kW). Unidades exteriores en X 20–30, Y 130–136, sobre bancada antivibratoria y separadas del borde.
- Circuito BdC ↔ acumuladores del sótano por el **patinillo P4**: ida y retorno, capa F-EQUIPOS o una capa nueva F-AEROTERMIA.
- Montantes O y E rematados en la última planta, con purgadores.

## 7. Planos y esquemas a generar (presentaciones / layouts)
Todos con **cajetín**, que debe llevar:
- Equipo **ET48**
- Capitán: **[RELLENAR NOMBRE]**
- Nº de plano, nombre del plano y escala.

Además, cada plano lleva una **leyenda de símbolos** usados (tubería AF, ACS, retorno, llave de corte, retención, filtro, contador, reductora, bomba, calderín, aljibe, acumulador, BdC, caldera, llave de escuadra, montante). Los rótulos deben ser **legibles a la escala**: a 1/100, unos 2,5 mm de papel, es decir 0,25 m en modelo.

| Nº | Plano | Escala |
|---|---|---|
| F-01 | Esquema de principio AF + ACS: desde la red, hornacina, cuarto AF (aljibes, grupo), directo PB-P7, bombeo P8-P11, producción ACS, reductora, ACS baja y alta, retornos. Con los ID de tramo y los diámetros de las tablas | s/e |
| F-02 | Planta sótano AF/ACS, con cuartos acotados | 1/100 (o 1/50 en el detalle de cuartos) |
| F-03 | Planta baja AF/ACS | 1/100 |
| F-04 | Planta tipo AF/ACS + tabla de montantes por planta | 1/100 |
| F-05 | Planta cubierta (BdC, salida P4) | 1/100 |
| F-06 | Isométrico de un baño estándar (AF azul, ACS roja, diámetros, llaves) | 1/20 |

Formato: A1 o A2. Si en A3, usar plano guía + recuadro sombreado del detalle a escala normalizada (Anexo V del enunciado). Exporta cada presentación a **PDF**.

## 8. Comprobaciones antes de terminar
- Cada tramo tiene **ID + material + diámetro** visible (ej.: `RL1 · MC 63x4.5`) y coincide con la hoja `Tramos` del Excel.
- AF en azul y ACS en rojo en todas las plantas. El retorno, discontinuo.
- Montantes en círculo en todas las plantas que atraviesan.
- No hay tuberías por dentro de habitaciones ajenas: solo por zonas comunes hasta la llave de entrada.
- Ninguna tubería atraviesa ascensores ni escaleras.
- Guardado en DWG 2013/2016 + PDFs.

## 9. Informe final que debes devolverme
1. Lista de archivos generados.
2. **Tabla de tramos cuya longitud real dibujada difiera más de un 10 %** de la usada en el cálculo (para recalcular el Excel). Longitudes de cálculo, en m:
   - General y sótano: G1 14 · G2 14 · DL1 12 · DR1 48 · BL1 12 · BR1 48 · BC1 8 · CAL1 y CBL1 20,7 · CAR1 y CBR1 39.
   - Ramales de planta tipo: RL1 3,9 · RL2 6,4 · RL3 6,1 · RL4 6,5 · RL5 1,65 · RR1 1,0 · RR2 5,5 · RR3 4,9 · RR4 1,6 · RR5 6,5 · RR6 1,65.
   - Planta baja: PBW 12 · PBE1 4 · PBE2 8,4 · PBE3 9 · PBE4 5 · PBE5 5,5 · PBE6 6.
3. Cualquier desplazamiento del trazado respecto a las coordenadas indicadas, y por qué.
4. Lo que no hayas podido hacer.
