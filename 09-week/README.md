# Taller en clase · Calidad de datos: diagnosticar, limpiar y medir

**Ciencia de Datos · Ingeniería Mecatrónica · CORHUILA 2026-B · Semana 9**
**Autor:** Cristian Camilo Quiguanas

Cuaderno de Jupyter donde se diagnostica, limpia y mide la calidad de un registro de producción de una planta de empaques del Huila, para responder una pregunta de negocio con datos confiables.

> **Pregunta de la gerencia:** ¿Qué máquina y qué turno tienen la mayor tasa de defectos? ¿A cuál le hacemos mantenimiento primero?

## Contenido

| Archivo | Descripción |
|---|---|
| [`taller-clase-Cristian Camilo Quiguanas.ipynb`](./taller-clase-Cristian%20Camilo%20Quiguanas.ipynb) | Cuaderno con el código, los resultados y las respuestas del taller |
| `README.md` | Este documento |

El cuaderno crea por sí mismo el archivo `registro_produccion.csv` (los datos viajan comprimidos dentro del cuaderno), y al final genera `registro_produccion_limpio.csv`.

## El caso

La planta tiene **4 máquinas** en dos líneas de producción y trabaja **3 turnos**. Los supervisores digitan a mano la producción, los defectos y la temperatura de cada máquina al cierre del turno. El registro cubre **4 semanas** (del 7 de septiembre al 3 de octubre de 2026, de lunes a sábado).

| Columna | Significado | Tipo esperado |
|---|---|---|
| `fecha` | Día del registro (`aaaa-mm-dd`) | Fecha |
| `turno` | Mañana, Tarde o Noche | Texto |
| `maquina` | M-01 a M-04 | Texto |
| `producidas` | Unidades fabricadas en el turno | Entero |
| `defectuosas` | Unidades que no pasaron control de calidad | Entero |
| `temperatura` | Temperatura al cerrar el turno, en °C | Decimal |

Reglas del negocio usadas para validar: máximo 1.800 unidades por turno, defectuosas entre 0 y las producidas, y temperatura del sensor entre 15 y 60 °C.

## Qué se hizo

### 1. Diagnóstico de calidad (antes de limpiar)

Se midieron cinco dimensiones de calidad con una función reutilizable, `reporte_calidad()`.

| Dimensión | Pregunta | Antes (%) | Después (%) |
|---|---|---|---|
| Completitud | ¿Están todos los datos? | 94,6 | 100 |
| Unicidad | ¿Hay filas repetidas? | 97,0 | 100 |
| Consistencia | ¿Se escribe igual siempre? | 88,9 | 100 |
| Formato | ¿Las fechas siguen `aaaa-mm-dd`? | 89,9 | 100 |
| Validez | ¿Cumple las reglas del negocio? | 80,8 | 100 |

Problemas encontrados en los 297 registros originales: 9 duplicados, 16 "máquinas" y 12 "turnos" distintos (por mayúsculas, espacios y errores de escritura), 30 fechas en formato `dd/mm/aaaa`, 20 temperaturas con coma decimal, 14 temperaturas en °F, 10 valores faltantes en `defectuosas`, 6 en `temperatura` y 7 filas imposibles.

### 2. Limpieza paso a paso (con bitácora)

Se trabajó sobre una copia (`limpio`) para no tocar el original, y cada paso quedó anotado en una bitácora.

| Paso | Acción | Técnica en pandas | Filas |
|---|---|---|---|
| 1 | Quitar duplicados | `drop_duplicates()` | 297 → 288 |
| 2 | Homologar máquinas y turnos | `.str.strip()`, `.str.upper()`, `.str.capitalize()`, diccionario + `replace()` | 288 |
| 3 | Temperatura a número y fechas a un solo formato | `pd.to_numeric()`, `pd.to_datetime(format=...)` + `fillna()` | 288 |
| 4 | Convertir °F a °C: `(°F − 32) × 5/9` | `.loc[...]` | 288 |
| 5a | Eliminar filas sin `defectuosas` | `dropna(subset=[...])` | 288 → 278 |
| 5b | Imputar `temperatura` con la mediana de su máquina | `groupby().transform("median")` | 278 |
| 6 | Eliminar filas imposibles | Reglas con `>`, `<`, `\|` y filtro `~` | 278 → 271 |

Decisiones de criterio:

- Las `defectuosas` faltantes se **eliminaron** (no se imputaron), porque es la variable que se quiere medir y rellenarla sería inventar defectos.
- Las temperaturas imputadas quedaron marcadas en la columna `temp_imputada`.
- Los valores imposibles se eliminaron en lugar de "adivinar" su corrección.
- Los **atípicos de temperatura no se eliminaron** (regla del IQR): están dentro del rango del sensor, son reales y resultaron ser una pista clave.

Resultado final: **271 filas** y 8 columnas (las 6 originales más `temp_imputada` y `tasa_defectos`).

### 3. Análisis con datos confiables

**Tasa de defectos por máquina** (planta completa: **2,21 %**)

| Máquina | Producidas | Defectuosas | Tasa (%) |
|---|---|---|---|
| **M-03** | 81.008 | 3.475 | **4,29** |
| M-01 | 80.475 | 1.389 | 1,73 |
| M-02 | 81.031 | 1.302 | 1,61 |
| M-04 | 80.958 | 982 | 1,21 |

**Tasa de defectos por turno**

| Turno | Tasa (%) |
|---|---|
| Mañana | 2,05 |
| **Tarde** | **2,69** |
| Noche | 1,88 |

**Cruce máquina × turno (%)**

| Máquina | Mañana | Tarde | Noche |
|---|---|---|---|
| M-01 | 1,76 | 1,69 | 1,73 |
| M-02 | 1,65 | 1,51 | 1,66 |
| **M-03** | 3,47 | **6,45** | 2,97 |
| M-04 | 1,32 | 1,15 | 1,17 |

## Conclusiones

1. **M-03 es la máquina con más defectos:** 4,29 %, casi el doble de la tasa de la planta (2,21 %).
2. **El turno Tarde de la M-03 es el punto crítico:** llega a 6,45 %.
3. **Las 13 temperaturas atípicas pertenecen a M-03** (12 de ellas en el turno Tarde), y la correlación entre temperatura y tasa de defectos en esa máquina es **0,81** (en M-01 es −0,05). Esto indica dónde investigar, pero **correlación no es causalidad**.

**Recomendación:** hacerle mantenimiento primero a la **M-03**, revisando especialmente su sistema de temperatura y las condiciones del turno Tarde.

**Por qué importa limpiar:** con los datos sucios, la máquina con mayor tasa parecía ser la M-01 (5,93 %); con los datos limpios, la M-03 (4,29 %). Los errores de digitación y las categorías inconsistentes habrían llevado a mandar a mantenimiento la máquina equivocada.

**Propuesta para mejorar el registro desde el origen:** formulario con listas desplegables para máquina y turno, campos obligatorios, controles automáticos de rango (producidas ≤ 1.800, defectuosas entre 0 y las producidas), fecha en un único formato, temperatura siempre en °C y revisión de duplicados antes de consolidar.

## Cómo ejecutarlo

1. Abre el cuaderno en **Google Colab** o **VS Code** (con Python 3).
2. Ejecuta todas las celdas en orden (*Ejecutar todo* / *Run All*). La primera celda instala `pandas` y `matplotlib` si faltan.
3. Se generan `registro_produccion.csv` (original) y `registro_produccion_limpio.csv` (tabla limpia).

**Librerías:** `pandas` 2.2.3 y `matplotlib`.
