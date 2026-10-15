"""Semana 8 · Consumo de una API pública con requests
API: Open-Meteo (clima, gratuita y sin API key): https://open-meteo.com
Etapas ETL que cubre este script:
  E (extraer)    -> requests.get() a la API
  T (transformar)-> pandas: renombrar columnas y convertir tipos
Uso:  python consumir_api.py
"""
import sys

import pandas as pd
import requests

URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {
    "latitude": 2.93,        # ajusta a la ubicación de tu invernadero
    "longitude": -75.28,
    "hourly": "temperature_2m,relative_humidity_2m",
    "forecast_days": 1,
    "timezone": "America/Bogota",
}


def extraer() -> dict:
    """E: consulta la API y devuelve el JSON."""
    respuesta = requests.get(URL, params=PARAMS, timeout=15)
    respuesta.raise_for_status()
    return respuesta.json()


def transformar(datos: dict) -> pd.DataFrame:
    """T: convierte el bloque 'hourly' en una tabla limpia."""
    df = pd.DataFrame(datos["hourly"]).rename(
        columns={
            "time": "fecha_hora",
            "temperature_2m": "temperatura_c",
            "relative_humidity_2m": "humedad_pct",
        }
    )
    df["fecha_hora"] = pd.to_datetime(df["fecha_hora"])
    return df


def main() -> None:
    try:
        datos = extraer()
    except requests.RequestException as error:
        sys.exit(f"No se pudo consultar la API: {error}")

    df = transformar(datos)
    print(f"Registros recibidos: {len(df)}")
    print("\nPrimeros 3 registros:")
    print(df.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
