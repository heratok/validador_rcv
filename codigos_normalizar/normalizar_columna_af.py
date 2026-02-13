import pandas as pd
import unicodedata
import re

ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_AF_Normalizada.xlsx"
INDICE_COLUMNA_AF = 31  # Columna AF es la número 32, índice 31 en Python
NUM_FILAS_A_SALTEAR = 3

# Normalización robusta para HTA o DM


def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.strip()
    return texto


def normalizar_af(valor):
    t = normalizar_texto(valor)
    # Normalizar variantes de 'NO TIENE ERC' (con espacios, mayúsculas, etc.)
    if t.replace(" ", "") == "notieneerc":
        return "No tiene ERC"
    if "no tiene erc" in t:
        return "No tiene ERC"
    # Si contiene hta, dm o diabetica, lo agrupamos
    if any(x in t for x in ["hta", "dm", "diabetica"]):
        return "HTA o DM"
    # Si contiene solo espacios, lo agrupamos igual
    if t.replace(" ", "") == "htaodm":
        return "HTA o DM"
    return "HTA o DM"  # Si no coincide, lo agrupamos igual


def normalizar_columna_af(
    archivo_entrada, archivo_salida, indice_columna_af, filas_a_saltar
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

    nombre_columna_af = df.columns[indice_columna_af]
    columna_af = df[nombre_columna_af]

    columna_af_normalizada = columna_af.apply(normalizar_af)

    print("Valores únicos normalizados:", columna_af_normalizada.unique())
    print("\nConteo de valores normalizados:")
    print(columna_af_normalizada.value_counts())

    print(f"Guardando columna AF normalizada en: {archivo_salida}")
    try:
        columna_af_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna AF normalizada."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


if __name__ == "__main__":
    normalizar_columna_af(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_AF, NUM_FILAS_A_SALTEAR
    )
