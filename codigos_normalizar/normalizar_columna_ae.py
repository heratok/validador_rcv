import pandas as pd
import unicodedata
import re

ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_AE_Normalizada.xlsx"
HOJA = 1  # Índice de la hoja "123456"
INDICE_COLUMNA_AE = 30  # Columna AE es la número 31, índice 30 en Python
NUM_FILAS_A_SALTEAR = 3


def normalizar_texto_ae(texto):
    if pd.isnull(texto) or str(texto).strip() == "":
        return "Sin Dato"
    t = str(texto)
    t = unicodedata.normalize("NFKD", t)
    t = "".join([c for c in t if not unicodedata.combining(c)])
    t = t.upper()
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    if t == "1845-01-01":
        return "No Aplica"
    return t


def normalizar_columna_ae(
    archivo_entrada, archivo_salida, hoja, indice_columna_ae, filas_a_saltar
):
    print(f"Iniciando la lectura del archivo: {archivo_entrada}, hoja índice {hoja}")
    try:
        df = pd.read_excel(
            archivo_entrada,
            header=None,
            skiprows=filas_a_saltar,
            engine="pyxlsb",
            sheet_name=hoja,
        )
        print(f"Datos cargados correctamente. Registros: {len(df)}")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    nombre_columna_ae = df.columns[indice_columna_ae]
    columna_ae = df[nombre_columna_ae]

    columna_ae_normalizada = columna_ae.apply(normalizar_texto_ae)

    print("Valores únicos normalizados:", columna_ae_normalizada.unique())
    print("\nConteo de valores normalizados:")
    print(columna_ae_normalizada.value_counts())

    print(f"Guardando columna AE normalizada en: {archivo_salida}")
    try:
        columna_ae_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna AE normalizada."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


if __name__ == "__main__":
    normalizar_columna_ae(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, HOJA, INDICE_COLUMNA_AE, NUM_FILAS_A_SALTEAR
    )
