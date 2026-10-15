# Semana 7 · Consultas SQL y pandas

**Estudiante:** Cristian Camilo Quiguanas Ossa
**Programa:** Ingeniería Mecatrónica · Corhuila
**Asignatura:** Ciencia de Datos · Periodo 2026-B · Unidad 2, Semana 7

---

## Dataset

Uso el modelo del **invernadero inteligente con ESP32** que diseñé en la Semana 6 (subconjunto del ERD): cuatro tablas con 2 invernaderos, 3 tipos de sensor, 6 sensores y 24 lecturas (4 por sensor, a las 06:00, 12:00, 16:00 y 20:00).

```
invernadero (id_invernadero PK, nombre, ubicacion)
tipo_sensor (id_tipo_sensor PK, nombre, unidad)
sensor      (id_sensor PK, modelo, id_invernadero FK, id_tipo_sensor FK)
lectura     (id_lectura PK, valor, fecha_hora, id_sensor FK)
```

## Archivos de esta carpeta

| Archivo | Contenido |
|---|---|
| `datos.sql` | Creación de las tablas y los datos de ejemplo |
| `consultas.sql` | Las 3 consultas SQL |
| `analisis_pandas.py` | Ejecuta las consultas y reproduce el `GROUP BY` con pandas |

Para reproducir todo: `python analisis_pandas.py` (requiere `pandas`; `sqlite3` ya viene con Python).

---

## Consulta 1 · WHERE

```sql
SELECT id_lectura, valor, fecha_hora
FROM lectura
WHERE id_sensor = 1
  AND valor > 28
ORDER BY fecha_hora;
```

**Resultado:**

| id_lectura | valor | fecha_hora |
|---|---|---|
| 2 | 31.8 | 2026-10-14 12:00:00 |
| 3 | 29.4 | 2026-10-14 16:00:00 |

**Qué responde:** ¿en qué momentos el sensor de temperatura del Invernadero Tomates (sensor 1) midió más de 28 °C? Sirve para detectar las horas de calor excesivo, por ejemplo para activar un ventilador. El `WHERE` filtra por sensor y por umbral antes de devolver las filas.

---

## Consulta 2 · JOIN

```sql
SELECT i.nombre AS invernadero,
       l.fecha_hora,
       l.valor,
       t.unidad
FROM lectura l
JOIN sensor s       ON s.id_sensor = l.id_sensor
JOIN tipo_sensor t  ON t.id_tipo_sensor = s.id_tipo_sensor
JOIN invernadero i  ON i.id_invernadero = s.id_invernadero
WHERE t.nombre = 'Temperatura'
ORDER BY i.nombre, l.fecha_hora;
```

**Resultado:**

| invernadero | fecha_hora | valor | unidad |
|---|---|---|---|
| Invernadero Lechugas | 2026-10-14 06:00:00 | 21.0 | °C |
| Invernadero Lechugas | 2026-10-14 12:00:00 | 28.6 | °C |
| Invernadero Lechugas | 2026-10-14 16:00:00 | 27.2 | °C |
| Invernadero Lechugas | 2026-10-14 20:00:00 | 23.0 | °C |
| Invernadero Tomates | 2026-10-14 06:00:00 | 22.5 | °C |
| Invernadero Tomates | 2026-10-14 12:00:00 | 31.8 | °C |
| Invernadero Tomates | 2026-10-14 16:00:00 | 29.4 | °C |
| Invernadero Tomates | 2026-10-14 20:00:00 | 24.1 | °C |

**Qué responde:** ¿cuáles son las lecturas de temperatura de cada invernadero, con su nombre y unidad en lugar de ids numéricos? La tabla `lectura` solo guarda `id_sensor`; con los `JOIN` se llega al sensor, a su tipo (de donde sale la unidad) y al invernadero (de donde sale el nombre). Esto es posible gracias a la normalización: cada dato vive en una sola tabla y se reconstruye al consultar.

---

## Consulta 3 · GROUP BY

```sql
SELECT i.nombre  AS invernadero,
       t.nombre  AS variable,
       t.unidad,
       COUNT(*)              AS n_lecturas,
       ROUND(AVG(l.valor),2) AS promedio,
       MIN(l.valor)          AS minimo,
       MAX(l.valor)          AS maximo
FROM lectura l
JOIN sensor s       ON s.id_sensor = l.id_sensor
JOIN tipo_sensor t  ON t.id_tipo_sensor = s.id_tipo_sensor
JOIN invernadero i  ON i.id_invernadero = s.id_invernadero
GROUP BY i.nombre, t.nombre, t.unidad
ORDER BY i.nombre, t.nombre;
```

