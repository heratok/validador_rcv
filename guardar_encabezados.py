import argparse
import json
import os

import pandas as pd


def detectar_engine(archivo):
    ext = os.path.splitext(archivo)[1].lower()
    if ext == ".xlsb":
        try:
            import pyxlsb  # noqa: F401
            return "pyxlsb"
        except ImportError:
            print("Falta pyxlsb. Instalar con: pip install pyxlsb")
            return None
    if ext in [".xlsx", ".xls"]:
        return "openpyxl"
    return None


def leer_encabezados_excel(archivo):
    engine = detectar_engine(archivo)
    if not engine:
        raise ValueError(f"Formato no soportado para encabezados: {archivo}")
    df_headers = pd.read_excel(archivo, header=None, skiprows=0, nrows=1, engine=engine)
    headers = df_headers.iloc[0].tolist()
    if not headers:
        raise ValueError("No se encontraron encabezados en la primera fila")
    return headers


def main():
    parser = argparse.ArgumentParser(description="Guardar encabezados en JSON")
    parser.add_argument("--archivo", required=True, help="Ruta del Excel origen")
    parser.add_argument(
        "--salida",
        default="encabezados.json",
        help="Ruta del JSON de salida",
    )
    args = parser.parse_args()

    encabezados = leer_encabezados_excel(args.archivo)

    with open(args.salida, "w", encoding="utf-8") as f:
        json.dump(encabezados, f, ensure_ascii=False, indent=2)

    print(f"Encabezados guardados en: {args.salida} ({len(encabezados)} columnas)")


if __name__ == "__main__":
    main()
