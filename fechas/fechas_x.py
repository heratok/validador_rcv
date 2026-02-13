import pandas as pd
from datetime import datetime
import os
import sys
import subprocess

# --- CONFIGURACIÓN DE ARCHIVOS Y COLUMNAS ---
ARCHIVO_ORIGINAL = "./limpieza.xlsx"
ARCHIVO_SALIDA = "Fechas_X_Estandarizadas.xlsx"
INDICE_COLUMNA_FECHA = 23  # Columna X es la número 24, índice 23 en Python
NUM_FILAS_A_SALTEAR = 1  # Saltar las primeras 2 filas, datos desde la fila 3

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
    # Si es datetime o pd.Timestamp, convertir directamente
    if isinstance(valor, (datetime, pd.Timestamp)):
        return valor.strftime("%Y/%m/%d")
    if es_fecha_especial(valor):
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            return fecha.strftime("%Y/%m/%d")
        except Exception:
            return valor
    if isinstance(valor, str):
        # Intentar varios formatos
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                fecha = datetime.strptime(valor, fmt)
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


def estandarizar_formato_fecha_x(
    archivo_entrada, archivo_salida, indice_columna_fecha, filas_a_saltar
):
    print(f"Iniciando la lectura del archivo: {archivo_entrada}")
    ext = os.path.splitext(archivo_entrada)[1].lower()
    engine = None
    if ext == ".xlsb":
        engine = "pyxlsb"
        try:
            import pyxlsb
        except ImportError:
            print("pyxlsb no está instalado. Instalando automáticamente...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyxlsb"])
            import pyxlsb
    elif ext == ".xlsx":
        engine = "openpyxl"
    try:
        df = pd.read_excel(
            archivo_entrada, header=None, skiprows=filas_a_saltar, engine=engine
        )
        print(f"Datos cargados correctamente. Registros: {len(df)}")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return
    nombre_columna_fecha = df.columns[indice_columna_fecha]
    print(
        f"Corrigiendo la Columna X (índice {nombre_columna_fecha}) de números de serie a fechas..."
    )
    columna = df[nombre_columna_fecha]
    print("Primeros 10 valores de la columna:")
    print(columna.head(10).tolist())
    fechas_final = []
    errores = []
    for idx, valor in columna.items():
        resultado = convertir_o_dejar(valor)
        if resultado is None:
            errores.append((idx + 1, valor))
            fechas_final.append("")
        else:
            fechas_final.append(resultado)
    print(
        f"Total valores convertidos: {len([f for f in fechas_final if f])} de {len(fechas_final)}"
    )
    if errores:
        print("Advertencia: No se pudo convertir los siguientes valores:")
        for fila, valor in errores[:10]:
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
    estandarizar_formato_fecha_x(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_FECHA, NUM_FILAS_A_SALTEAR
    )
