import pandas as pd
import os
import sys
from collections import defaultdict

# --- CONFIGURACIÓN ---
ARCHIVO_EXCEL = "prueba.xlsx"
LOG_SALIDA = "Normalizacion_Valores_Unicos.log"
EXCEL_SALIDA = "Valores_Unicos_Normalizados.xlsx"
NUM_FILAS_A_SALTEAR = 1

# Índices de columnas que son fechas (excluir de la búsqueda)
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


def detectar_engine(archivo):
    """Detecta el engine según la extensión del archivo"""
    ext = os.path.splitext(archivo)[1].lower()
    if ext == ".xlsb":
        try:
            import pyxlsb

            return "pyxlsb"
        except ImportError:
            print("Instalando pyxlsb...")
            import subprocess

            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyxlsb"])
            return "pyxlsb"
    elif ext == ".xlsx":
        return "openpyxl"
    return None


def leer_encabezados(archivo):
    """Lee los encabezados del archivo"""
    engine = detectar_engine(archivo)
    try:
        df_headers = pd.read_excel(
            archivo, header=None, skiprows=0, nrows=1, engine=engine
        )
        return df_headers.iloc[0].tolist()
    except Exception as e:
        print(f"Error al leer encabezados: {e}")
        return []


def leer_datos(archivo, filas_a_saltar):
    """Lee todos los datos del archivo"""
    engine = detectar_engine(archivo)
    try:
        df = pd.read_excel(archivo, header=None, skiprows=filas_a_saltar, engine=engine)
        return df
    except Exception as e:
        print(f"Error al leer datos: {e}")
        return None


def encontrar_variantes(valores):
    """
    Agrupa valores por su versión normalizada (minúsculas sin espacios extras)
    y retorna grupos con múltiples variantes
    """
    grupos = defaultdict(list)

    for valor in valores:
        if pd.isna(valor):
            continue
        valor_str = str(valor).strip()
        # Clave normalizada: minúsculas
        clave = valor_str.lower()
        grupos[clave].append(valor_str)

    # Retornar solo los grupos con variantes (más de 1 valor distinto)
    variantes = {}
    for clave, valores_list in grupos.items():
        valores_unicos = list(set(valores_list))
        if len(valores_unicos) > 1:
            variantes[clave] = {
                "variantes": valores_unicos,
                "cuenta": {v: valores_list.count(v) for v in valores_unicos},
                "total": len(valores_list),
            }

    return variantes


def analizar_todas_columnas(archivo, filas_a_saltar):
    """Analiza todas las columnas NO-fecha buscando variantes"""
    print(f"\n{'='*80}")
    print("🔍 ANALIZADOR DE VALORES ÚNICOS CON NORMALIZACIÓN")
    print(f"{'='*80}\n")

    print(f"Leyendo archivo: {archivo}")

    encabezados = leer_encabezados(archivo)
    if not encabezados:
        print("No se pudieron leer los encabezados.")
        return

    df = leer_datos(archivo, filas_a_saltar)
    if df is None:
        return

    print(f"✓ Datos cargados: {len(df)} registros × {len(df.columns)} columnas\n")

    # Log
    with open(LOG_SALIDA, "w", encoding="utf-8") as log:
        log.write("ANÁLISIS DE VALORES ÚNICOS Y VARIANTES DE CAPITALIZACIÓN\n")
        log.write(f"Archivo: {archivo}\n")
        log.write(f"Total de registros: {len(df)}\n")
        log.write(
            f"Columnas analizadas: {len([i for i in range(len(encabezados)) if i not in INDICES_FECHAS])}\n"
        )
        log.write("=" * 80 + "\n\n")

        resumen_general = []

        # Analizar cada columna NO-fecha
        for i, encabezado in enumerate(encabezados):
            if i in INDICES_FECHAS:
                continue

            columna = df.iloc[:, i]
            valores_unicos = columna.dropna().unique()

            log.write(f"\n{'='*80}\n")
            log.write(f"📊 COLUMNA: {encabezado} (Índice {i})\n")
            log.write(f"{'='*80}\n")
            log.write(f"Total de valores únicos: {len(valores_unicos)}\n")
            log.write(f"Total de registros: {len(columna)}\n")
            log.write(f"Registros vacíos: {columna.isna().sum()}\n\n")

            # Buscar variantes
            variantes = encontrar_variantes(valores_unicos)

            if variantes:
                log.write(
                    f"⚠️  ENCONTRADAS {len(variantes)} VARIANTES DE CAPITALIZACIÓN:\n\n"
                )
                resumen_general.append(
                    {
                        "columna": encabezado,
                        "indice": i,
                        "variantes_encontradas": len(variantes),
                    }
                )

                for idx, (clave, info) in enumerate(variantes.items(), 1):
                    log.write(f"  {idx}. Grupo normalizado: '{clave}'\n")
                    log.write(f"     Variantes encontradas:\n")
                    for var in sorted(info["variantes"]):
                        cantidad = info["cuenta"][var]
                        log.write(f"       • '{var}' → {cantidad} veces\n")
                    log.write(f"     Total en grupo: {info['total']} registros\n")
                    log.write(
                        f"     Recomendación: Normalizar a '{info['variantes'][0]}' o '{clave.title()}'\n\n"
                    )
            else:
                log.write("✓ No hay variantes de capitalización en esta columna.\n\n")

            # Mostrar valores únicos (máximo 20)
            log.write(f"📋 Primeros valores únicos:\n")
            for idx, valor in enumerate(sorted(valores_unicos.astype(str))[:20], 1):
                log.write(f"   {idx}. '{valor}'\n")
            if len(valores_unicos) > 20:
                log.write(f"   ... y {len(valores_unicos) - 20} valores más\n")
            log.write("\n")

        # Resumen general
        log.write("\n" + "=" * 80 + "\n")
        log.write("📊 RESUMEN GENERAL\n")
        log.write("=" * 80 + "\n\n")

        if resumen_general:
            log.write(f"Columnas con variantes encontradas: {len(resumen_general)}\n\n")
            for item in resumen_general:
                log.write(
                    f"  • {item['columna']} (índice {item['indice']}): {item['variantes_encontradas']} grupos de variantes\n"
                )
        else:
            log.write(
                "No se encontraron variantes de capitalización en las columnas analizadas.\n"
            )

    print(f"✓ Log generado: {LOG_SALIDA}")
    print(f"\n📄 Revisa {LOG_SALIDA} para ver todas las variantes encontradas")
    return resumen_general


def aplicar_normalizacion(archivo, filas_a_saltar):
    """
    Opción para normalizar valores después de revisar el log
    """
    print(f"\n¿Deseas aplicar normalización a valores? (s/n): ", end="")
    aplicar = input().strip().lower()

    if aplicar != "s":
        print("Operación cancelada.")
        return

    print("\nFunción de normalización manual:")
    print("Edita el diccionario 'REEMPLAZOS' en el código con los mapeos deseados")
    print("Formato: {'valor_a_reemplazar': 'valor_nuevo'}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🔍 BUSQUEDA DE VARIANTES Y NORMALIZACIÓN DE VALORES")
    print("=" * 80)

    resumen = analizar_todas_columnas(ARCHIVO_EXCEL, NUM_FILAS_A_SALTEAR)

    if resumen:
        print(f"\n⚠️  Se encontraron variantes en {len(resumen)} columnas")
        print(f"Revisa {LOG_SALIDA} para ver los detalles")
    else:
        print("\n✓ No se encontraron variantes de capitalización")
