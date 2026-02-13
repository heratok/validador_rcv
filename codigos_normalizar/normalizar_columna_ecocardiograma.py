import pandas as pd
import unicodedata
import re

ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "./ECOCARDIOGRAMA_NORMALIZADO.xlsx"
NUM_FILAS_A_SALTEAR = 3  # Saltar las primeras 3 filas, datos desde la fila 4
INDICE_COL_ECO = 67  # Columna 'ECOCARDIOGRAMA'


# Función para normalizar texto
def normalizar_texto(texto):
    if pd.isna(texto) or texto == 0:
        return "SIN DATO"
    if isinstance(texto, str):
        # Quitar tildes, espacios extra y pasar a minúsculas
        texto = unicodedata.normalize("NFKD", texto)
        texto = "".join([c for c in texto if not unicodedata.combining(c)])
        texto = texto.strip().lower()
        texto = re.sub(r"\s+", " ", texto)
        # Normalizar variantes de 'normal'
        if "normal" in texto:
            return "Normal"
    return "Anormal"


def normalizar_columna_ecocardiograma(
    archivo_entrada, indice_col, filas_a_saltar, archivo_salida
):
    print(f"Leyendo archivo: {archivo_entrada}")
    df = pd.read_excel(
        archivo_entrada, header=None, skiprows=filas_a_saltar, engine="pyxlsb"
    )
    nombre_col = df.columns[indice_col]
    col = df[nombre_col]
    print(f"Normalizando columna {indice_col}: '{nombre_col}'")
    df["ECOCARDIOGRAMA_NORMALIZADO"] = col.apply(normalizar_texto)
    print("Valores únicos normalizados:", df["ECOCARDIOGRAMA_NORMALIZADO"].unique())
    print(
        f"Total de valores únicos normalizados: {len(df['ECOCARDIOGRAMA_NORMALIZADO'].unique())}"
    )
    df[[nombre_col, "ECOCARDIOGRAMA_NORMALIZADO"]].to_excel(archivo_salida, index=False)
    print(f"Archivo de salida generado: {archivo_salida}")


if __name__ == "__main__":
    normalizar_columna_ecocardiograma(
        ARCHIVO_ORIGINAL, INDICE_COL_ECO, NUM_FILAS_A_SALTEAR, ARCHIVO_SALIDA
    )
