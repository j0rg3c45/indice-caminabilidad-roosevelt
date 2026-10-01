"""
AWS Lambda — Índice de Caminabilidad (CaliTrack)
================================================

Replica el pipeline del notebook `caminabilidad_barrio_obrero_v2.ipynb`:

1. Carga el polígono de la zona (desde S3, GeoJSON/ZIP) y lo normaliza a WGS84.
2. Descarga la red peatonal de OpenStreetMap (OSMnx, network_type='walk', simplify=False).
3. Calcula las métricas de caminabilidad (intersecciones, longitud de red,
   densidad de calle, densidad de intersecciones, etc.).
4. (Opcional) Compara con un polígono de referencia (p. ej. la comuna que la contiene).
5. Calcula el Índice de Caminabilidad (0–100) con referencias fijas y pesos configurables.
6. Genera el mapa interactivo Folium con las capas de la "Celda 9" del notebook
   (bases CartoDB/OSM/Esri/Google, polígono, tramo, red peatonal, nodos, mapa de calor,
   y capas de eventos), y lo guarda como HTML.
7. Escribe métricas (JSON/CSV), red peatonal (GeoJSON) y mapa (HTML) en S3.

Sistema de referencia: WGS84 (EPSG:4326) para todo; EPSG:3116 solo para área/distancia.

--------------------------------------------------------------------------------
EVENTO DE ENTRADA (JSON). Todos los campos son opcionales excepto que debe haber
una forma de obtener el polígono (poligono_s3_key o bbox).

{
  "zona_nombre": "Barrio Obrero",
  "bucket": "aca-prod-calitrack-sismo-cali",
  "poligono_s3_key": "insumos/barrio_obrero/Geojson_Barrio_Obrero.geojson",
  "poligono_capa_en_zip": "Geojson_Barrio_Obrero.geojson",   # si la key es un .zip
  "tramo_s3_key": "insumos/barrio_obrero/tramo_Barrio_obrero.geojson",  # opcional
  "eventos": {                                               # opcional
     "comparendos": "insumos/barrio_obrero/comparendos.geojson",
     "hurtos": "insumos/barrio_obrero/hurtos.geojson"
  },
  "referencia_poligono_s3_key": "insumos/comuna9/comuna9.geojson",  # opcional (comparación)
  "referencia_nombre": "Comuna 9",
  "pesos": {"densidad_intersecciones_km2": 0.45, "densidad_calle_km_km2": 0.35, "longitud_promedio_segmento_m": 0.20},
  "salida_prefix": "resultados/caminabilidad/barrio_obrero"   # prefijo en S3 para las salidas
}

Variables de entorno (con valores por defecto):
  OUTPUT_BUCKET   -> bucket por defecto para leer/escribir (default: aca-prod-calitrack-sismo-cali)
  DEFAULT_PREFIX  -> prefijo de salida por defecto (default: resultados/caminabilidad)
"""

import os
import io
import re
import json
import zipfile
import logging
import datetime
import tempfile

import boto3
import numpy as np
import geopandas as gpd
import osmnx as ox
import folium
from folium.plugins import HeatMap

logging.getLogger("pyogrio").setLevel(logging.ERROR)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
CRS_WGS84 = "EPSG:4326"
CRS_COLOMBIA = "EPSG:3116"

DEFAULT_BUCKET = os.environ.get("OUTPUT_BUCKET", "aca-prod-calitrack-sismo-cali")
DEFAULT_PREFIX = os.environ.get("DEFAULT_PREFIX", "resultados/caminabilidad")

# Referencias fijas (ref_min, ref_max, sentido) para el índice de caminabilidad
REFERENCIAS = {
    "densidad_intersecciones_km2": (100, 800, "directo"),
    "densidad_calle_km_km2":       (20,  90,  "directo"),
    "longitud_promedio_segmento_m": (40, 150, "inverso"),
}
PESOS_DEFAULT = {
    "densidad_intersecciones_km2": 0.45,
    "densidad_calle_km_km2":       0.35,
    "longitud_promedio_segmento_m": 0.20,
}

COLORES_EVENTOS = {
    "comparendos": "orange", "homicidios": "darkred",
    "hurtos": "purple", "vif": "darkpurple", "censo_arboreo": "green",
}

# OSMnx: usar carpeta de cache escribible en Lambda (/tmp)
try:
    ox.settings.cache_folder = "/tmp/osmnx_cache"
    ox.settings.use_cache = True
    ox.settings.log_console = False
except Exception:
    pass

s3 = boto3.client("s3")


