"""
Gráficos Base — Línea Base de Caminabilidad Av. Roosevelt
ITT Cali Inteligente · Equipo de Gobierno de Datos

Genera los 6 gráficos base para evaluación de caminabilidad:
1. Mapa de red peatonal
2. Heatmap de densidad de intersecciones
3. Histograma de longitud de segmentos
4. Boxplot de segmentos peatonales
5. Scatter plot de conectividad
6. Tabla resumen de métricas urbanas

Uso:
    uv run notebooks_py/graficos_base_caminabilidad.py

Repositorio: https://github.com/j0rg3c45/indice-caminabilidad-roosevelt.git
"""

import datetime
import logging
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox
import pandas as pd
from scipy.stats import gaussian_kde

warnings.filterwarnings("ignore")
logging.getLogger("pyogrio").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
GEOJSON_DIR = PROJECT_ROOT / "data" / "itt_roosevelt" / "Roosevelt" / "Geojson_Roosevelt"
POLIGONO_PATH = GEOJSON_DIR / "Geojson_tramos_Roosevelt_Buffer_100.geojson"
IMG_DIR = PROJECT_ROOT / "outputs" / "figures"
RESULTS_DIR = PROJECT_ROOT / "outputs" / "results"

CRS_WGS84 = "EPSG:4326"
CRS_COLOMBIA = "EPSG:3116"
ZONA_NOMBRE = "Av. Roosevelt — Cali"


# ---------------------------------------------------------------------------
# Funciones
# ---------------------------------------------------------------------------
def cargar_datos():
    """Carga polígono y descarga red peatonal."""
    print("[1/8] Cargando polígono...")
    gdf = gpd.read_file(POLIGONO_PATH)
    if gdf.crs is None:
        gdf = gdf.set_crs(CRS_WGS84)
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(CRS_WGS84)

    polygon = gdf.geometry.iloc[0]
    gdf_m = gdf.to_crs(CRS_COLOMBIA)
    area_m2 = gdf_m.geometry.area.iloc[0]
    print(f"      Área: {area_m2:,.0f} m² ({area_m2/10000:.2f} ha)")

    print("[2/8] Descargando red peatonal (simplify=False)...")
    G = ox.graph_from_polygon(polygon, network_type="walk", simplify=False)
    print(f"      Nodos: {len(G.nodes)} | Segmentos: {len(G.edges)}")

    return G, gdf, polygon, area_m2


