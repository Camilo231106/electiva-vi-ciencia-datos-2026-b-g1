"""c3-activity - Corte 3: Analisis temporal y visualizacion (Ciencia de Datos, Ing. Mecatronica).
Serie: piezas producidas por dia en una linea de manufactura automatizada.
Si existe 'produccion.csv' (columnas: fecha,piezas) se usa; si no, se genera una serie
sintetica reproducible (seed fija).
"""
import os, sqlite3, time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------- 1. Carga de la serie temporal ----------
csv = os.path.join(OUT, "produccion.csv")
if os.path.exists(csv):
    df = pd.read_csv(csv, parse_dates=["fecha"])
else:
    rng = np.random.default_rng(42)
    dias = pd.date_range("2023-01-01", "2025-12-31", freq="D")
    t = np.arange(len(dias))
    tendencia = 200 + 0.12 * t
    estacional = 40 * np.sin(2 * np.pi * (dias.dayofyear - 80) / 365.25)  # pico en verano/mitad de año
    ruido = rng.normal(0, 15, len(dias))
    df = pd.DataFrame({"fecha": dias, "piezas": (tendencia + estacional + ruido).round().astype(int)})
    df.to_csv(csv, index=False)

serie = df.set_index("fecha")["piezas"]

# ---------- 2. Resample + media movil ----------
mensual = serie.resample("MS").sum().to_frame("piezas")
mensual["media_movil_3m"] = mensual["piezas"].rolling(window=3).mean()
mensual["media_movil_12m"] = mensual["piezas"].rolling(window=12).mean()
print(mensual.tail(), "\n")

# Tendencia: pendiente de regresion lineal sobre la serie mensual
x = np.arange(len(mensual))
pend, inter = np.polyfit(x, mensual["piezas"].values, 1)
crec = (mensual["piezas"].iloc[-12:].sum() / mensual["piezas"].iloc[:12].sum() - 1) * 100
print(f"Pendiente: {pend:.1f} piezas/mes | Crecimiento ultimo anio vs primero: {crec:.1f}%")

# Estacionalidad: promedio por mes del anio (indice vs. promedio global)
mensual["mes"] = mensual.index.month
# Se quita primero la tendencia lineal para que el indice mida SOLO estacionalidad
mensual["tendencia"] = inter + pend * x
mensual["ratio"] = mensual["piezas"] / mensual["tendencia"]
indice = mensual.groupby("mes")["ratio"].mean()
indice = indice / indice.mean()
mes_pico, mes_valle = indice.idxmax(), indice.idxmin()
MESES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
print(f"Pico: {MESES[mes_pico-1]} ({indice.max():.2f}x) | Valle: {MESES[mes_valle-1]} ({indice.min():.2f}x)")

# ---------- 3. Visualizaciones ----------
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

# 3.1 Evolucion (linea): serie mensual + medias moviles
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(mensual.index, mensual["piezas"], color="#b0b7c3", lw=1.5, label="Producción mensual")
ax.plot(mensual.index, mensual["media_movil_3m"], color="#1f77b4", lw=2.2, label="Media móvil 3 meses")
ax.plot(mensual.index, mensual["media_movil_12m"], color="#d62728", lw=2.5, label="Media móvil 12 meses")
ax.set_title(f"La producción crece de forma sostenida: +{crec:.0f}% entre el primer y el último año",
             loc="left", fontweight="bold")
ax.set_xlabel("Mes"); ax.set_ylabel("Piezas producidas por mes")
ax.set_ylim(bottom=0)  # eje honesto: parte de cero
ax.legend(frameon=False, loc="lower right")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "chart1_evolucion.png"), dpi=150); plt.close(fig)

# 3.2 Comparacion (barras): indice estacional por mes
fig, ax = plt.subplots(figsize=(10, 5))
colores = ["#d62728" if m == mes_pico else "#1f77b4" if m == mes_valle else "#b0b7c3" for m in indice.index]
ax.bar([MESES[m-1] for m in indice.index], indice.values, color=colores)
ax.axhline(1, color="black", lw=1, ls="--")
ax.text(11.45, 1.01, "Nivel esperado por la tendencia = 1.0", ha="right", va="bottom", fontsize=9)
ax.set_title(f"{MESES[mes_pico-1]} produce {indice.max():.2f}x el promedio y {MESES[mes_valle-1]} solo {indice.min():.2f}x",
             loc="left", fontweight="bold")
ax.set_xlabel("Mes del año"); ax.set_ylabel("Índice estacional (producción / tendencia, normalizado)")
ax.set_ylim(bottom=0)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "chart2_estacionalidad.png"), dpi=150); plt.close(fig)

# ---------- 4. Optimizacion SQL (SQLite) ----------
con = sqlite3.connect(":memory:")
# Tabla grande: 300k filas para que la diferencia sea medible
rng = np.random.default_rng(1)
big = pd.DataFrame({
    "fecha": rng.choice(pd.date_range("2020-01-01", "2025-12-31").strftime("%Y-%m-%d"), 300_000),
    "maquina_id": rng.integers(1, 50, 300_000),
    "piezas": rng.integers(1, 100, 300_000)})
big.to_sql("produccion", con, index=False)

q_lenta = """SELECT maquina_id, SUM(piezas) AS total FROM produccion
             WHERE strftime('%Y', fecha) = '2025' GROUP BY maquina_id"""
q_rapida = """SELECT maquina_id, SUM(piezas) AS total FROM produccion
              WHERE fecha >= '2025-01-01' AND fecha < '2026-01-01' GROUP BY maquina_id"""

def medir(q, n=5):
    ts = []
    for _ in range(n):
        t0 = time.perf_counter(); con.execute(q).fetchall(); ts.append(time.perf_counter() - t0)
    return min(ts) * 1000

t_antes = medir(q_lenta)
plan_antes = con.execute("EXPLAIN QUERY PLAN " + q_lenta).fetchall()
con.execute("CREATE INDEX idx_prod_fecha_maq ON produccion(fecha, maquina_id, piezas)")
t_despues = medir(q_rapida)
plan_despues = con.execute("EXPLAIN QUERY PLAN " + q_rapida).fetchall()
print("\nPlan ANTES :", [p[-1] for p in plan_antes])
print("Plan DESPUES:", [p[-1] for p in plan_despues])
print(f"Tiempo antes: {t_antes:.1f} ms | despues: {t_despues:.1f} ms | mejora: {t_antes/t_despues:.1f}x")
