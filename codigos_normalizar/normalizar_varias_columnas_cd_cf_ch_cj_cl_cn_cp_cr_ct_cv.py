import pandas as pd
import unicodedata
import re

ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columnas_Normalizadas_CD_CF_CH_CJ_CL_CN_CP_CR_CT_CV.xlsx"
NUM_FILAS_A_SALTEAR = 3
# Letras y sus índices
columnas_letras = ["CD", "CF", "CH", "CJ", "CL", "CN", "CP", "CR", "CT", "CV"]


def letra_a_indice(letra):
    base = ord("A")
    if len(letra) == 1:
        return ord(letra) - base
    else:
        return (ord(letra[0]) - base + 1) * 26 + (ord(letra[1]) - base)


columnas_indices = [letra_a_indice(letra) for letra in columnas_letras]

# Normalización robusta


def normalizar_texto(val):
    if pd.isnull(val):
        return "SIN DATO"
    t = str(val)
    t = unicodedata.normalize("NFKD", t)
    t = "".join([c for c in t if not unicodedata.combining(c)])
    t = t.upper()
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    # Fechas especiales
    if t in ["1800-01-01", ""]:
        return "SIN DATO"
    if t == "1845-01-01":
        return "NO APLICA"
    # MEDICO Y ENFERMERIA (prioridad)
    if (
        "MEDICO Y ENFERMERIA" in t
        or "MEDICO Y ENFERMERA" in t
        or "MEDICO ENFERMERA" in t
    ):
        return "MEDICO Y ENFERMERIA"
    # ENFERMERIA
    if "ENFERMERIA" in t or "ENFERMERA" in t:
        return "ENFERMERIA"
    # MEDICO GENERAL
    if t in ["MEDICO GRAL", "MEDICINA GRAL", "MEDICO GENERAL"]:
        return "MEDICO GENERAL"
    if "MEDICO GRAL" in t or "MEDICINA GRAL" in t or "MEDICO GENERAL" in t:
        return "MEDICO GENERAL"
    # MEDICO INTERNISTA
    if "INTERNISTA" in t or "NEFROLOGIA" in t:
        return "MEDICO INTERNISTA"
    # NUTRICIONISTA
    if "NUTRICIONISTA" in t:
        return "NUTRICIONISTA"
    # PSICOLOGIA
    if "PSICOLOGIA" in t:
        return "PSICOLOGIA"
    # NO APLICA
    if t == "NO APLICA":
        return "NO APLICA"
    return "SIN DATO"


def normalizar_varias_columnas(
    archivo_entrada, archivo_salida, columnas_indices, filas_a_saltar
):
    print(f"Iniciando la lectura del archivo: {archivo_entrada}")
    df = pd.read_excel(
        archivo_entrada, header=None, skiprows=filas_a_saltar, engine="pyxlsb"
    )
    df_salida = pd.DataFrame()
    for letra, idx in zip(columnas_letras, columnas_indices):
        nombre_columna = df.columns[idx]
        columna = df[nombre_columna]
        columna_normalizada = columna.apply(normalizar_texto)
        print(
            f"\nColumna {letra} normalizada. Valores únicos:",
            columna_normalizada.unique(),
        )
        print("Conteo:", columna_normalizada.value_counts())
        df_salida[f"{letra}_Normalizada"] = columna_normalizada
    print(f"\nGuardando columnas normalizadas en: {archivo_salida}")
    try:
        df_salida.to_excel(archivo_salida, index=False, header=True)
        print(
            "¡Proceso completado! Archivo de salida creado con todas las columnas normalizadas."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


if __name__ == "__main__":
    normalizar_varias_columnas(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, columnas_indices, NUM_FILAS_A_SALTEAR
    )
