import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE ARCHIVOS Y COLUMNAS ---
ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Fechas_AZ_Estandarizadas.xlsx"
INDICE_COLUMNA_FECHA = 51  # Columna AZ es la número 52, índice 51 en Python
NUM_FILAS_A_SALTEAR = 2  # Saltar las primeras 2 filas, datos desde la fila 3

FECHAS_ESPECIALES = {"1800-01-01", "1845-01-01"}


def es_fecha_especial(valor):
    if isinstance(valor, str):
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            return valor in FECHAS_ESPECIALES
        except Exception:
            return False
    return False


def convertir_o_dejar(valor):
    if pd.isnull(valor):
        return ""
    # Si el valor es 'NORMAL', devolver el comodín especial
    if isinstance(valor, str) and valor.strip().upper() == "NORMAL":
        return "1800/01/01"
    # Si ya es fecha especial en texto, devolverla con formato YYYY/MM/DD
    if es_fecha_especial(valor):
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            return fecha.strftime("%Y/%m/%d")
        except Exception:
            return valor
    # Si es string tipo fecha pero no especial, intentar primero DD/MM/YYYY
    if isinstance(valor, str):
        # Intentar DD/MM/YYYY
        try:
            fecha = datetime.strptime(valor, "%d/%m/%Y")
            return fecha.strftime("%Y/%m/%d")
        except Exception:
            pass
        # Intentar YYYY-MM-DD
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            return fecha.strftime("%Y/%m/%d")
        except Exception:
            pass
    # Si es número, convertir a fecha Excel corrigiendo el desfase de 2 días
    try:
        num = float(valor)
        fecha = pd.to_datetime(num - 2, unit="D", origin="1900-01-01", errors="raise")
        fecha_str = fecha.strftime("%Y/%m/%d")
        return fecha_str
    except Exception:
        return None  # Para loguear después


def estandarizar_formato_fecha_az(
    archivo_entrada, archivo_salida, indice_columna_fecha, filas_a_saltar
):
    print(f"Iniciando la lectura del archivo: {archivo_entrada}")
    df = pd.read_excel(
        archivo_entrada, header=None, skiprows=filas_a_saltar, engine="pyxlsb"
    )
    print(f"Datos cargados correctamente. Registros: {len(df)}")
    nombre_columna_fecha = df.columns[indice_columna_fecha]
    print(
        f"Corrigiendo la Columna AZ (índice {nombre_columna_fecha}) de números de serie a fechas..."
    )
    columna = df[nombre_columna_fecha]
    fechas_final = []
    errores = []
    for idx, valor in columna.items():
        resultado = convertir_o_dejar(valor)
        if resultado is None:
            errores.append((idx + 1, valor))
            fechas_final.append("")
        else:
            fechas_final.append(resultado)
    # Log de errores
    if errores:
        print("Advertencia: No se pudo convertir los siguientes valores:")
        for fila, valor in errores:
            print(f"  Fila {fila}: '{valor}'")
    else:
        print("Todas las fechas fueron convertidas correctamente o son especiales.")
    # Guardar solo la columna de fechas convertidas en el archivo de salida
    print(f"Guardando solo la columna de fechas estandarizadas en: {archivo_salida}")
    try:
        pd.Series(fechas_final).to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna de fechas en formato YYYY/MM/DD o fechas especiales."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


if __name__ == "__main__":
    estandarizar_formato_fecha_az(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_FECHA, NUM_FILAS_A_SALTEAR
    )
