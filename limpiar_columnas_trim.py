import pandas as pd
import os
import sys

# --- CONFIGURACIÓN ---
ARCHIVO_EXCEL = "prueba.xlsx"
ARCHIVO_SALIDA = "Columnas_Con_Trim.xlsx"
LOG_SALIDA = "Analisis_Trim.log"
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


def analizar_columna(df, indice, nombre_encabezado):
    """Analiza una columna y retorna información sobre valores únicos y espacios"""
    columna = df.iloc[:, indice]
    valores_unicos = columna.dropna().unique()

    # Detectar valores con espacios
    valores_con_espacios = []
    for valor in valores_unicos:
        valor_str = str(valor)
        if valor_str != valor_str.strip():
            valores_con_espacios.append((valor_str, (columna == valor).sum()))

    return {
        "indice": indice,
        "nombre": nombre_encabezado,
        "total_unicos": len(valores_unicos),
        "total_registros": len(columna),
        "valores_con_espacios": valores_con_espacios,
        "columna": columna,
        "todos_valores": valores_unicos,
    }


def mostrar_analisis_columna(analisis, log_file=None):
    """Muestra o escribe el análisis de una columna"""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append(f"📊 Columna: {analisis['nombre']} (Índice: {analisis['indice']})")
    lines.append("=" * 80)
    lines.append(f"Total de valores únicos: {analisis['total_unicos']}")
    lines.append(f"Total de registros: {analisis['total_registros']}")

    if analisis["valores_con_espacios"]:
        lines.append(
            f"\n⚠️  {len(analisis['valores_con_espacios'])} valores con espacios extras (necesitan TRIM):"
        )
        for valor, cantidad in analisis["valores_con_espacios"][:15]:
            lines.append(f"    • '{valor}' → {cantidad} veces")
        if len(analisis["valores_con_espacios"]) > 15:
            lines.append(f"    ... y {len(analisis['valores_con_espacios']) - 15} más")
    else:
        lines.append("\n✓ No hay valores con espacios extras")

    lines.append(f"\n📋 Primeros valores únicos:")
    for i, valor in enumerate(sorted(analisis["todos_valores"].astype(str))[:10], 1):
        lines.append(f"    {i}. '{valor}'")

    output = "\n".join(lines)
    if log_file:
        log_file.write(output + "\n")
    else:
        print(output)