**Resultado:**

| invernadero | variable | unidad | n_lecturas | promedio | minimo | maximo |
|---|---|---|---|---|---|---|
| Invernadero Lechugas | Humedad | % | 4 | 70.75 | 62.0 | 80.0 |
| Invernadero Lechugas | Luz | lux | 4 | 357.50 | 30.0 | 780.0 |
| Invernadero Lechugas | Temperatura | °C | 4 | 24.95 | 21.0 | 28.6 |
| Invernadero Tomates | Humedad | % | 4 | 66.25 | 55.0 | 78.0 |
| Invernadero Tomates | Luz | lux | 4 | 402.50 | 40.0 | 850.0 |
| Invernadero Tomates | Temperatura | °C | 4 | 26.95 | 22.5 | 31.8 |

**Qué responde:** ¿cuál es el comportamiento de cada variable (temperatura, luz, humedad) en cada invernadero? Agrupa las lecturas por invernadero y variable, y calcula cuántas hay, el promedio, el mínimo y el máximo. Por ejemplo, el Invernadero Tomates es más caliente (promedio 26.95 °C, máximo 31.8 °C) y recibe más luz que el de Lechugas (24.95 °C).

---

## Equivalente en pandas (groupby)

Se reproduce la **Consulta 3**. Los `JOIN` de SQL se convierten en `merge` y el `GROUP BY` con funciones de agregación en `groupby` + `agg`.

```python
import sqlite3
import pandas as pd

con = sqlite3.connect(":memory:")
con.executescript(open("datos.sql", encoding="utf-8").read())

lectura = pd.read_sql("SELECT * FROM lectura", con)
sensor  = pd.read_sql("SELECT * FROM sensor", con)
tipo    = pd.read_sql("SELECT * FROM tipo_sensor", con)
inv     = pd.read_sql("SELECT * FROM invernadero", con)

# JOIN: unir las 4 tablas
df = (
    lectura
    .merge(sensor, on="id_sensor")
    .merge(tipo, on="id_tipo_sensor", suffixes=("", "_tipo"))
    .merge(inv, on="id_invernadero", suffixes=("", "_inv"))
    .rename(columns={"nombre_inv": "invernadero", "nombre": "variable"})
)

# GROUP BY: agrupar y agregar
res_pd = (
    df.groupby(["invernadero", "variable", "unidad"])["valor"]
      .agg(n_lecturas="count", promedio="mean", minimo="min", maximo="max")
      .round({"promedio": 2})
      .reset_index()
      .sort_values(["invernadero", "variable"])
      .reset_index(drop=True)
)
print(res_pd)
```

**Resultado en pandas** (idéntico al de SQL):

| invernadero | variable | unidad | n_lecturas | promedio | minimo | maximo |
|---|---|---|---|---|---|---|
| Invernadero Lechugas | Humedad | % | 4 | 70.75 | 62.0 | 80.0 |
| Invernadero Lechugas | Luz | lux | 4 | 357.50 | 30.0 | 780.0 |
| Invernadero Lechugas | Temperatura | °C | 4 | 24.95 | 21.0 | 28.6 |
| Invernadero Tomates | Humedad | % | 4 | 66.25 | 55.0 | 78.0 |
| Invernadero Tomates | Luz | lux | 4 | 402.50 | 40.0 | 850.0 |
| Invernadero Tomates | Temperatura | °C | 4 | 26.95 | 22.5 | 31.8 |

**Equivalencias SQL → pandas**

| SQL | pandas |
|---|---|
| `JOIN ... ON` | `.merge(..., on=...)` |
| `GROUP BY a, b, c` | `.groupby(["a", "b", "c"])` |
| `COUNT(*)`, `AVG()`, `MIN()`, `MAX()` | `.agg(count, mean, min, max)` |
| `ROUND(x, 2)` | `.round(2)` |
| `ORDER BY` | `.sort_values()` |

El script `analisis_pandas.py` compara ambos resultados y confirma que coinciden.
