"""Genera un dataset sintético 'sucio' de pedidos de una tienda de electrónica
(data/pedidos_raw.csv). Se usa semilla fija para que sea reproducible."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 400

customers = [(i, n, c) for i, (n, c) in enumerate([
    ("Laura Gómez", "Neiva"), ("Carlos Pérez", "Pitalito"), ("Ana Rojas", "Garzón"),
    ("Juan Torres", "Neiva"), ("María Díaz", "La Plata"), ("Andrés Silva", "Neiva"),
    ("Paula Ortiz", "Pitalito"), ("Diego Mora", "Garzón"), ("Sofía Vargas", "Neiva"),
    ("Camilo Reyes", "La Plata"), ("Valentina Cruz", "Neiva"), ("Felipe Ramos", "Pitalito"),
], start=1)]
products = [
    (101, "Sensor Ultrasónico HC-SR04", "sensores", 9500),
    (102, "ESP32 DevKit 30 pines", "microcontroladores", 38000),
    (103, "Arduino Uno R3", "microcontroladores", 52000),
    (104, "Driver L298N", "actuadores", 14000),
    (105, "Servomotor SG90", "actuadores", 12500),
    (106, "Sensor TCRT5000", "sensores", 4500),
    (107, "Protoboard 830 puntos", "accesorios", 11000),
    (108, "Kit de Cables Dupont", "accesorios", 8000),
]
pay = ["tarjeta", "efectivo", "nequi", "transferencia"]

rows = []
for oid in range(1, N + 1):
    cid, cname, city = customers[rng.integers(len(customers))]
    pid, pname, cat, price = products[rng.integers(len(products))]
    date = pd.Timestamp("2026-01-01") + pd.Timedelta(days=int(rng.integers(0, 240)))
    fmt = rng.choice(["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"])
    rows.append({
        "order_id": oid,
        "order_date": date.strftime(fmt),
        "customer_id": cid,
        "customer_name": cname,
        "city": city,
        "email": cname.lower().replace(" ", ".").replace("ó", "o").replace("é", "e")
                 .replace("í", "i").replace("á", "a").replace("ú", "u") + "@correo.com",
        "product_id": pid,
        "product_name": pname,
        "category": cat,
        "unit_price": f"${price:,}" if rng.random() < 0.5 else str(price),
        "quantity": str(int(rng.integers(1, 6))),
        "payment_method": rng.choice(pay),
    })
df = pd.DataFrame(rows)

# --- ensuciar ---
for col in ["customer_name", "city", "product_name"]:
    idx = rng.choice(N, 60, replace=False)
    df.loc[idx, col] = df.loc[idx, col].map(lambda s: f"  {s.upper()} ")
idx = rng.choice(N, 50, replace=False); df.loc[idx, "category"] = df.loc[idx, "category"].str.title()
idx = rng.choice(N, 40, replace=False); df.loc[idx, "payment_method"] = df.loc[idx, "payment_method"].str.upper()
for col, k in [("city", 30), ("email", 25), ("quantity", 20), ("unit_price", 15), ("payment_method", 18)]:
    df.loc[rng.choice(N, k, replace=False), col] = np.nan
df.loc[rng.choice(N, 5, replace=False), "order_date"] = np.nan
df = pd.concat([df, df.sample(25, random_state=1)], ignore_index=True)   # duplicados exactos
df = df.sample(frac=1, random_state=7).reset_index(drop=True)
df.to_csv("data/pedidos_raw.csv", index=False)
print("Dataset generado:", df.shape)
