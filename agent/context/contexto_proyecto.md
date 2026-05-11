# Contexto para agente - Proyecto ITT

Este agente apoya consulta, interpretacion y explicacion del **Indice de Transformacion Territorial (ITT)** dentro del repositorio `itt-transformacion-territorial`.

## Objetivo del proyecto

Calcular el ITT para zonas de intervencion urbana en Cali y comparar resultados entre zonas.

## Zonas del repo

- ITT Roosevelt.
- Avenida Ciudad de Cali.
- Barrio Obrero.

## Estado actual

- `01_itt_roosevelt.ipynb`: implementado con estructura homologada a Barrio Obrero y `ref_min/ref_max` fijos.
- `02_itt_avenida_ciudad_de_cali.ipynb`: implementado, pero aun usa min-max relativo en la normalizacion de indicadores reales.
- `03_itt_barrio_obrero.ipynb`: implementado y alineado con `ref_min/ref_max` fijos.
- `04_itt_pulmon_oriente_2026.ipynb`: salida parcial de seguimiento.
- `05_comparativo_itt_zonas.ipynb`: plantilla comparativa.

## Regla metodologica para agentes

La referencia metodologica vigente del proyecto esta en:

- `agent/knowledge_base/Guia_ITT_Metodologia_Notebook.md`

Los agentes deben asumir como correcto:

- Uso de `ref_min/ref_max` fijos.
- Referentes provisionales para dimensiones sin datos propios.
- Necesidad de escalar refs segun tamano de zona.

Los agentes no deben asumir como vigente:

- Min-max relativo como metodo recomendado general.

## Uso esperado por el agente

El agente debe diferenciar entre:

- Metodologia vigente.
- Implementacion ya migrada.
- Implementacion pendiente de migrar.
- Datos presentes en el repo.
- Datos esperados pero no versionados.

## Seguimiento reciente

- Roosevelt ya dispone de datos fuente en `data/itt_roosevelt/`.
- Se revisaron errores de consistencia por `ano` y `año`; la convencion vigente en Roosevelt es `año`.
- Se agregaron Excel de vivienda en `data/referencia/` para evaluar si `Entorno Urbano` puede dejar de depender de un referente fijo.
- `03_itt_barrio_obrero.ipynb` ya usa experimentalmente `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx` para recalcular `Entorno Urbano` con `Comuna 9` como proxy territorial.
- Ese insumo de `Entorno Urbano` es un corte anual `2024`; la visualizacion reciente recomendada es un `heatmap` de componentes del deficit cualitativo.
- Para Pulmon de Oriente 2026, se implemento deduplicacion por fecha+coordenada y generacion de valores Proxy para Q2, Q3 y Q4 basados en promedio historico trimestral 2023-2025.
- Los valores Proxy se marcan con doble asterisco (`**`) en todas las salidas.
- Referencia metodologica completa: `docs/05_nota_metodologica_proxy_2026.md`.
