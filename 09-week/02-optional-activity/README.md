# Semana 9 · Limpieza de un dataset

**Estudiante:** Cristian Camilo Quiguanas Ossa
**Programa:** Ingeniería Mecatrónica · Corhuila
**Asignatura:** Ciencia de Datos · Periodo 2026-B · Unidad 2, Semana 9

---

## 1. Dataset

Sigo con el caso del **invernadero inteligente con ESP32** (semanas 6, 7 y 8). Como la guía permite "ensuciar" un dataset, creé `datos_sucios.csv` con **66 lecturas** de dos invernaderos (Tomates y Lechugas) y tres variables (temperatura, luz y humedad), con los problemas de calidad que suelen aparecer al recibir datos de sensores y de captura manual:

| Problema introducido | Ejemplo en el archivo |
|---|---|
| Valores nulos | `valor`, `unidad` e `invernadero` vacíos o con `N/A` |
| Valores centinela | `-999` (el sensor lo reporta cuando falla la lectura) |
| Duplicados | Filas repetidas, algunas idénticas y otras que solo difieren en mayúsculas o espacios |
| Tipos incorrectos | `valor` con coma decimal (`28,4`), que vuelve la columna texto |
| Formato de texto inconsistente | `Tomates`, `TOMATES`, ` tomates `; `Temperatura`, `temp`, `TEMPERATURA` |
| Fechas en dos formatos y una inválida | `2026-10-14 08:00:00`, `14/10/2026 08:00` y `sin fecha` |

## 2. Archivos de esta carpeta

| Archivo | Contenido |
|---|---|
| `datos_sucios.csv` | Dataset original con problemas de calidad |
| `limpieza.py` | Script de limpieza en pandas, con el reporte antes/después |
| `datos_limpios.csv` | Resultado de la limpieza (evidencia) |
| `README.md` | Este documento |

Para reproducir: `pip install pandas` y luego `python limpieza.py` desde esta carpeta.

---

## 3. Qué hace el script de limpieza

El orden de los pasos importa: primero se normaliza y se corrigen los tipos, y solo después se buscan duplicados y se tratan los faltantes.

| Paso | Problema | Qué hice | Código |
|---|---|---|---|
| 1 | Texto inconsistente | Quité espacios, unifiqué mayúsculas y convertí sinónimos (`temp` → `Temperatura`) | `str.strip()`, `str.title()`, `map()` |
| 2 | Tipos incorrectos | Cambié la coma decimal por punto y convertí `valor` a número; convertí `fecha_hora` a fecha en sus dos formatos | `to_numeric()`, `to_datetime()` |
| 3 | Valores centinela | Convertí `-999` en nulo, porque no es una medición real | `df.loc[... == -999] = NA` |
| 4 | Duplicados | Eliminé filas repetidas **después** de normalizar, así también caen las que solo diferían en el formato | `drop_duplicates()` |
| 5a | Sin invernadero o sin fecha válida | Eliminé la fila, porque no se puede ubicar la lectura en el tiempo ni en el espacio | `dropna(subset=...)` |
| 5b | Unidad faltante | La deduje de la variable (Temperatura → °C, Luz → lux, Humedad → %) | `fillna(map(...))` |
| 5c | Valor faltante | Imputé con la **mediana** de su invernadero y su variable, y marqué esas filas en la columna `valor_imputado` | `groupby().transform("median")` |

---

## 4. Evidencia antes / después

Salida real de `python limpieza.py`:

```
=== REPORTE ANTES / DESPUÉS ===
Métrica                                  Antes   Después
Filas                                       66        57
Nulos (total de celdas)                     12         0
Duplicados (filas exactas)                   4         0
Valores centinela (-999)                     2         0
Valores con coma decimal                     5         0
Formatos de invernadero distintos            6         2
Formatos de variable distintos              11         3
Fechas inválidas                             1         0

Valores imputados con la mediana: 9
```

| Métrica | Antes | Después |
|---|---|---|
| Filas | 66 | 57 |
| Nulos (total de celdas) | 12 | 0 |
| Duplicados | 4 | 0 |
| Valores centinela (-999) | 2 | 0 |
| Valores con coma decimal | 5 | 0 |
| Formas distintas de escribir el invernadero | 6 | 2 |
| Formas distintas de escribir la variable | 11 | 3 |
| Fechas inválidas | 1 | 0 |
| Tipo de `valor` | texto | número decimal |
| Tipo de `fecha_hora` | texto | fecha y hora |

**De dónde salen las 9 filas menos (66 → 57):**
- 6 duplicados eliminados: los 4 exactos que se ven en la tabla, más 2 que solo se detectaron después de normalizar el texto (por eso en "Antes" aparecen 4 y no 6).
- 2 filas sin invernadero.
- 1 fila con la fecha `sin fecha`.

**Qué pasó con los 12 nulos y los 2 centinelas:** 2 se fueron con las filas eliminadas, 3 nulos de `unidad` se completaron con el mapa de unidades, y los valores faltantes de `valor` (nulos, `N/A` y los `-999`) se imputaron con la mediana. En total hay 9 valores imputados, todos marcados con `valor_imputado = True`.

---

## 5. Dimensiones de calidad que mejoré

### 1) Completitud: ¿están todos los datos que necesito?

Antes había 12 celdas vacías y 2 valores `-999` que en realidad eran datos faltantes disfrazados, así que algunas lecturas no se podían usar tal cual. Después el dataset tiene **0 nulos**: completé la unidad a partir de la variable, imputé los valores con la mediana de su grupo y eliminé las 3 filas que no se podían ubicar. La imputación deja una marca (`valor_imputado`) para poder excluir o revisar esas filas en un análisis posterior.

**Limitación:** imputar con la mediana es una solución razonable para un ejercicio, pero no reemplaza una medición real. En un caso real, con muchos faltantes consecutivos, convendría interpolar por hora o revisar el sensor.

### 2) Consistencia: ¿el mismo dato se escribe siempre igual?

Antes el mismo invernadero aparecía de 6 formas (`Tomates`, `TOMATES`, ` tomates `, ...) y la misma variable de 11 formas. Un `GROUP BY` o un `groupby` habría tratado cada forma como un grupo distinto, y los promedios por invernadero habrían salido mal. Después quedan **2 invernaderos y 3 variables**, con un solo formato cada uno, las fechas en un único formato y `valor` como número. Esto además hizo visibles 2 duplicados que antes pasaban desapercibidos.

> Como complemento, la limpieza también mejoró la **unicidad** (de 4 a 0 filas repetidas) y la **validez** (se eliminaron el `-999` y la fecha `sin fecha`).
