# Lambda — Índice de Caminabilidad (CaliTrack)

Replica en AWS el flujo del notebook `caminabilidad_barrio_obrero_v2.ipynb`:
carga del polígono → red peatonal OSM (OSMnx) → métricas → índice de caminabilidad
→ mapa interactivo multicapa (Celda 9) → salidas en S3 (JSON, CSV, GeoJSON, HTML).

- Región: `us-east-1`
- Perfil AWS: `calitrack` (cuenta 285757764705)
- Convención de nombres: `aca-prod-calitrack-*` + tag `Proyecto: CaliTrack`

---

## 1. Dependencias y herramientas, por capas

### Capa 0 — Herramientas de empaquetado/despliegue (en tu máquina)
- **Docker** (para construir la imagen del contenedor).
- **AWS CLI v2** autenticado por SSO (`aws sso login --profile calitrack`).
- (Opcional) **uv** para pruebas locales del handler.

### Capa 1 — Runtime base
- **Imagen base**: `public.ecr.aws/lambda/python:3.12` (AWS Lambda Python 3.12).
- **boto3** (incluido en el runtime de Lambda; se añade a requirements solo para pruebas locales).

### Capa 2 — Librerías geoespaciales (con binarios nativos GDAL/GEOS/PROJ)
- `osmnx==2.1.0` — descarga y análisis de la red peatonal desde OpenStreetMap.
- `geopandas==1.1.3` — manejo de datos vectoriales.
- `shapely==2.1.2` — geometrías.
- `pyogrio==0.12.1` — lectura/escritura de GeoJSON (motor de GeoPandas).
- `pyproj==3.7.2` — reproyecciones de CRS (WGS84 ↔ EPSG:3116).

> Estas librerías traen wheels `manylinux` que incluyen GDAL/GEOS/PROJ, por eso NO
> hace falta instalarlos aparte en la imagen. Es también la razón por la que se usa
> **imagen de contenedor** y no un ZIP de Lambda (superarían el límite de 250 MB).

### Capa 3 — Cálculo y grafos
- `networkx==3.6.1` — grafo de la red peatonal.
- `scipy==1.17.1` — KDE del mapa de calor.
- `numpy==2.4.4`, `pandas==3.0.2` — cálculo numérico y tabular.

### Capa 4 — Mapas interactivos
- `folium==0.20.0`, `branca==0.8.2`, `mapclassify==2.11.0` — mapa HTML multicapa
  (capas base CartoDB/OSM/Esri/Google, polígono, tramo, red peatonal, nodos,
  mapa de calor y eventos).

### Capa 5 — Infraestructura AWS
- **ECR** (repositorio de la imagen): `aca-prod-calitrack-caminabilidad`.
- **Lambda** (contenedor): `aca-prod-calitrack-caminabilidad`.
  - Memoria recomendada: **2048 MB** (geoprocesamiento + descarga OSM).
  - Timeout recomendado: **600 s** (OSMnx consulta la API Overpass por red).
  - Almacenamiento efímero `/tmp`: **1024 MB**.
  - **Salida a internet**: sin VPC, o VPC con NAT Gateway (OSMnx necesita llamar a OSM).
- **S3** (insumos y resultados): `aca-prod-calitrack-sismo-cali`.
- **Rol de ejecución**: usar uno ya habilitado (no hay permiso IAM para crear roles)
  con permisos de lectura/escritura al bucket y logs en CloudWatch.

---

## 2. Subir los insumos a S3

Desde la raíz del repo, con el perfil autenticado:

```powershell
aws sso login --profile calitrack
$env:PYTHONUTF8="1"
uv run lambda/caminabilidad/subir_insumos_s3.py
```

Esto sube polígono, tramo, eventos y la Comuna 9 a
`s3://aca-prod-calitrack-sismo-cali/insumos/barrio_obrero/` y genera
`evento_barrio_obrero.json` (el payload de invocación).

---

