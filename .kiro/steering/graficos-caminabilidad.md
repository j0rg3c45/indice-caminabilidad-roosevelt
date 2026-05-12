---
inclusion: manual
---

# Prompt técnico — Generación de gráficos base para evaluación de caminabilidad en Av. Roosevelt

Actúa como un científico de datos especializado en análisis urbano, redes peatonales y evaluación de caminabilidad usando Python, OSMnx, GeoPandas, NetworkX y visualización geoespacial.

## Objetivo

Generar únicamente los gráficos base del corredor de Avenida Roosevelt, antes de seleccionar el territorio espejo. Estos gráficos deben servir como línea base metodológica para futuras comparaciones urbanas y análisis Difference-in-Differences.

El análisis debe utilizar:
- OpenStreetMap
- OSMnx
- `network_type='walk'`
- Buffer de 100 metros alrededor del corredor
- Red peatonal recortada al polígono de estudio

Los gráficos deben ser reproducibles en Jupyter Notebook o Google Colab.

---

## Gráficos obligatorios a generar

### 1. Mapa de red peatonal

Generar un mapa de la red peatonal walkable de Roosevelt mostrando:
- nodos
- edges
- conectividad urbana

**Objetivo:** Visualizar la estructura peatonal y la continuidad urbana del corredor.

**Requerimientos:**
- Fondo claro
- Alta resolución
- Etiqueta de título
- Escala gráfica
- Exportar en PNG

---

### 2. Heatmap de densidad de intersecciones

Calcular y visualizar la concentración espacial de intersecciones peatonales usando:
- Kernel Density
- o Hexbin spatial aggregation

**Objetivo:** Identificar zonas de mayor conectividad peatonal.

**Interpretación esperada:**
- zonas calientes = mayor caminabilidad
- zonas frías = baja conectividad

---

### 3. Histograma de longitud de segmentos

Construir un histograma usando la longitud de todos los segmentos peatonales.

**Variables:** longitud de edges en metros

**Objetivo:** Evaluar granularidad urbana y tamaño promedio de manzana.

**Interpretación:**
- segmentos cortos = mejor caminabilidad
- segmentos largos = menor permeabilidad urbana

---

### 4. Boxplot de segmentos peatonales

Generar boxplot para:
- longitud de segmentos
- distribución de calles

**Objetivo:** Detectar dispersión, heterogeneidad y outliers urbanos.

---

### 5. Scatter plot de conectividad

Construir gráfico de dispersión con:
- Eje X: longitud promedio de segmento
- Eje Y: densidad de intersecciones

**Objetivo:** Establecer posición morfológica inicial de Roosevelt para futuras comparaciones con el territorio espejo.

---

### 6. Tabla resumen de métricas urbanas

Generar tabla consolidada con:
- área total
- número de intersecciones
- longitud total de red
- longitud promedio de segmento
- densidad de calle
- densidad de intersecciones

**Exportar:** CSV, DataFrame, PNG opcional

---

## Requerimientos técnicos

Usar exclusivamente:
- Python
- OSMnx
- GeoPandas
- Matplotlib
- NetworkX
- Contextily (opcional)

Evitar:
- gráficos innecesarios
- dashboards complejos
- análisis temporal aún
- comparaciones con otras zonas por ahora

---

## Objetivo metodológico

Estos gráficos constituyen la línea base oficial del corredor Roosevelt para:
- evaluación de impacto urbano
- comparación futura con territorio espejo
- análisis longitudinal 2026–2028
- validación de caminabilidad
- análisis cuasi experimental

La prioridad actual es construir una caracterización espacial y topológica robusta del corredor Roosevelt antes de seleccionar el área espejo.

---

## Resultado esperado

El sistema debe generar:
1. Gráficos en alta resolución
2. Métricas reproducibles
3. Outputs exportables
4. Notebook documentado
5. Estructura lista para futura comparación espejo vs Roosevelt
