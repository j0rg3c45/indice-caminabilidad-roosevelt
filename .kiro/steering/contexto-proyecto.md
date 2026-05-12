---
inclusion: auto
---

# Contexto del Proyecto — Índice de Caminabilidad Av. Roosevelt

## Entorno de desarrollo

- **OS:** Windows
- **Gestor de paquetes:** uv (v0.11.11)
- **Python:** usar siempre `uv run` para ejecutar scripts, `uv pip install` para dependencias, `uv venv` para entornos
- **Repositorio:** https://github.com/j0rg3c45/indice-caminabilidad-roosevelt.git
- **Rama principal:** main

## Reglas del proyecto

- **CRS de trabajo:** WGS84 (EPSG:4326) para toda la información geoespacial
- **CRS para cálculos:** EPSG:3116 (Colombia) solo para área y distancia
- **OSMnx:** siempre usar `simplify=False` para conservar vértices de las líneas
- **Datos fuente:** `data/itt_roosevelt/Roosevelt/Geojson_Roosevelt/`
- **Outputs:** `outputs/results/` (CSV) y `outputs/figures/` (imágenes)
- **Google tiles en Folium:** usar formato `http://{s}.google.com/vt/lyrs=...` con `subdomains=['mt0','mt1','mt2','mt3']`
- **Warnings pyogrio:** silenciar con `logging.getLogger('pyogrio').setLevel(logging.ERROR)`

## Estructura clave

```
notebooks/caminabilidad_roosevelt_v2.ipynb  → Notebook principal (Colab/local)
notebooks_py/caminabilidad_roosevelt.py     → Pipeline completo como script
notebooks_py/descargar_red_peatonal.py      → Solo descarga red peatonal
data/itt_roosevelt/Roosevelt/Geojson_Roosevelt/ → GeoJSON zona de estudio
```

## Convenciones

- Commits en español, prefijos: feat, fix, docs, data, config, update
- Documentación en español
- Siempre hacer push después de commit
- Actualizar README.md y docs/referencia_proceso.md cuando hay cambios significativos
