"""Genera serie.csv: producción diaria (unidades) de una línea de ensamblaje, 2023-2025.
Se usa una semilla fija para que los resultados sean reproducibles."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
fechas = pd.date_range("2023-01-01", "2025-12-31", freq="D")
t = np.arange(len(fechas))

tendencia = 500 + 0.35 * t                                # crece ~10.6 u/mes
estacional = 60 * np.sin(2 * np.pi * (t - 90) / 365.25)   # ciclo anual: pico ~jul, valle ~dic
ruido = rng.normal(0, 25, len(t))
produccion = tendencia + estacional + ruido

df = pd.DataFrame({"fecha": fechas, "produccion": produccion.round(1)})
df.to_csv("serie.csv", index=False)
print(df.head(), "\nFilas:", len(df))
