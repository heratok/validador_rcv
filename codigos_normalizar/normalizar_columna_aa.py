import pandas as pd
import unicodedata
import re

# --- CONFIGURACIÓN DE ARCHIVOS Y COLUMNAS ---
ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_AA_Normalizada.xlsx"
INDICE_COLUMNA_AA = 26  # Columna AA es la número 27, índice 26 en Python
NUM_FILAS_A_SALTEAR = 3  # Saltar las primeras 3 filas, datos desde la fila 4

MAPEO_AA = {
    "si": "Si",
    "sí": "Si",
    "no": "No",
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


def normalizar_aa(valor):
    t = normalizar_texto(valor)
    return MAPEO_AA.get(t, "")


def normalizar_columna_aa(
    archivo_entrada, archivo_salida, indice_columna_aa, filas_a_saltar
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

    # Obtener la columna AA
    nombre_columna_aa = df.columns[indice_columna_aa]
    columna_aa = df[nombre_columna_aa]

    # Normalizar valores
    columna_aa_normalizada = columna_aa.apply(normalizar_aa)

    # Log de filas en blanco y su valor original
    filas_en_blanco = columna_aa_normalizada[
        columna_aa_normalizada == ""
    ].index.tolist()
    if filas_en_blanco:
        print(
            "Advertencia: Las siguientes filas quedaron en blanco tras la normalización:"
        )
        for idx in filas_en_blanco:
            valor_original = columna_aa.loc[idx]
            print(f"  Fila {idx + 1}: '{valor_original}'")
    else:
        print("No quedaron filas en blanco tras la normalización.")

    # Guardar solo la columna normalizada en el archivo de salida, sin encabezado ni índice
    print(f"Guardando columna AA normalizada en: {archivo_salida}")
    try:
        columna_aa_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna AA normalizada."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


# Ejecutar la función
normalizar_columna_aa(
    ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_AA, NUM_FILAS_A_SALTEAR
)
