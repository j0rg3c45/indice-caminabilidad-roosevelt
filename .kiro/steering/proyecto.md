# Contexto del Proyecto — Índice de Caminabilidad Av. Roosevelt

## Entorno del desarrollador
- Sistema operativo: Windows
- Gestor de paquetes: **uv** (v0.11.11)
- Para instalar dependencias: `uv pip install -r requirements.txt`
- Para ejecutar scripts: `uv run notebooks_py/<script>.py`
- Para crear entornos: `uv venv`
- NO usar pip ni python -m venv directamente

## Repositorio
- URL: https://github.com/j0rg3c45/indice-caminabilidad-roosevelt.git
- Branch principal: main
- Siempre hacer push después de commits

## Sistema de referencia geoespacial
- CRS de trabajo: WGS84 (EPSG:4326) — para toda visualización y datos
- CRS de cálculo: EPSG:3116 (Colombia) — solo para área/distancia
- OSMnx siempre recibe polígonos en WGS84
- Todos los GeoJSON se normalizan a WGS84 al cargar

## Estructura clave
- Datos fuente: `data/itt_roosevelt/Roosevelt/Geojson_Roosevelt/`
- Notebook principal: `notebooks/caminabilidad_roosevelt_v2.ipynb`
- Scripts: `notebooks_py/`
- Resultados: `outputs/results/` y `outputs/figures/`

## Notas técnicas
- Red peatonal OSM se descarga con `simplify=False` para conservar vértices
- Google tiles en Folium: usar `http://{s}.google.com/vt/lyrs=...` con `subdomains=['mt0','mt1','mt2','mt3']`
- Silenciar warnings de pyogrio: `logging.getLogger('pyogrio').setLevel(logging.ERROR)`
- El notebook funciona en Colab (clona el repo) y en local (rutas relativas)

## Reglas de sincronización
- Cada vez que se modifique el notebook (.ipynb), actualizar también:
  - README.md (pipeline, capas, métricas, scripts)
  - docs/referencia_proceso.md (pipeline, historial de commits)
  - Scripts .py en notebooks_py/ (funciones equivalentes al notebook)
- Siempre hacer commit y push después de los cambios
- No esperar a que el usuario lo pida — hacerlo automáticamente
