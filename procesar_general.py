"""
Script orquestador general: procesa normalización, fechas y validación.

Flujo:
1. Lee el archivo de entrada
2. Aplica normalizaciones de valores (normalizadores_lib)
3. Estandariza fechas (fechas_lib)
4. Valida contra validaciones_config.json
5. Genera Excel final + reporte de errores

Uso:
    python procesar_general.py
"""
import pandas as pd
import json
import os
import re
import unicodedata
from datetime import datetime

# Importar bibliotecas locales
from normalizadores_lib import (
    aplicar_todos_normalizadores, 
    aplicar_trim_general, 
    rellenar_sindato_columnas,
    rellenar_medicamentos_sindato,
    normalizar_variantes_sin_dato
)
from fechas_lib import procesar_fechas_df, INDICES_FECHAS

# --- CONFIGURACIÓN ---
ARCHIVO_ENTRADA = "./enero/BDRUTACCVMENERO2026_DUSAKAWIEPS_con_encabezados.xlsx"
ARCHIVO_SALIDA = "Procesado_Final.xlsx"
REPORTE_ERRORES_CSV = "Reporte_Validacion_Errores.csv"
REPORTE_ERRORES_EXCEL = "Reporte_Validacion_Errores.xlsx"
REPORTE_ERRORES_TOTALES_CSV = "Reporte_Validacion_Errores_Totales.csv"
REPORTE_ERRORES_TOTALES_EXCEL = "Reporte_Validacion_Errores_Totales.xlsx"
LOG_SALIDA = "Procesamiento_General.log"

NUM_FILAS_A_SALTEAR = 1  # Según instructivo
CONFIG_JSON = "validaciones_config.json"


def _append_log(log_path, mensaje):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(mensaje.rstrip() + "\n")


def detectar_engine(archivo):
    """Detecta el engine necesario según la extensión del archivo"""
    ext = os.path.splitext(archivo)[1].lower()
    if ext == ".xlsb":
        try:
            import pyxlsb  # noqa: F401
            return "pyxlsb"
        except ImportError:
            print("Falta pyxlsb. Instalar con: pip install pyxlsb")
            return None
    if ext == ".xlsx":
        return "openpyxl"
    return None


def leer_encabezados(archivo):
    """Lee los encabezados del archivo (primera fila)"""
    engine = detectar_engine(archivo)
    if not engine:
        return []
    try:
        df_headers = pd.read_excel(
            archivo, header=None, skiprows=0, nrows=1, engine=engine
        )
        return df_headers.iloc[0].tolist()
    except Exception as e:
        print(f"Error al leer encabezados: {e}")
        return []


def leer_datos(archivo, filas_a_saltar):
    """Lee los datos del archivo"""
    engine = detectar_engine(archivo)
    if not engine:
        return None
    try:
        return pd.read_excel(
            archivo, header=None, skiprows=filas_a_saltar, engine=engine
        )
    except Exception as e:
        print(f"Error al leer datos: {e}")
        return None


def cargar_configuracion(ruta_json):
    """Carga la configuración de validaciones desde JSON"""
    if not os.path.exists(ruta_json):
        print(f"No se encontró el archivo de configuración: {ruta_json}")
        return []

    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error al leer configuración: {e}")
        return []

    columnas = data.get("columnas_validacion", [])
    configuradas = []

    for item in columnas:
        indice = item.get("indice")
        validos = set(item.get("validos", []))
        if indice is None or not validos:
            continue
        configuradas.append(
            {
                "indice": indice,
                "nombre": item.get("nombre", ""),
                "validos": validos,
            }
        )

    return configuradas


def _normalizar_base(valor):
    """Normaliza texto para comparaciones: sin tildes, mayusculas, espacios compactos"""
    if not isinstance(valor, str):
        return ""
    texto = unicodedata.normalize("NFKD", valor)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = texto.upper()
    texto = re.sub(r"\s+", " ", texto).strip()
    texto = re.sub(r"\s*,\s*", ", ", texto)
    return texto


def _normalizar_valor_basico(valor):
    """Normaliza valor sin variantes (solo limpieza y SIN DATO)."""
    if pd.isna(valor):
        return ""
    val = _normalizar_base(str(valor))
    if val in ("", "NAN", "NONE", "NULL"):
        return ""
    if val in ("SIN DATO", "SIN DATOS", "SINDATO", "SIN_DATO"):
        return "SINDATO"
    return val


