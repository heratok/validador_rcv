import pandas as pd
from datetime import datetime

ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Fechas_AT_Estandarizadas.xlsx"
INDICE_COLUMNA_FECHA = 45  # Columna AT es la número 46, índice 45
NUM_FILAS_A_SALTEAR = 2

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
    if isinstance(valor, str) and valor.strip().upper() == "NORMAL":
        return "1800/01/01"
    if es_fecha_especial(valor):
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            return fecha.strftime("%Y/%m/%d")
        except Exception:
            return valor
    if isinstance(valor, str):
        try:
            fecha = datetime.strptime(valor, "%d/%m/%Y")
            return fecha.strftime("%Y/%m/%d")
        except Exception:
            pass
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            return fecha.strftime("%Y/%m/%d")
        except Exception:
            pass
    try:
        num = float(valor)
        fecha = pd.to_datetime(num - 2, unit="D", origin="1900-01-01", errors="raise")
        fecha_str = fecha.strftime("%Y/%m/%d")
        return fecha_str
    except Exception:
        return None


def estandarizar_formato_fecha_at(
    archivo_entrada, archivo_salida, indice_columna_fecha, filas_a_saltar
):
    print(f"Iniciando la lectura del archivo: {archivo_entrada}")
    df = pd.read_excel(
        archivo_entrada, header=None, skiprows=filas_a_saltar, engine="pyxlsb"
    )
    print(f"Datos cargados correctamente. Registros: {len(df)}")
    nombre_columna_fecha = df.columns[indice_columna_fecha]
    print(
        f"Corrigiendo la Columna AT (índice {nombre_columna_fecha}) de números de serie a fechas..."
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
    if errores:
        print("Advertencia: No se pudo convertir los siguientes valores:")
        for fila, valor in errores:
            print(f"  Fila {fila}: '{valor}'")
    else:
        print("Todas las fechas fueron convertidas correctamente o son especiales.")
    print(f"Guardando solo la columna de fechas estandarizadas en: {archivo_salida}")
    try:
        pd.Series(fechas_final).to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna de fechas en formato YYYY/MM/DD o fechas especiales."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


if __name__ == "__main__":
    estandarizar_formato_fecha_at(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_FECHA, NUM_FILAS_A_SALTEAR
    )
