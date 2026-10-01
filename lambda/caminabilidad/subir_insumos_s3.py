"""
Sube a S3 los insumos que necesita el Lambda de caminabilidad y genera el evento JSON.

- Renombra los archivos a nombres cortos y estables (comparendos.geojson, hurtos.geojson, ...).
- Extrae la Comuna 9 desde comunas.geojson (IDESC) y la sube como comuna9.geojson.
- Deja todo bajo:  s3://<bucket>/insumos/<zona_slug>/
- Escribe un evento de ejemplo (evento_barrio_obrero.json) listo para invocar el Lambda.

Uso (con el perfil calitrack ya autenticado por SSO):
    aws sso login --profile calitrack
    uv run lambda/caminabilidad/subir_insumos_s3.py

Opciones:
    --bucket   Bucket destino (default: aca-prod-calitrack-sismo-cali)
    --perfil   Perfil AWS CLI/boto3 (default: calitrack)
    --zona     Nombre de la zona (default: Barrio Obrero)
    --dry-run  No sube nada; solo muestra qué haría y genera el evento.
"""

import argparse
import json
import re
from pathlib import Path

import boto3
import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_BO = PROJECT_ROOT / "data" / "Geojson_Barrio_Obrero"
EVENTOS_DIR = DATA_BO / "nueva_data" / "geojson_filtrado_poligono_Barrio_Obrero"
IDESC_DIR = DATA_BO / "GeoJson_IDESC"

# Mapeo: nombre destino en S3  ->  archivo local de origen
POLIGONO_LOCAL = DATA_BO / "Geojson_Barrio_Obrero.geojson"
TRAMO_LOCAL = DATA_BO / "tramo_Barrio_obrero.geojson"

EVENTOS_MAP = {
    "comparendos.geojson": EVENTOS_DIR / "DATIC_comparendos_2023_2026T1_filtrado_poligono_Barrio_Obrero.geojson",
    "hurtos.geojson":      EVENTOS_DIR / "DATIC_hurtos_2023_2026T1_filtrado_poligono_Barrio_Obrero.geojson",
    "homicidios.geojson":  EVENTOS_DIR / "DATIC_homicidios_2023_2026T1_filtrado_poligono_Barrio_Obrero.geojson",
    "vif.geojson":         EVENTOS_DIR / "DATIC_violencia_intrafamiliar_2023_2026T1_filtrado_poligono_Barrio_Obrero.geojson",
    "censo_arboreo.geojson": EVENTOS_DIR / "CENSO_ARBOREO_filtrado_poligono_Barrio_Obrero.geojson",
}


def _slug(texto):
    s = texto.lower().strip()
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")]:
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_") or "zona"


def _subir(s3, bucket, key, ruta_local, dry_run):
    if not ruta_local.exists():
        print(f"  [SKIP] no existe: {ruta_local.name}")
        return False
    if dry_run:
        print(f"  [DRY]  {ruta_local.name}  ->  s3://{bucket}/{key}")
        return True
    s3.upload_file(str(ruta_local), bucket, key,
                   ExtraArgs={"ContentType": "application/geo+json"})
    print(f"  [OK]   s3://{bucket}/{key}")
    return True


def _extraer_comuna9(dry_run):
    """Extrae la Comuna 9 de comunas.geojson y la guarda como archivo temporal local."""
    src = IDESC_DIR / "comunas.geojson"
    if not src.exists():
        print(f"  [SKIP] no existe comunas.geojson en {IDESC_DIR}")
        return None
    gdf = gpd.read_file(src)
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")
    elif gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    c9 = gdf[gdf["comuna"].astype(str) == "9"]
    if len(c9) == 0:
        print("  [SKIP] Comuna 9 no encontrada en comunas.geojson")
        return None
    out = DATA_BO / "comuna9.geojson"
    if not dry_run:
        c9.to_file(out, driver="GeoJSON")
    print(f"  [OK]   Comuna 9 extraída -> {out.name}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", default="aca-prod-calitrack-sismo-cali")
    ap.add_argument("--perfil", default="calitrack")
    ap.add_argument("--zona", default="Barrio Obrero")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    zona_slug = _slug(args.zona)
    prefijo = f"insumos/{zona_slug}"

    session = boto3.Session(profile_name=args.perfil)
    s3 = session.client("s3")

    print(f"Zona: {args.zona}  |  bucket: {args.bucket}  |  perfil: {args.perfil}")
    print(f"Prefijo destino: s3://{args.bucket}/{prefijo}/")
    if args.dry_run:
        print("(DRY-RUN: no se sube nada)\n")

    evento = {
        "zona_nombre": args.zona,
        "bucket": args.bucket,
        "salida_prefix": f"resultados/caminabilidad/{zona_slug}",
        "eventos": {},
    }

    print("\n1) Polígono de la zona")
    if _subir(s3, args.bucket, f"{prefijo}/poligono.geojson", POLIGONO_LOCAL, args.dry_run):
        evento["poligono_s3_key"] = f"{prefijo}/poligono.geojson"

    print("\n2) Tramo / eje (opcional)")
    if _subir(s3, args.bucket, f"{prefijo}/tramo.geojson", TRAMO_LOCAL, args.dry_run):
        evento["tramo_s3_key"] = f"{prefijo}/tramo.geojson"

    print("\n3) Eventos complementarios (opcionales)")
    for destino, origen in EVENTOS_MAP.items():
        if _subir(s3, args.bucket, f"{prefijo}/{destino}", origen, args.dry_run):
            nombre = destino.replace(".geojson", "")
            evento["eventos"][nombre] = f"{prefijo}/{destino}"

    print("\n4) Polígono de referencia — Comuna 9 (opcional)")
    comuna9 = _extraer_comuna9(args.dry_run)
    if comuna9 is not None:
        # En dry-run el archivo no se escribe, pero igual reflejamos la key en el evento.
        subido = _subir(s3, args.bucket, f"{prefijo}/comuna9.geojson", comuna9, args.dry_run) if comuna9.exists() else args.dry_run
        if subido:
            evento["referencia_poligono_s3_key"] = f"{prefijo}/comuna9.geojson"
            evento["referencia_nombre"] = "Comuna 9"

    # Guardar evento de ejemplo
    evento_path = Path(__file__).resolve().parent / "evento_barrio_obrero.json"
    evento_path.write_text(json.dumps(evento, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nEvento generado: {evento_path}")
    print(json.dumps(evento, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