# ---------------------------------------------------------------------------
# Utilidades S3 / carga de geometrías
# ---------------------------------------------------------------------------
def _leer_gdf_desde_s3(bucket, key, capa_en_zip=None):
    """Descarga un objeto de S3 y lo carga como GeoDataFrame, normalizado a WGS84.
    Soporta .geojson/.json directos y .zip (indicando la capa interna)."""
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj["Body"].read()

    if key.lower().endswith(".zip"):
        # Guardar el zip en /tmp y leer con el prefijo zip://
        tmp_zip = os.path.join(tempfile.gettempdir(), os.path.basename(key))
        with open(tmp_zip, "wb") as f:
            f.write(data)
        if capa_en_zip is None:
            # Buscar el primer .geojson dentro del zip
            with zipfile.ZipFile(tmp_zip) as z:
                candidatos = [n for n in z.namelist() if n.lower().endswith(".geojson")]
                if not candidatos:
                    raise ValueError(f"No hay .geojson dentro de {key}")
                capa_en_zip = candidatos[0]
        gdf = gpd.read_file(f"zip://{tmp_zip}!{capa_en_zip}")
    else:
        gdf = gpd.read_file(io.BytesIO(data))

    return _asegurar_wgs84(gdf)


def _asegurar_wgs84(gdf):
    if gdf.crs is None:
        gdf = gdf.set_crs(CRS_WGS84)
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(CRS_WGS84)
    return gdf


def _poligono_desde_bbox(bbox):
    """bbox = [min_lon, min_lat, max_lon, max_lat] -> GeoDataFrame WGS84."""
    from shapely.geometry import box
    geom = box(bbox[0], bbox[1], bbox[2], bbox[3])
    return gpd.GeoDataFrame(geometry=[geom], crs=CRS_WGS84)


def _subir_s3(bucket, key, cuerpo, content_type):
    s3.put_object(Bucket=bucket, Key=key, Body=cuerpo, ContentType=content_type)
    logger.info("Subido a s3://%s/%s", bucket, key)
    return f"s3://{bucket}/{key}"


# ---------------------------------------------------------------------------
# Núcleo del análisis
# ---------------------------------------------------------------------------
def _metricas_de_poligono(gdf_poligono):
    """Descarga la red peatonal OSM del polígono y calcula métricas + grafo."""
    polygon_wgs84 = gdf_poligono.geometry.union_all() if hasattr(gdf_poligono.geometry, "union_all") \
        else gdf_poligono.geometry.unary_union

    area_m2 = gdf_poligono.to_crs(CRS_COLOMBIA).geometry.area.sum()
    area_km2 = area_m2 / 1_000_000

    G = ox.graph_from_polygon(polygon_wgs84, network_type="walk", simplify=False)
    stats = ox.basic_stats(G, area=area_m2)
    edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
    longitudes = edges["length"].values

    longitud_total_km = stats["edge_length_total"] / 1000
    metricas = {
        "area_m2": round(float(area_m2), 0),
        "area_ha": round(float(area_m2) / 10000, 2),
        "intersecciones_peatonales": int(stats["intersection_count"]),
        "longitud_red_peatonal_km": round(float(longitud_total_km), 2),
        "longitud_promedio_segmento_m": round(float(np.mean(longitudes)), 1),
        "densidad_calle_km_km2": round(float(longitud_total_km / area_km2), 2),
        "densidad_intersecciones_km2": round(float(stats["intersection_count"] / area_km2), 0),
        "nodos_osm": int(len(G.nodes)),
        "segmentos_osm": int(len(G.edges)),
    }
    return G, metricas, polygon_wgs84


def _score(valor, ref_min, ref_max, sentido):
    if sentido == "inverso":
        s = 100.0 * (ref_max - valor) / (ref_max - ref_min)
    else:
        s = 100.0 * (valor - ref_min) / (ref_max - ref_min)
    return float(max(0.0, min(100.0, s)))


def _indice_caminabilidad(metricas, pesos):
    """Calcula el índice 0–100 a partir de las métricas y los pesos."""
    detalle = {}
    indice = 0.0
    for ind, (rmin, rmax, sentido) in REFERENCIAS.items():
        val = metricas[ind]
        sc = _score(val, rmin, rmax, sentido)
        detalle[ind] = {"valor": round(val, 2), "score": round(sc, 1)}
        indice += pesos[ind] * sc
    return round(indice, 1), detalle


