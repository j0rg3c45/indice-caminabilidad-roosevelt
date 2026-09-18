"""
Índice de Caminabilidad — Barrio Obrero
ITT Cali Inteligente · Equipo de Gobierno de Datos

Script modular para calcular métricas de caminabilidad del Barrio Obrero usando OSMnx.
A diferencia de Roosevelt (corredor con buffer), la unidad de análisis es el
polígono único del barrio y NO se calcula territorio espejo.

Descarga la red peatonal y la guarda como GeoJSON en la carpeta de datos.

Uso:
    uv run notebooks_py/caminabilidad_barrio_obrero.py

Repositorio: https://github.com/j0rg3c45/indice-caminabilidad-roosevelt.git
"""

import argparse
import datetime
import logging
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as ox
import pandas as pd

warnings.filterwarnings("ignore")
logging.getLogger("pyogrio").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Carpeta de datos de la zona de estudio (GeoJSON)
GEOJSON_DIR = PROJECT_ROOT / "data" / "Geojson_Barrio_Obrero"

# Carpeta de eventos complementarios filtrados al polígono
EVENTOS_DIR = GEOJSON_DIR / "nueva_data" / "geojson_filtrado_poligono_Barrio_Obrero"

# Polígono por defecto (unidad de análisis: barrio).
# Se lee directamente desde el ZIP versionado con el prefijo zip:// (geopandas/fiona),
# sin necesidad de descomprimir la carpeta. Respaldo: .geojson descomprimido.
ZIP_POLIGONO = GEOJSON_DIR / "Geojson_Barrio_Obrero.zip"
GEOJSON_EN_ZIP = "Geojson_Barrio_Obrero.geojson"
if ZIP_POLIGONO.exists():
    DEFAULT_GEOJSON = f"zip://{ZIP_POLIGONO.as_posix()}!{GEOJSON_EN_ZIP}"
else:
    DEFAULT_GEOJSON = str(GEOJSON_DIR / "Geojson_Barrio_Obrero.geojson")

# Salidas
RESULTS_DIR = PROJECT_ROOT / "outputs" / "results"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

# CRS
CRS_WGS84 = "EPSG:4326"
CRS_COLOMBIA = "EPSG:3116"


# ---------------------------------------------------------------------------
# Funciones
# ---------------------------------------------------------------------------
def cargar_poligono(geojson_path: str):
    """Carga el GeoJSON, asegura WGS84 y retorna polígono + área en m²."""
    gdf = gpd.read_file(geojson_path)

    # Asegurar WGS84
    if gdf.crs is None:
        gdf = gdf.set_crs(CRS_WGS84)
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(CRS_WGS84)

    polygon = gdf.geometry.iloc[0]

    # Área en sistema proyectado
    gdf_m = gdf.to_crs(CRS_COLOMBIA)
    area_m2 = gdf_m.geometry.area.iloc[0]

    return polygon, area_m2, gdf


def descargar_red_peatonal(polygon):
    """Descarga la red peatonal desde OSM (polígono en WGS84).
    simplify=False conserva todos los vértices intermedios de las líneas."""
    G = ox.graph_from_polygon(polygon, network_type="walk", simplify=False)
    return G


def exportar_red_peatonal(G, output_path: Path):
    """Exporta la red peatonal como GeoJSON en WGS84."""
    _, gdf_aristas = ox.graph_to_gdfs(G)
    gdf_wgs84 = gdf_aristas.to_crs(CRS_WGS84)
    gdf_wgs84.to_file(output_path, driver="GeoJSON")
    print(f"      Red peatonal GeoJSON: {output_path}")
    print(f"      Segmentos exportados: {len(gdf_wgs84)}")


