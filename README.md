# Índice de Caminabilidad — Av. Roosevelt, Cali

**ITT Cali Inteligente · Equipo de Gobierno de Datos**

Proyecto de evaluación de impacto de la intervención urbana en Av. Roosevelt
(Cali, Colombia). Calcula métricas de caminabilidad usando la red peatonal de
OpenStreetMap como línea base pre-intervención.

**Repositorio:** https://github.com/j0rg3c45/indice-caminabilidad-roosevelt.git

---

## Descripción

Este repositorio contiene el pipeline de análisis para:

1. Calcular indicadores de caminabilidad (intersecciones, densidad de red,
   longitud de segmentos) usando OSMnx.
2. Establecer la **línea base** (mayo 2026) antes de la intervención física.
3. Integrar datos geoespaciales complementarios (siniestros, hurtos, homicidios,
   comparendos, sedes educativas, VBG, VIF).
4. Generar mapas interactivos con capas de Google Streets y red peatonal OSM.
5. Definir criterios para seleccionar un **territorio espejo** (grupo control).
6. Permitir mediciones futuras comparables (2026–2028).

---

## Sistema de Referencia Geoespacial

| Propósito | CRS | EPSG |
|-----------|-----|------|
| Trabajo general (visualización, OSMnx, Folium) | WGS84 | 4326 |
| Cálculos de área y distancia | Colombia Bogotá Zone | 3116 |

---

## Estructura del Proyecto

```
├── data/
│   ├── raw/                          # Copias de trabajo
│   ├── processed/                    # Datos procesados
│   ├── external/                     # Parámetros territorio espejo
│   └── itt_roosevelt/Roosevelt/
│       └── Geojson_Roosevelt/        # GeoJSON fuente (input principal)
├── notebooks/
│   └── caminabilidad_roosevelt_v2.ipynb  # Notebook principal
├── notebooks_py/
│   └── caminabilidad_roosevelt.py        # Script modular
├── agent/
│   ├── context/                      # Contexto del agente
│   ├── knowledge_base/               # Base de conocimiento
│   └── prompts/                      # Prompts del sistema
├── outputs/
│   ├── results/                      # CSVs y GeoJSON de resultados
│   └── figures/                      # Mapas generados
├── docs/
│   └── referencia_proceso.md         # Documentación del proceso
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Cómo Ejecutar

### Google Colab (recomendado)

1. Abrir `notebooks/caminabilidad_roosevelt_v2.ipynb` en Google Colab.
2. Ejecutar todas las celdas — el repo se clona automáticamente.
3. Los mapas interactivos y resultados se generan inline.

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

## Pipeline del Notebook

1. Instalación de dependencias
2. Configuración de CRS (WGS84 trabajo / EPSG:3116 cálculos)
3. Detección de entorno (Colab / local) y carga de datos
4. Carga del polígono buffer 100m + validación CRS
5. Descarga de red peatonal desde OpenStreetMap (simplify=False, conserva vértices)
6. Cálculo de métricas + exportación red peatonal como GeoJSON
7. Carga de datasets complementarios (normalizados a WGS84)
8. Mapa estático de la red peatonal
9. Mapa interactivo (Esri/Google Streets + red peatonal OSM + capas de datos)
10. Indicadores complementarios (densidad por hectárea)
11. Exportación de resultados a CSV
12. Visualización del mapa como imagen
13. Configuración de zonas espejo (Calle 5 y Calle 7)
14. Cálculo de caminabilidad para cada espejo + conteo de eventos
15. Comparación Roosevelt vs Espejo + validación de criterios
16. Gráfico comparativo de conectividad (scatter plot)
17. Exportación de CSVs comparativos

---

## Scripts Disponibles

| Script | Comando | Descripción |
|--------|---------|-------------|
| `caminabilidad_roosevelt.py` | `uv run notebooks_py/caminabilidad_roosevelt.py` | Pipeline completo Roosevelt: red peatonal + métricas + mapa |
| `descargar_red_peatonal.py` | `uv run notebooks_py/descargar_red_peatonal.py` | Solo descarga red peatonal y guarda GeoJSON |
| `graficos_base_caminabilidad.py` | `uv run notebooks_py/graficos_base_caminabilidad.py` | 6 gráficos base de caminabilidad |
| `caminabilidad_espejo.py` | `uv run notebooks_py/caminabilidad_espejo.py` | Caminabilidad territorios espejo + comparación vs Roosevelt |
| `convertir_poligonos_espejo.py` | `uv run notebooks_py/convertir_poligonos_espejo.py` | Convierte polígonos espejo de .shp a .geojson (WGS84) |

---

## Métricas de Línea Base (11 mayo 2026)

| Indicador | Valor |
|-----------|-------|
| Área del polígono | 42.9 ha |
| Intersecciones peatonales | 232 |
| Longitud red peatonal | 31.78 km |
| Longitud promedio segmento | 41.7 m |
| Densidad de calle | 74.07 km/km² |

---

## Mapa Interactivo — Capas Disponibles

**Capas base (se alternan):**
- CartoDB Claro
- OpenStreetMap
- Esri Satélite
- Google Streets (subdomains: mt0–mt3)
- Google Satélite (subdomains: mt0–mt3)

Nota: los tiles de Google usan el formato `http://{s}.google.com/vt/lyrs=...`
con `subdomains=['mt0', 'mt1', 'mt2', 'mt3']` para compatibilidad con Folium/Leaflet.

**Capas de datos (se superponen):**
- Red peatonal OSM — líneas (verde)
- Vértices de líneas — todos los puntos de cada segmento (oscuro)
- Nodos (intersecciones) — puntos rojos
- Tramos Roosevelt — eje del corredor (rojo)
- Polígono intervención — buffer 100m (azul)
- Siniestros, Comparendos, Homicidios, Hurtos, Sedes, VBG, VIF

---

## Territorio Espejo (Control)

Criterios en `data/external/parametros_territorio_espejo.txt`:

- Corredor de 500–700 m, buffer 100 m, área 38–48 ha
- Uso mixto comercial-residencial
- Sin intervención planificada 2026–2028
- Densidad de intersecciones entre 400–700 int/km²

---

## Tecnologías

- **Jupyter Notebook / Google Colab** — Entorno principal de desarrollo y análisis
- **uv** — Gestor de paquetes y entornos virtuales (ejecución local)
- **OSMnx** — Red peatonal desde OpenStreetMap
- **GeoPandas** — Datos geoespaciales
- **Folium** — Mapas interactivos (Esri Streets/Satélite, capas)
- **Matplotlib** — Mapas estáticos
- **Pandas / NumPy** — Procesamiento tabular

---

## Equipo

ITT Cali Inteligente — Equipo de Gobierno de Datos

---

## Licencia

Uso interno ITT · Cali Inteligente. Todos los derechos reservados.