## 3. Construir y publicar la imagen (ECR)

```powershell
$ACCOUNT = "285757764705"
$REGION  = "us-east-1"
$REPO    = "aca-prod-calitrack-caminabilidad"
$ECR     = "$ACCOUNT.dkr.ecr.$REGION.amazonaws.com"

# 3.1 Crear el repositorio ECR (una sola vez)
aws ecr create-repository --repository-name $REPO --region $REGION --profile calitrack

# 3.2 Login de Docker contra ECR
aws ecr get-login-password --region $REGION --profile calitrack | docker login --username AWS --password-stdin $ECR

# 3.3 Build (ejecutar dentro de lambda/caminabilidad)
cd lambda/caminabilidad
docker build -t ${REPO}:latest .

# 3.4 Tag + push
docker tag ${REPO}:latest ${ECR}/${REPO}:latest
docker push ${ECR}/${REPO}:latest
```

---

## 4. Crear o actualizar el Lambda

```powershell
$ACCOUNT = "285757764705"; $REGION = "us-east-1"
$REPO = "aca-prod-calitrack-caminabilidad"
$ECR  = "$ACCOUNT.dkr.ecr.$REGION.amazonaws.com"
$ROL  = "arn:aws:iam::$ACCOUNT:role/<ROL-EJECUCION-YA-HABILITADO>"   # usar uno existente

# Crear (primera vez)
aws lambda create-function `
  --function-name $REPO `
  --package-type Image `
  --code ImageUri=${ECR}/${REPO}:latest `
  --role $ROL `
  --timeout 600 --memory-size 2048 `
  --ephemeral-storage Size=1024 `
  --environment "Variables={OUTPUT_BUCKET=aca-prod-calitrack-sismo-cali,DEFAULT_PREFIX=resultados/caminabilidad}" `
  --tags Proyecto=CaliTrack `
  --region $REGION --profile calitrack

# Actualizar código tras un nuevo push de imagen
aws lambda update-function-code `
  --function-name $REPO `
  --image-uri ${ECR}/${REPO}:latest `
  --region $REGION --profile calitrack
```

---

## 5. Invocar

```powershell
aws lambda invoke `
  --function-name aca-prod-calitrack-caminabilidad `
  --payload fileb://lambda/caminabilidad/evento_barrio_obrero.json `
  --cli-binary-format raw-in-base64-out `
  --region us-east-1 --profile calitrack `
  salida.json

Get-Content salida.json
```

Las salidas quedan en:
`s3://aca-prod-calitrack-sismo-cali/resultados/caminabilidad/barrio_obrero/<fecha>/`
- `resultado_caminabilidad.json` — métricas, índice y comparación.
- `metricas_caminabilidad.csv`
- `red_peatonal_osm.geojson`
- `mapa_caminabilidad.html` — mapa interactivo (Celda 9).

---

## 6. Prueba local del handler (sin desplegar)

```powershell
$env:PYTHONUTF8="1"
uv run lambda/caminabilidad/lambda_function.py lambda/caminabilidad/evento_barrio_obrero.json
```

(Requiere acceso a S3 con el perfil `calitrack` y salida a internet para OSM.)

---

## Notas

- OSMnx consulta la API Overpass de OpenStreetMap: el Lambda **necesita salida a
  internet** y un timeout holgado. Si falla por tiempo, subir memoria/timeout.
- El token SSO expira; si un comando falla con `Token has expired`, correr de nuevo
  `aws sso login --profile calitrack`.
- No se crean roles/políticas (sin permiso IAM): reutilizar un rol de ejecución ya
  habilitado que permita leer/escribir el bucket y escribir logs en CloudWatch.
- Alternativas de cómputo equivalentes: la misma imagen sirve para **ECS/Fargate** o
  una **EC2** (Ubuntu/Amazon Linux) o **SageMaker**; cambia solo cómo se invoca, no
  las dependencias de las capas 2–4.
