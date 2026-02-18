import json
import os
import sys
import pandas as pd
import re
import unicodedata

# --- CONFIGURACION ---
ARCHIVO_EXCEL = "./noviembre/copia_nov_con_encabezados.xlsx"
LOG_SALIDA = "Validacion_Columnas.log"
NUM_FILAS_A_SALTEAR = 1

CONFIG_JSON = "validaciones_config.json"


def detectar_engine(archivo):
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
    if not os.path.exists(ruta_json):
        print(f"No se encontro el archivo de configuracion: {ruta_json}")
        return []

    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error al leer configuracion: {e}")
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


def normalizar_valor(valor):
    """Normaliza un valor para la validación: mayúsculas, sin espacios extra, SIN DATO → SINDATO"""
    if pd.isna(valor):
        return ""
    val = _normalizar_base(str(valor))
    if val in ("", "NAN", "NONE", "NULL"):
        return ""

    # Normalizar variantes de "SIN DATO"
    if val in ("SIN DATO", "SIN DATOS", "SINDATO", "SIN_DATO"):
        return "SINDATO"

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
    }
    if val in variantes:
        return variantes[val]

    return val


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
    col_norm = col.apply(normalizar_valor)

    # Excluir vacios
    col_norm_no_vacio = col_norm[col_norm != ""]

    validos = normalizar_lista_validos(config.get("validos", set()))
    invalidos = col_norm_no_vacio[~col_norm_no_vacio.isin(validos)]
    conteo_invalidos = invalidos.value_counts()

    log.write("-" * 80 + "\n")
    log.write(f"Índice JSON (columna Excel): {indice_json}\n")
    log.write(f"Índice pandas (0-based): {indice}\n")
    log.write(f"Nombre: {nombre_columna}\n")
    log.write(f"Total registros: {len(col)}\n")
    log.write(f"Total no vacios: {len(col_norm_no_vacio)}\n")
    log.write(f"Total invalidos: {len(invalidos)}\n")

    errores = []
    if conteo_invalidos.empty:
        log.write("No se encontraron valores invalidos.\n")
    else:
        log.write("Valores invalidos encontrados:\n")
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
    
    return errores


def ejecutar_validacion(
    archivo_excel,
    log_salida=LOG_SALIDA,
    num_filas_a_saltar=NUM_FILAS_A_SALTEAR,
    config_json=CONFIG_JSON,
    csv_salida=None,
):
    print(f"Leyendo archivo: {archivo_excel}")

    configuracion = cargar_configuracion(config_json)
    if not configuracion:
        print("No hay columnas configuradas para validar.")
        return None

    encabezados = leer_encabezados(archivo_excel)
    if not encabezados:
        print("No se pudieron leer los encabezados.")
        return None

    df = leer_datos(archivo_excel, num_filas_a_saltar)
    if df is None:
        return None

    todos_los_errores = []

    with open(log_salida, "w", encoding="utf-8") as log:
        log.write("VALIDACION DE VALORES - COLUMNAS\n")
        log.write(f"Archivo: {archivo_excel}\n")
        log.write(f"Columnas configuradas: {len(configuracion)}\n")

        for item in configuracion:
            errores = validar_columna(
                df,
                encabezados,
                item["indice"],
                item,
                log,
                num_filas_a_saltar,
            )
            todos_los_errores.extend(errores)

    print(f"Log generado: {log_salida}")

    archivo_errores_csv = None
    if todos_los_errores:
        df_errores = pd.DataFrame(todos_los_errores)
        archivo_errores_csv = csv_salida or "Validacion_Errores.csv"
        df_errores.to_csv(archivo_errores_csv, index=False, encoding="utf-8-sig", sep=";")
        print(
            f"Reporte de errores generado: {archivo_errores_csv} ({len(todos_los_errores)} errores)"
        )
    else:
        print("No se encontraron errores de validación.")

    return {
        "errores": todos_los_errores,
        "log": log_salida,
        "csv": archivo_errores_csv,
    }


def main(argv=None):
    argv = argv or sys.argv[1:]
    archivo_excel = argv[0] if argv else ARCHIVO_EXCEL
    ejecutar_validacion(archivo_excel)


if __name__ == "__main__":
    main()
