import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
ARCHIVO_ORIGINAL = "./rcv_cesar.xlsx"
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
    102,
    104,
    108,
    119,
    123,
]

FECHAS_ESPECIALES = {"1800-01-01", "1845-01-01", "1845-01-02"}


def detectar_fecha_especial(valor):
    """Detecta si un valor es una fecha especial en cualquier formato y retorna su tipo"""
    if pd.isnull(valor):
        return None
    
    fecha_parseada = None
    
    # Si ya es Timestamp o datetime
    if isinstance(valor, (pd.Timestamp, datetime)):
        try:
            # Intentar convertir a fecha string, si falla no es fecha válida
            fecha_parseada = valor
        except Exception:
            return None
    
    # Intentar parsear string en diferentes formatos
    if isinstance(valor, str):
        for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]:
            try:
                fecha_parseada = datetime.strptime(valor, fmt)
                break
            except Exception:
                continue
    
    # Intentar número de serie Excel (solo si es un número razonable para fechas)
    if not fecha_parseada and not isinstance(valor, (pd.Timestamp, datetime)):
        try:
            num = float(valor)
            # Validar rango razonable para fechas Excel (entre 1900 y 2100 aprox)
            if 0 < num < 100000:
                fecha_parseada = pd.to_datetime(num - 2, unit="D", origin="1900-01-01", errors="raise")
        except Exception:
            pass
    
    # Verificar si la fecha parseada es especial
    if fecha_parseada:
        try:
            fecha_str = fecha_parseada.strftime("%Y-%m-%d")
            if fecha_str == "1800-01-01":
                return "SINDATO"
            elif fecha_str in ["1845-01-01", "1845-01-02"]:
                return "NO APLICA"
        except (ValueError, OSError):
            # strftime falla para fechas fuera de rango - no es fecha especial
            return None
    
    return None


def limpiar_valor_no_fecha(valor):
    """Limpia valores en columnas que NO son de fechas, reemplazando fechas especiales por texto"""
    tipo_especial = detectar_fecha_especial(valor)
    if tipo_especial:
        return tipo_especial
    return valor


