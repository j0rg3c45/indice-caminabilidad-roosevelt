"""
Descargar red peatonal OSM para la zona de estudio Av. Roosevelt.
Guarda el resultado como GeoJSON en data/itt_roosevelt/Roosevelt/Geojson_Roosevelt/

Uso:
    uv run notebooks_py/descargar_red_peatonal.py

Requisitos:
    uv pip install osmnx geopandas
"""

import warnings
import logging
from pathlib import Path

import geopandas as gpd
import osmnx as ox

warnings.filterwarnings("ignore")
logging.getLogger("pyogrio").setLevel(logging.ERROR)

# Configuración
CRS_WGS84 = "EPSG:4326"
CRS_COLOMBIA = "EPSG:3116"

# Rutas
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "itt_roosevelt" / "Roosevelt" / "Geojson_Roosevelt"
POLIGONO_PATH = DATA_DIR / "Geojson_tramos_Roosevelt_Buffer_100.geojson"
OUTPUT_PATH = DATA_DIR / "red_peatonal_osm_roosevelt.geojson"


def main():
    print("=" * 50)
    print("DESCARGA RED PEATONAL OSM — Av. Roosevelt")
    print("=" * 50)

    # 1. Cargar polígono
    print("\n[1/4] Cargando polígono...")
    gdf = gpd.read_file(POLIGONO_PATH)
    if gdf.crs is None:
        gdf = gdf.set_crs(CRS_WGS84)
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(CRS_WGS84)

    polygon = gdf.geometry.iloc[0]
    print(f"      Polígono cargado en {CRS_WGS84}")

    # 2. Calcular área
    print("\n[2/4] Calculando área...")
    gdf_m = gdf.to_crs(CRS_COLOMBIA)
    area_m2 = gdf_m.geometry.area.iloc[0]
    print(f"      Área: {area_m2:,.0f} m² ({area_m2/10000:.2f} ha)")

    # 3. Descargar red peatonal
    print("\n[3/4] Descargando red peatonal desde OpenStreetMap...")
    G = ox.graph_from_polygon(polygon, network_type="walk")
    print(f"      Nodos: {len(G.nodes)} | Segmentos: {len(G.edges)}")

    # 4. Exportar como GeoJSON
    print("\n[4/4] Exportando GeoJSON...")
    gdf_nodos, gdf_aristas = ox.graph_to_gdfs(G)
    gdf_aristas_wgs84 = gdf_aristas.to_crs(CRS_WGS84)
    gdf_aristas_wgs84.to_file(OUTPUT_PATH, driver="GeoJSON")
    print(f"      Guardado: {OUTPUT_PATH}")
    print(f"      CRS: {CRS_WGS84}")
    print(f"      Segmentos: {len(gdf_aristas_wgs84)}")

    print("\n✓ Red peatonal descargada y guardada en la zona de estudio.")


if __name__ == "__main__":
    main()
