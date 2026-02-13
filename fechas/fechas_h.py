import pandas as pd
import os

# --- CONFIGURACIÓN DE ARCHIVOS Y COLUMNAS ---
# 1. Nombre de tu archivo de Excel original (.xlsb requiere 'pyxlsb')
ARCHIVO_ORIGINAL = "limpieza.xlsx"

# 2. Nombre del nuevo archivo de Excel para verificar los resultados
ARCHIVO_SALIDA = "Fechas_H_Estandarizadas_Prueba_5_Registros.xlsx"

# 3. La columna H es la octava columna, su índice en Python/Pandas es 7 (contando desde 0)
INDICE_COLUMNA_FECHA = 7

# 4. Los datos comienzan en la fila 4 de Excel, por lo que saltamos las 3 primeras filas.
NUM_FILAS_A_SALTEAR = 2

# --- FUNCIÓN PRINCIPAL ---


def estandarizar_formato_fecha(
    archivo_entrada, archivo_salida, indice_columna_fecha, filas_a_saltar
):
    print(f"Iniciando la lectura del archivo: {archivo_entrada}")

    try:
        # Detectar el engine según la extensión
        ext = os.path.splitext(archivo_entrada)[1].lower()
        if ext == ".xlsb":
            df = pd.read_excel(
                archivo_entrada, header=None, skiprows=filas_a_saltar, engine="pyxlsb"
            )
        else:
            df = pd.read_excel(archivo_entrada, header=None, skiprows=filas_a_saltar)
        print(f"Datos cargados correctamente. Registros: {len(df)}")

    except FileNotFoundError:
        print(
            f"Error: El archivo '{archivo_entrada}' no se encontró en la carpeta actual."
        )
        return
    except ImportError:
        print(
            "Error: Asegúrate de instalar 'pyxlsb' (pip install pyxlsb) para leer archivos .xlsb."
        )
        return
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")
        return

    # --- MODIFICACIÓN: LIMITAR A LOS PRIMEROS 5 REGISTROS DE DATOS ---
    # df = df.head(5)
    # print(
    #    f"Limitando el procesamiento a los primeros {len(df)} registros para la prueba."
    # )

    # 1. Identificar el nombre (índice numérico) de la Columna H
    nombre_columna_fecha = df.columns[indice_columna_fecha]

    # --- PASO CRÍTICO: CONVERTIR NÚMEROS DE SERIE DE EXCEL A FECHAS ---
    # 2. Convertir la columna de números de serie (int64) a tipo de dato 'datetime'.
    print(
        f"Corrigiendo la Columna H (índice {nombre_columna_fecha}) de números de serie a fechas..."
    )
    # Intentar primero DD/MM/YYYY, luego YYYY-MM-DD, luego número de serie Excel
    fechas_convertidas = []
    for valor in df[nombre_columna_fecha]:
        if pd.isnull(valor):
            fechas_convertidas.append("")
            continue
        # Si ya es Timestamp, convertir directamente
        if isinstance(valor, pd.Timestamp):
            fechas_convertidas.append(valor.strftime("%Y/%m/%d"))
            continue
        # Intentar DD/MM/YYYY
        if isinstance(valor, str):
            try:
                fecha = pd.to_datetime(valor, format="%d/%m/%Y", errors="raise")
                fechas_convertidas.append(fecha.strftime("%Y/%m/%d"))
                continue
            except Exception:
                pass
            # Intentar YYYY-MM-DD
            try:
                fecha = pd.to_datetime(valor, format="%Y-%m-%d", errors="raise")
                fechas_convertidas.append(fecha.strftime("%Y/%m/%d"))
                continue
            except Exception:
                pass
        # Intentar número de serie Excel (corrigiendo desfase de 2 días)
        try:
            num = float(valor)
            fecha = pd.to_datetime(
                num - 2, unit="D", origin="1900-01-01", errors="raise"
            )
            fechas_convertidas.append(fecha.strftime("%Y/%m/%d"))
            continue
        except Exception:
            fechas_convertidas.append("")
    df["FECHA_CONVERTIDA"] = fechas_convertidas

    # 3. Guardar solo la columna de fechas convertidas en el archivo de salida
    print(f"Guardando solo la columna de fechas estandarizadas en: {archivo_salida}")
    try:
        # Guardar solo esa columna, sin encabezado ni índice
        df["FECHA_CONVERTIDA"].to_excel(archivo_salida, index=False, header=False)
        print(
            "¡Proceso completado! Archivo de salida creado solo con la columna de fechas en formato YYYY/MM/DD."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


# Ejecutar la función
estandarizar_formato_fecha(
    ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_COLUMNA_FECHA, NUM_FILAS_A_SALTEAR
)
