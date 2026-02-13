import pandas as pd
import unicodedata
import re

ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_AY_Normalizada.xlsx"
INDICE_COLUMNA_AY = 50  # Columna AY es la número 51, índice 50 en Python
NUM_FILAS_A_SALTEAR = 3


def normalizar_texto_ay(texto):
    if pd.isnull(texto) or texto == 0 or str(texto).strip() == "":
        return "Sin Dato"
    t = str(texto)
    t = unicodedata.normalize("NFKD", t)
    t = "".join([c for c in t if not unicodedata.combining(c)])
    t = t.lower()
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    if t == "normal":
        return "Normal"
    if t == "patologico" or t == "patalogico":
        return "Patologico"
    if t == "no patologico":
        return "Normal"
    return "Sin Dato"


def normalizar_columna_ay(
    archivo_entrada, archivo_salida, indice_columna_ay, filas_a_saltar
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

    nombre_columna_ay = df.columns[indice_columna_ay]
    columna_ay = df[nombre_columna_ay]

    columna_ay_normalizada = columna_ay.apply(normalizar_texto_ay)

    print("Valores únicos normalizados:", columna_ay_normalizada.unique())
    print("\nConteo de valores normalizados:")
    print(columna_ay_normalizada.value_counts())

    print(f"Guardando columna AY normalizada en: {archivo_salida}")
    try:
        columna_ay_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna AY normalizada."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


if __name__ == "__main__":
    normalizar_columna_ay(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_AY, NUM_FILAS_A_SALTEAR
    )
