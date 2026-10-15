"""Semana 10 · Mini-proyecto de datos (cierre del Corte 2)
Flujo completo:  EXTRAER (CSV) -> LIMPIAR (pandas) -> CARGAR (SQLite, según el ERD)
                 -> ANALIZAR (2 consultas: filtro + agregación)

Uso:
    python pipeline.py                       # base de datos en memoria
    python pipeline.py --db invernadero.db   # además guarda la base en un archivo
"""
import argparse
import sqlite3
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
ENTRADA = BASE / "datos_crudos.csv"
ESQUEMA = BASE / "schema.sql"
SALIDA = BASE / "datos_limpios.csv"

CENTINELA = -999
MAPA_VARIABLE = {"temp": "Temperatura", "temperatura": "Temperatura",
                 "luz": "Luz", "humedad": "Humedad"}
MAPA_UNIDAD = {"Temperatura": "°C", "Luz": "lux", "Humedad": "%"}
RANGOS = {"Temperatura": (-10, 60), "Luz": (0, 100000), "Humedad": (0, 100)}


# ----------------------------------------------------------------- 1. EXTRAER
def extraer() -> pd.DataFrame:
    return pd.read_csv(ENTRADA)


# ------------------------------------------------------------------ 2. LIMPIAR
def parsear_fecha(serie: pd.Series) -> pd.Series:
    iso = pd.to_datetime(serie, format="%Y-%m-%d %H:%M:%S", errors="coerce")
    latino = pd.to_datetime(serie, format="%d/%m/%Y %H:%M", errors="coerce")
    return iso.fillna(latino)


