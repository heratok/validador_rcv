import pandas as pd
import unicodedata
import re

ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_DN_Normalizada.xlsx"
INDICE_COLUMNA_DN = 117  # Columna DN es la número 118, índice 117 en Python
NUM_FILAS_A_SALTEAR = 3


def normalizar_texto_dn(texto):
    if pd.isnull(texto) or str(texto).strip() == "":
        return "SIN DATO"
    t = str(texto)
    t = unicodedata.normalize("NFKD", t)
    t = "".join([c for c in t if not unicodedata.combining(c)])
    t = t.upper()
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    if t == "SI":
        return "Si"
    if t == "NO":
        return "No"
    if t == "SIN DATOS" or t == "SIN DATO":
        return "SIN DATO"
    return "SIN DATO"


def normalizar_columna_dn(
    archivo_entrada, archivo_salida, indice_columna_dn, filas_a_saltar
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

    nombre_columna_dn = df.columns[indice_columna_dn]
    columna_dn = df[nombre_columna_dn]

    columna_dn_normalizada = columna_dn.apply(normalizar_texto_dn)

    print("Valores únicos normalizados:", columna_dn_normalizada.unique())
    print("\nConteo de valores normalizados:")
    print(columna_dn_normalizada.value_counts())

    print(f"Guardando columna DN normalizada en: {archivo_salida}")
    try:
        columna_dn_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna DN normalizada."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


if __name__ == "__main__":
    normalizar_columna_dn(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_DN, NUM_FILAS_A_SALTEAR
    )
