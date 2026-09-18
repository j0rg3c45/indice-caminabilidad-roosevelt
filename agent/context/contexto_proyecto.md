# Contexto para agente — Proyecto Índice de Caminabilidad

Este agente apoya consulta, interpretación y desarrollo del **Índice de Caminabilidad**
para zonas de intervención urbana en Cali, Colombia, dentro del repositorio
`indice-caminabilidad-roosevelt`.

## Objetivo del proyecto

Evaluar el impacto de intervenciones urbanas midiendo la **caminabilidad** de la
red peatonal (OpenStreetMap vía OSMnx), estableciendo una línea base pre-intervención
y permitiendo comparaciones entre zonas y en el tiempo (2026–2028).

Métricas centrales: intersecciones peatonales, longitud de red, longitud promedio de
segmento, densidad de calle (km/km²) y densidad de intersecciones (int/km²).

## Repositorio

- URL: https://github.com/j0rg3c45/indice-caminabilidad-roosevelt.git
- Branch principal: `main`
- Convención: hacer commit y push después de cada cambio.

## Sistema de referencia geoespacial

- CRS de trabajo (todo dato y visualización): WGS84 (EPSG:4326).
- CRS de cálculo (solo área/distancia): EPSG:3116 (Colombia).
- OSMnx siempre recibe polígonos en WGS84.
- Todo GeoJSON se normaliza a WGS84 al cargar (si no tiene CRS se asigna 4326; si tiene otro, se reproyecta).

## Zonas del repo

- **Av. Roosevelt** — corredor con buffer de 100 m. Con territorio espejo (Calle 5, Calle 7).
- **Barrio Obrero** — polígono único de barrio. Sin territorio espejo.

## Estado actual de notebooks

- `notebooks/caminabilidad_roosevelt_v2.ipynb`: notebook principal. Corredor con buffer,
  red peatonal OSM, indicadores complementarios y comparación con territorios espejo
  (Calle 5 y Calle 7).
- `notebooks/caminabilidad_barrio_obrero_v2.ipynb`: replica la lógica de Roosevelt
  adaptada a polígono único de barrio, sin sección de territorio espejo. Incluye censo
  arbóreo como indicador complementario.
- `notebooks/ejemplo_04_itt_pulmon_oriente_2026_v2.ipynb`: notebook de referencia externo
  (ejemplo ITT), no forma parte del pipeline de caminabilidad.

## Scripts equivalentes (`notebooks_py/`)

- `caminabilidad_roosevelt.py`: pipeline Roosevelt (red peatonal + métricas + mapa).
- `caminabilidad_barrio_obrero.py`: pipeline Barrio Obrero (red peatonal + métricas + eventos + mapa).
- `caminabilidad_espejo.py`: caminabilidad territorios espejo + comparación vs Roosevelt.
- `descargar_red_peatonal.py`: solo descarga la red peatonal y la guarda como GeoJSON.
- `graficos_base_caminabilidad.py`: gráficos base de caminabilidad.
- `convertir_poligonos_espejo.py`: convierte polígonos espejo de `.shp` a `.geojson` (WGS84).

## Entorno de ejecución

- Sistema operativo: Windows. Gestor de paquetes: `uv` (v0.11.11).
- Instalar dependencias: `uv pip install -r requirements.txt`.
- Ejecutar scripts: `uv run notebooks_py/<script>.py`.
- No usar `pip` ni `python -m venv` directamente.
- El notebook funciona en Colab (clona el repo) y en local (rutas relativas).

## Notas técnicas

- Red peatonal OSM se descarga con `simplify=False` para conservar todos los vértices.
- Google tiles en Folium: `http://{s}.google.com/vt/lyrs=...` con `subdomains=['mt0','mt1','mt2','mt3']`.
- Silenciar warnings de pyogrio: `logging.getLogger('pyogrio').setLevel(logging.ERROR)`.

## Datos versionados

Convención del `.gitignore`: en `data/` solo se versionan `.zip` y archivos pequeños;
los `.geojson`, `.shp` y afines crudos están ignorados.

- Roosevelt: `data/itt_roosevelt/Roosevelt.zip` (fuente) + carpeta de trabajo descomprimida.
- Barrio Obrero: `data/Geojson_Barrio_Obrero.zip` (fuente) + carpeta de trabajo descomprimida.
- Polígonos espejo: `data/Informacion_espejo/geojson_espejo_poligonos.zip`.
- Datos filtrados espejo: `data/processed/Filtro_Calle_5/` y `data/processed/Filtro_Calle_7/`.
- Capas base de Cali (IDESC): `data/GeoJson_IDESC.zip` — barrios (339), comunas (22) y
  nomenclatura vial (11.295), en EPSG:6249; normalizar a WGS84 al cargar. Útiles para
  delimitar zonas por barrio/comuna y como capas de contexto en los mapas.

## Nota sobre el polígono de Barrio Obrero

La Celda 4 del notebook (y el script) leen el polígono directamente desde
`data/Geojson_Barrio_Obrero/Geojson_Barrio_Obrero.zip` con el prefijo `zip://`,
sin descomprimir la carpeta. El polígono vigente tiene 37.73 ha (reemplazó a uno previo
de 7.47 ha); los eventos en `nueva_data/` fueron filtrados contra el polígono anterior.

## Regla de sincronización

Cada vez que se modifique un notebook, actualizar también en el mismo cambio:

- `README.md` (pipeline, capas, métricas, scripts).
- `docs/referencia_proceso.md` (pipeline, datos, métricas, historial de commits).
- El script `.py` equivalente en `notebooks_py/`.
- Estos archivos de contexto del agente cuando cambie el estado del proyecto.

Hacer commit y push automáticamente, sin esperar a que el usuario lo pida.
