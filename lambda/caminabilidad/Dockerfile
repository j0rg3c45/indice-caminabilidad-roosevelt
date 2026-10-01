# ==============================================================================
# Imagen de contenedor para el Lambda de Caminabilidad (CaliTrack)
# ------------------------------------------------------------------------------
# Se usa imagen de contenedor (no ZIP) porque geopandas + osmnx + shapely traen
# binarios nativos (GDAL/GEOS/PROJ) que superan el límite de 250 MB del ZIP.
# Base oficial de AWS Lambda para Python 3.12.
# ==============================================================================
FROM public.ecr.aws/lambda/python:3.12

# Dependencias del sistema útiles para compilar/instalar wheels geoespaciales.
# La mayoría de paquetes traen wheels manylinux, pero gcc/g++ ayudan como respaldo.
RUN microdnf install -y gcc gcc-c++ make && microdnf clean all

# Instalar dependencias de Python
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Código del handler
COPY lambda_function.py ${LAMBDA_TASK_ROOT}/

# OSMnx y matplotlib escriben cache/config: apuntar a /tmp (único writable en Lambda)
ENV OSMNX_CACHE_FOLDER=/tmp/osmnx_cache \
    MPLCONFIGDIR=/tmp/matplotlib \
    HOME=/tmp

# Handler: archivo.funcion
CMD ["lambda_function.lambda_handler"]
