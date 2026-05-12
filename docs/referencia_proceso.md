# Referencia del Proceso — Índice de Caminabilidad Av. Roosevelt

**ITT Cali Inteligente · Equipo de Gobierno de Datos**
**Fecha de inicio:** 11 de mayo de 2026
**Repositorio:** https://github.com/j0rg3c45/indice-caminabilidad-roosevelt.git

---

## 1. Objetivo del Proyecto

Evaluar el impacto de la intervención urbana en Av. Roosevelt (Cali, Colombia)
mediante un índice de caminabilidad basado en la red peatonal de OpenStreetMap.

El proyecto establece una línea base pre-intervención y define criterios para
un territorio espejo (grupo de control) que permita comparaciones válidas
durante el período 2026–2028.

---

## 2. Estructura del Repositorio

```
indice-caminabilidad-roosevelt/
├── data/
│   ├── raw/                          # Copias de trabajo (GeoJSON + Shapefile)
│   ├── processed/                    # Datos procesados
│   ├── external/                     # Parámetros territorio espejo
│   └── itt_roosevelt/                # Datos fuente originales
│       └── Roosevelt/
│           ├── Geojson_Roosevelt/    # GeoJSON (input principal del notebook)
│           └── shape_Roosevelt/      # Shapefiles equivalentes
├── notebooks/
│   ├── caminabilidad_roosevelt_v2.ipynb    # Notebook principal
│   └── ejemplo_04_itt_pulmon_oriente_2026_v2.ipynb  # Referencia ITT
├── notebooks_py/
│   └── caminabilidad_roosevelt.py          # Script modular
├── agent/
│   ├── context/                      # Contexto del agente
│   ├── knowledge_base/               # Base de conocimiento
│   └── prompts/                      # Prompts del sistema
├── outputs/
│   ├── results/                      # CSVs con métricas
│   └── figures/                      # Mapas generados
├── docs/
│   └── referencia_proceso.md         # Este archivo
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 3. Sistema de Referencia Geoespacial

| Propósito | CRS | EPSG |
|-----------|-----|------|
| Trabajo general (visualización, OSMnx, Folium) | WGS84 | 4326 |
| Cálculos de área y distancia | Colombia Bogotá Zone | 3116 |

Reglas implementadas en el notebook:
- Si un GeoJSON no tiene CRS definido → se asigna WGS84
- Si tiene un CRS diferente a 4326 → se reproyecta a WGS84
- Para cálculos métricos → se proyecta temporalmente a EPSG:3116

---

## 4. Datos Geoespaciales Disponibles

Ubicación: `data/itt_roosevelt/Roosevelt/Geojson_Roosevelt/`

| Archivo | Descripción |
|---------|-------------|
| Geojson_tramos_Roosevelt_Buffer_100.geojson | Polígono de intervención (buffer 100m) |
| Geojson_tramos_Roosevelt.geojson | Tramos del corredor sin buffer |
| red_peatonal_osm_roosevelt.geojson | Red peatonal OSM (con todos los vértices, simplify=False) |
| BD_SINIESTROS_2023_2025_COMUNA_BARRIO_4326_Roosevelt.geojson | Siniestros viales |
| COMPARENDOS_2023_2025_Roosevelt.geojson | Comparendos de tránsito |
| HOMICIDIOS_2023_2025_Roosevelt.geojson | Homicidios |
| HURTOS_2023_2025_Roosevelt.geojson | Hurtos |
| Sedes_educativas_oficiales_Roosevelt.geojson | Sedes educativas |
| VBG_2025_Roosevelt.geojson | Violencia basada en género |
| VIOLENCIA_INTRAFAMILIAR_2023_2025_Roosevelt.geojson | Violencia intrafamiliar |

---

## 5. Métricas de Línea Base (11 mayo 2026)

| Indicador | Valor |
|-----------|-------|
| Área del polígono | 42.9 ha (429,014 m²) |
| Intersecciones peatonales | 232 |
| Longitud red peatonal | 31.78 km |
| Longitud promedio segmento | 41.7 m |
| Densidad de calle | 74.07 km/km² |
| Nodos OSM | 246 |
| Segmentos OSM | 762 |

Fuente: OpenStreetMap via OSMnx (network_type='walk')

---

## 6. Pipeline del Notebook

El notebook `caminabilidad_roosevelt_v2.ipynb` ejecuta:

1. Instalación de dependencias (osmnx, geopandas, folium, seaborn)
2. Configuración de CRS (WGS84 trabajo, EPSG:3116 cálculos)
3. Detección de entorno (Colab clona el repo / local usa rutas relativas)
4. Carga del polígono buffer 100m + validación CRS → WGS84
5. Descarga de red peatonal desde OSM (simplify=False, conserva todos los vértices)
6. Cálculo de métricas + exportación de red peatonal como GeoJSON en zona de estudio
7. Carga de datasets complementarios (todos normalizados a WGS84)
8. Mapa estático de la red peatonal
9. Mapa interactivo con:
   - Capas base: CartoDB, Google Streets, Google Satélite, Google Híbrido
   - Red peatonal OSM (verde, descargada de OpenStreetMap)
   - Tramos Roosevelt — eje del corredor (rojo)
   - Polígono de intervención buffer 100m (azul)
   - Capas de datos: siniestros, comparendos, homicidios, hurtos, sedes, VBG, VIF
10. Resumen de indicadores complementarios (densidad por ha)
11. Exportación de resultados a CSV
12. Visualización del mapa como imagen en el notebook

---

## 7. Territorio Espejo (Control)

Criterios documentados en `data/external/parametros_territorio_espejo.txt`:

- Corredor vial de 500–700 m de longitud
- Buffer de 100 m a cada lado del eje
- Área resultante entre 38–48 hectáreas
- Uso mixto comercial-residencial
- Sin intervención planificada 2026–2028
- Densidad de intersecciones entre 400–700 int/km²

---

## 8. Tecnologías

| Herramienta | Uso |
|-------------|-----|
| Jupyter Notebook / Google Colab | Entorno principal de desarrollo y análisis |
| Python 3.10+ | Lenguaje principal |
| uv | Gestor de paquetes y entornos virtuales (local) |
| OSMnx 2.0 | Red peatonal desde OpenStreetMap |
| GeoPandas | Datos geoespaciales |
| Folium | Mapas interactivos (Esri Streets/Satélite, capas) |
| Matplotlib | Mapas estáticos |
| Pandas / NumPy | Procesamiento tabular |

---

## 9. Cómo Ejecutar

### Google Colab
1. Abrir `notebooks/caminabilidad_roosevelt_v2.ipynb` en Colab
2. Ejecutar todas las celdas — el repo se clona automáticamente

### Local (con uv)
```bash
git clone https://github.com/j0rg3c45/indice-caminabilidad-roosevelt.git
cd indice-caminabilidad-roosevelt
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt

