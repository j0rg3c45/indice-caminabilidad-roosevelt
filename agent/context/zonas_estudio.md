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
| Área del polígono | 7.47 ha (74,692 m²) |
| Intersecciones peatonales | 26 |
| Longitud red peatonal | 3.6 km |
| Longitud promedio segmento | 54.6 m |
| Densidad de calle | 48.26 km/km² |
| Densidad de intersecciones | 348 int/km² |
| Nodos OSM | 26 |
| Segmentos OSM | 66 |

Eventos complementarios: comparendos 3.741, hurtos 663, violencia intrafamiliar 82,
homicidios 27, censo arbóreo 874.

## Notas de comparabilidad

- Roosevelt y Barrio Obrero usan la misma metodología de caminabilidad (red peatonal
  OSM con `simplify=False`, mismas métricas), pero con unidad de análisis distinta:
  corredor con buffer vs polígono de barrio.
- Las densidades (por hectárea, km/km², int/km²) permiten comparar zonas de tamaño
  diferente de forma normalizada.
