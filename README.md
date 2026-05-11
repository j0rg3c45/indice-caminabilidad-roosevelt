# 🚶 Índice de Caminabilidad — Av. Roosevelt, Cali

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![OSMnx](https://img.shields.io/badge/OSMnx-2.0-green)
![Status](https://img.shields.io/badge/Estado-Línea%20Base-orange)
![License](https://img.shields.io/badge/Licencia-ITT%20Cali-lightgrey)

**ITT Cali Inteligente · Equipo de Gobierno de Datos**

Proyecto de evaluación de impacto de la intervención urbana en Av. Roosevelt
(Cali, Colombia). Calcula métricas de caminabilidad usando la red peatonal de
OpenStreetMap como línea base pre-intervención.

---

## 📋 Descripción

Este repositorio contiene el pipeline de análisis para:

1. Calcular indicadores de caminabilidad (intersecciones, densidad de red,
   longitud de segmentos) usando OSMnx.
2. Establecer la **línea base** (mayo 2026) antes de la intervención física.
3. Definir criterios para seleccionar un **territorio espejo** (grupo control).
4. Permitir mediciones futuras comparables (2026–2028).

---

## 📁 Estructura del Proyecto

```
├── data/
│   ├── raw/                  # Datos originales sin modificar
│   ├── processed/            # Datos procesados listos para análisis
│   └── external/             # Parámetros y documentos de referencia
├── notebooks/                # Jupyter notebooks exploratorios (Colab)
├── notebooks_py/             # Scripts .py limpios y modulares
├── agent/                    # Pipeline automatizado / agente (futuro)
├── outputs/
│   ├── results/              # CSVs con métricas calculadas
│   └── figures/              # Mapas y gráficos generados
├── docs/                     # Documentación y diagramas
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Este archivo
```

---

## 🚀 Cómo Ejecutar

### Opción 1: Google Colab (recomendado para exploración)

1. Abrir `notebooks/caminabilidad_roosevelt_v2.ipynb` en Google Colab.
2. Subir el archivo GeoJSON del polígono cuando se solicite.
3. Ejecutar todas las celdas en orden.

### Opción 2: Script local

```bash
# Clonar el repositorio
git clone <url-del-repo>

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el análisis
python notebooks_py/caminabilidad_roosevelt.py \
    --geojson data/raw/Geojson_tramos_Roosevelt_Buffer_100.geojson \
    --nombre "Av. Roosevelt - Buffer 100m"
```

---

## 📊 Métricas Calculadas

| Indicador | Valor (Línea Base) | Fecha |
|-----------|-------------------|-------|
| Área del polígono | 42.9 ha | 2026-05-11 |
| Intersecciones peatonales | 232 | 2026-05-11 |
| Longitud red peatonal | 31.78 km | 2026-05-11 |
| Longitud promedio segmento | 41.7 m | 2026-05-11 |
| Densidad de calle | 74.07 km/km² | 2026-05-11 |

---

## 🔬 Territorio Espejo (Control)

Los criterios para seleccionar el corredor de control están documentados en
`data/external/parametros_territorio_espejo.txt`. Resumen:

- Corredor de 500–700 m, buffer 100 m, área 38–48 ha
- Uso mixto comercial-residencial
- Sin intervención planificada 2026–2028
- Densidad de intersecciones entre 400–700 int/km²

---

## 🛠️ Tecnologías

- **OSMnx** — Descarga y análisis de redes viales desde OpenStreetMap
- **GeoPandas** — Manejo de datos geoespaciales
- **Matplotlib** — Visualización de mapas
- **Pandas** — Procesamiento de datos tabulares

---

## 👥 Equipo

ITT Cali Inteligente — Equipo de Gobierno de Datos

---

## 📄 Licencia

Uso interno ITT · Cali Inteligente. Todos los derechos reservados.
