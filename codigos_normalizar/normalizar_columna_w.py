import pandas as pd
import unicodedata
import re

ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_W_Normalizada.xlsx"
INDICE_COLUMNA_W = 22  # Columna W es la número 23, índice 22 en Python
NUM_FILAS_A_SALTEAR = 3


def normalizar_texto_w(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = texto.upper()
    texto = re.sub(r"\s+", " ", texto)  # Un solo espacio entre palabras
    texto = texto.strip()
    return texto


def normalizar_columna_w(
    archivo_entrada, archivo_salida, indice_columna_w, filas_a_saltar
):
    print(f"Iniciando la lectura del archivo: {archivo_entrada}")
    try:
        df = pd.read_excel(
            archivo_entrada, header=None, skiprows=filas_a_saltar, engine="pyxlsb"
        )
        print(f"Datos cargados correctamente. Registros: {len(df)}")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    nombre_columna_w = df.columns[indice_columna_w]
    columna_w = df[nombre_columna_w]

    columna_w_normalizada = columna_w.apply(normalizar_texto_w)

    print("Valores únicos normalizados:", columna_w_normalizada.unique())
    print("\nConteo de valores normalizados:")
    print(columna_w_normalizada.value_counts())

    print(f"Guardando columna W normalizada en: {archivo_salida}")
    try:
        columna_w_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna W normalizada."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


if __name__ == "__main__":
    normalizar_columna_w(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_W, NUM_FILAS_A_SALTEAR
    )