# Pipeline completo (red peatonal + métricas + mapa)
uv run notebooks_py/caminabilidad_roosevelt.py

# Solo descargar la red peatonal como GeoJSON
uv run notebooks_py/descargar_red_peatonal.py
```

---

## 10. Historial de Commits

| Commit | Descripción |
|--------|-------------|
| `019bb74` | Estructura inicial del proyecto |
| `a2a2b7c` | README limpio sin badges |
| `9a949bd` | Notebook apunta a data/itt_roosevelt |
| `7676955` | Integración de datos GeoJSON + mapa interactivo |
| `615ff47` | Normalización a WGS84 (EPSG:4326) |
| `dc1f322` | Rutas Colab actualizadas al nuevo repo |
| `fd0cdf2` | Estructura agent/ + notebook ejemplo ITT |
| `19e3681` | Fix ox.projection.default_crs (OSMnx 2.x) |
| `f911430` | Celda 12 muestra mapa como imagen |
| `2fdfe27` | Capas Google Streets/Satélite/Híbrido en mapa |
| `1f95475` | Capa de tramos Roosevelt (eje) en mapa |
| `34d6505` | Red peatonal OSM en mapa interactivo + export GeoJSON |

---

## 11. Próximos Pasos

- [ ] Identificar y validar territorio espejo
- [ ] Calcular línea base del territorio espejo
- [ ] Medición post-intervención (2027–2028)
- [ ] Análisis comparativo (diferencia en diferencias)
- [ ] Integración con ITT completo (5 dimensiones)