# ---------------------------------------------------------------------------
# Mapa interactivo (equivalente a la Celda 9 del notebook)
# ---------------------------------------------------------------------------
def _construir_mapa(gdf_poligono, G, gdf_tramo=None, datasets=None, zona_nombre="Zona"):
    datasets = datasets or {}
    polygon_wgs84 = gdf_poligono.geometry.union_all() if hasattr(gdf_poligono.geometry, "union_all") \
        else gdf_poligono.geometry.unary_union
    centroid = polygon_wgs84.centroid

    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=16, tiles=None)

    # Capas base
    folium.TileLayer("CartoDB positron", name="CartoDB Claro").add_to(m)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Esri Satélite", overlay=False,
    ).add_to(m)
    folium.TileLayer(
        tiles="http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google", name="Google Streets",
        subdomains=["mt0", "mt1", "mt2", "mt3"], overlay=False,
    ).add_to(m)
    folium.TileLayer(
        tiles="http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google", name="Google Satélite",
        subdomains=["mt0", "mt1", "mt2", "mt3"], overlay=False,
    ).add_to(m)

    # Polígono de la zona
    folium.GeoJson(
        gdf_poligono.__geo_interface__,
        name=f"Polígono {zona_nombre}",
        style_function=lambda x: {"color": "#1B4F8A", "fillColor": "#2E7D32",
                                  "fillOpacity": 0.1, "weight": 2},
    ).add_to(m)

    # Tramo / eje (opcional)
    if gdf_tramo is not None and len(gdf_tramo) > 0:
        folium.GeoJson(
            gdf_tramo.__geo_interface__,
            name=f"Tramo {zona_nombre} (eje)",
            style_function=lambda x: {"color": "#E53935", "weight": 4, "opacity": 0.9},
        ).add_to(m)

    # Red peatonal OSM (líneas)
    gdf_edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
    gdf_edges = gdf_edges.to_crs(CRS_WGS84) if gdf_edges.crs.to_epsg() != 4326 else gdf_edges
    folium.GeoJson(
        gdf_edges[["geometry"]].__geo_interface__,
        name="Red peatonal OSM (líneas)",
        style_function=lambda x: {"color": "#2A9C8A", "weight": 2, "opacity": 0.7},
    ).add_to(m)

    # Nodos (intersecciones)
    gdf_nodes = ox.graph_to_gdfs(G, nodes=True, edges=False)
    gdf_nodes = gdf_nodes.to_crs(CRS_WGS84) if gdf_nodes.crs.to_epsg() != 4326 else gdf_nodes
    fg_nodos = folium.FeatureGroup(name="Nodos (intersecciones)", show=True)
    for _, row in gdf_nodes.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=3, color="#E53935", fill=True, fill_opacity=0.9, weight=1,
        ).add_to(fg_nodos)
    fg_nodos.add_to(m)

    # Mapa de calor de intersecciones
    if "street_count" in gdf_nodes.columns:
        inter = gdf_nodes[gdf_nodes["street_count"] > 2]
    else:
        inter = gdf_nodes
    heat_data = [[pt.y, pt.x] for pt in inter.geometry]
    fg_heat = folium.FeatureGroup(name="Mapa de calor — intersecciones", show=False)
    HeatMap(heat_data, radius=18, blur=15, min_opacity=0.3).add_to(fg_heat)
    fg_heat.add_to(m)

    # Capas de eventos
    for nombre, gdf in datasets.items():
        fg = folium.FeatureGroup(name=nombre.replace("_", " ").capitalize(), show=False)
        color = COLORES_EVENTOS.get(nombre, "gray")
        for _, row in gdf.iterrows():
            geom = row.geometry
            if geom is None or geom.geom_type != "Point":
                continue
            folium.CircleMarker(
                location=[geom.y, geom.x],
                radius=3, color=color, fill=True, fill_opacity=0.6,
            ).add_to(fg)
        fg.add_to(m)

    folium.LayerControl().add_to(m)
    return m, len(heat_data)


# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------
def lambda_handler(event, context):
    event = event or {}
    zona_nombre = event.get("zona_nombre", "Barrio Obrero")
    bucket = event.get("bucket", DEFAULT_BUCKET)
    pesos = event.get("pesos", PESOS_DEFAULT)
    salida_prefix = event.get("salida_prefix", f"{DEFAULT_PREFIX}/{_slug(zona_nombre)}")
    fecha = datetime.date.today().isoformat()

    logger.info("Iniciando caminabilidad para '%s' (bucket=%s)", zona_nombre, bucket)

    # 1) Polígono de la zona
    if event.get("poligono_s3_key"):
        gdf_poligono = _leer_gdf_desde_s3(
            bucket, event["poligono_s3_key"], event.get("poligono_capa_en_zip"))
    elif event.get("bbox"):
        gdf_poligono = _poligono_desde_bbox(event["bbox"])
    else:
        raise ValueError("Debe proporcionar 'poligono_s3_key' o 'bbox' en el evento.")

    # 2-3) Red peatonal + métricas
    G, metricas, _ = _metricas_de_poligono(gdf_poligono)
    logger.info("Métricas zona: %s", metricas)

    # 4) Tramo (opcional)
    gdf_tramo = None
    if event.get("tramo_s3_key"):
        try:
            gdf_tramo = _leer_gdf_desde_s3(bucket, event["tramo_s3_key"])
        except Exception as e:
            logger.warning("No se pudo cargar el tramo: %s", e)

    # 5) Eventos (opcional)
    datasets = {}
    indicadores = {}
    for nombre, key in (event.get("eventos") or {}).items():
        try:
            gdf_ev = _leer_gdf_desde_s3(bucket, key)
            datasets[nombre] = gdf_ev
            dens = len(gdf_ev) / (metricas["area_ha"] or 1)
            indicadores[nombre] = {"total": int(len(gdf_ev)), "densidad_por_ha": round(dens, 2)}
        except Exception as e:
            logger.warning("No se pudo cargar el evento '%s': %s", nombre, e)

    # 6) Índice de caminabilidad de la zona
    indice, detalle = _indice_caminabilidad(metricas, pesos)

    # 7) Comparación con polígono de referencia (opcional)
    referencia = None
    if event.get("referencia_poligono_s3_key"):
        try:
            gdf_ref = _leer_gdf_desde_s3(bucket, event["referencia_poligono_s3_key"])
            _, met_ref, _ = _metricas_de_poligono(gdf_ref)
            idx_ref, det_ref = _indice_caminabilidad(met_ref, pesos)
            referencia = {
                "nombre": event.get("referencia_nombre", "Referencia"),
                "metricas": met_ref,
                "indice_caminabilidad": idx_ref,
                "detalle_indice": det_ref,
            }
        except Exception as e:
            logger.warning("No se pudo procesar la referencia: %s", e)

    # --- Ensamblar resultado ---
    resultado = {
        "zona": zona_nombre,
        "fecha_medicion": fecha,
        "crs_trabajo": CRS_WGS84,
        "crs_calculo": CRS_COLOMBIA,
        "fuente": "OpenStreetMap via OSMnx",
        "metricas": metricas,
        "indicadores_complementarios": indicadores,
        "indice_caminabilidad": indice,
        "detalle_indice": detalle,
        "pesos": pesos,
        "referencias_indice": {k: {"ref_min": v[0], "ref_max": v[1], "sentido": v[2]}
                               for k, v in REFERENCIAS.items()},
        "comparacion_referencia": referencia,
    }

    # --- Escribir salidas en S3 ---
    salidas = {}

    # JSON de resultados
    salidas["json"] = _subir_s3(
        bucket, f"{salida_prefix}/{fecha}/resultado_caminabilidad.json",
        json.dumps(resultado, ensure_ascii=False, indent=2).encode("utf-8"),
        "application/json; charset=utf-8")

    # CSV plano de métricas + índice
    csv_row = {**{"zona": zona_nombre, "fecha": fecha}, **metricas,
               "indice_caminabilidad": indice}
    csv_txt = ",".join(csv_row.keys()) + "\n" + ",".join(str(v) for v in csv_row.values()) + "\n"
    salidas["csv"] = _subir_s3(
        bucket, f"{salida_prefix}/{fecha}/metricas_caminabilidad.csv",
        csv_txt.encode("utf-8"), "text/csv; charset=utf-8")

    # Red peatonal como GeoJSON
    gdf_edges = ox.graph_to_gdfs(G, nodes=False, edges=True).to_crs(CRS_WGS84)
    salidas["red_geojson"] = _subir_s3(
        bucket, f"{salida_prefix}/{fecha}/red_peatonal_osm.geojson",
        gdf_edges[["geometry"]].to_json().encode("utf-8"),
        "application/geo+json; charset=utf-8")

    # Mapa interactivo HTML (Celda 9)
    m, n_heat = _construir_mapa(gdf_poligono, G, gdf_tramo, datasets, zona_nombre)
    html = m.get_root().render()
    salidas["mapa_html"] = _subir_s3(
        bucket, f"{salida_prefix}/{fecha}/mapa_caminabilidad.html",
        html.encode("utf-8"), "text/html; charset=utf-8")

    logger.info("Proceso completado. Índice=%s | intersecciones heat=%s", indice, n_heat)

    return {
        "statusCode": 200,
        "body": {
            "zona": zona_nombre,
            "indice_caminabilidad": indice,
            "metricas": metricas,
            "comparacion": (
                {"nombre": referencia["nombre"], "indice": referencia["indice_caminabilidad"]}
                if referencia else None
            ),
            "salidas_s3": salidas,
        },
    }


def _slug(texto):
    s = texto.lower().strip()
    s = re.sub(r"[áàä]", "a", s); s = re.sub(r"[éèë]", "e", s)
    s = re.sub(r"[íìï]", "i", s); s = re.sub(r"[óòö]", "o", s)
    s = re.sub(r"[úùü]", "u", s); s = re.sub(r"ñ", "n", s)
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s or "zona"


# Ejecución local para pruebas: python lambda_function.py evento.json
if __name__ == "__main__":
    import sys
    ev = {}
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            ev = json.load(f)
    print(json.dumps(lambda_handler(ev, None), ensure_ascii=False, indent=2, default=str))
