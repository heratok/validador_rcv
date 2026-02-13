import pandas as pd

# --- CONFIGURACIÓN DE ARCHIVOS Y COLUMNAS ---
ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_N_Normalizada.xlsx"
INDICE_COLUMNA_N = 13  # Columna N es la número 14, índice 13 en Python
NUM_FILAS_A_SALTEAR = 3  # Saltar las primeras 3 filas, datos desde la fila 4

# Diccionario de normalización
MAPEO_N = {
    # Comunidades Indígenas
    "comunidades  indígenas": "Comunidades Indígenas",
    "comunidades indigenas": "Comunidades Indígenas",
    # Discapacitados
    "discapacitados": "Discapacitados",
    # Víctimas del Conflicto Armado
    "víctima del conflicto aramdo interno": "Víctimas del Conflicto Armado",
    "víctima del conflicto armado interno": "Víctimas del Conflicto Armado",
    # Desmovilizados
    "desplazados": "Desmovilizados",
    # Adulto Mayor
    "adulto mayor": "Adulto Mayor",
}

import unicodedata
import re

# Diccionario de variantes (palabras clave a buscar, resultado)
VARIANTES = [
    (["comunidades indigenas"], "Comunidades Indígenas"),
    (["discapacitados"], "Discapacitados"),
    (["victima del conflicto", "armado"], "Víctimas del Conflicto Armado"),
    (["desplazados"], "Desmovilizados"),
    (["adulto mayor"], "Adulto Mayor"),
    (["madres comunitarias"], "Mujer Cabeza de Hogar"),
    (
        [
            "poblacion con sisben",
            "habitante de calle",
            "migrante venezolano",
            "artista y compusitores",
            "cabeza de familia",
            "trajador rural",
            "poblacion rural migratoria",
            "trajador urbano",
            "otro grupo poblacional",
            "afiliacion de oficio sin encuesta sisben",
            "migrante colombiano repatriado",
            "jovenes vulnerables urbano",
            "poblacion rural no migratoria",
            "mujer embarazada",
        ],
        "Otro Grupo Poblacional",
    ),
]


def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    # Quitar tildes, pasar a minúsculas, quitar dobles espacios
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.strip()
    return texto


def buscar_variante(valor):
    t = normalizar_texto(valor)
    for claves, resultado in VARIANTES:
        for clave in claves:
            if all(pal in t for pal in clave.split()):
                return resultado
    return ""


def normalizar_columna_n(
    archivo_entrada, archivo_salida, indice_columna_n, filas_a_saltar
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

    # Obtener la columna N
    nombre_columna_n = df.columns[indice_columna_n]
    columna_n = df[nombre_columna_n]

    # Normalizar valores
    columna_n_normalizada = columna_n.apply(buscar_variante)

    # Log de filas en blanco y su valor original
    filas_en_blanco = columna_n_normalizada[columna_n_normalizada == ""].index.tolist()
    if filas_en_blanco:
        print(
            "Advertencia: Las siguientes filas quedaron en blanco tras la normalización:"
        )
        for idx in filas_en_blanco:
            valor_original = columna_n.loc[idx]
            print(f"  Fila {idx + 1}: '{valor_original}'")
    else:
        print("No quedaron filas en blanco tras la normalización.")

    # Guardar solo la columna normalizada en el archivo de salida, sin encabezado ni índice
    print(f"Guardando columna N normalizada en: {archivo_salida}")
    try:
        columna_n_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna N normalizada."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


# Ejecutar la función
normalizar_columna_n(
    ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_N, NUM_FILAS_A_SALTEAR
)