def normalizar_valor(valor):
    """Normaliza un valor para la validación: mayúsculas, sin espacios extra, SIN DATO → SINDATO"""
    val = _normalizar_valor_basico(valor)
    if val == "":
        return ""
    # Mapear variantes conocidas a un valor canonico
    variantes = {
        "NINGUNA DE LAS ANTERIORES": "NINGUNAS DE LAS ANTERIORES",
        "NINGUNAS DE LAS ANTERIORES": "NINGUNAS DE LAS ANTERIORES",
        "NEGRO(A), MULATO(A), AFROCOLOMBIANO O AFRODECENDIENTE": "NEGRO (A), MULATO, AFROAMERICANO",
        "NEGRO(A), MULATO(A), AFROCOLOMBIANO O AFRODESCENDIENTE": "NEGRO (A), MULATO, AFROAMERICANO",
        "NEGRO (A), MULATO (A), AFROCOLOMBIANO O AFRODECENDIENTE": "NEGRO (A), MULATO, AFROAMERICANO",
        "NEGRO (A), MULATO (A), AFROCOLOMBIANO O AFRODESCENDIENTE": "NEGRO (A), MULATO, AFROAMERICANO",
        "COMUNIDADES INDIGENAS": "COMUNIDADES INDIGINAS",
        "VICTIMA DEL CONFLICTO ARMADO INTERNO": "VICTIMAS DEL CONFLICTO ARMADO",
        "AFROCOLOMBIANO O AFRODECENDIENTE": "OTRO GRUPO POBLACIONAL",
        "POBLACION RURAL NO MIGRATORIA": "OTRO GRUPO POBLACIONAL",
        "U": "URBANA",
        "R": "RURAL",
        "CP": "URBANA",  # CP = Cabecera o Pueblo (categoría urbana)
    }
    return variantes.get(val, val)


def normalizar_lista_validos(validos):
    """Normaliza la lista de valores válidos con las mismas reglas"""
    return {normalizar_valor(v) for v in validos}


def validar_columna(df, encabezados, indice_json, config, log, num_filas_saltadas):
    """Valida una columna y retorna lista de errores detallados
    
    Args:
        indice_json: Índice desde JSON (1-based, número de columna Excel)
    """
    # Convertir índice de JSON (1-based) a índice pandas (0-based)
    indice = indice_json - 1
    
    if indice < 0 or indice >= len(df.columns):
        log.write(f"Índice {indice_json} (pandas: {indice}) fuera de rango.\n")
        return []

    nombre_columna = config.get("nombre", "")
    if not nombre_columna and indice < len(encabezados):
        nombre_columna = str(encabezados[indice]).strip()

    col = df.iloc[:, indice]
    col_norm_basico = col.apply(_normalizar_valor_basico)
    col_norm = col.apply(normalizar_valor)

    # Excluir vacíos
    col_norm_no_vacio = col_norm[col_norm != ""]
    col_norm_basico_no_vacio = col_norm_basico[col_norm_basico != ""]

    validos = normalizar_lista_validos(config.get("validos", set()))
    invalidos_total = col_norm_basico_no_vacio[~col_norm_basico_no_vacio.isin(validos)]
    invalidos = col_norm_no_vacio[~col_norm_no_vacio.isin(validos)]
    conteo_invalidos = invalidos.value_counts()
    conteo_invalidos_total = invalidos_total.value_counts()

    log.write("-" * 80 + "\n")
    log.write(f"Índice JSON (columna Excel): {indice_json}\n")
    log.write(f"Índice pandas (0-based): {indice}\n")
    log.write(f"Nombre: {nombre_columna}\n")
    log.write(f"Total registros: {len(col)}\n")
    log.write(f"Total no vacíos: {len(col_norm_no_vacio)}\n")
    log.write(f"Total inválidos (antes de normalizar): {len(invalidos_total)}\n")
    log.write(f"Total inválidos (después de normalizar): {len(invalidos)}\n")

    errores = []
    errores_totales = []
    if conteo_invalidos_total.empty and conteo_invalidos.empty:
        log.write("No se encontraron valores inválidos.\n")
    else:
        if not conteo_invalidos_total.empty:
            log.write("Valores inválidos (antes de normalizar):\n")
            for valor, cantidad in conteo_invalidos_total.items():
                log.write(f"  - '{valor}': {cantidad}\n")
        if not conteo_invalidos.empty:
            log.write("Valores inválidos (después de normalizar):\n")
            for valor, cantidad in conteo_invalidos.items():
                log.write(f"  - '{valor}': {cantidad}\n")
        
        # Generar lista detallada de errores (fila, columna, valor original, valor normalizado)
        for fila_idx, val_norm in enumerate(col_norm):
            if val_norm != "" and val_norm not in validos:
                errores.append({
                    "fila": fila_idx + num_filas_saltadas + 1,  # +1 para header original
                    "columna_idx": indice_json,
                    "columna_nombre": nombre_columna,
                    "valor_original": col.iloc[fila_idx],
                    "valor_normalizado": val_norm,
                    "validos_esperados": ", ".join(sorted(validos))
                })
        for fila_idx, val_norm in enumerate(col_norm_basico):
            if val_norm != "" and val_norm not in validos:
                errores_totales.append({
                    "fila": fila_idx + num_filas_saltadas + 1,
                    "columna_idx": indice_json,
                    "columna_nombre": nombre_columna,
                    "valor_original": col.iloc[fila_idx],
                    "valor_normalizado": val_norm,
                    "validos_esperados": ", ".join(sorted(validos))
                })
    
    return errores, errores_totales