def main():
    print("\n" + "=" * 80)
    print("🔍 ANALIZADOR DE COLUMNAS CON TRIM")
    print("=" * 80)

    # Leer encabezados
    print(f"\nLeyendo archivo: {ARCHIVO_EXCEL}")
    encabezados = leer_encabezados(ARCHIVO_EXCEL)

    if not encabezados:
        print("No se pudieron leer los encabezados.")
        return

    # Filtrar columnas NO-fecha
    columnas_no_fecha = []
    for i, enc in enumerate(encabezados):
        if i not in INDICES_FECHAS:
            columnas_no_fecha.append((i, str(enc).strip()))

    print(f"\nTotal de columnas NO-fecha disponibles: {len(columnas_no_fecha)}")
    print("\n📋 Columnas disponibles para analizar:")
    for idx, (indice, nombre) in enumerate(columnas_no_fecha, 1):
        print(f"  {idx:2d}. [{indice:3d}] {nombre}")

    # Menú interactivo
    print("\n" + "=" * 80)
    print("Opciones:")
    print("  1. Analizar UNA columna específica")
    print("  2. Analizar TODAS las columnas")
    print("  3. Seleccionar múltiples columnas manualmente")
    print("  4. Salir")
    print("=" * 80)

    opcion = input("\nSelecciona una opción (1-4): ").strip()

    if opcion == "4":
        print("Saliendo...")
        return

    # Leer datos
    df = leer_datos(ARCHIVO_EXCEL, NUM_FILAS_A_SALTEAR)
    if df is None:
        return

    columnas_a_procesar = []

    if opcion == "1":
        # Analizar una columna
        num = input(
            f"\nIngresa el número de columna (1-{len(columnas_no_fecha)}): "
        ).strip()
        try:
            idx = int(num) - 1
            if 0 <= idx < len(columnas_no_fecha):
                indice, nombre = columnas_no_fecha[idx]
                columnas_a_procesar.append((indice, nombre))
            else:
                print("Número inválido")
                return
        except ValueError:
            print("Entrada inválida")
            return

    elif opcion == "2":
        # Analizar todas
        columnas_a_procesar = columnas_no_fecha
        print(f"\nAnalizando {len(columnas_a_procesar)} columnas...")

    elif opcion == "3":
        # Selección múltiple
        print("\nIngresa los números separados por comas (ej: 1,3,5):")
        entrada = input("> ").strip()
        try:
            numeros = [int(n.strip()) - 1 for n in entrada.split(",")]
            for num in numeros:
                if 0 <= num < len(columnas_no_fecha):
                    columnas_a_procesar.append(columnas_no_fecha[num])
            if not columnas_a_procesar:
                print("Ninguna columna válida seleccionada")
                return
        except ValueError:
            print("Formato inválido")
            return
    else:
        print("Opción inválida")
        return

    # Analizar columnas seleccionadas
    print("\n" + "=" * 80)
    print(f"🔍 ANALIZANDO {len(columnas_a_procesar)} COLUMNA(S)...")
    print("=" * 80)

    analisis_list = []

    # Modo log si opcion 2 (todas) para evitar saturar consola
    log_mode = opcion == "2"
    log_handle = None
    if log_mode:
        log_handle = open(LOG_SALIDA, "w", encoding="utf-8")
        log_handle.write("ANÁLISIS DE COLUMNAS NO-FECHA\n")
        log_handle.write(f"Archivo: {ARCHIVO_EXCEL}\n")
        log_handle.write(f"Columnas analizadas: {len(columnas_a_procesar)}\n")
        log_handle.write("=" * 80 + "\n")

    for indice, nombre in columnas_a_procesar:
        analisis = analizar_columna(df, indice, nombre)
        analisis_list.append(analisis)
        if log_mode:
            mostrar_analisis_columna(analisis, log_file=log_handle)
            print(f"  ✔ Guardado en log: [{indice}] {nombre}")
        else:
            mostrar_analisis_columna(analisis)

    if log_handle:
        log_handle.close()
        print(f"\n📄 Log generado: {LOG_SALIDA} (revisa ahí todo el detalle)")

    # Preguntar si aplicar TRIM
    print("\n" + "=" * 80)
    tiene_espacios = any(a["valores_con_espacios"] for a in analisis_list)

    if tiene_espacios:
        print("\n⚠️  Algunas columnas tienen valores con espacios.")
        aplicar = (
            input("\n¿Deseas aplicar TRIM a estas columnas? (s/n): ").strip().lower()
        )

        if aplicar == "s":
            print(f"\n💾 Generando Excel con TRIM aplicado: {ARCHIVO_SALIDA}")

            # Crear DataFrame de salida con TODAS las columnas
            df_salida = pd.DataFrame()

            # Recargar el DataFrame completo para incluir todas las columnas
            df_completo = leer_datos(ARCHIVO_EXCEL, NUM_FILAS_A_SALTEAR)
            encabezados_completos = leer_encabezados(ARCHIVO_EXCEL)

            # Procesar todas las columnas
            for i, encabezado in enumerate(encabezados_completos):
                columna_original = df_completo.iloc[:, i]

                # Si esta columna fue analizada, aplicar TRIM
                fue_analizada = any(a["indice"] == i for a in analisis_list)

                if fue_analizada:
                    # Aplicar TRIM (strip)
                    columna_limpia = columna_original.apply(
                        lambda x: str(x).strip() if pd.notna(x) else x
                    )
                    df_salida[encabezado] = columna_limpia
                else:
                    # Copiar sin modificar
                    df_salida[encabezado] = columna_original

            try:
                df_salida.to_excel(ARCHIVO_SALIDA, index=False, header=True)
                print(f"\n✓ ¡Archivo generado exitosamente!")
                print(f"  Filas: {len(df_salida)}")
                print(f"  Columnas: {len(df_salida.columns)}")
                print(f"  Ubicación: {os.path.abspath(ARCHIVO_SALIDA)}")
                print(f"\n📊 Resumen de TRIM aplicado:")
                print(f"  • Columnas con TRIM: {len(analisis_list)}")
                print(
                    f"  • Columnas sin modificar: {len(encabezados_completos) - len(analisis_list)}"
                )
            except Exception as e:
                print(f"\n❌ Error al guardar: {e}")
        else:
            print("\nOperación cancelada.")
    else:
        print("\n✓ No hay espacios extras en las columnas analizadas.")


if __name__ == "__main__":
    main()
