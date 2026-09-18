"""
Genera un informe PDF de caminabilidad de Barrio Obrero.

Compila las métricas de línea base y las figuras generadas por el notebook
(caminabilidad_barrio_obrero_v2.ipynb) en un único PDF.

NOTA: se excluye la sección "Indicadores complementarios" (Celda 10), por no ser
relevante para el análisis de caminabilidad de este trabajo.

Uso:
    uv run notebooks_py/generar_informe_barrio_obrero.py

Requiere: matplotlib (y pillow para leer PNG). No requiere reportlab.
"""

import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = PROJECT_ROOT / "outputs" / "figures"
RESULTS_DIR = PROJECT_ROOT / "outputs" / "results"
INFORMES_DIR = PROJECT_ROOT / "outputs" / "informes"
INFORMES_DIR.mkdir(parents=True, exist_ok=True)

FECHA = datetime.date.today().isoformat()

# Métricas de línea base (Barrio Obrero) y referencia Comuna 9
METRICAS_BO = [
    ("Área del polígono", "37.73 ha (377,329 m²)"),
    ("Intersecciones peatonales", "233"),
    ("Longitud red peatonal", "26.93 km"),
    ("Longitud promedio de segmento", "41.6 m"),
    ("Densidad de calle", "71.38 km/km²"),
    ("Densidad de intersecciones", "617 int/km²"),
    ("Nodos OSM", "233"),
    ("Segmentos OSM", "648"),
]

COMPARACION = [
    ("Métrica", "Barrio Obrero", "Comuna 9"),
    ("Área (ha)", "37.73", "290.38"),
    ("Intersecciones", "233", "2.255"),
    ("Longitud red (km)", "26.93", "227.52"),
    ("Long. prom. segmento (m)", "41.6", "34.8"),
    ("Densidad calle (km/km²)", "71.38", "78.35"),
    ("Densidad intersecciones (int/km²)", "617", "777"),
]

# Figuras a incluir (título, archivo). Se EXCLUYE indicadores complementarios.
FIGURAS = [
    ("Red peatonal — línea base", "graf_01_red_peatonal_barrio_obrero.png"),
    ("Densidad de intersecciones (KDE) y ejes viales IDESC", "graf_02_heatmap_intersecciones_barrio_obrero.png"),
    ("Distribución de longitud de segmentos", "graf_03_histograma_segmentos_barrio_obrero.png"),
    ("Boxplot de segmentos peatonales", "graf_04_boxplot_segmentos_barrio_obrero.png"),
    ("Posición morfológica — Barrio Obrero vs Comuna 9", "graf_05_scatter_conectividad_barrio_obrero.png"),
    ("Tabla resumen de métricas urbanas", "graf_06_tabla_metricas_barrio_obrero.png"),
    ("Panel de métricas de caminabilidad", "graf_metricas_caminabilidad_barrio_obrero.png"),
    ("Comparación Barrio Obrero vs Comuna 9", "graf_comparacion_barrio_obrero_vs_comuna9.png"),
]

AZUL = "#1B4F8A"
VERDE = "#2E7D32"


def _pagina_portada(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))  # A4 vertical
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0.82), 1, 0.18, color=AZUL, transform=ax.transAxes))
    ax.text(0.5, 0.90, "Índice de Caminabilidad", ha="center", va="center",
            fontsize=24, fontweight="bold", color="white", transform=ax.transAxes)
    ax.text(0.5, 0.855, "Barrio Obrero — Cali", ha="center", va="center",
            fontsize=18, color="white", transform=ax.transAxes)
    ax.text(0.5, 0.70, "Informe de línea base de caminabilidad", ha="center",
            fontsize=15, fontweight="bold", color=AZUL, transform=ax.transAxes)
    ax.text(0.5, 0.655, "ITT Cali Inteligente · Equipo de Gobierno de Datos",
            ha="center", fontsize=11, color="#444444", transform=ax.transAxes)
    ax.text(0.5, 0.62, f"Fecha: {FECHA}", ha="center", fontsize=11,
            color="#444444", transform=ax.transAxes)

    resumen = (
        "Este informe presenta las métricas de caminabilidad del Barrio Obrero (Cali),\n"
        "calculadas a partir de la red peatonal de OpenStreetMap (OSMnx). La unidad de\n"
        "análisis es el polígono único del barrio (37.73 ha). Se incluye la comparación\n"
        "con la Comuna 9, que contiene al barrio, como contexto territorial.\n\n"
        "Sistema de referencia: WGS84 (EPSG:4326) para datos y visualización; EPSG:3116\n"
        "solo para cálculos de área y distancia.\n\n"
        "Nota: se excluye la sección de indicadores complementarios (eventos), por no ser\n"
        "relevante para el análisis de caminabilidad de este trabajo."
    )
    ax.text(0.1, 0.50, resumen, ha="left", va="top", fontsize=10.5,
            color="#222222", transform=ax.transAxes, linespacing=1.6)

    # Métricas clave en portada
    ax.text(0.1, 0.30, "Métricas de línea base", fontsize=13, fontweight="bold",
            color=VERDE, transform=ax.transAxes)
    y = 0.265
    for k, v in METRICAS_BO:
        ax.text(0.12, y, f"•  {k}:", fontsize=10.5, color="#222222", transform=ax.transAxes)
        ax.text(0.62, y, v, fontsize=10.5, fontweight="bold", color="#222222", transform=ax.transAxes)
        y -= 0.028
    pdf.savefig(fig); plt.close(fig)


