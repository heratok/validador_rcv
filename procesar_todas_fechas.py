import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
ARCHIVO_ORIGINAL = "limpieza.xlsx"
ARCHIVO_SALIDA = "Todas_Fechas_Estandarizadas.xlsx"
NUM_FILAS_A_SALTEAR = 1

# Lista de índices de columnas de fechas a procesar
# Índices extraídos y validados de los scripts originales en la carpeta fechas/
INDICES_FECHAS = [
    7,
    23,
    27,
    29,
    43,
    45,
    47,
    49,
    51,
    53,
    58,
    59,
    61,
    64,
    66,
    68,
    74,
    76,
    80,
    82,
    84,
    86,
    88,
    90,
    92,
    94,
    96,
    98,
    100,
    104,
    108,
    119,
]

FECHAS_ESPECIALES = {"1800-01-01", "1845-01-01", "1845-01-02"}


def es_fecha_especial(valor):
    """Verifica si un valor es una fecha especial"""
    if isinstance(valor, str):
        try:
            datetime.strptime(valor, "%Y-%m-%d")
            return valor in FECHAS_ESPECIALES
        except Exception:
            return False
    return False


def convertir_fecha(valor):
    """Convierte cualquier formato de fecha al formato YYYY/MM/DD con manejo de comodines"""
    if pd.isnull(valor):
        return ""

    # Manejar comodines de texto
    if isinstance(valor, str):
        val = valor.strip().upper()
        if val == "NORMAL":
            return "1800/01/01"
        if val in ("NO APLICA", "SI"):
            return "1845/01/01"

    # Si ya es Timestamp o datetime, convertir directamente
    if isinstance(valor, (pd.Timestamp, datetime)):
        return valor.strftime("%Y/%m/%d")

    # Si es fecha especial, devolver con '/' como separador
    if es_fecha_especial(valor):
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            return fecha.strftime("%Y/%m/%d")
        except Exception:
            if isinstance(valor, str) and valor in FECHAS_ESPECIALES:
                return valor.replace("-", "/")
            return valor

    # Intentar DD/MM/YYYY
    if isinstance(valor, str):
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
        # Intentar YYYY-MM-DD HH:MM:SS
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")
            return fecha.strftime("%Y/%m/%d")
        except Exception:
            pass

    # Intentar número de serie Excel
    try:
        num = float(valor)
        fecha = pd.to_datetime(num - 2, unit="D", origin="1900-01-01", errors="raise")
        return fecha.strftime("%Y/%m/%d")
    except Exception:
        return ""


def procesar_todas_fechas(
    archivo_entrada, archivo_salida, columnas_fechas, filas_a_saltar
):
    print(f"Leyendo archivo: {archivo_entrada}")

    try:
        # Detectar el engine según la extensión
        ext = os.path.splitext(archivo_entrada)[1].lower()
        if ext == ".xlsb":
            df = pd.read_excel(
                archivo_entrada, header=None, skiprows=filas_a_saltar, engine="pyxlsb"
            )
        else:
            df = pd.read_excel(archivo_entrada, header=None, skiprows=filas_a_saltar)
        print(f"Datos cargados correctamente. Registros: {len(df)}\n")
    except FileNotFoundError:
        print(f"Error: El archivo '{archivo_entrada}' no se encontró.")
        return
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    # Leer los encabezados (primera fila del archivo original)
    try:
        if ext == ".xlsb":
            df_headers = pd.read_excel(
                archivo_entrada, header=None, skiprows=0, engine="pyxlsb", nrows=1
            )
        else:
            df_headers = pd.read_excel(
                archivo_entrada, header=None, skiprows=0, nrows=1
            )
        encabezados = df_headers.iloc[0].tolist()
    except Exception:
        encabezados = {}

    # Crear DataFrame de salida
    df_salida = pd.DataFrame()
    usados = set()

    # Procesar cada columna de fecha
    for indice in columnas_fechas:
        try:
            if indice >= len(df.columns):
                print(
                    f"  -> Error: Índice {indice} no existe (total: {len(df.columns)})"
                )
                continue

            col = df.iloc[:, indice]

            # Obtener el nombre del encabezado
            nombre_encabezado = ""
            if indice < len(encabezados):
                nombre_encabezado = str(encabezados[indice]).strip()

            print(f"Procesando columna índice {indice} - [{nombre_encabezado}]...")

            # Convertir todas las fechas
            fechas_convertidas = col.apply(convertir_fecha)

            # Registrar filas vacías o sin datos
            filas_vacias = [i for i, val in enumerate(fechas_convertidas) if val == ""]
            if filas_vacias:
                print(f"  ⚠ Advertencia: {len(filas_vacias)} filas quedaron en blanco")
                if len(filas_vacias) <= 20:
                    print(f"    Filas: {filas_vacias}")
                else:
                    print(f"    Primeras 20 filas: {filas_vacias[:20]}")
            else:
                print(
                    f"  ✓ Todas las {len(fechas_convertidas)} filas se convirtieron correctamente"
                )

            nombre_salida = (
                nombre_encabezado if nombre_encabezado else f"Fecha_{indice}"
            )
            # Evitar colisiones de nombres
            if nombre_salida in usados:
                nombre_salida = f"{nombre_salida}_{indice}"
            usados.add(nombre_salida)

            df_salida[nombre_salida] = fechas_convertidas
            print(f"  -> Índice {indice} completado (columna: {nombre_salida})")
        except Exception as e:
            print(f"  -> Error al procesar índice {indice}: {e}")

    # Guardar el archivo de salida
    print(f"\nGuardando archivo: {archivo_salida}")
    try:
        df_salida.to_excel(archivo_salida, index=False, header=True)
        print(
            "¡Proceso completado! Todas las fechas han sido estandarizadas en formato YYYY/MM/DD"
        )
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")


if __name__ == "__main__":
    procesar_todas_fechas(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICES_FECHAS, NUM_FILAS_A_SALTEAR
    )
