import os
import pandas as pd

ARCHIVO_ENTRADA = "rcv_cesar.xlsx"
NUM_FILAS_A_SALTEAR = 0

# Copiar/ajustar la lista segun necesidad
INDICES_FECHAS = [
    7,
    23,
    27,
    29,
    43,
    45,
    47,
    49,
    51,
    53,
    58,
    59,
    61,
    64,
    66,
    68,
    74,
    76,
    80,
    82,
    84,
    86,
    88,
    90,
    92,
    94,
    96,
    98,
    100,
    102,
    104,
    108,
    119,
    123,
]


def leer_encabezados(archivo_entrada, filas_a_saltar):
    if not os.path.exists(archivo_entrada):
        raise FileNotFoundError(f"No se encontro el archivo: {archivo_entrada}")

    ext = os.path.splitext(archivo_entrada)[1].lower()
    if ext == ".xlsb":
        df_headers = pd.read_excel(
            archivo_entrada, header=None, skiprows=filas_a_saltar, engine="pyxlsb", nrows=1
        )
    else:
        df_headers = pd.read_excel(archivo_entrada, header=None, skiprows=filas_a_saltar, nrows=1)

    if df_headers.empty:
        return []

    return df_headers.iloc[0].tolist()


def imprimir_mapeo(indices_fechas, encabezados):
    total_cols = len(encabezados)
    print(f"Total de columnas en encabezados: {total_cols}")

    for indice in indices_fechas:
        if indice >= total_cols:
            print(f"Indice {indice}: (FUERA DE RANGO)")
            continue
        nombre = str(encabezados[indice]).strip()
        print(f"Indice {indice}: {nombre}")


if __name__ == "__main__":
    print(f"Leyendo encabezados desde: {ARCHIVO_ENTRADA}")
    encabezados = leer_encabezados(ARCHIVO_ENTRADA, NUM_FILAS_A_SALTEAR)
    if not encabezados:
        print("No se pudieron leer encabezados.")
    else:
        imprimir_mapeo(INDICES_FECHAS, encabezados)