def perfilar(df: pd.DataFrame) -> dict:
    return {"Filas": len(df),
            "Nulos (celdas)": int(df.isna().sum().sum()),
            "Duplicados (exactos)": int(df.duplicated().sum())}


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Texto: espacios, mayúsculas y sinónimos
    df["invernadero"] = df["invernadero"].str.strip().str.title()
    df["variable"] = df["variable"].str.strip().str.lower().map(MAPA_VARIABLE)
    df["sensor"] = df["sensor"].str.strip().str.upper()
    # Tipos: coma decimal -> número; fechas en dos formatos
    df["valor"] = pd.to_numeric(
        df["valor"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    df["fecha_hora"] = parsear_fecha(df["fecha_hora"])
    # Validez: centinela y valores fuera de rango físico -> nulo
    df.loc[df["valor"] == CENTINELA, "valor"] = float("nan")
    for variable, (minimo, maximo) in RANGOS.items():
        fuera = (df["variable"] == variable) & ((df["valor"] < minimo) | (df["valor"] > maximo))
        df.loc[fuera, "valor"] = float("nan")
    # Unicidad (después de normalizar)
    df = df.drop_duplicates().reset_index(drop=True)
    # Completitud
    df = df.dropna(subset=["invernadero", "fecha_hora"]).copy()
    df["unidad"] = df["unidad"].fillna(df["variable"].map(MAPA_UNIDAD))
    df["valor_imputado"] = df["valor"].isna()
    mediana = df.groupby(["invernadero", "variable"])["valor"].transform("median")
    df["valor"] = df["valor"].fillna(mediana).round(1)
    return df.sort_values("id_lectura").reset_index(drop=True)


# ------------------------------------------------------------------ 3. CARGAR
def cargar(df: pd.DataFrame, ruta_db: str = ":memory:") -> sqlite3.Connection:
    """Reparte el CSV plano en las 4 tablas del modelo (normalización)."""
    con = sqlite3.connect(ruta_db)
    con.executescript(ESQUEMA.read_text(encoding="utf-8"))

    invernaderos = sorted(df["invernadero"].unique())
    id_inv = {n: i for i, n in enumerate(invernaderos, start=1)}
    tipos = df[["variable", "unidad"]].drop_duplicates().sort_values("variable")
    id_tipo = {v: i for i, v in enumerate(tipos["variable"], start=1)}
    sensores = df[["invernadero", "variable", "sensor"]].drop_duplicates() \
                 .sort_values(["invernadero", "variable"]).reset_index(drop=True)
    id_sen = {(r.invernadero, r.variable): i for i, r in enumerate(sensores.itertuples(), start=1)}

    con.executemany("INSERT INTO invernadero VALUES (?, ?)",
                    [(id_inv[n], n) for n in invernaderos])
    con.executemany("INSERT INTO tipo_sensor VALUES (?, ?, ?)",
                    [(id_tipo[r.variable], r.variable, r.unidad) for r in tipos.itertuples()])
    con.executemany("INSERT INTO sensor VALUES (?, ?, ?, ?)",
                    [(id_sen[(r.invernadero, r.variable)], r.sensor,
                      id_inv[r.invernadero], id_tipo[r.variable]) for r in sensores.itertuples()])
    con.executemany(
        "INSERT INTO lectura VALUES (?, ?, ?, ?, ?)",
        [(int(r.id_lectura), float(r.valor), r.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
          int(r.valor_imputado), id_sen[(r.invernadero, r.variable)])
         for r in df.itertuples()])
    con.commit()
    return con


# ---------------------------------------------------------------- 4. ANALIZAR
# Pregunta 1 (SQL): ¿cuántas lecturas de temperatura superaron 30 °C, por invernadero y día?
CONSULTA_1 = """
SELECT i.nombre              AS invernadero,
       date(l.fecha_hora)    AS dia,
       COUNT(*)              AS lecturas_sobre_30,
       ROUND(MAX(l.valor),1) AS maxima_c
FROM lectura l
JOIN sensor s      ON s.id_sensor = l.id_sensor
JOIN tipo_sensor t ON t.id_tipo_sensor = s.id_tipo_sensor
JOIN invernadero i ON i.id_invernadero = s.id_invernadero
WHERE t.nombre = 'Temperatura'
  AND l.valor > 30
  AND l.valor_imputado = 0
GROUP BY i.nombre, date(l.fecha_hora)
ORDER BY i.nombre, dia;
"""


def pregunta_2(df: pd.DataFrame) -> pd.DataFrame:
    """Pregunta 2 (pandas): ¿cuánta luz recibe cada invernadero entre las 09:00 y las 15:00?"""
    filtro = (
        (df["variable"] == "Luz")
        & (df["fecha_hora"].dt.hour.between(9, 15))
        & (~df["valor_imputado"])
    )
    return (df[filtro]
            .groupby("invernadero")["valor"]
            .agg(n_lecturas="count", luz_promedio="mean", luz_maxima="max")
            .round(1)
            .reset_index())


def verificar_consulta_1_con_pandas(df: pd.DataFrame, resultado_sql: pd.DataFrame) -> bool:
    """Comprueba que la consulta SQL 1 da lo mismo que su versión en pandas."""
    filtro = (df["variable"] == "Temperatura") & (df["valor"] > 30) & (~df["valor_imputado"])
    pd_res = (df[filtro]
              .assign(dia=df["fecha_hora"].dt.strftime("%Y-%m-%d"))
              .groupby(["invernadero", "dia"])["valor"]
              .agg(lecturas_sobre_30="count", maxima_c="max")
              .round(1).reset_index()
              .sort_values(["invernadero", "dia"]).reset_index(drop=True))
    return resultado_sql.values.tolist() == pd_res.values.tolist()


# ------------------------------------------------------------------------ MAIN
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=":memory:", help="ruta para guardar la base SQLite")
    args = parser.parse_args()

    print("1) EXTRAER")
    crudo = extraer()
    antes = perfilar(crudo)
    print(f"   {len(crudo)} filas leídas de {ENTRADA.name}")

    print("2) LIMPIAR")
    limpio = limpiar(crudo)
    despues = perfilar(limpio)
    print(f"   {'Métrica':<24}{'Antes':>8}{'Después':>10}")
    for k in antes:
        print(f"   {k:<24}{antes[k]:>8}{despues[k]:>10}")
    print(f"   Valores imputados con la mediana: {int(limpio['valor_imputado'].sum())}")
    limpio.to_csv(SALIDA, index=False)

    print("3) CARGAR (SQLite, 4 tablas según el ERD)")
    con = cargar(limpio, args.db)
    for tabla in ["invernadero", "tipo_sensor", "sensor", "lectura"]:
        n = con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
        print(f"   {tabla:<12}{n:>4} filas")

    print("4) ANALIZAR")
    print("\n   Pregunta 1 (SQL): lecturas de temperatura > 30 °C por invernadero y día")
    r1 = pd.read_sql(CONSULTA_1, con)
    print(r1.to_string(index=False))
    print("   ¿Coincide con la versión en pandas?", verificar_consulta_1_con_pandas(limpio, r1))

    print("\n   Pregunta 2 (pandas): luz entre las 09:00 y las 15:00 por invernadero")
    r2 = pregunta_2(limpio)
    print(r2.to_string(index=False))

    assert limpio.isna().sum().sum() == 0 and limpio.duplicated().sum() == 0
    print(f"\nListo. Datos limpios guardados en {SALIDA.name}")


if __name__ == "__main__":
    main()
