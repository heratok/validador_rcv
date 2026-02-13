import pandas as pd
import unicodedata
import re

# --- CONFIGURACIÓN DE ARCHIVOS Y COLUMNAS ---
ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "AQ_AS_Normalizadas.xlsx"
INDICE_COLUMNA_AQ = 42  # Columna AQ es la número 43, índice 42 en Python
INDICE_COLUMNA_AS = 44  # Columna AS es la número 45, índice 44 en Python
NUM_FILAS_A_SALTEAR = 3  # Saltar las primeras 3 filas, datos desde la fila 4

MAPEO_RIESGO = {
    "riesgo alto": "Riesgo Alto",
    "riesgo muy alto": "Riesgo Alto",
    "riesgo bajo": "Riesgo Bajo",
    "riesgo moderado": "Riesgo Moderado",
    "no se clasifico": "No se Clasifico",
    "no se clasifco": "No se Clasifico",
    "no se clasificado": "No se Clasifico",
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


def normalizar_riesgo(valor):
    t = normalizar_texto(valor)
    # Quitar espacios finales
    t = t.rstrip()
    # Unificar variantes con espacios
    t = t.replace("  ", " ")
    return MAPEO_RIESGO.get(t, "")


def normalizar_columnas_aq_as(
    archivo_entrada, archivo_salida, indice_col_aq, indice_col_as, filas_a_saltar
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

    # AQ
    nombre_col_aq = df.columns[indice_col_aq]
    col_aq = df[nombre_col_aq]
    col_aq_norm = col_aq.apply(normalizar_riesgo)
    # AS
    nombre_col_as = df.columns[indice_col_as]
    col_as = df[nombre_col_as]
    col_as_norm = col_as.apply(normalizar_riesgo)

    # Log de filas en blanco y su valor original AQ
    filas_blanco_aq = col_aq_norm[col_aq_norm == ""].index.tolist()
    if filas_blanco_aq:
        print(
            "\nAdvertencia: Las siguientes filas de AQ quedaron en blanco tras la normalización:"
        )
        for idx in filas_blanco_aq:
            print(f"  Fila {idx + 1}: '{col_aq.loc[idx]}'")
    else:
        print("\nNo quedaron filas en blanco en AQ tras la normalización.")

    # Log de filas en blanco y su valor original AS
    filas_blanco_as = col_as_norm[col_as_norm == ""].index.tolist()
    if filas_blanco_as:
        print(
            "\nAdvertencia: Las siguientes filas de AS quedaron en blanco tras la normalización:"
        )
        for idx in filas_blanco_as:
            print(f"  Fila {idx + 1}: '{col_as.loc[idx]}'")
    else:
        print("\nNo quedaron filas en blanco en AS tras la normalización.")

    # Guardar ambas columnas normalizadas en un archivo Excel
    df_salida = pd.DataFrame(
        {"AQ_Normalizada": col_aq_norm, "AS_Normalizada": col_as_norm}
    )
    print(f"\nGuardando columnas normalizadas en: {archivo_salida}")
    try:
        df_salida.to_excel(archivo_salida, index=False, header=True)
        print(
            "¡Proceso completado! Archivo de salida creado con ambas columnas normalizadas."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


# Ejecutar la función
normalizar_columnas_aq_as(
    ARCHIVO_ORIGINAL,
    ARCHIVO_SALIDA,
    INDICE_COLUMNA_AQ,
    INDICE_COLUMNA_AS,
    NUM_FILAS_A_SALTEAR,
)
