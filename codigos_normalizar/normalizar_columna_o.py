import pandas as pd
import unicodedata
import re

# --- CONFIGURACIÓN DE ARCHIVOS Y COLUMNAS ---
ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_O_Normalizada.xlsx"
INDICE_COLUMNA_O = 14  # Columna O es la número 15, índice 14 en Python
NUM_FILAS_A_SALTEAR = 3  # Saltar las primeras 3 filas, datos desde la fila 4

# Mapeo de valores a opciones válidas
MAPEO_O = {
    "yukpa": "Yukpa",
    "wiwa": "Wiwa",
    "sin etnia": "Sin Etnia",
    "kankuama": "Kankuamo",
    "kankuamo": "Kankuamo",
    "kankuama ": "Kankuamo",
    "wayuu": "Wayuu",
    "arhuaca": "Arhuaco",
    "arhuaco": "Arhuaco",
    "zenu": "Zenu",
    "ingas": "Inga",
    "chimila": "Chimila",
    "kogui": "Kogui",
    "indigena arauca": "Sin Etnia",
    "afrodecendiente": "Sin Etnia",
}


def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.strip()
    return texto


def normalizar_o(valor):
    t = normalizar_texto(valor)
    return MAPEO_O.get(t, "")


def normalizar_columna_o(
    archivo_entrada, archivo_salida, indice_columna_o, filas_a_saltar
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

    # Obtener la columna O
    nombre_columna_o = df.columns[indice_columna_o]
    columna_o = df[nombre_columna_o]

    # Normalizar valores
    columna_o_normalizada = columna_o.apply(normalizar_o)

    # Log de filas en blanco y su valor original
    filas_en_blanco = columna_o_normalizada[columna_o_normalizada == ""].index.tolist()
    if filas_en_blanco:
        print(
            "Advertencia: Las siguientes filas quedaron en blanco tras la normalización:"
        )
        for idx in filas_en_blanco:
            valor_original = columna_o.loc[idx]
            print(f"  Fila {idx + 1}: '{valor_original}'")
    else:
        print("No quedaron filas en blanco tras la normalización.")

    # Guardar solo la columna normalizada en el archivo de salida, sin encabezado ni índice
    print(f"Guardando columna O normalizada en: {archivo_salida}")
    try:
        columna_o_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna O normalizada."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


# Ejecutar la función
normalizar_columna_o(
    ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_O, NUM_FILAS_A_SALTEAR
)