def graf_01_red_peatonal(G):
    """Mapa de red peatonal."""
    print("[3/8] Gráfico 1: Mapa de red peatonal...")
    fig, ax = ox.plot_graph(
        G, node_size=15, node_color="#E53935",
        edge_linewidth=1.5, edge_color="#2A9C8A",
        bgcolor="white", figsize=(14, 14), show=False, close=False
    )
    ax.set_title(
        f"Red Peatonal — {ZONA_NOMBRE}\nLínea Base · {datetime.date.today().isoformat()}",
        fontsize=14, pad=15, fontweight="bold"
    )
    plt.tight_layout()
    plt.savefig(IMG_DIR / "graf_01_red_peatonal.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"      Exportado: graf_01_red_peatonal.png")


def graf_02_heatmap_intersecciones(G, gdf_poligono):
    """Heatmap de densidad de intersecciones."""
    print("[4/8] Gráfico 2: Heatmap de intersecciones...")
    gdf_nodes = ox.graph_to_gdfs(G, nodes=True, edges=False).to_crs(CRS_WGS84)

    if "street_count" in gdf_nodes.columns:
        intersecciones = gdf_nodes[gdf_nodes["street_count"] > 2]
    else:
        intersecciones = gdf_nodes

    x = intersecciones.geometry.x.values
    y = intersecciones.geometry.y.values

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    if len(x) > 5:
        xy = np.vstack([x, y])
        kde = gaussian_kde(xy)
        xmin, xmax = x.min(), x.max()
        ymin, ymax = y.min(), y.max()
        xx, yy = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
        positions = np.vstack([xx.ravel(), yy.ravel()])
        density = kde(positions).reshape(xx.shape)
        ax.imshow(np.rot90(density), extent=[xmin, xmax, ymin, ymax],
                  cmap="YlOrRd", aspect="auto", alpha=0.8)
        ax.scatter(x, y, s=10, c="black", alpha=0.5, zorder=5)

    gdf_poligono.boundary.plot(ax=ax, color="#1B4F8A", linewidth=1.5)
    ax.set_title(f"Densidad de Intersecciones — {ZONA_NOMBRE}\nKernel Density",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    plt.tight_layout()
    plt.savefig(IMG_DIR / "graf_02_heatmap_intersecciones.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"      Intersecciones: {len(intersecciones)} | Exportado: graf_02_heatmap_intersecciones.png")


def graf_03_histograma(longitudes):
    """Histograma de longitud de segmentos."""
    print("[5/8] Gráfico 3: Histograma de segmentos...")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(longitudes, bins=50, color="#2A9C8A", edgecolor="white", alpha=0.85)
    ax.axvline(np.mean(longitudes), color="#E53935", linestyle="--", linewidth=2,
               label=f"Media: {np.mean(longitudes):.1f} m")
    ax.axvline(np.median(longitudes), color="#1B4F8A", linestyle=":", linewidth=2,
               label=f"Mediana: {np.median(longitudes):.1f} m")
    ax.set_xlabel("Longitud del segmento (m)", fontsize=12)
    ax.set_ylabel("Frecuencia", fontsize=12)
    ax.set_title(f"Distribución de Longitud de Segmentos — {ZONA_NOMBRE}",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(IMG_DIR / "graf_03_histograma_segmentos.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"      Media: {np.mean(longitudes):.1f}m | Mediana: {np.median(longitudes):.1f}m")


def graf_04_boxplot(longitudes):
    """Boxplot de segmentos peatonales."""
    print("[6/8] Gráfico 4: Boxplot de segmentos...")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.boxplot(longitudes, vert=True, patch_artist=True,
               boxprops=dict(facecolor="#2A9C8A", alpha=0.7),
               medianprops=dict(color="#E53935", linewidth=2),
               flierprops=dict(marker="o", markerfacecolor="#1B4F8A", markersize=4, alpha=0.5))
    ax.set_ylabel("Longitud (m)", fontsize=12)
    ax.set_title(f"Boxplot de Segmentos Peatonales — {ZONA_NOMBRE}",
                 fontsize=13, fontweight="bold")
    ax.set_xticklabels(["Segmentos peatonales"])
    stats_text = (f"n={len(longitudes)}\nMedia={np.mean(longitudes):.1f}m\n"
                  f"Mediana={np.median(longitudes):.1f}m\nStd={np.std(longitudes):.1f}m")
    ax.text(1.3, np.median(longitudes), stats_text, fontsize=10,
            verticalalignment="center", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
    plt.tight_layout()
    plt.savefig(IMG_DIR / "graf_04_boxplot_segmentos.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"      Exportado: graf_04_boxplot_segmentos.png")


def graf_05_scatter(longitudes, stats_osm, area_km2):
    """Scatter plot de conectividad."""
    print("[7/8] Gráfico 5: Scatter de conectividad...")
    long_prom = np.mean(longitudes)
    densidad_int = stats_osm["intersection_count"] / area_km2

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(long_prom, densidad_int, s=200, c="#2E7D32", marker="D",
               edgecolors="black", linewidth=1.5, zorder=5)
    ax.annotate(f"Roosevelt\n({long_prom:.1f}m, {densidad_int:.0f} int/km²)",
                xy=(long_prom, densidad_int),
                xytext=(long_prom + 5, densidad_int + 30),
                fontsize=11, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="black"))
    ax.axhspan(400, 700, alpha=0.1, color="green", label="Rango espejo válido (400-700 int/km²)")
    ax.axhline(400, color="green", linestyle="--", alpha=0.4)
    ax.axhline(700, color="green", linestyle="--", alpha=0.4)
    ax.set_xlabel("Longitud promedio de segmento (m)", fontsize=12)
    ax.set_ylabel("Densidad de intersecciones (int/km²)", fontsize=12)
    ax.set_title(f"Posición Morfológica — {ZONA_NOMBRE}", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(IMG_DIR / "graf_05_scatter_conectividad.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"      Long. promedio: {long_prom:.1f}m | Densidad: {densidad_int:.0f} int/km²")


def graf_06_tabla(stats_osm, longitudes, area_m2, area_km2, G):
    """Tabla resumen de métricas urbanas."""
    print("[8/8] Gráfico 6: Tabla resumen...")
    longitud_total_km = stats_osm["edge_length_total"] / 1000
    densidad_km_km2 = longitud_total_km / area_km2
    densidad_int_km2 = stats_osm["intersection_count"] / area_km2

    tabla = pd.DataFrame({
        "Métrica": [
            "Área total (ha)", "Área total (km²)", "Intersecciones peatonales",
            "Longitud total de red (km)", "Longitud promedio segmento (m)",
            "Mediana segmento (m)", "Densidad de calle (km/km²)",
            "Densidad de intersecciones (int/km²)", "Nodos OSM", "Segmentos OSM",
        ],
        "Valor": [
            round(area_m2 / 10000, 2), round(area_km2, 4),
            stats_osm["intersection_count"], round(longitud_total_km, 2),
            round(np.mean(longitudes), 1), round(np.median(longitudes), 1),
            round(densidad_km_km2, 2), round(densidad_int_km2, 0),
            len(G.nodes), len(G.edges),
        ]
    })

    print(tabla.to_string(index=False))
    tabla.to_csv(RESULTS_DIR / "roosevelt_tabla_resumen_metricas.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    table = ax.table(cellText=tabla.values, colLabels=tabla.columns,
                     cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    ax.set_title(f"Métricas Urbanas — {ZONA_NOMBRE}\n{datetime.date.today().isoformat()}",
                 fontsize=12, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(IMG_DIR / "graf_06_tabla_metricas.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"      CSV: roosevelt_tabla_resumen_metricas.csv")
    print(f"      PNG: graf_06_tabla_metricas.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"GRÁFICOS BASE — CAMINABILIDAD — {ZONA_NOMBRE}")
    print(f"Fecha: {datetime.date.today().isoformat()} | CRS: {CRS_WGS84}")
    print("=" * 60)

    G, gdf_poligono, polygon, area_m2 = cargar_datos()
    area_km2 = area_m2 / 1_000_000

    stats_osm = ox.basic_stats(G, area=area_m2)
    gdf_edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
    longitudes = gdf_edges["length"].values

    graf_01_red_peatonal(G)
    graf_02_heatmap_intersecciones(G, gdf_poligono)
    graf_03_histograma(longitudes)
    graf_04_boxplot(longitudes)
    graf_05_scatter(longitudes, stats_osm, area_km2)
    graf_06_tabla(stats_osm, longitudes, area_m2, area_km2, G)

    print("\n" + "=" * 60)
    print("✓ 6 gráficos generados en:", IMG_DIR)
    print("✓ Tabla CSV en:", RESULTS_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()
