"""
Convierte los polígonos espejo de .shp a .geojson (WGS84)
para que funcionen en Colab donde no se suben los .shp.

Uso:
    uv run notebooks_py/convertir_poligonos_espejo.py

Genera:
    data/processed/Filtro_Calle_5/calle_5_area_Espejo_Bf100.geojson
    data/processed/Filtro_Calle_7/calle_7_area_Espejo_Bf100.geojson
"""

import logging
import warnings
from pathlib import Path

import geopandas as gpd

warnings.filterwarnings("ignore")
logging.getLogger("pyogrio").setLevel(logging.ERROR)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ESPEJO_SHAPE_DIR = PROJECT_ROOT / "data" / "Informacion_espejo" / "info_shape"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

CRS_WGS84 = "EPSG:4326"

POLIGONOS = {
    "Calle 5": {
        "shp": ESPEJO_SHAPE_DIR / "calle_5_area_Espejo_Bf100.shp",
        "geojson": PROCESSED_DIR / "Filtro_Calle_5" / "calle_5_area_Espejo_Bf100.geojson",
    },
    "Calle 7": {
        "shp": ESPEJO_SHAPE_DIR / "calle_7_area_Espejo_Bf100.shp",
        "geojson": PROCESSED_DIR / "Filtro_Calle_7" / "calle_7_area_Espejo_Bf100.geojson",
    },
}


def main():
    print("Convirtiendo polígonos espejo .shp → .geojson (WGS84)")
    print()

    for nombre, rutas in POLIGONOS.items():
        if not rutas["shp"].exists():
            print(f"  ✗ {nombre}: .shp no encontrado")
            continue

        gdf = gpd.read_file(rutas["shp"])
        if gdf.crs is None:
            gdf = gdf.set_crs(CRS_WGS84)
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(CRS_WGS84)

        rutas["geojson"].parent.mkdir(parents=True, exist_ok=True)
        gdf.to_file(rutas["geojson"], driver="GeoJSON")
        print(f"  ✓ {nombre}: {rutas['geojson'].name} ({len(gdf)} features)")

    print("\n✓ Conversión completada.")


if __name__ == "__main__":
    main()
