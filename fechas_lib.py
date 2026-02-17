"""
Biblioteca de procesamiento de fechas reutilizable.
Extrae la lógica de procesar_todas_fechas.py para uso en pipelines.

IMPORTANTE: Los índices en INDICES_FECHAS son 0-based (índices pandas).
"""
import pandas as pd
from datetime import datetime

# Lista de índices de columnas de fechas a procesar (0-based)
INDICES_FECHAS = [
    7, 23, 27, 29, 43, 45, 47, 49, 51, 53, 58, 59, 61, 64, 66, 68,
    74, 76, 80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104,
    108, 119, 123,
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


def procesar_fechas_df(df, columnas_fechas=None):
    """
    Procesa todas las fechas en un DataFrame.
    
    Args:
        df: DataFrame con todas las columnas
        columnas_fechas: Lista de índices de columnas de fechas (por defecto INDICES_FECHAS)
    
    Returns:
        DataFrame con fechas procesadas
    """
    if columnas_fechas is None:
        columnas_fechas = INDICES_FECHAS
    
    indices_fechas_set = set(columnas_fechas)
    
    print(f"Procesando fechas en {len(columnas_fechas)} columnas...")
    
    for indice in range(len(df.columns)):
        es_columna_fecha = indice in indices_fechas_set
        
        try:
            if es_columna_fecha:
                # Convertir fechas al formato YYYY/MM/DD
                col_procesada = df.iloc[:, indice].apply(convertir_fecha)
                df[df.columns[indice]] = col_procesada.values
            else:
                # Limpiar fechas especiales en columnas que NO son de fechas
                col_procesada = df.iloc[:, indice].apply(limpiar_valor_no_fecha)
                df[df.columns[indice]] = col_procesada.values
        except Exception as e:
            # Si falla, continuar sin modificar la columna
            pass
    
    print("✓ Fechas procesadas")
    return df
