# Contexto Maestro para Agente — Índice de Caminabilidad

Este archivo resume el contexto más importante del repo para que otro agente pueda
trabajar con buen criterio técnico y operativo desde el inicio.

## 1. Objetivo del proyecto

El repositorio calcula un **Índice de Caminabilidad** para zonas de intervención
urbana de Cali, Colombia, usando la red peatonal de OpenStreetMap (OSMnx).

Busca establecer una línea base pre-intervención y permitir comparaciones entre
zonas y a lo largo del tiempo (2026–2028), a partir de métricas topológicas de la
red peatonal.

- Repositorio: https://github.com/j0rg3c45/indice-caminabilidad-roosevelt.git
- Branch principal: `main`.

## 2. Métricas centrales

Se derivan del grafo peatonal descargado con OSMnx (`network_type='walk'`, `simplify=False`):

- Intersecciones peatonales.
- Longitud total de red (km).
- Longitud promedio de segmento (m).
- Densidad de calle (km/km²).
- Densidad de intersecciones (int/km²).
- Nodos y segmentos OSM.

Además se cargan datasets complementarios por zona (eventos de seguridad, sedes,
censo arbóreo, etc.) y se reportan como total y densidad por hectárea.

## 3. Sistema de referencia geoespacial

- CRS de trabajo (datos y visualización): WGS84 (EPSG:4326).
- CRS de cálculo (solo área/distancia): EPSG:3116 (Colombia).
- OSMnx siempre recibe polígonos en WGS84.
- Todo GeoJSON se normaliza a WGS84 al cargar.

## 4. Zonas del repo y cómo pensarlas

### Av. Roosevelt

- Unidad de análisis: corredor vial con buffer de 100 m.
- Notebook: `notebooks/caminabilidad_roosevelt_v2.ipynb` (referencia principal).
- Tiene sección de **territorios espejo** (Calle 5 y Calle 7) como controles candidatos.
- Datasets: siniestros, comparendos, homicidios, hurtos, sedes educativas, VBG, VIF.

### Barrio Obrero

- Unidad de análisis: **polígono único de barrio** (no corredor, no buffer, sin espejo).
- Notebook: `notebooks/caminabilidad_barrio_obrero_v2.ipynb`.
- El polígono llega en CRS `ESRI:103599` y se reproyecta a WGS84 al cargar.
- Datasets (2023–2026 T1): comparendos, homicidios, hurtos, violencia intrafamiliar y
  censo arbóreo (indicador propio de esta zona).

## 5. Estado real de notebooks y scripts

Notebooks (`notebooks/`):

- `caminabilidad_roosevelt_v2.ipynb`: pipeline completo Roosevelt + comparación espejo.
- `caminabilidad_barrio_obrero_v2.ipynb`: pipeline Barrio Obrero (polígono único, sin espejo).
- `ejemplo_04_itt_pulmon_oriente_2026_v2.ipynb`: ejemplo externo de ITT, NO forma parte
  del pipeline de caminabilidad; tratarlo solo como referencia.

Scripts (`notebooks_py/`):

- `caminabilidad_roosevelt.py`, `caminabilidad_barrio_obrero.py`: pipelines equivalentes a los notebooks.
- `caminabilidad_espejo.py`: caminabilidad de territorios espejo + comparación vs Roosevelt.
- `descargar_red_peatonal.py`: descarga y guarda la red peatonal como GeoJSON.
- `graficos_base_caminabilidad.py`: gráficos base.
- `convertir_poligonos_espejo.py`: convierte polígonos espejo `.shp` → `.geojson` (WGS84).

## 6. Disponibilidad real de datos

Convención del `.gitignore`: en `data/` solo se versionan `.zip` y archivos pequeños;
los `.geojson`, `.shp`, `.qmd`, `.kmz` crudos están ignorados.

- Roosevelt: `data/itt_roosevelt/Roosevelt.zip` + carpeta de trabajo descomprimida.
- Barrio Obrero: `data/Geojson_Barrio_Obrero.zip` + carpeta de trabajo descomprimida.
- Polígonos espejo: `data/Informacion_espejo/geojson_espejo_poligonos.zip`.
- Datos filtrados espejo: `data/processed/Filtro_Calle_5/` y `data/processed/Filtro_Calle_7/`.

## 7. Entorno de ejecución

- Sistema operativo: Windows. Gestor de paquetes: `uv` (v0.11.11).
- Instalar dependencias: `uv pip install -r requirements.txt`.
- Ejecutar scripts: `uv run notebooks_py/<script>.py`.
- No usar `pip` ni `python -m venv` directamente.
- El notebook funciona en Colab (clona el repo) y en local (rutas relativas).
- Notas técnicas: `simplify=False` en OSM; Google tiles con subdomains `mt0-mt3`;
  silenciar warnings de pyogrio con `logging.getLogger('pyogrio').setLevel(logging.ERROR)`.

## 8. Regla de sincronización

Cada vez que se modifique un notebook, actualizar en el mismo cambio:

- `README.md` (pipeline, capas, métricas, scripts).
- `docs/referencia_proceso.md` (pipeline, datos, métricas, historial de commits).
- El script `.py` equivalente en `notebooks_py/`.
- Estos archivos de contexto del agente cuando cambie el estado del proyecto.

Hacer commit y push automáticamente después de los cambios.

## 9. Dónde vive el conocimiento

Para responder bien sobre este repo, leer en este orden:

1. `README.md`
2. `docs/referencia_proceso.md`
3. `agent/context/contexto_proyecto.md`
4. `agent/context/zonas_estudio.md`
5. `notebooks/caminabilidad_roosevelt_v2.ipynb`
6. `notebooks/caminabilidad_barrio_obrero_v2.ipynb`

## 10. Precauciones para otro agente

- Este repo es de **caminabilidad** (red peatonal OSM), no un ITT de 5 dimensiones con
  scores normalizados. No asumir dimensiones, pesos ni referentes provisionales de un
  ITT genérico salvo que el usuario lo pida explícitamente.
- No confundir `ejemplo_04_itt_pulmon_oriente_2026_v2.ipynb` con el pipeline de caminabilidad.
- Distinguir la unidad de análisis: Roosevelt es corredor con buffer; Barrio Obrero es
  polígono único de barrio (sin espejo).
- Los `.geojson` crudos NO se versionan; los datos fuente van como `.zip` en `data/`.
- Las figuras (`outputs/figures/*.png`) están en `.gitignore`; los CSV de resultados sí se versionan.

## 11. Resumen ejecutivo para handoff rápido

Este repo calcula un índice de caminabilidad de zonas urbanas de Cali con OSMnx.
`caminabilidad_roosevelt_v2.ipynb` es la referencia principal (corredor con buffer +
territorios espejo Calle 5/7). `caminabilidad_barrio_obrero_v2.ipynb` replica esa lógica
para un polígono único de barrio, sin espejo, e incorpora censo arbóreo. Todo trabaja en
WGS84 y usa EPSG:3116 solo para área/distancia. Los datos fuente se versionan como `.zip`.
Al cambiar un notebook, sincronizar README, `docs/referencia_proceso.md`, el script `.py`
equivalente y estos archivos de contexto, y hacer commit + push.
