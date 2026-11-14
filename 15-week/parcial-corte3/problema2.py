"""Problema 2: elección del gráfico correcto y corrección de errores de diseño."""
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("serie.csv", parse_dates=["fecha"], index_col="fecha")

# ---------- 2a. TRES PREGUNTAS, TRES GRÁFICOS ----------
# P1 EVOLUCIÓN: ¿cómo cambió la producción mensual en el tiempo?  → LÍNEAS
mensual = df["produccion"].resample("ME").mean()
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(mensual.index, mensual, marker="o", ms=3)
ax.set_title("Evolución: producción mensual promedio (2023-2025)")
ax.set_ylabel("Unidades por día"); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("p2_evolucion_lineas.png", dpi=150)

# P2 COMPARACIÓN: ¿qué línea de producción rindió más en 2025?  → BARRAS horizontales ordenadas
lineas = pd.Series({"Línea A": 15200, "Línea B": 13800, "Línea C": 11900, "Línea D": 9400}).sort_values()
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.barh(lineas.index, lineas.values, color="#1f77b4")
for i, v in enumerate(lineas.values):
    ax.text(v + 150, i, f"{v:,}", va="center")
ax.set_xlim(0, lineas.max() * 1.15)                       # eje desde 0
ax.set_title("Comparación: producción anual 2025 por línea (unidades)")
fig.tight_layout(); fig.savefig("p2_comparacion_barras.png", dpi=150)

# P3 PROPORCIÓN: ¿qué porcentaje del total de fallas aporta cada tipo?  → DONA (pocas categorías)
fallas = pd.Series({"Mecánica": 45, "Eléctrica": 30, "Software": 15, "Otras": 10})
fig, ax = plt.subplots(figsize=(5.5, 5.5))
ax.pie(fallas, labels=fallas.index, autopct="%1.0f%%", startangle=90,
       wedgeprops=dict(width=0.45), pctdistance=0.78)
ax.set_title("Proporción: fallas por tipo (% del total)")
fig.tight_layout(); fig.savefig("p2_proporcion_dona.png", dpi=150)

# ---------- 2b. ERRORES DE DISEÑO: ANTES vs DESPUÉS ----------
# ERROR 1: eje Y truncado en barras
turnos = ["Turno 1", "Turno 2", "Turno 3"]
eficiencia = [96.0, 97.5, 98.0]                           # diferencia real: 2 puntos porcentuales
# ERROR 2: torta saturada (10 categorías)
cats = [f"Falla {i}" for i in range(1, 11)]
vals = [18, 16, 14, 12, 10, 8, 7, 6, 5, 4]

fig, axs = plt.subplots(2, 2, figsize=(11, 8))
axs[0, 0].bar(turnos, eficiencia); axs[0, 0].set_ylim(95.5, 98.5)
axs[0, 0].set_title("ERROR: eje Y truncado (Turno 3 parece 5 veces el Turno 1)")
axs[0, 1].bar(turnos, eficiencia); axs[0, 1].set_ylim(0, 110)
axs[0, 1].set_title("CORRECTO: eje desde 0 (diferencia real pequeña)")
axs[0, 1].set_ylabel("Eficiencia (%)")
for i, v in enumerate(eficiencia):
    axs[0, 1].text(i, v + 1, f"{v}%", ha="center")

axs[1, 0].pie(vals, labels=cats, autopct="%1.0f%%", textprops={"fontsize": 7})
axs[1, 0].set_title("ERROR: torta saturada (10 porciones)")
orden = sorted(zip(vals, cats))
axs[1, 1].barh([c for _, c in orden], [v for v, _ in orden], color="#1f77b4")
axs[1, 1].set_title("CORRECTO: barras ordenadas")
axs[1, 1].set_xlabel("% del total de fallas")
fig.tight_layout(); fig.savefig("p2_error_vs_correccion.png", dpi=150)
print("Gráficos del Problema 2 generados.")
