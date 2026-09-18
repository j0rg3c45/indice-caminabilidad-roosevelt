# Glosario — Índice de Caminabilidad

| Término | Definición |
|---|---|
| Caminabilidad | Grado en que el entorno construido favorece el desplazamiento a pie, medido aquí con métricas topológicas de la red peatonal |
| Red peatonal | Grafo de calles caminables descargado de OpenStreetMap con OSMnx (`network_type='walk'`) |
| OSMnx | Librería de Python para descargar y analizar redes de calles desde OpenStreetMap |
| Nodo | Vértice del grafo peatonal (típicamente una intersección o extremo de segmento) |
| Segmento (edge) | Tramo de calle peatonal entre dos nodos |
| Intersección peatonal | Nodo con más de dos calles conectadas (`street_count > 2`) |
| Densidad de calle | Longitud total de red por unidad de área (km/km²) |
| Densidad de intersecciones | Número de intersecciones por unidad de área (int/km²) |
| `simplify=False` | Opción de OSMnx que conserva todos los vértices intermedios de cada segmento |
| Buffer | Zona de influencia alrededor de un eje vial (Roosevelt usa 100 m a cada lado) |
| Corredor | Eje vial analizado con buffer (unidad de análisis de Roosevelt) |
| Polígono de barrio | Unidad de análisis de Barrio Obrero (área completa del barrio, sin buffer) |
| Territorio espejo | Zona de control candidata para comparación (Calle 5, Calle 7 en Roosevelt) |
| Línea base | Medición pre-intervención usada como referencia para evaluar impacto futuro |
| CRS | Sistema de referencia de coordenadas |
| WGS84 (EPSG:4326) | CRS de trabajo del proyecto para datos y visualización |
| EPSG:3116 | CRS proyectado (Colombia) usado solo para cálculos de área y distancia |
| ESRI:103599 | CRS de origen del polígono de Barrio Obrero (MAGNA-SIRGAS CMT12), se reproyecta a WGS84 |
| Densidad por hectárea | Total de registros de un dataset dividido por el área en hectáreas |
| Censo arbóreo | Inventario de árboles; indicador complementario propio de Barrio Obrero |
