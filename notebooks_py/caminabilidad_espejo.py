"""
Índice de Caminabilidad — Territorios Espejo (Calle 5 y Calle 7)
ITT Cali Inteligente · Equipo de Gobierno de Datos

Calcula métricas de caminabilidad para los territorios espejo candidatos
y genera comparación con Av. Roosevelt.

Datos procesados en:
  - data/processed/Filtro_Calle_5/geojson_filtrado_calle_5_area_Espejo_Bf100/
  - data/processed/Filtro_Calle_7/geojson_filtrado_calle_7_area_Espejo_Bf100/

Polígonos espejo en:
  - data/Informacion_espejo/info_shape/calle_5_area_Espejo_Bf100.shp
  - data/Informacion_espejo/info_shape/calle_7_area_Espejo_Bf100.shp

Uso:
    uv run notebooks_py/caminabilidad_espejo.py

Repositorio: https://github.com/j0rg3c45/indice-caminabilidad-roosevelt.git
"""

import datetime
import logging
import os
import re
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox
import pandas as pd

warnings.filterwarnings("ignore")
logging.getLogger("pyogrio").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ESPEJO_SHAPE_DIR = PROJECT_ROOT / "data" / "Informacion_espejo" / "info_shape"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "outputs" / "results"
IMG_DIR = PROJECT_ROOT / "outputs" / "figures"

CRS_WGS84 = "EPSG:4326"
CRS_COLOMBIA = "EPSG:3116"


# Zonas espejo — polígonos en info_shape/, datos en processed/
ZONAS_ESPEJO = {
    "Calle 5": {
        "poligono": ESPEJO_SHAPE_DIR / "calle_5_area_Espejo_Bf100.shp",
        "geojson_dir": PROCESSED_DIR / "Filtro_Calle_5" / "geojson_filtrado_calle_5_area_Espejo_Bf100",
    },
    "Calle 7": {
        "poligono": ESPEJO_SHAPE_DIR / "calle_7_area_Espejo_Bf100.shp",
        "geojson_dir": PROCESSED_DIR / "Filtro_Calle_7" / "geojson_filtrado_calle_7_area_Espejo_Bf100",
    },
}

# Línea base Roosevelt (del CSV generado anteriormente)
ROOSEVELT_CSV = RESULTS_DIR / "roosevelt_caminabilidad_linea_base.csv"


# ---------------------------------------------------------------------------
# Funciones
# ---------------------------------------------------------------------------
def cargar_poligono(path):
    """Carga polígono y asegura WGS84."""
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf = gdf.set_crs(CRS_WGS84)
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(CRS_WGS84)
    return gdf


def calcular_caminabilidad(gdf_poligono, nombre):
    """Calcula métricas de caminabilidad para un polígono."""
    polygon = gdf_poligono.geometry.iloc[0]

    # Área
    gdf_m = gdf_poligono.to_crs(CRS_COLOMBIA)
    area_m2 = gdf_m.geometry.area.iloc[0]
    area_km2 = area_m2 / 1_000_000

    # Red peatonal
    print(f"      Descargando red peatonal OSM...")
    G = ox.graph_from_polygon(polygon, network_type="walk", simplify=False)

    # Métricas
    stats = ox.basic_stats(G, area=area_m2)
    gdf_edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
    longitudes = gdf_edges["length"].values
    longitud_total_km = stats["edge_length_total"] / 1000
    densidad_km_km2 = longitud_total_km / area_km2
    densidad_int_km2 = stats["intersection_count"] / area_km2

    return {
        "zona": nombre,
        "fecha_medicion": datetime.date.today().isoformat(),
        "area_m2": round(area_m2, 0),
        "area_ha": round(area_m2 / 10000, 2),
        "area_km2": round(area_km2, 4),
        "intersecciones_peatonales": stats["intersection_count"],
        "densidad_intersecciones_km2": round(densidad_int_km2, 0),
        "longitud_red_peatonal_km": round(longitud_total_km, 2),
        "longitud_promedio_segmento_m": round(np.mean(longitudes), 1),
        "mediana_segmento_m": round(np.median(longitudes), 1),
        "densidad_calle_km_km2": round(densidad_km_km2, 2),
        "nodos_osm": len(G.nodes),
        "segmentos_osm": len(G.edges),
    }, G, longitudes


def contar_eventos_geojson(geojson_dir):
    """Cuenta registros por dataset en la carpeta de GeoJSON filtrados."""
    conteos = {}
    if not geojson_dir.exists():
        return conteos
    for f in sorted(geojson_dir.glob("*.geojson")):
        gdf = gpd.read_file(f)
        nombre = f.stem.split("_filtrado_")[0]
        conteos[nombre] = len(gdf)
    return conteos


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("CAMINABILIDAD — TERRITORIOS ESPEJO")
    print(f"Fecha: {datetime.date.today().isoformat()} | CRS: {CRS_WGS84}")
    print("=" * 60)

    resultados = []

    for nombre, config in ZONAS_ESPEJO.items():
        print(f"\n{'─' * 40}")
        print(f"  ZONA: {nombre}")
        print(f"{'─' * 40}")

        if not config["poligono"].exists():
            print(f"  ⚠ Polígono no encontrado: {config['poligono']}")
            continue

        print(f"  [1/3] Cargando polígono...")
        gdf_poligono = cargar_poligono(config["poligono"])
        print(f"        CRS: {gdf_poligono.crs}")

        print(f"  [2/3] Calculando caminabilidad...")
        metricas, G, longitudes = calcular_caminabilidad(gdf_poligono, nombre)
        for k, v in metricas.items():
            print(f"        {k}: {v}")

        print(f"  [3/3] Contando eventos complementarios...")
        conteos = contar_eventos_geojson(config["geojson_dir"])
        for dataset, n in conteos.items():
            print(f"        {dataset}: {n}")
            metricas[f"total_{dataset}"] = n

        resultados.append(metricas)

    # Exportar resultados espejo
    df_espejo = pd.DataFrame(resultados)
    output_csv = RESULTS_DIR / "espejo_caminabilidad_linea_base.csv"
    df_espejo.to_csv(output_csv, index=False)
    print(f"\n{'=' * 60}")
    print(f"CSV espejo exportado: {output_csv}")

    # Comparación con Roosevelt
    print(f"\n{'=' * 60}")
    print("COMPARACIÓN: Roosevelt vs Territorios Espejo")
    print(f"{'=' * 60}")

    if ROOSEVELT_CSV.exists():
        df_roosevelt = pd.read_csv(ROOSEVELT_CSV)
        df_roosevelt["zona"] = "Av. Roosevelt"

        # Métricas comunes para comparar
        cols_comparar = [
            "zona", "area_ha", "intersecciones_peatonales",
            "longitud_red_peatonal_km", "longitud_promedio_segmento_m",
            "densidad_calle_km_km2",
        ]
        cols_disponibles = [c for c in cols_comparar if c in df_roosevelt.columns and c in df_espejo.columns]

        df_comparacion = pd.concat([
            df_roosevelt[cols_disponibles],
            df_espejo[cols_disponibles]
        ], ignore_index=True)

        print(df_comparacion.to_string(index=False))
        comparacion_csv = RESULTS_DIR / "comparacion_roosevelt_vs_espejo.csv"
        df_comparacion.to_csv(comparacion_csv, index=False)
        print(f"\nComparación exportada: {comparacion_csv}")
    else:
        print("⚠ No se encontró CSV de Roosevelt. Ejecuta primero caminabilidad_roosevelt.py")

    print(f"\n{'=' * 60}")
    print("✓ Proceso completado.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
