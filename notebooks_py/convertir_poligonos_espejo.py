"""
Convierte los polígonos espejo de .shp a .geojson (WGS84).

NOTA: Los polígonos GeoJSON ya están disponibles en:
    data/Informacion_espejo/geojson_espejo_poligonos/

Este script es útil solo si se necesita regenerar los GeoJSON
a partir de los shapefiles originales en info_shape/.

Uso:
    uv run notebooks_py/convertir_poligonos_espejo.py

Genera:
    data/Informacion_espejo/geojson_espejo_poligonos/calle_5_area_Espejo_Bf100.geojson
    data/Informacion_espejo/geojson_espejo_poligonos/calle_7_area_Espejo_Bf100.geojson
"""

import logging
import warnings
from pathlib import Path

import geopandas as gpd

warnings.filterwarnings("ignore")
logging.getLogger("pyogrio").setLevel(logging.ERROR)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ESPEJO_SHAPE_DIR = PROJECT_ROOT / "data" / "Informacion_espejo" / "info_shape"
ESPEJO_GEOJSON_DIR = PROJECT_ROOT / "data" / "Informacion_espejo" / "geojson_espejo_poligonos"

CRS_WGS84 = "EPSG:4326"

POLIGONOS = {
    "Calle 5": {
        "shp": ESPEJO_SHAPE_DIR / "calle_5_area_Espejo_Bf100.shp",
        "geojson": ESPEJO_GEOJSON_DIR / "calle_5_area_Espejo_Bf100.geojson",
    },
    "Calle 7": {
        "shp": ESPEJO_SHAPE_DIR / "calle_7_area_Espejo_Bf100.shp",
        "geojson": ESPEJO_GEOJSON_DIR / "calle_7_area_Espejo_Bf100.geojson",
    },
}


def main():
    print("Convirtiendo polígonos espejo .shp → .geojson (WGS84)")
    print()

    ESPEJO_GEOJSON_DIR.mkdir(parents=True, exist_ok=True)

    for nombre, rutas in POLIGONOS.items():
        if not rutas["shp"].exists():
            print(f"  ✗ {nombre}: .shp no encontrado")
            continue

        gdf = gpd.read_file(rutas["shp"])
        if gdf.crs is None:
            gdf = gdf.set_crs(CRS_WGS84)
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(CRS_WGS84)

        gdf.to_file(rutas["geojson"], driver="GeoJSON")
        print(f"  ✓ {nombre}: {rutas['geojson'].name} ({len(gdf)} features)")

    print("\n✓ Conversión completada.")


if __name__ == "__main__":
    main()
