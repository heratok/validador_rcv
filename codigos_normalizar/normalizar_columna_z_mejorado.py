import pandas as pd
import unicodedata
import re

# --- CONFIGURACIÓN DE ARCHIVOS Y COLUMNAS ---
ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_Z_Normalizada.xlsx"
INDICE_COLUMNA_Z = 25  # Columna Z es la número 26, índice 25 en Python
NUM_FILAS_A_SALTEAR = 3  # Saltar las primeras 3 filas, datos desde la fila 4

MAPEO_Z = {
    "si": "Si",
    "sí": "Si",
    "no": "No",
    "sin dato": "SIN DATO",
    "": "SIN DATO",
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


def normalizar_z(valor):
    t = normalizar_texto(valor)
    # Si contiene 'sin dato' en cualquier parte, es SIN DATO
    if "sin dato" in t:
        return "SIN DATO"
    # Si está vacío, también es SIN DATO
    if t == "":
        return "SIN DATO"
    # Si empieza con si/no
    if t.startswith("si") or t.startswith("sí"):
        return "Si"
    if t.startswith("no"):
        return "No"
    return "SIN DATO"


def normalizar_columna_z(
    archivo_entrada, archivo_salida, indice_columna_z, filas_a_saltar
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

    # Obtener la columna Z
    nombre_columna_z = df.columns[indice_columna_z]
    columna_z = df[nombre_columna_z]

    # Normalizar valores
    columna_z_normalizada = columna_z.apply(normalizar_z)

    # Log de filas en blanco y su valor original
    filas_en_blanco = columna_z_normalizada[columna_z_normalizada == ""].index.tolist()
    if filas_en_blanco:
        print(
            "Advertencia: Las siguientes filas quedaron en blanco tras la normalización:"
        )
        for idx in filas_en_blanco:
            valor_original = columna_z.loc[idx]
            print(f"  Fila {idx + 1}: '{valor_original}'")
    else:
        print("No quedaron filas en blanco tras la normalización.")

    # Guardar solo la columna normalizada en el archivo de salida, sin encabezado ni índice
    print(f"Guardando columna Z normalizada en: {archivo_salida}")
    try:
        columna_z_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna Z normalizada."
        )
        print("Valores únicos normalizados:", columna_z_normalizada.unique())
        print("\nConteo de valores normalizados:")
        print(columna_z_normalizada.value_counts())
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


# Ejecutar la función
normalizar_columna_z(
    ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_Z, NUM_FILAS_A_SALTEAR
)