def convertir_fecha(valor):
    """Convierte cualquier formato de fecha al formato YYYY/MM/DD con manejo de comodines.
    Los valores vacíos se convierten a 1800/01/01 (SINDATO)"""
    if pd.isnull(valor):
        return "1800/01/01"

    # Manejar comodines de texto
    if isinstance(valor, str):
        val = valor.strip().upper()
        if val == "NORMAL":
            return "1800/01/01"
        if val in ("NO APLICA", "SI"):
            return "1845/01/01"

    # Si ya es Timestamp o datetime, verificar si es fecha especial
    if isinstance(valor, (pd.Timestamp, datetime)):
        fecha_str = valor.strftime("%Y-%m-%d")
        if fecha_str in FECHAS_ESPECIALES:
            return valor.strftime("%Y/%m/%d")
        return valor.strftime("%Y/%m/%d")

    # Intentar parsear en diferentes formatos y verificar si es fecha especial
    fecha_parseada = None
    
    # Intentar DD/MM/YYYY
    if isinstance(valor, str):
        try:
            fecha_parseada = datetime.strptime(valor, "%d/%m/%Y")
        except Exception:
            pass
    
    # Intentar DD-MM-YYYY
    if isinstance(valor, str) and not fecha_parseada:
        try:
            fecha_parseada = datetime.strptime(valor, "%d-%m-%Y")
        except Exception:
            pass
    
    # Intentar YYYY/MM/DD
    if isinstance(valor, str) and not fecha_parseada:
        try:
            fecha_parseada = datetime.strptime(valor, "%Y/%m/%d")
        except Exception:
            pass
    
    # Intentar YYYY-MM-DD
    if isinstance(valor, str) and not fecha_parseada:
        try:
            fecha_parseada = datetime.strptime(valor, "%Y-%m-%d")
        except Exception:
            pass
    
    # Intentar YYYY-MM-DD HH:MM:SS
    if isinstance(valor, str) and not fecha_parseada:
        try:
            fecha_parseada = datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    # Si se parseó exitosamente, verificar si es fecha especial y devolver
    if fecha_parseada:
        fecha_str = fecha_parseada.strftime("%Y-%m-%d")
        if fecha_str in FECHAS_ESPECIALES:
            return fecha_parseada.strftime("%Y/%m/%d")
        return fecha_parseada.strftime("%Y/%m/%d")

    # Intentar número de serie Excel
    try:
        num = float(valor)
        fecha = pd.to_datetime(num - 2, unit="D", origin="1900-01-01", errors="raise")
        fecha_str = fecha.strftime("%Y-%m-%d")
        if fecha_str in FECHAS_ESPECIALES:
            return fecha.strftime("%Y/%m/%d")
        return fecha.strftime("%Y/%m/%d")
    except Exception:
        # Si no se pudo convertir, usar fecha SINDATO
        return "1800/01/01"


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

    # Crear DataFrame de salida con todas las columnas
    df_salida = pd.DataFrame()
    usados = set()
    
    # Convertir columnas_fechas a set para búsqueda rápida
    indices_fechas_set = set(columnas_fechas)

    # Procesar TODAS las columnas
    print(f"Total de columnas a procesar: {len(df.columns)}\n")
    
    for indice in range(len(df.columns)):
        col = df.iloc[:, indice]

        # Obtener el nombre del encabezado
        nombre_encabezado = ""
        if indice < len(encabezados):
            nombre_encabezado = str(encabezados[indice]).strip()

        # Determinar si es columna de fecha
        es_columna_fecha = indice in indices_fechas_set
        tipo_col = "FECHA" if es_columna_fecha else "DATO"
        
        print(f"[{tipo_col}] Procesando columna {indice} - [{nombre_encabezado}]...")

        try:
            # Procesar según el tipo de columna
            if es_columna_fecha:
                # Convertir fechas al formato YYYY/MM/DD
                col_procesada = col.apply(convertir_fecha)
                
                # Registrar filas vacías o sin datos
                filas_vacias = [i for i, val in enumerate(col_procesada) if val == ""]
                if filas_vacias:
                    print(f"  ⚠ Advertencia: {len(filas_vacias)} filas quedaron en blanco")
                    if len(filas_vacias) <= 10:
                        print(f"    Filas: {filas_vacias}")
                else:
                    print(f"  ✓ Todas las filas se convirtieron correctamente")
            else:
                # Limpiar fechas especiales en columnas que NO son de fechas
                col_procesada = col.apply(limpiar_valor_no_fecha)
                
                # Contar cuántas fechas especiales se limpiaron
                cambios = sum(1 for i in range(len(col)) if col.iloc[i] != col_procesada.iloc[i])
                if cambios > 0:
                    print(f"  ✓ Se limpiaron {cambios} fechas especiales")
                else:
                    print(f"  ✓ Sin fechas especiales detectadas")
        except Exception as e:
            print(f"  ⚠ Error al procesar: {e}")
            print(f"  → Guardando columna sin modificar")
            col_procesada = col

        nombre_salida = (
            nombre_encabezado if nombre_encabezado else f"Columna_{indice}"
        )
        # Evitar colisiones de nombres
        if nombre_salida in usados:
            nombre_salida = f"{nombre_salida}_{indice}"
        usados.add(nombre_salida)

        df_salida[nombre_salida] = col_procesada
        print(f"  -> Columna {indice} completada\n")

    # Guardar el archivo de salida
    print(f"\nGuardando archivo: {archivo_salida}")
    try:
        df_salida.to_excel(archivo_salida, index=False, header=True)
        print(
            "¡Proceso completado!\n"
            "- Columnas de fechas estandarizadas en formato YYYY/MM/DD\n"
            "- Fechas especiales en columnas no-fecha convertidas a texto"
        )
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")


if __name__ == "__main__":
    procesar_todas_fechas(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICES_FECHAS, NUM_FILAS_A_SALTEAR
    )
