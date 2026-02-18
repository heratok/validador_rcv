import pandas as pd
import os
import sys
import csv
import argparse

ARCHIVO_EXCEL = "./nov_limpio.xlsx"
NUM_FILAS_A_SALTEAR = 1
INDICE_IPS = 22  # columna con nombre de IPS
NOMBRE_CONSECUTIVO_IPS = "CONSECUTIVO_IPS"
CARPETA_SALIDA = "Reportes_Por_IPS_CSV"


def obtener_carpeta_mes(archivo, carpeta_base=CARPETA_SALIDA):
    base = os.path.basename(archivo)
    nombre, _ext = os.path.splitext(base)
    prefijo = nombre.split("_")[0].strip().lower()
    mapa = {"nov": "noviembre", "dic": "diciembre", "ene": "enero"}
    carpeta_mes = mapa.get(prefijo, prefijo or "otros")
    return os.path.join(carpeta_base, carpeta_mes)


def parsear_args():
    parser = argparse.ArgumentParser(
        description="Separar archivo por IPS y generar CSV por mes."
    )
    parser.add_argument(
        "--archivo",
        default=None,
        help="Ruta del Excel de entrada (ej: nov_limpio.xlsx). Si no se indica, procesa todos los *_limpio.xlsx de la carpeta.",
    )
    parser.add_argument(
        "--carpeta",
        default="./limpios",
        help="Carpeta donde buscar *_limpio.xlsx cuando no se indica --archivo.",
    )
    return parser.parse_args()


def detectar_engine(archivo):
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


