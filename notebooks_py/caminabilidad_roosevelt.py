"""
Índice de Caminabilidad — Piloto Av. Roosevelt
ITT Cali Inteligente · Equipo de Gobierno de Datos

Script modular para calcular métricas de caminabilidad usando OSMnx.
Uso: python notebooks_py/caminabilidad_roosevelt.py --geojson <ruta_geojson>
"""

import argparse
import datetime
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as ox
import pandas as pd

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
RESULTS_DIR = OUTPUT_DIR / "results"
FIGURES_DIR = OUTPUT_DIR / "figures"
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "geojson_roosevelt"
DEFAULT_GEOJSON = DATA_DIR / "Geojson_tramos_Roosevelt_Buffer_100.geojson"
CRS_COLOMBIA = 3116


def cargar_poligono(geojson_path: str):
    """Carga el GeoJSON y retorna el polígono y su área en m²."""
    gdf = gpd.read_file(geojson_path)
    polygon = gdf.geometry.iloc[0]
    gdf_m = gdf.to_crs(epsg=CRS_COLOMBIA)
    area_m2 = gdf_m.geometry.area.iloc[0]
    return polygon, area_m2, gdf


def descargar_red_peatonal(polygon):
    """Descarga la red peatonal desde OSM dentro del polígono."""
    G = ox.graph_from_polygon(polygon, network_type="walk")
    return G


def calcular_metricas(G, area_m2: float) -> dict:
    """Calcula métricas de caminabilidad a partir del grafo."""
    stats = ox.basic_stats(G, area=area_m2)
    longitud_total_km = stats["edge_length_total"] / 1000
    area_km2 = area_m2 / 1_000_000
    densidad_km_km2 = longitud_total_km / area_km2

    return {
        "fecha_medicion": datetime.date.today().isoformat(),
        "area_m2": round(area_m2, 0),
        "area_ha": round(area_m2 / 10000, 2),
        "intersecciones_peatonales": stats["intersection_count"],
        "longitud_red_peatonal_km": round(longitud_total_km, 2),
        "longitud_promedio_segmento_m": round(stats["edge_length_avg"], 1),
        "densidad_calle_km_km2": round(densidad_km_km2, 2),
        "nodos_osm": len(G.nodes),
        "segmentos_osm": len(G.edges),
        "fuente": "OpenStreetMap via OSMnx",
        "momento": "linea_base_pre_intervencion",
    }


def generar_mapa(G, output_path: Path):
    """Genera y guarda el mapa de la red peatonal."""
    fig, ax = ox.plot_graph(
        G,
        node_size=12,
        edge_linewidth=1.2,
        bgcolor="white",
        node_color="#2A9C8A",
        edge_color="#1A3A4A",
        figsize=(12, 12),
        show=False,
        close=False,
    )
    ax.set_title(
        "Red peatonal — Av. Roosevelt\nLínea base ITT · Cali Inteligente",
        fontsize=13,
        pad=15,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Mapa guardado: {output_path}")


def exportar_csv(metricas: dict, output_path: Path):
    """Exporta las métricas a CSV."""
    df = pd.DataFrame([metricas])
    df.to_csv(output_path, index=False)
    print(f"CSV exportado: {output_path}")
    print(df.T.to_string())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Calcula métricas de caminabilidad para un corredor vial."
    )
    parser.add_argument(
        "--geojson",
        default=str(DEFAULT_GEOJSON),
        help="Ruta al archivo GeoJSON del polígono de intervención.",
    )
    parser.add_argument(
        "--nombre",
        default="Av. Roosevelt - Buffer 100m",
        help="Nombre del polígono para el reporte.",
    )
    args = parser.parse_args()

    # Asegurar que existan los directorios de salida
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Pipeline
    print("=" * 50)
    print("CAMINABILIDAD — LÍNEA BASE")
    print("=" * 50)

    print("\n[1/4] Cargando polígono...")
    polygon, area_m2, gdf = cargar_poligono(args.geojson)
    print(f"      Área: {area_m2:,.0f} m² ({area_m2/10000:.2f} ha)")

    print("\n[2/4] Descargando red peatonal desde OSM...")
    G = descargar_red_peatonal(polygon)
    print(f"      Nodos: {len(G.nodes)} | Segmentos: {len(G.edges)}")

    print("\n[3/4] Calculando métricas...")
    metricas = calcular_metricas(G, area_m2)
    metricas["poligono"] = args.nombre
    for k, v in metricas.items():
        print(f"      {k}: {v}")

    print("\n[4/4] Exportando resultados...")
    exportar_csv(metricas, RESULTS_DIR / "roosevelt_caminabilidad_linea_base.csv")
    generar_mapa(G, FIGURES_DIR / "roosevelt_red_peatonal_linea_base.png")

    print("\n✓ Proceso completado.")


if __name__ == "__main__":
    main()
