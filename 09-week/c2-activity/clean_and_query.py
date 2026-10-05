"""
Actividad c2 - Corte 2: Modelo, consulta y limpieza de datos
Autor: Cristian Camilo Quiguanas Ossa - Ingeniería Mecatrónica, Corhuila
Dataset: pedidos de una tienda de electrónica (data/pedidos_raw.csv)
"""
import pandas as pd

pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

# ------------------------------------------------------------------ 1. CARGA
df = pd.read_csv("data/pedidos_raw.csv", dtype=str)   # todo como texto: lo tipamos nosotros
raw = df.copy()

def snapshot(d):
    """Métricas para el reporte antes/después."""
    return {
        "filas": len(d),
        "columnas": d.shape[1],
        "nulos_totales": int(d.isna().sum().sum()),
        "duplicados_exactos": int(d.duplicated().sum()),
        "duplicados_por_order_id": int(d.duplicated(subset="order_id").sum()),
    }

before = snapshot(df)
nulls_before = df.isna().sum()
dtypes_before = df.dtypes.astype(str)

print("=== NULOS POR COLUMNA (antes) ===")
print(nulls_before[nulls_before > 0], "\n")

# ------------------------------------------------- 2. NORMALIZACIÓN DE TEXTO
# Espacios sobrantes + minúsculas (mayúsculas inicial para nombres y ciudades)
text_cols = ["customer_name", "city", "email", "product_name", "category", "payment_method"]
for c in text_cols:
    df[c] = df[c].str.strip().str.replace(r"\s+", " ", regex=True)
for c in ["email", "category", "payment_method"]:
    df[c] = df[c].str.lower()
for c in ["customer_name", "city", "product_name"]:
    df[c] = df[c].str.title()
# Restaurar siglas que Title Case deforma (HC-SR04, TCRT5000, ESP32, SG90)
for bad, good in [("Hc-Sr04", "HC-SR04"), ("Tcrt5000", "TCRT5000"), ("Esp32", "ESP32"), ("Sg90", "SG90"), ("L298n", "L298N")]:
    df["product_name"] = df["product_name"].str.replace(bad, good, regex=False)

# ------------------------------------------------------- 3. CORRECCIÓN DE TIPOS
# 3a. Fechas con formatos mezclados (YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY)
d = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
    d = d.fillna(pd.to_datetime(df["order_date"], format=fmt, errors="coerce"))
df["order_date"] = d

# 3b. Precio: quitar "$" y separadores -> numérico
df["unit_price"] = pd.to_numeric(df["unit_price"].str.replace(r"[$,]", "", regex=True), errors="coerce")
# 3c. Enteros / categóricos
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
for c in ["order_id", "customer_id", "product_id"]:
    df[c] = df[c].astype(int)
for c in ["category", "payment_method", "city"]:
    df[c] = df[c].astype("category")

# --------------------------------------------------------------- 4. DUPLICADOS
# Tras normalizar, un pedido repetido = mismo order_id
n_dup = int(df.duplicated(subset="order_id").sum())
df = df.drop_duplicates(subset="order_id", keep="first")
print(f"Duplicados eliminados: {n_dup}\n")

# ------------------------------------------------------------------- 5. NULOS
nulls_after_norm = df.isna().sum()
# Estrategias:
#  - order_date: ELIMINAR (sin fecha el pedido no sirve para análisis temporal)
#  - unit_price: IMPUTAR con la moda del precio del mismo producto (catálogo)
#  - city, email: IMPUTAR con el valor del mismo cliente (customer_id)
#  - quantity: IMPUTAR con la mediana
#  - payment_method: IMPUTAR con 'desconocido'
df = df.dropna(subset=["order_date"])
df["unit_price"] = df["unit_price"].fillna(df.groupby("product_id")["unit_price"].transform(lambda s: s.mode().iloc[0]))
for c in ["city", "email"]:
    df[c] = df[c].astype("object")
    df[c] = df[c].fillna(df.groupby("customer_id")[c].transform(lambda s: s.mode().iloc[0] if s.notna().any() else None))
df["city"] = df["city"].astype("category")
df["quantity"] = df["quantity"].fillna(df["quantity"].median()).astype(int)
df["payment_method"] = df["payment_method"].cat.add_categories("desconocido").fillna("desconocido")

# Columna derivada
df["total"] = df["unit_price"] * df["quantity"]
df["month"] = df["order_date"].dt.to_period("M").astype(str)
df = df.reset_index(drop=True)

# ------------------------------------------------------- 6. REPORTE ANTES/DESPUÉS
after = snapshot(df.drop(columns=["total", "month"]))
resumen = pd.DataFrame({"antes": before, "después": after})
resumen["cambio"] = resumen["después"] - resumen["antes"]
print("=== REPORTE ANTES / DESPUÉS ===")
print(resumen, "\n")

nulos = pd.DataFrame({"nulos_antes": nulls_before,
                      "nulos_después": df[raw.columns].isna().sum()})
nulos["corregidos"] = nulos["nulos_antes"] - nulos["nulos_después"]
print(nulos[nulos["nulos_antes"] > 0], "\n")

tipos = pd.DataFrame({"tipo_antes": dtypes_before,
                      "tipo_después": df[raw.columns].dtypes.astype(str)})
tipos["corregido"] = tipos["tipo_antes"] != tipos["tipo_después"]
print(tipos, "\n")
print("Tipos corregidos:", int(tipos["corregido"].sum()), "de", len(tipos), "columnas\n")

# ------------------------------------------------------------------ 7. CONSULTAS
print("=== PREGUNTA 1 ===")
print("¿Qué categorías generan más ingresos en pedidos grandes (quantity >= 3) y cuál es su ticket promedio?")
q1 = (df[df["quantity"] >= 3]
      .groupby("category", observed=True)
      .agg(pedidos=("order_id", "count"), ingresos=("total", "sum"), ticket_promedio=("total", "mean"))
      .round(0).sort_values("ingresos", ascending=False))
print(q1, "\n")

print("=== PREGUNTA 2 ===")
print("¿Cómo se distribuyen los ingresos por ciudad y medio de pago en pedidos de microcontroladores?")
q2 = (df[df["category"] == "microcontroladores"]
      .pivot_table(index="city", columns="payment_method", values="total",
                   aggfunc="sum", fill_value=0, observed=True, margins=True, margins_name="TOTAL")
      .sort_values("TOTAL", ascending=False))
print(q2, "\n")

# ------------------------------------------------------------------ 8. SALIDAS
df.to_csv("data/pedidos_clean.csv", index=False)
resumen.to_csv("data/reporte_antes_despues.csv")
print("Archivos guardados: data/pedidos_clean.csv, data/reporte_antes_despues.csv")