def validar_df(df, encabezados, configuracion, log, num_filas_saltadas):
    """Valida el DataFrame completo y retorna listas de errores"""
    todos_los_errores = []
    todos_los_errores_totales = []
    
    log.write("=" * 80 + "\n")
    log.write("VALIDACIÓN DE VALORES - COLUMNAS\n")
    log.write(f"Columnas configuradas: {len(configuracion)}\n")
    log.write("=" * 80 + "\n\n")

    for item in configuracion:
        errores, errores_totales = validar_columna(
            df,
            encabezados,
            item["indice"],
            item,
            log,
            num_filas_saltadas,
        )
        todos_los_errores.extend(errores)
        todos_los_errores_totales.extend(errores_totales)
    
    return todos_los_errores, todos_los_errores_totales


def ejecutar_procesamiento_general(
    archivo_entrada,
    archivo_salida=ARCHIVO_SALIDA,
    reporte_errores_csv=REPORTE_ERRORES_CSV,
    reporte_errores_excel=REPORTE_ERRORES_EXCEL,
    reporte_errores_totales_csv=REPORTE_ERRORES_TOTALES_CSV,
    reporte_errores_totales_excel=REPORTE_ERRORES_TOTALES_EXCEL,
    log_salida=LOG_SALIDA,
    num_filas_a_saltar=NUM_FILAS_A_SALTEAR,
    config_json=CONFIG_JSON,
):
    _append_log(log_salida, "=" * 80)
    _append_log(
        log_salida,
        "PROCESAMIENTO GENERAL: NORMALIZACION + FECHAS + VALIDACION",
    )
    _append_log(log_salida, "=" * 80)
    _append_log(log_salida, f"Archivo de entrada: {archivo_entrada}")
    _append_log(
        log_salida,
        f"Fecha de ejecucion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    )

    print("=" * 80)
    print("PROCESAMIENTO GENERAL: NORMALIZACIÓN + FECHAS + VALIDACIÓN")
    print("=" * 80)
    print(f"Archivo de entrada: {archivo_entrada}")
    print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # --- 1. LEER DATOS ---
    print("[1/5] Leyendo archivo de entrada...")
    encabezados = leer_encabezados(archivo_entrada)
    if not encabezados:
        mensaje = "ERROR - No se pudieron leer los encabezados."
        print(mensaje)
        _append_log(log_salida, mensaje)
        return None

    df = leer_datos(archivo_entrada, num_filas_a_saltar)
    if df is None:
        mensaje = "ERROR - No se pudieron leer los datos."
        print(mensaje)
        _append_log(log_salida, mensaje)
        return None

    # Eliminar filas sin consecutivo (columna 1 en Excel -> indice 0)
    try:
        col_consecutivo = df.iloc[:, 0]
        sin_consecutivo = col_consecutivo.isna() | (col_consecutivo.astype(str).str.strip() == "")
        filas_sin_consecutivo = int(sin_consecutivo.sum())
        if filas_sin_consecutivo > 0:
            df = df.loc[~sin_consecutivo].copy()
            print(f"  OK - Filas sin consecutivo eliminadas: {filas_sin_consecutivo}")
            _append_log(
                log_salida,
                f"Filas sin consecutivo eliminadas: {filas_sin_consecutivo}",
            )
    except Exception:
        pass

    print(f"  OK - Datos cargados: {len(df)} registros, {len(df.columns)} columnas")
    print()

    # --- 1.5. NORMALIZAR VARIANTES DE "SIN DATO" → "SINDATO" (PRIMERO) ---
    print("[1.5/7] Normalizando variantes 'SIN DATO' → 'SINDATO'...")
    try:
        df = normalizar_variantes_sin_dato(df)
        print("  OK - Variantes de 'SIN DATO' normalizadas")
        _append_log(log_salida, "OK - Variantes de 'SIN DATO' normalizadas")
    except Exception as e:
        print(f"  WARNING - Error al normalizar 'SIN DATO': {e}")
        _append_log(log_salida, f"WARNING - Error al normalizar 'SIN DATO': {e}")
        print("  → Continuando...")
    print()

    # --- 2. APLICAR TRIM GENERAL ---
    print("[2/7] Aplicando TRIM general a columnas NO-fecha...")
    try:
        # Excluir las columnas de fechas del TRIM (se procesan en el paso de fechas)
        df = aplicar_trim_general(df, indices_excluir=INDICES_FECHAS)
        print("  OK - TRIM aplicado correctamente")
        _append_log(log_salida, "OK - TRIM aplicado correctamente")
    except Exception as e:
        print(f"  WARNING - Error en TRIM: {e}")
        _append_log(log_salida, f"WARNING - Error en TRIM: {e}")
        print("  - Continuando sin TRIM...")
    print()

    # --- 3. RELLENAR SINDATO EN VALORES VACÍOS ---
    print("[3/7] Rellenando SINDATO en columnas de texto vacías...")
    try:
        df = rellenar_sindato_columnas(df)
        print("  OK - SINDATO rellenado correctamente")
        _append_log(log_salida, "OK - SINDATO rellenado correctamente")
    except Exception as e:
        print(f"  WARNING - Error al rellenar SINDATO: {e}")
        _append_log(log_salida, f"WARNING - Error al rellenar SINDATO: {e}")
        print("  - Continuando sin rellenar SINDATO...")
    print()

    # --- 3.5. RELLENAR SINDATO EN MEDICAMENTOS (vacíos Y ceros) ---
    print("[3.5/7] Rellenando SINDATO en columnas de medicamentos (vacíos y ceros)...")
    try:
        df = rellenar_medicamentos_sindato(df)
        print("  OK - Medicamentos procesados correctamente")
        _append_log(log_salida, "OK - Medicamentos procesados correctamente")
    except Exception as e:
        print(f"  WARNING - Error al procesar medicamentos: {e}")
        _append_log(log_salida, f"WARNING - Error al procesar medicamentos: {e}")
        print("  - Continuando sin procesar medicamentos...")
    print()

    # --- 4. NORMALIZAR VALORES ---
    print("[4/7] Aplicando normalizaciones de valores específicas...")
    try:
        df = aplicar_todos_normalizadores(df)
        print("  OK - Normalizaciones aplicadas correctamente")
        _append_log(log_salida, "OK - Normalizaciones aplicadas correctamente")
    except Exception as e:
        print(f"  WARNING - Error en normalizacion: {e}")
        _append_log(log_salida, f"WARNING - Error en normalizacion: {e}")
        print("  - Continuando sin normalizaciones...")
    print()

    # --- 5. PROCESAR FECHAS ---
    print("[5/7] Procesando fechas...")
    try:
        df = procesar_fechas_df(df, INDICES_FECHAS)
        print("  OK - Fechas procesadas correctamente")
        _append_log(log_salida, "OK - Fechas procesadas correctamente")
    except Exception as e:
        print(f"  WARNING - Error en procesamiento de fechas: {e}")
        _append_log(log_salida, f"WARNING - Error en procesamiento de fechas: {e}")
        print("  - Continuando sin procesar fechas...")
    print()

    # --- 6. VALIDAR ---
    print("[6/7] Validando contra configuración...")
    configuracion = cargar_configuracion(config_json)
    if not configuracion:
        print("  WARNING - No hay columnas configuradas para validar.")
        _append_log(log_salida, "WARNING - No hay columnas configuradas para validar.")
        todos_los_errores = []
        todos_los_errores_totales = []
    else:
        with open(log_salida, "w", encoding="utf-8") as log:
            todos_los_errores, todos_los_errores_totales = validar_df(
                df,
                encabezados,
                configuracion,
                log,
                num_filas_a_saltar,
            )
        
        print(f"  OK - Validacion completada")
        print(f"    - Log generado: {LOG_SALIDA}")
        
        if todos_los_errores_totales:
            print(f"    - Errores totales (antes de normalizar): {len(todos_los_errores_totales)}")
            df_errores_totales = pd.DataFrame(todos_los_errores_totales)
            df_errores_totales.to_csv(
                reporte_errores_totales_csv,
                index=False,
                encoding="utf-8-sig",
                sep=";",
            )
            df_errores_totales.to_excel(reporte_errores_totales_excel, index=False)
            print(f"    - Reporte CSV total: {reporte_errores_totales_csv}")
            print(f"    - Reporte Excel total: {reporte_errores_totales_excel}")

        if todos_los_errores:
            print(f"    - Errores encontrados: {len(todos_los_errores)}")
            
            # Generar reporte de errores en CSV
            df_errores = pd.DataFrame(todos_los_errores)
            df_errores.to_csv(
                reporte_errores_csv, index=False, encoding="utf-8-sig", sep=";"
            )
            print(f"    - Reporte CSV: {reporte_errores_csv}")
            
            # Generar reporte de errores en Excel
            df_errores.to_excel(reporte_errores_excel, index=False)
            print(f"    - Reporte Excel: {reporte_errores_excel}")
        else:
            print("    - OK - No se encontraron errores de validacion")
    print()

    # --- 7. GUARDAR RESULTADO FINAL ---
    print("[7/7] Guardando archivo final...")
    try:
        # Crear DataFrame con encabezados
        df_final = pd.DataFrame(df.values, columns=encabezados[:len(df.columns)])
        df_final.to_excel(archivo_salida, index=False)
        print(f"  OK - Archivo guardado: {archivo_salida}")
    except Exception as e:
        print(f"  ❌ Error al guardar archivo: {e}")
        _append_log(log_salida, f"ERROR - No se pudo guardar archivo: {e}")
        return None
    print()

    print("=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80)
    print(f"📊 Resultado: {archivo_salida}")
    if todos_los_errores:
        print(f"⚠ Errores de validación: {len(todos_los_errores)}")
        print(f"📋 Ver detalles en: {reporte_errores_csv}")
    else:
        print("OK - Sin errores de validacion")

    return {
        "archivo_salida": archivo_salida,
        "log": log_salida,
        "reporte_errores_csv": reporte_errores_csv,
        "reporte_errores_excel": reporte_errores_excel,
        "reporte_errores_totales_csv": reporte_errores_totales_csv,
        "reporte_errores_totales_excel": reporte_errores_totales_excel,
        "errores": todos_los_errores,
        "errores_totales": todos_los_errores_totales,
    }


def main():
    resultado = ejecutar_procesamiento_general(
        ARCHIVO_ENTRADA,
        archivo_salida=ARCHIVO_SALIDA,
        reporte_errores_csv=REPORTE_ERRORES_CSV,
        reporte_errores_excel=REPORTE_ERRORES_EXCEL,
        reporte_errores_totales_csv=REPORTE_ERRORES_TOTALES_CSV,
        reporte_errores_totales_excel=REPORTE_ERRORES_TOTALES_EXCEL,
        log_salida=LOG_SALIDA,
        num_filas_a_saltar=NUM_FILAS_A_SALTEAR,
        config_json=CONFIG_JSON,
    )
    if not resultado:
        print(f"ERROR - Revisa el log: {LOG_SALIDA}")


if __name__ == "__main__":
    main()
