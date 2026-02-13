import pandas as pd
import unicodedata
import re

# --- CONFIGURACIÓN DE ARCHIVOS Y COLUMNAS ---
ARCHIVO_ORIGINAL = "../BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_M_Normalizada.xlsx"
INDICE_COLUMNA_M = 12  # Columna M es la número 13, índice 12 en Python
NUM_FILAS_A_SALTEAR = 3  # Saltar las primeras 3 filas, datos desde la fila 4

# Función para normalizar texto: quita tildes, pasa a minúsculas, elimina espacios extra


def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.strip()
    return texto


# Función de normalización con coincidencias parciales


def normalizar_etnia(valor):
    t = normalizar_texto(valor)
    if any(x in t for x in ["negro", "afro", "mulato"]):
        return "Negro(a)/Afroamericano"
    if "indigena" in t:
        return "Indígena"
    if "rom" in t or "gitano" in t:
        return "ROM (Gitano)"
    if "raizal" in t:
        return "Raizal"
    if "mestizo" in t:
        return "Mestizo"
    if "ninguna" in t:
        return "Ninguna"
    return "Ninguna"


def normalizar_columna_m(
    archivo_entrada, archivo_salida, indice_columna_m, filas_a_saltar
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

    nombre_columna_m = df.columns[indice_columna_m]
    columna_m = df[nombre_columna_m]

    columna_m_normalizada = columna_m.apply(normalizar_etnia)

    print("Valores únicos normalizados:", columna_m_normalizada.unique())
    print("\nConteo de valores normalizados:")
    print(columna_m_normalizada.value_counts())

    print(f"Guardando columna M normalizada en: {archivo_salida}")
    try:
        columna_m_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna M normalizada."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


# Ejecutar la función
normalizar_columna_m(
    ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_M, NUM_FILAS_A_SALTEAR
)