def procesar_archivo(
    archivo_excel,
    carpeta_salida_base=CARPETA_SALIDA,
    num_filas_a_saltar=NUM_FILAS_A_SALTEAR,
    indice_ips=INDICE_IPS,
):
    print("Leyendo archivo:", archivo_excel)
    engine = detectar_engine(archivo_excel)
    df_headers = pd.read_excel(
        archivo_excel, header=None, skiprows=0, nrows=1, engine=engine
    )
    encabezados = df_headers.iloc[0].tolist()

    df = pd.read_excel(
        archivo_excel, header=None, skiprows=num_filas_a_saltar, engine=engine
    )
    if indice_ips >= len(df.columns):
        print(f"El índice {indice_ips} no existe en el archivo.")
        return

    # Asignar nombres de columnas usando encabezados
    df.columns = [str(h) for h in encabezados]
    nombre_col_ips = df.columns[indice_ips]

    print(f"Agrupando por IPS en columna índice {indice_ips} - '{nombre_col_ips}'")
    print(f"Total de columnas en el archivo original: {len(df.columns)}")

    # Crear consecutivo por IPS (1..n dentro de cada grupo) - temporal
    df[NOMBRE_CONSECUTIVO_IPS] = df.groupby(nombre_col_ips).cumcount() + 1

    # Ordenar por IPS y consecutivo para claridad
    df_ordenado = df.sort_values(by=[nombre_col_ips, NOMBRE_CONSECUTIVO_IPS])

    # Generar CSV separados por IPS
    carpeta_salida = obtener_carpeta_mes(archivo_excel, carpeta_base=carpeta_salida_base)
    os.makedirs(carpeta_salida, exist_ok=True)
    print("\nGenerando CSV por IPS en:", os.path.abspath(carpeta_salida))
    for ips, grupo in df_ordenado.groupby(nombre_col_ips):
        # Reemplazar caracteres inválidos de Windows
        nombre_seguro = (str(ips).strip()
                        .replace("/", "-")
                        .replace("\\", "-")
                        .replace("<", "-")
                        .replace(">", "-")
                        .replace(":", "-")
                        .replace('"', "-")
                        .replace("|", "-")
                        .replace("?", "-")
                        .replace("*", "-"))
        salida_ips = os.path.join(carpeta_salida, f"{nombre_seguro}.csv")

        # Reiniciar consecutivo desde 1 para cada CSV
        grupo = grupo.copy()

        # Si existe una columna CONSECUTIVO en las 125 originales, actualizarla.
        # NO agregar columnas nuevas para mantener exactamente 125 columnas.
        if "CONSECUTIVO" in grupo.columns:
            grupo["CONSECUTIVO"] = range(1, len(grupo) + 1)

        # Eliminar la columna temporal CONSECUTIVO_IPS
        if NOMBRE_CONSECUTIVO_IPS in grupo.columns:
            grupo = grupo.drop(columns=[NOMBRE_CONSECUTIVO_IPS])

        # Normalizar valores vacíos y variantes de "SIN DATO" a "SINDATO"
        for col in grupo.columns:
            # Reemplazar variantes de "SIN DATO" (case-insensitive)
            grupo[col] = grupo[col].astype(str).str.strip()
            grupo[col] = grupo[col].replace(
                {
                    "nan": "SINDATO",
                    "NaN": "SINDATO",
                    "": "SINDATO",
                    "SIN DATO": "SINDATO",
                    "SIN DATOS": "SINDATO",
                    "Sin Dato": "SINDATO",
                    "Sin Datos": "SINDATO",
                    "sin dato": "SINDATO",
                    "sin datos": "SINDATO",
                    "SINDATOS": "SINDATO",
                    "Sin datos": "SINDATO",
                }
            )

        # Llenar cualquier NaN restante con SINDATO
        grupo = grupo.fillna("SINDATO")

        # LIMPIEZA EXHAUSTIVA: Eliminar todos los caracteres que pueden romper el CSV
        for col in grupo.columns:
            # Convertir a string primero
            grupo[col] = grupo[col].astype(str)
            
            # Eliminar saltos de línea, retornos de carro y tabulaciones
            grupo[col] = grupo[col].str.replace("\n", " ", regex=False)
            grupo[col] = grupo[col].str.replace("\r", " ", regex=False)
            grupo[col] = grupo[col].str.replace("\t", " ", regex=False)
            
            # Eliminar punto y coma (;) - delimitador del CSV
            grupo[col] = grupo[col].str.replace(";", "", regex=False)
            
            # Eliminar comillas dobles y simples que pueden causar problemas
            grupo[col] = grupo[col].str.replace('"', "", regex=False)
            grupo[col] = grupo[col].str.replace("'", "", regex=False)
            
            # Eliminar backslashes que pueden causar problemas con escapechar
            grupo[col] = grupo[col].str.replace("\\", "", regex=False)
            
            # Limpiar espacios múltiples que quedan después de los reemplazos
            grupo[col] = grupo[col].str.replace(r"\s+", " ", regex=True)
            
            # Limpiar espacios al inicio y final
            grupo[col] = grupo[col].str.strip()
            
            # Reemplazar strings vacíos resultantes con SINDATO
            grupo[col] = grupo[col].replace("", "SINDATO")

        # Verificar que tengamos exactamente 125 columnas
        if len(grupo.columns) != 125:
            print(
                f"  ⚠ ADVERTENCIA: {nombre_seguro} tiene {len(grupo.columns)} columnas (esperadas: 125)"
            )

        # Guardar CSV con encabezados, delimitado por ';', sin comillas, en UTF-8
        try:
            grupo.to_csv(
                salida_ips,
                index=False,
                header=True,
                sep=";",
                encoding="utf-8-sig",  # UTF-8 con BOM para mejor compatibilidad
                quoting=csv.QUOTE_NONE,
                escapechar="",  # Sin escapechar para evitar problemas
                lineterminator="\n",  # Asegurar terminadores de línea consistentes
            )
            
            # VALIDACIÓN POST-GUARDADO: Verificar que el CSV se guardó correctamente
            with open(salida_ips, "r", encoding="utf-8-sig") as f:
                lineas = f.readlines()
                total_lineas = len(lineas)
                
                # Verificar algunas filas aleatorias para asegurar que tienen 125 columnas
                problemas_encontrados = []
                for idx in [1, min(10, total_lineas-1), min(100, total_lineas-1), total_lineas-1]:
                    if idx < total_lineas:
                        cols = lineas[idx].count(";") + 1
                        if cols != 125:
                            problemas_encontrados.append((idx+1, cols))
                
                if problemas_encontrados:
                    print(f"  ⚠️ ERROR CRÍTICO en {nombre_seguro}:")
                    for fila, cols in problemas_encontrados:
                        print(f"     Fila {fila}: {cols} columnas detectadas (esperadas: 125)")
                else:
                    print(
                        f"  ✔ {salida_ips} ({len(grupo)} registros, {len(grupo.columns)} columnas) - VALIDADO"
                    )
        except Exception as e:
            print(f"  ❌ ERROR al guardar {nombre_seguro}: {str(e)}")
            raise
    print("\n✓ CSV por IPS generados.")
    return carpeta_salida


def separar_por_ips(
    archivo_excel,
    carpeta_salida_base=CARPETA_SALIDA,
    num_filas_a_saltar=NUM_FILAS_A_SALTEAR,
    indice_ips=INDICE_IPS,
):
    return procesar_archivo(
        archivo_excel,
        carpeta_salida_base=carpeta_salida_base,
        num_filas_a_saltar=num_filas_a_saltar,
        indice_ips=indice_ips,
    )


def main():
    args = parsear_args()
    if args.archivo:
        procesar_archivo(args.archivo)
        return

    carpeta = args.carpeta
    patron = "_limpio.xlsx"
    archivos = [
        os.path.join(carpeta, f)
        for f in os.listdir(carpeta)
        if f.lower().endswith(patron)
    ]

    if not archivos:
        print(
            f"No se encontraron archivos '*{patron}' en: {os.path.abspath(carpeta)}"
        )
        return

    for archivo in sorted(archivos):
        procesar_archivo(archivo)


if __name__ == "__main__":
    main()
