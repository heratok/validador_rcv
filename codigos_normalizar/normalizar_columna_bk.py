import pandas as pd
import unicodedata
import re

ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_BK_Normalizada.xlsx"
INDICE_COLUMNA_BK = 62  # Columna BK es la número 63, índice 62 en Python
NUM_FILAS_A_SALTEAR = 3

MAPEO_BK = {
    "si": "Si",
    "no": "No",
    "no aplica": "No Aplica",
    "": "No Aplica",
}


def normalizar_texto_bk(texto):
    if not isinstance(texto, str):
        return "No Aplica"
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.strip()
    return texto


def normalizar_bk(valor):
    t = normalizar_texto_bk(valor)
    if t == "si":
        return "Si"
    if t == "no":
        return "No"
    if t == "no aplica":
        return "No Aplica"
    return "No Aplica"


def normalizar_columna_bk(
    archivo_entrada, archivo_salida, indice_columna_bk, filas_a_saltar
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

    nombre_columna_bk = df.columns[indice_columna_bk]
    columna_bk = df[nombre_columna_bk]

    columna_bk_normalizada = columna_bk.apply(normalizar_bk)

    print("Valores únicos normalizados:", columna_bk_normalizada.unique())
    print("\nConteo de valores normalizados:")
    print(columna_bk_normalizada.value_counts())

    print(f"Guardando columna BK normalizada en: {archivo_salida}")
    try:
        columna_bk_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna BK normalizada."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


if __name__ == "__main__":
    normalizar_columna_bk(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_BK, NUM_FILAS_A_SALTEAR
    )
