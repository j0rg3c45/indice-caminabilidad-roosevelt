# Contexto Maestro para Agente

Este archivo resume el contexto mas importante del repo para que otro agente pueda trabajar con buen criterio metodologico y operativo desde el inicio.

## 1. Objetivo del proyecto

El repositorio calcula el **Indice de Transformacion Territorial (ITT)** para zonas de intervencion urbana de Cali, Colombia.

El ITT busca medir transformacion positiva del territorio en escala `0-100` y permitir comparaciones entre zonas usando una metodologia comun.

## 2. Regla metodologica principal

La metodologia vigente del proyecto exige:

- Usar `ref_min/ref_max` fijos por indicador.
- No usar min-max relativo calculado desde la propia muestra de la zona cuando el territorio es pequeno o los conteos son bajos.
- Diferenciar entre datos reales, referentes provisionales y resultados efectivamente calculados.

La fuente metodologica principal y prioritaria es:

- `agent/knowledge_base/Guia_ITT_Metodologia_Notebook.md`

Si hay contradiccion entre un resumen corto en `docs/` y la guia metodologica completa, debe priorizarse la guia metodologica completa y luego el estado real de los notebooks.

## 3. Dimensiones y pesos oficiales

El ITT vigente usa 5 dimensiones:

- Seguridad: `0.30`
- Movilidad: `0.25`
- Entorno Urbano: `0.20`
- Educacion y Desarrollo: `0.13`
- Cohesion Social: `0.12`

La suma de los pesos debe ser `1.0`.

## 4. Referentes provisionales actuales

Mientras una zona no tenga datos propios para ciertas dimensiones o indicadores, el proyecto usa referentes de `Pulmon de Oriente`.

Valores vigentes:

- `Entorno Urbano = 39.2`
- `Educacion y Desarrollo = 54.9`
- `Vulnerabilidad = 54.1`

Estos valores deben tratarse como **provisionales**, no como mediciones propias de la zona analizada.

Excepcion actual importante:

- En `notebooks/03_itt_barrio_obrero.ipynb`, `Entorno Urbano` ya puede dejar de usar `39.2` si se ejecuta la celda proxy basada en `deficit habitacional 2024`.

## 5. Estado real de notebooks

### Notebook de referencia principal

- `notebooks/03_itt_barrio_obrero.ipynb`

Este notebook es la referencia operativa mas importante del repo porque:

- Ya usa `ref_min/ref_max` fijos.
- Tiene la estructura metodologica vigente.
- Es el mejor punto de partida para revisar logica de calculo, normalizacion, pesos, series anuales y trimestrales, y exportacion.
- Ademas, ya documenta un caso real de reemplazo parcial del referente fijo de `Entorno Urbano` mediante un proxy territorial.

### Detalle actual de Entorno Urbano en Barrio Obrero

- La celda `3B` recalcula `REF_ENTORNO_U` con `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx`.
- La base territorial usada es `Comuna 9`, como aproximacion a `Barrio Obrero`.
- El proxy combina dos componentes:
  - `Deficit Cualitativo`
  - `Deficit Cualitativo / Deficit Habitacional`
- Ambos componentes se normalizan con referencias fijas y luego se promedian.
- La celda `3C` agrega una visualizacion `heatmap` de componentes del deficit cualitativo 2024.
- Ese insumo no tiene periodicidad mensual ni trimestral observada; es un corte anual `2024`.
- `Predios titulados` y `subsidios de mejoramiento` fueron revisados, pero no hacen parte del calculo actual de esta dimension.

### Roosevelt

- `notebooks/01_itt_roosevelt.ipynb`

Estado:

- Implementado.
- Ya migrado a `ref_min/ref_max` fijos.
- Replica la estructura de Barrio Obrero, adaptada a corredor con buffer.
- Usa referentes provisionales para `Entorno Urbano`, `Educacion y Desarrollo` y `Vulnerabilidad`.

