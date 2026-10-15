"""Semana 7 · Consultas SQL y pandas
Ejecuta las 3 consultas SQL sobre datos.sql (SQLite en memoria) y reproduce
la consulta GROUP BY con pandas (groupby). Uso:  python analisis_pandas.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent

# --- Crear la base de datos en memoria a partir de datos.sql -----------------
con = sqlite3.connect(":memory:")
con.executescript((BASE / "datos.sql").read_text(encoding="utf-8"))

# --- Consultas SQL -----------------------------------------------------------
q1 = """
SELECT id_lectura, valor, fecha_hora
FROM lectura
WHERE id_sensor = 1 AND valor > 28
ORDER BY fecha_hora;
"""

q2 = """
SELECT i.nombre AS invernadero, l.fecha_hora, l.valor, t.unidad
FROM lectura l
JOIN sensor s      ON s.id_sensor = l.id_sensor
JOIN tipo_sensor t ON t.id_tipo_sensor = s.id_tipo_sensor
JOIN invernadero i ON i.id_invernadero = s.id_invernadero
WHERE t.nombre = 'Temperatura'
ORDER BY i.nombre, l.fecha_hora;
"""

q3 = """
SELECT i.nombre AS invernadero, t.nombre AS variable, t.unidad,
       COUNT(*) AS n_lecturas,
       ROUND(AVG(l.valor),2) AS promedio,
       MIN(l.valor) AS minimo,
       MAX(l.valor) AS maximo
FROM lectura l
JOIN sensor s      ON s.id_sensor = l.id_sensor
JOIN tipo_sensor t ON t.id_tipo_sensor = s.id_tipo_sensor
JOIN invernadero i ON i.id_invernadero = s.id_invernadero
GROUP BY i.nombre, t.nombre, t.unidad
ORDER BY i.nombre, t.nombre;
"""

print("=== Consulta 1 · WHERE ===")
print(pd.read_sql(q1, con).to_string(index=False))
print("\n=== Consulta 2 · JOIN ===")
print(pd.read_sql(q2, con).to_string(index=False))
res_sql = pd.read_sql(q3, con)
print("\n=== Consulta 3 · GROUP BY (SQL) ===")
print(res_sql.to_string(index=False))

# --- Equivalente en pandas (groupby) ----------------------------------------
lectura = pd.read_sql("SELECT * FROM lectura", con)
sensor = pd.read_sql("SELECT * FROM sensor", con)
tipo = pd.read_sql("SELECT * FROM tipo_sensor", con)
inv = pd.read_sql("SELECT * FROM invernadero", con)

df = (
    lectura
    .merge(sensor, on="id_sensor")
    .merge(tipo, on="id_tipo_sensor", suffixes=("", "_tipo"))
    .merge(inv, on="id_invernadero", suffixes=("", "_inv"))
    .rename(columns={"nombre_inv": "invernadero", "nombre": "variable"})
)

res_pd = (
    df.groupby(["invernadero", "variable", "unidad"])["valor"]
      .agg(n_lecturas="count", promedio="mean", minimo="min", maximo="max")
      .round({"promedio": 2})
      .reset_index()
      .sort_values(["invernadero", "variable"])
      .reset_index(drop=True)
)

print("\n=== Consulta 3 · GROUP BY (pandas) ===")
print(res_pd.to_string(index=False))

# --- Verificación: SQL y pandas deben dar lo mismo --------------------------
iguales = res_sql.astype(str).equals(res_pd.astype(str)) or \
    (res_sql.round(2).values.tolist() == res_pd.round(2).values.tolist())
print("\n¿SQL y pandas coinciden?", iguales)