def calcular_metricas(G, area_m2: float) -> dict:
    """Calcula métricas de caminabilidad a partir del grafo."""
    stats = ox.basic_stats(G, area=area_m2)
    longitud_total_km = stats["edge_length_total"] / 1000
    area_km2 = area_m2 / 1_000_000
    densidad_km_km2 = longitud_total_km / area_km2

    return {
        "fecha_medicion": datetime.date.today().isoformat(),
        "crs_trabajo": CRS_WGS84,
        "crs_calculo": CRS_COLOMBIA,
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


def contar_eventos(area_m2: float) -> dict:
    """Cuenta eventos complementarios (comparendos, hurtos, homicidios, VIF,
    censo arbóreo) dentro del polígono y calcula densidad por hectárea."""
    indicadores = {}
    if not EVENTOS_DIR.exists():
        print(f"      AVISO: carpeta de eventos no encontrada: {EVENTOS_DIR}")
        return indicadores

    for f in sorted(EVENTOS_DIR.glob("*.geojson")):
        gdf = gpd.read_file(f)
        if gdf.crs is None:
            gdf = gdf.set_crs(CRS_WGS84)
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(CRS_WGS84)
        # Nombre corto del dataset
        nombre = (
            f.stem.split("_filtrado_")[0]
            .replace("DATIC_", "")
            .replace("_2023_2026T1", "")
            .replace("CENSO_ARBOREO", "censo_arboreo")
        )
        densidad = len(gdf) / (area_m2 / 10000)
        indicadores[nombre] = {
            "total": len(gdf),
            "densidad_por_ha": round(densidad, 2),
        }
        print(f"      {nombre:20s}: {len(gdf):>5} registros | {densidad:.2f} por ha")
    return indicadores


def generar_mapa(G, output_path: Path):
    """Genera y guarda el mapa estático de la red peatonal."""
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
        f"Red peatonal — Barrio Obrero\nLínea base ITT · {CRS_WGS84}",
        fontsize=13,
        pad=15,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"      Mapa PNG: {output_path}")


def exportar_csv(metricas: dict, output_path: Path):
    """Exporta las métricas a CSV."""
    df = pd.DataFrame([metricas])
    df.to_csv(output_path, index=False)
    print(f"      CSV: {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Calcula métricas de caminabilidad y descarga red peatonal OSM (Barrio Obrero)."
    )
    parser.add_argument(
        "--geojson",
        default=str(DEFAULT_GEOJSON),
        help="Ruta al GeoJSON del polígono del barrio.",
    )
    parser.add_argument(
        "--nombre",
        default="Barrio Obrero",
        help="Nombre del polígono para el reporte.",
    )
    args = parser.parse_args()

    # Asegurar directorios
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    GEOJSON_DIR.mkdir(parents=True, exist_ok=True)

    # Pipeline
    print("=" * 60)
    print("CAMINABILIDAD — Barrio Obrero — LÍNEA BASE")
    print(f"CRS trabajo: {CRS_WGS84} | CRS cálculos: {CRS_COLOMBIA}")
    print("=" * 60)

    print("\n[1/6] Cargando polígono...")
    polygon, area_m2, gdf = cargar_poligono(args.geojson)
    print(f"      Área: {area_m2:,.0f} m² ({area_m2/10000:.2f} ha)")
    print(f"      CRS: {CRS_WGS84}")

    print("\n[2/6] Descargando red peatonal desde OpenStreetMap...")
    G = descargar_red_peatonal(polygon)
    print(f"      Nodos: {len(G.nodes)} | Segmentos: {len(G.edges)}")

    print("\n[3/6] Guardando red peatonal como GeoJSON en zona de estudio...")
    exportar_red_peatonal(G, GEOJSON_DIR / "red_peatonal_osm_barrio_obrero.geojson")

    print("\n[4/6] Calculando métricas...")
    metricas = calcular_metricas(G, area_m2)
    metricas["poligono"] = args.nombre
    for k, v in metricas.items():
        print(f"      {k}: {v}")

    print("\n[5/6] Contando eventos complementarios...")
    indicadores = contar_eventos(area_m2)
    for nombre, vals in indicadores.items():
        metricas[f"total_{nombre}"] = vals["total"]
        metricas[f"densidad_{nombre}_por_ha"] = vals["densidad_por_ha"]

    print("\n[6/6] Exportando resultados...")
    exportar_csv(metricas, RESULTS_DIR / "barrio_obrero_caminabilidad_linea_base.csv")
    generar_mapa(G, FIGURES_DIR / "barrio_obrero_red_peatonal_linea_base.png")

    print("\n" + "=" * 60)
    print("Proceso completado.")
    print(f"  Red peatonal: {GEOJSON_DIR / 'red_peatonal_osm_barrio_obrero.geojson'}")
    print(f"  Métricas CSV: {RESULTS_DIR / 'barrio_obrero_caminabilidad_linea_base.csv'}")
    print(f"  Mapa PNG:     {FIGURES_DIR / 'barrio_obrero_red_peatonal_linea_base.png'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
