import pandas as pd

# --- CONFIGURACIÓN DE ARCHIVOS Y COLUMNAS ---
ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Columna_K_Normalizada.xlsx"
INDICE_COLUMNA_K = 10  # Columna K es la número 11, índice 10 en Python
NUM_FILAS_A_SALTEAR = 3  # Saltar las primeras 3 filas, datos desde la fila 4


def normalizar_columna_k(
    archivo_entrada, archivo_salida, indice_columna_k, filas_a_saltar
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

    # Obtener la columna K
    nombre_columna_k = df.columns[indice_columna_k]
    columna_k = df[nombre_columna_k].astype(str)

    # Normalizar valores
    columna_k_normalizada = columna_k.replace(
        {"FEMENINO": "Femenino", "MASCULINO": "Masculino"}
    )

    # Guardar solo la columna normalizada en el archivo de salida, sin encabezado ni índice
    print(f"Guardando columna K normalizada en: {archivo_salida}")
    try:
        columna_k_normalizada.to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna K normalizada."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


# Ejecutar la función
dormalizar_columna_k = normalizar_columna_k  # alias para evitar error de tipeo
normalizar_columna_k(
    ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_K, NUM_FILAS_A_SALTEAR
)
