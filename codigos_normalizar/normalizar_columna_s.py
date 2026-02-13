import pandas as pd
import unicodedata
import re

# --- CONFIGURACIÓN DE ARCHIVOS Y COLUMNAS ---
ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_S_Normalizada.xlsx"
INDICE_COLUMNA_S = 18  # Columna S es la número 19, índice 18 en Python
NUM_FILAS_A_SALTEAR = 3  # Saltar las primeras 3 filas, datos desde la fila 4


def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.strip()
    return texto


def normalizar_s(valor):
    t = normalizar_texto(valor)
    if t == "r":
        return "Rural"
    if t == "u":
        return "Urbana"
    return ""


def normalizar_columna_s(
    archivo_entrada, archivo_salida, indice_columna_s, filas_a_saltar
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

    # Obtener la columna S
    nombre_columna_s = df.columns[indice_columna_s]
    columna_s = df[nombre_columna_s]

    # Normalizar valores
    columna_s_normalizada = columna_s.apply(normalizar_s)

    # Log de filas en blanco y su valor original
    filas_en_blanco = columna_s_normalizada[columna_s_normalizada == ""].index.tolist()
    if filas_en_blanco:
        print(
            "Advertencia: Las siguientes filas quedaron en blanco tras la normalización:"
        )
        for idx in filas_en_blanco:
            valor_original = columna_s.loc[idx]
            print(f"  Fila {idx + 1}: '{valor_original}'")
    else:
        print("No quedaron filas en blanco tras la normalización.")

    # Guardar solo la columna normalizada en el archivo de salida, sin encabezado ni índice
    print(f"Guardando columna S normalizada en: {archivo_salida}")
    try:
        columna_s_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna S normalizada."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


# Ejecutar la función
normalizar_columna_s(
    ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_S, NUM_FILAS_A_SALTEAR
)