### Avenida Ciudad de Cali

- `notebooks/02_itt_avenida_ciudad_de_cali.ipynb`

Estado:

- Implementado y funcional.
- Analiza 8 tramos buffer de 100 m sobre corredor vial.
- Requiere `spatial join` de eventos a tramos.
- Sigue usando min-max relativo para normalizar indicadores reales.

Conclusion importante:

- Es la principal deuda metodologica del repo.
- No debe asumirse como notebook plenamente homologado al metodo vigente.

### Pulmon de Oriente 2026

- `notebooks/04_itt_pulmon_oriente_2026_v2.ipynb`

Estado:

- No es el notebook comparativo del proyecto.
- Es una salida completa para Seguridad y Cohesion Social 2023-2026.
- 2026 solo tiene datos reales de T1; Q2, Q3 y Q4 se estiman con valores Proxy (promedio historico trimestral 2023-2025).
- Los valores Proxy se marcan con doble asterisco (`**`).
- Incluye deduplicacion automatica por fecha+coordenada.

Rol en el proyecto:

- Sirve como referencia de seguimiento con serie temporal completa (real + Proxy).
- Pulmon de Oriente tambien es la base de los referentes provisionales usados por otras zonas.

### Comparativo entre zonas

- `notebooks/05_comparativo_itt_zonas.ipynb`

Estado:

- Es la plantilla comparativa real que existe hoy en disco.
- Depende de resultados exportados por zona.
- Todavia no representa un flujo consolidado totalmente maduro.

## 6. Zonas del repo y como pensarlas

### Barrio Obrero

- Unidad de analisis: poligono unico.
- No requiere `spatial join` por tramo.
- Caso mas limpio para entender la metodologia vigente.
- Caso actual mas importante para entender el uso experimental de `deficit habitacional` dentro de `Entorno Urbano`.

### Roosevelt

- Unidad de analisis: corredor con buffer de 100 m.
- Periodo trabajado: `2023-2025`.
- Caso homologado a la metodologia vigente pero en contexto de corredor.

### Avenida Ciudad de Cali

- Unidad de analisis: 8 tramos.
- Metodo espacial: `spatial join`.
- Caso mas complejo espacialmente.
- Todavia no esta homologado en normalizacion.

### Pulmon de Oriente

- Funciona como referencia metodologica.
- Aporta los scores provisionales usados en otras zonas.
- Tiene notebook propio parcial 2026, pero no equivale al flujo principal de comparacion entre zonas.

## 7. Disponibilidad real de datos

### Datos presentes en el repo

Hay ZIP versionados para:

- `data/itt_roosevelt/`
- `data/itt_barrio_obrero/`
- `data/itt_pulmon_oriente/`

Estos ZIP contienen insumos reales para trabajo territorial y validan que Roosevelt, Barrio Obrero y Pulmon de Oriente si tienen base de datos local dentro del repo.

### Datos no versionados en el repo

- `data/itt_avenida_ciudad_de_cali/` tiene estructura y README, pero no trae los insumos fuente versionados.

Implicacion:

- Su ejecucion depende de carga externa, Colab o entrega manual de archivos.

## 8. Referencias territoriales y su estado actual

La carpeta `data/referencia/` contiene Excel de apoyo metodologico:

- `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx`
- `BD_PREDIOS_TITULADOS 2023-2025 (1).xlsx`
- `BD_SUBSIDIOS_MEJORAMIENTO_VIV_AÑOS_2024_2025 (1).xlsx`

Lectura correcta:

- No todos hacen parte del calculo actual del ITT.
- Se consideran insumos potenciales para fortalecer `Entorno Urbano` u otras lecturas territoriales futuras.
- El candidato mas fuerte documentado hoy para `Entorno Urbano` es el deficit habitacional.
- Ese candidato ya fue incorporado de forma experimental en `03_itt_barrio_obrero.ipynb`.
- `Predios titulados` y `subsidios de mejoramiento` siguen fuera del calculo actual de la dimension.

