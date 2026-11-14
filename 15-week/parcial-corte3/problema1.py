"""Problema 1: Serie de tiempo (resample + media móvil + tendencia y estacionalidad)."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1) CARGA con la fecha como índice (DatetimeIndex)
df = pd.read_csv("serie.csv", parse_dates=["fecha"], index_col="fecha").sort_index()
print(df.index.dtype, "| rango:", df.index.min().date(), "→", df.index.max().date())

# 2) AGREGACIÓN por periodo: diario → mensual (promedio de cada mes)
#    'ME' = month end (pandas >= 2.2; en versiones anteriores se escribe 'M')
mensual = df["produccion"].resample("ME").mean()

# MEDIAS MÓVILES
mm3 = mensual.rolling(window=3).mean()      # suaviza el ruido de corto plazo
mm12 = mensual.rolling(window=12).mean()    # = un ciclo anual completo → aísla la tendencia

# 3) TENDENCIA Y ESTACIONALIDAD (descomposición aditiva hecha "a mano")
#    observado = tendencia + estacionalidad + residuo
# 3.1 Tendencia: media móvil centrada 2x12 (promedio de dos MM12 desfasadas)
tendencia = mensual.rolling(12, center=True).mean().rolling(2).mean().shift(-1)
# 3.2 Estacionalidad: promedio del (observado - tendencia) por mes del año
sin_tend = mensual - tendencia
estacional = sin_tend.groupby(sin_tend.index.month).mean()
estacional = estacional - estacional.mean()              # centrado en 0
efecto = mensual.index.month.map(estacional)             # un valor por cada mes de la serie
# 3.3 Residuo
residuo = mensual - tendencia - efecto

# Cuantificar la tendencia con una regresión lineal (pendiente por mes)
x = np.arange(len(mensual))
pendiente, intercepto = np.polyfit(x, mensual.values, 1)
print(f"\nTENDENCIA: {pendiente:.2f} unidades/mes (≈ {pendiente*12:.0f} por año)")
nombres = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
print("\nESTACIONALIDAD (efecto promedio por mes, unidades):")
for m, v in estacional.items():
    print(f"  {nombres[m-1]}: {v:+.1f}")
print(f"\nPico estacional: {nombres[estacional.idxmax()-1]} | Valle: {nombres[estacional.idxmin()-1]}")

# GRÁFICO 1: serie, medias móviles y recta de tendencia
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(mensual.index, mensual, label="Promedio mensual", alpha=0.55)
ax.plot(mm3.index, mm3, label="Media móvil 3 meses")
ax.plot(mm12.index, mm12, label="Media móvil 12 meses", linewidth=2.2)
ax.plot(mensual.index, pendiente * x + intercepto, "--", color="gray", label="Recta de tendencia")
ax.set_title("Producción mensual promedio con medias móviles")
ax.set_ylabel("Unidades por día"); ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("p1_serie_media_movil.png", dpi=150)

# GRÁFICO 2: descomposición en 4 paneles
fig, axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
for a, serie, titulo in zip(axs, [mensual, tendencia, pd.Series(efecto, index=mensual.index), residuo],
                            ["Observado", "Tendencia", "Estacionalidad", "Residuo"]):
    a.plot(serie.index, serie); a.set_ylabel(titulo); a.grid(alpha=0.3)
fig.suptitle("Descomposición aditiva (periodo = 12 meses)")
fig.tight_layout(); fig.savefig("p1_descomposicion.png", dpi=150)
