"""Semana 9 · Limpieza de un dataset con pandas
Dataset: lecturas del invernadero inteligente (datos_sucios.csv), con problemas
de calidad introducidos a propósito: nulos, valores centinela, duplicados,
tipos incorrectos y formatos de texto/fecha inconsistentes.

Uso:  python limpieza.py
Salida: imprime el reporte antes/después y guarda datos_limpios.csv
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
ENTRADA = BASE / "datos_sucios.csv"
SALIDA = BASE / "datos_limpios.csv"

CENTINELA = -999  # valor que el sensor reporta cuando falla la lectura
MAPA_VARIABLE = {"temp": "Temperatura", "temperatura": "Temperatura",
                 "luz": "Luz", "humedad": "Humedad"}
MAPA_UNIDAD = {"Temperatura": "°C", "Luz": "lux", "Humedad": "%"}


def perfilar(df: pd.DataFrame) -> dict:
    """Métricas de calidad de un DataFrame."""
    valor_txt = df["valor"].astype(str)
    return {
        "Filas": len(df),
        "Nulos (total de celdas)": int(df.isna().sum().sum()),
        "Duplicados (filas exactas)": int(df.duplicated().sum()),
        "Valores centinela (-999)": int((pd.to_numeric(
            valor_txt.str.replace(",", ".", regex=False), errors="coerce") == CENTINELA).sum()),
        "Valores con coma decimal": int(valor_txt.str.contains(",", regex=False).sum()),
        "Formatos de invernadero distintos": df["invernadero"].dropna().nunique(),
        "Formatos de variable distintos": df["variable"].dropna().nunique(),
    }


def parsear_fecha(serie: pd.Series) -> pd.Series:
    """Convierte fechas en dos formatos (ISO y dd/mm/aaaa); lo demás queda NaT."""
    iso = pd.to_datetime(serie, format="%Y-%m-%d %H:%M:%S", errors="coerce")
    latino = pd.to_datetime(serie, format="%d/%m/%Y %H:%M", errors="coerce")
    return iso.fillna(latino)


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1) Normalizar texto: espacios, mayúsculas/minúsculas y sinónimos
    df["invernadero"] = df["invernadero"].str.strip().str.title()
    df["variable"] = df["variable"].str.strip().str.lower().map(MAPA_VARIABLE)

    # 2) Corregir tipos
    df["valor"] = pd.to_numeric(
        df["valor"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    df["fecha_hora"] = parsear_fecha(df["fecha_hora"])

    # 3) Valores centinela -> nulos (un -999 no es una medición real)
    df.loc[df["valor"] == CENTINELA, "valor"] = pd.NA
    df["valor"] = df["valor"].astype(float)

    # 4) Duplicados (después de normalizar, para detectar los que solo
    #    diferían en el formato del texto)
    df = df.drop_duplicates().reset_index(drop=True)

    # 5) Faltantes
    #    - Sin invernadero o sin fecha válida: no se puede ubicar la lectura -> se elimina
    df = df.dropna(subset=["invernadero", "fecha_hora"]).copy()
    #    - Unidad faltante: se deduce de la variable
    df["unidad"] = df["unidad"].fillna(df["variable"].map(MAPA_UNIDAD))
    #    - Valor faltante: se imputa con la mediana de su invernadero y variable
    df["valor_imputado"] = df["valor"].isna()
    mediana = df.groupby(["invernadero", "variable"])["valor"].transform("median")
    df["valor"] = df["valor"].fillna(mediana).round(1)

    return df.sort_values("id_lectura").reset_index(drop=True)


def main() -> None:
    sucio = pd.read_csv(ENTRADA)
    limpio = limpiar(sucio)

    antes = perfilar(sucio)
    despues = perfilar(limpio)
    despues["Valores centinela (-999)"] = int((limpio["valor"] == CENTINELA).sum())
    despues["Valores con coma decimal"] = 0  # la columna ahora es numérica

    fechas_invalidas = int(parsear_fecha(sucio["fecha_hora"]).isna().sum())

    print("=== REPORTE ANTES / DESPUÉS ===")
    print(f"{'Métrica':<38}{'Antes':>8}{'Después':>10}")
    for clave in antes:
        print(f"{clave:<38}{antes[clave]:>8}{despues[clave]:>10}")
    print(f"{'Fechas inválidas':<38}{fechas_invalidas:>8}{int(limpio['fecha_hora'].isna().sum()):>10}")
    print(f"\nValores imputados con la mediana: {int(limpio['valor_imputado'].sum())}")
    print("\nTipos de dato antes:  ", dict(sucio.dtypes.astype(str)))
    print("Tipos de dato después:", dict(limpio.dtypes.astype(str)))

    # Verificaciones de calidad
    assert limpio.isna().sum().sum() == 0
    assert limpio.duplicated().sum() == 0
    assert limpio["valor"].dtype == float

    limpio.to_csv(SALIDA, index=False)
    print(f"\nArchivo limpio guardado en: {SALIDA.name}")


if __name__ == "__main__":
    main()
