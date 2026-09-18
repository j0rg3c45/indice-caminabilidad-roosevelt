# Zonas de estudio — Índice de Caminabilidad

## Av. Roosevelt

- Estado: implementado (notebook principal).
- Notebook: `notebooks/caminabilidad_roosevelt_v2.ipynb`
- Script: `notebooks_py/caminabilidad_roosevelt.py`
- Unidad de análisis: corredor vial con buffer de 100 m.
- Territorio espejo: sí (Calle 5 y Calle 7 como controles candidatos).
- Datos fuente: `data/itt_roosevelt/Roosevelt/Geojson_Roosevelt/` (versionado como `Roosevelt.zip`).
- Datasets complementarios: siniestros, comparendos, homicidios, hurtos, sedes educativas, VBG, VIF.
- Criterios de territorio espejo (`data/external/parametros_territorio_espejo.txt`):
  corredor 500–700 m, buffer 100 m, área 38–48 ha, densidad de intersecciones 400–700 int/km².

### Métricas de línea base — Roosevelt (11 mayo 2026)

| Indicador | Valor |
|---|---|
| Área del polígono | 42.9 ha (429,014 m²) |
| Intersecciones peatonales | 232 |
| Longitud red peatonal | 31.78 km |
| Longitud promedio segmento | 41.7 m |
| Densidad de calle | 74.07 km/km² |
| Nodos OSM | 246 |
| Segmentos OSM | 762 |

## Barrio Obrero

- Estado: implementado.
- Notebook: `notebooks/caminabilidad_barrio_obrero_v2.ipynb`
- Script: `notebooks_py/caminabilidad_barrio_obrero.py`
- Unidad de análisis: **polígono único de barrio** (no corredor, no buffer).
- Territorio espejo: no aplica.
- Datos fuente: `data/Geojson_Barrio_Obrero/` (versionado como `Geojson_Barrio_Obrero.zip`).
- El polígono viene en CRS `ESRI:103599` (MAGNA-SIRGAS CMT12) y se reproyecta a WGS84 al cargar.
- Datasets complementarios (2023–2026 T1): comparendos, homicidios, hurtos, violencia
  intrafamiliar y censo arbóreo (indicador adicional propio de esta zona).

### Métricas de línea base — Barrio Obrero (18 septiembre 2026)

| Indicador | Valor |
|---|---|
| Área del polígono | 37.73 ha (377,329 m²) |
| Intersecciones peatonales | 233 |
| Longitud red peatonal | 26.93 km |
| Longitud promedio segmento | 41.6 m |
| Densidad de calle | 71.38 km/km² |
| Densidad de intersecciones | 618 int/km² |
| Nodos OSM | 233 |
| Segmentos OSM | 648 |

Eventos complementarios: comparendos 3.741, hurtos 663, violencia intrafamiliar 82,
homicidios 27, censo arbóreo 874.

El polígono se carga directamente desde `data/Geojson_Barrio_Obrero/Geojson_Barrio_Obrero.zip`
(prefijo `zip://`). Nota: este polígono (37.73 ha) reemplazó al polígono previo de 7.47 ha;
los eventos en `nueva_data/` fueron filtrados contra el polígono anterior, por lo que un
re-filtrado contra el nuevo polígono está pendiente si se requiere exactitud en conteos.

### Estructura actual del notebook de Barrio Obrero

- Celda de **glosario** al inicio (siglas y unidades: int/km², km/km², CRS, OSM, IDESC, etc.).
- Celda 4 carga el polígono desde el ZIP (`zip://`).
- Celda 9 (mapa interactivo): incluye polígono, **tramo/eje** (`tramo_Barrio_obrero.geojson`,
  ~553 m), red peatonal OSM, nodos, **capa de mapa de calor** de intersecciones (HeatMap) y
  capas de eventos; todo activable desde el control de capas.
- Gráfico 2: heatmap KDE de intersecciones en 2 paneles (borde del polígono y con **ejes
  viales IDESC** de fondo).
- Gráfico 5 (posición morfológica): compara Barrio Obrero vs **Comuna 9** en el scatter
  (longitud de segmento vs densidad de intersecciones), con bandas de referencia
  (400–700 int/km²) y umbral de salud pública (~100 int/km²). Incluye una celda markdown con
  contexto internacional/nacional y referencias (US EPA EnviroAtlas, IPEN/U. Melbourne,
  Queensland, Stangl 2015).
- Celda 14B: panel de las 5 métricas de caminabilidad de la zona.
- Celda 14C: comparación Barrio Obrero vs Comuna 9 (descarga red OSM de la comuna, tabla,
  gráfica y CSV `comparacion_barrio_obrero_vs_comuna9.csv`).
- Celda 14D: **Índice de Caminabilidad (0–100)**. Normaliza 3 indicadores con `ref_min/ref_max`
  fijos (no min-max relativo) y los pondera. Referencias: densidad de intersecciones
  (100–800, directo), densidad de calle (20–90, directo), longitud de segmento (40–150,
  inverso). Pesos por defecto 0.45 / 0.35 / 0.20 (configurables en `PESOS`). Resultado:
  Barrio Obrero **78.7** vs Comuna 9 **92.7**. Exporta
  `indice_caminabilidad_barrio_obrero_vs_comuna9.csv`.

### Comparación caminabilidad — Barrio Obrero vs Comuna 9

| Métrica | Barrio Obrero | Comuna 9 |
|---|---|---|
| Área (ha) | 37.73 | 290.38 |
| Intersecciones | 233 | 2.255 |
| Longitud red (km) | 26.93 | 227.52 |
| Long. prom. segmento (m) | 41.6 | 34.8 |
| Densidad calle (km/km²) | 71.38 | 78.35 |
| Densidad intersecciones (int/km²) | 617 | 777 |

Las densidades (km/km², int/km²) son las métricas comparables entre zonas de distinto tamaño.
Barrio Obrero y la Comuna 9 están por encima del umbral de salud pública (~100 int/km²).

### Capas base de Cali (IDESC)

`data/GeoJson_IDESC.zip` — barrios (339), comunas (22), nomenclatura vial (11.295), en
EPSG:6249. Se usan para extraer el polígono de la Comuna 9 (comparación) y como contexto
en los mapas/gráficos.

## Notas de comparabilidad

- Roosevelt y Barrio Obrero usan la misma metodología de caminabilidad (red peatonal
  OSM con `simplify=False`, mismas métricas), pero con unidad de análisis distinta:
  corredor con buffer vs polígono de barrio.
- Las densidades (por hectárea, km/km², int/km²) permiten comparar zonas de tamaño
  diferente de forma normalizada.
