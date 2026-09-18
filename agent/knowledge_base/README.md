# Knowledge base del agente

Guardar aquí los documentos y resultados que un agente debe consultar para responder
con contexto técnico correcto sobre el **Índice de Caminabilidad**.

## Prioridad de consulta

1. `README.md` (raíz del repo)
2. `docs/referencia_proceso.md`
3. `agent/context/contexto_proyecto.md` y `agent/context/zonas_estudio.md`
4. Notebooks: `caminabilidad_roosevelt_v2.ipynb`, `caminabilidad_barrio_obrero_v2.ipynb`
5. Resultados exportados en `outputs/results/`

## Contenido recomendado

- Documentación del proceso y del pipeline de caminabilidad.
- Resúmenes de métricas por zona.
- Inventario de fuentes de datos y observaciones de calidad.
- Criterios de territorio espejo (para Roosevelt).

## Regla de consistencia

Si existe diferencia entre un resumen corto y la documentación completa
(`README.md` + `docs/referencia_proceso.md`), priorizar la documentación completa y
luego verificar el estado real de los notebooks y scripts.

## Estado de referencia actual

- `caminabilidad_roosevelt_v2.ipynb` es el notebook de referencia principal
  (corredor con buffer + territorios espejo Calle 5/7).
- `caminabilidad_barrio_obrero_v2.ipynb` replica esa estructura para un polígono único
  de barrio, sin territorio espejo, con censo arbóreo como indicador adicional.
- `ejemplo_04_itt_pulmon_oriente_2026_v2.ipynb` es un ejemplo externo de ITT; no forma
  parte del pipeline de caminabilidad.