## 9. Donde vive el conocimiento

Para responder bien sobre este repo, un agente debe leer en este orden:

1. `agent/knowledge_base/Guia_ITT_Metodologia_Notebook.md`
2. `agent/context/contexto_proyecto.md`
3. `agent/context/zonas_estudio.md`
4. `docs/03_fuentes_datos.md`
5. `notebooks/03_itt_barrio_obrero.ipynb`
6. `notebooks/01_itt_roosevelt.ipynb`
7. `notebooks/02_itt_avenida_ciudad_de_cali.ipynb`

## 10. Precauciones para otro agente

- No asumir que todo notebook implementado ya esta metodologicamente homologado.
- No confundir `04_itt_pulmon_oriente_2026.ipynb` con el comparativo entre zonas.
- No asumir que `outputs/` ya contiene resultados versionados listos para consolidacion.
- Tratar con cuidado textos con problemas de codificacion como `año`, `T1`, o caracteres especiales en algunos `.md` y notebooks.
- Distinguir siempre entre:
  - dato observado real
  - score normalizado
  - referente provisional
  - valor Proxy estimado (marcado con `**`)
  - resultado exportado
- No presentar el proxy de `Entorno Urbano` de Barrio Obrero como serie mensual o trimestral observada.
- Los valores Proxy de 2026 Q2-Q4 deben identificarse siempre con doble asterisco (`**`) y no deben presentarse como datos reales observados.
- Cuando se reemplacen valores Proxy por datos reales, actualizar simultaneamente todos los `.md` del proyecto.

## 11. Resumen ejecutivo para handoff rapido

Este repo ya tiene una metodologia definida y parcialmente consolidada. `Barrio Obrero` es la referencia operativa vigente. `Roosevelt` ya esta alineado con esa metodologia. `Avenida Ciudad de Cali` sigue funcional, pero pendiente de migrar desde min-max relativo hacia `ref_min/ref_max` fijos. `Pulmon de Oriente` es la referencia metodologica de fondo y la fuente de los scores provisionales usados en otras zonas. Los datos versionados existen para Roosevelt, Barrio Obrero y Pulmon de Oriente, pero no para Avenida Ciudad de Cali. En Barrio Obrero, `Entorno Urbano` ya puede recalcularse con un proxy experimental de `deficit habitacional 2024` para `Comuna 9`, explicado con un `heatmap` de componentes del deficit cualitativo 2024.

## 12. Prompt sugerido para otro agente

Puedes iniciar a otro agente con este texto:

> Este repo calcula el ITT de zonas urbanas de Cali. La metodologia vigente exige `ref_min/ref_max` fijos por indicador y esta documentada en `agent/knowledge_base/Guia_ITT_Metodologia_Notebook.md`. `notebooks/03_itt_barrio_obrero.ipynb` es la referencia operativa principal; `notebooks/01_itt_roosevelt.ipynb` ya esta alineado a esa logica; `notebooks/02_itt_avenida_ciudad_de_cali.ipynb` sigue funcional pero aun usa min-max relativo y debe tratarse como implementacion pendiente de homologacion. Los referentes provisionales actuales provenientes de Pulmon de Oriente son `Entorno Urbano = 39.2`, `Educacion y Desarrollo = 54.9` y `Vulnerabilidad = 54.1`, pero en Barrio Obrero `Entorno Urbano` ya puede sobrescribirse con un proxy experimental de `deficit habitacional 2024` para `Comuna 9`. Ese proxy no tiene periodicidad mensual o trimestral observada; su visualizacion adecuada hoy es el `heatmap` de componentes del deficit cualitativo 2024. Distingue siempre entre datos reales, scores provisionales y metodologia vigente. No inventes outputs no versionados ni asumas que el comparativo ya esta completo.