def _pagina_comparacion(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.08, 0.55, 0.84, 0.4]); ax.axis("off")
    ax.set_title("Comparación de caminabilidad — Barrio Obrero vs Comuna 9",
                 fontsize=13, fontweight="bold", color=AZUL, pad=20)
    tabla = ax.table(cellText=COMPARACION[1:], colLabels=COMPARACION[0],
                     cellLoc="center", loc="center")
    tabla.auto_set_font_size(False); tabla.set_fontsize(9.5); tabla.scale(1, 1.8)
    for j in range(3):
        tabla[0, j].set_facecolor(AZUL)
        tabla[0, j].set_text_props(color="white", fontweight="bold")

    ax2 = fig.add_axes([0.08, 0.08, 0.84, 0.4]); ax2.axis("off")
    interp = (
        "Interpretación\n\n"
        "Las densidades (km/km² y int/km²) son las métricas comparables entre zonas de\n"
        "distinto tamaño; las cifras absolutas (intersecciones, longitud total) favorecen a\n"
        "la Comuna 9 solo por su mayor área.\n\n"
        "Barrio Obrero registra 617 int/km² y 71.38 km/km², valores propios de una trama\n"
        "urbana densa y caminable, muy por encima del umbral de salud pública (~100 int/km²).\n"
        "La Comuna 9 es algo más densa (777 int/km²) y con segmentos más cortos (34.8 m vs\n"
        "41.6 m), lo que ubica a Barrio Obrero como un barrio bien conectado dentro de un\n"
        "contexto comunal favorable para caminar.\n\n"
        "Referencias de contexto: US EPA EnviroAtlas; estudio IPEN / U. de Melbourne\n"
        "(~100 int/km² como umbral); regulación de barrios caminables de Queensland (cuadras\n"
        "≤ 250 m); Stangl (2015). Umbrales mayormente anglosajones, usados como comparación."
    )
    ax2.text(0, 1, interp, ha="left", va="top", fontsize=10, color="#222222",
             transform=ax2.transAxes, linespacing=1.6)
    pdf.savefig(fig); plt.close(fig)


def _pagina_figura(pdf, titulo, archivo):
    ruta = FIG_DIR / archivo
    if not ruta.exists():
        print(f"  ! figura no encontrada, se omite: {archivo}")
        return False
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.95, titulo, ha="center", fontsize=13, fontweight="bold", color=AZUL)
    ax = fig.add_axes([0.05, 0.06, 0.9, 0.85]); ax.axis("off")
    img = mpimg.imread(ruta)
    ax.imshow(img)
    pdf.savefig(fig); plt.close(fig)
    return True


def main():
    salida = INFORMES_DIR / "informe_caminabilidad_barrio_obrero.pdf"
    print("Generando informe PDF...")
    with PdfPages(salida) as pdf:
        _pagina_portada(pdf)
        _pagina_comparacion(pdf)
        incluidas = 0
        for titulo, archivo in FIGURAS:
            if _pagina_figura(pdf, titulo, archivo):
                incluidas += 1
        d = pdf.infodict()
        d["Title"] = "Informe Caminabilidad — Barrio Obrero"
        d["Author"] = "ITT Cali Inteligente · Gobierno de Datos"
        d["Subject"] = "Línea base de caminabilidad (OSMnx)"
    print(f"  Figuras incluidas: {incluidas}/{len(FIGURAS)}")
    print(f"  (Excluida la sección de indicadores complementarios)")
    print(f"PDF generado: {salida}")


if __name__ == "__main__":
    main()
