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


def obtener_carpeta_mes(archivo):
    base = os.path.basename(archivo)
    nombre, _ext = os.path.splitext(base)
    prefijo = nombre.split("_")[0].strip().lower()
    mapa = {"nov": "noviembre", "dic": "diciembre", "ene": "enero"}
    carpeta_mes = mapa.get(prefijo, prefijo or "otros")
    return os.path.join(CARPETA_SALIDA, carpeta_mes)


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


def procesar_archivo(archivo_excel):
    print("Leyendo archivo:", archivo_excel)
    engine = detectar_engine(archivo_excel)
    df_headers = pd.read_excel(
        archivo_excel, header=None, skiprows=0, nrows=1, engine=engine
    )
    encabezados = df_headers.iloc[0].tolist()

    df = pd.read_excel(
        archivo_excel, header=None, skiprows=NUM_FILAS_A_SALTEAR, engine=engine
    )
    if INDICE_IPS >= len(df.columns):
        print(f"El índice {INDICE_IPS} no existe en el archivo.")
        return

    # Asignar nombres de columnas usando encabezados
    df.columns = [str(h) for h in encabezados]
    nombre_col_ips = df.columns[INDICE_IPS]

    print(f"Agrupando por IPS en columna índice {INDICE_IPS} - '{nombre_col_ips}'")
    print(f"Total de columnas en el archivo original: {len(df.columns)}")

    # Crear consecutivo por IPS (1..n dentro de cada grupo) - temporal
    df[NOMBRE_CONSECUTIVO_IPS] = df.groupby(nombre_col_ips).cumcount() + 1

    # Ordenar por IPS y consecutivo para claridad
    df_ordenado = df.sort_values(by=[nombre_col_ips, NOMBRE_CONSECUTIVO_IPS])

    # Generar CSV separados por IPS
    carpeta_salida = obtener_carpeta_mes(archivo_excel)
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

        # Limpiar punto y coma (;) de TODAS las columnas para evitar problemas con el delimitador
        for col in grupo.columns:
            grupo[col] = grupo[col].astype(str).str.replace(";", "", regex=False)

        # Verificar que tengamos exactamente 125 columnas
        if len(grupo.columns) != 125:
            print(
                f"  ⚠ ADVERTENCIA: {nombre_seguro} tiene {len(grupo.columns)} columnas (esperadas: 125)"
            )

        # Guardar CSV con encabezados, delimitado por ';', sin comillas, en UTF-8
        grupo.to_csv(
            salida_ips,
            index=False,
            header=True,
            sep=";",
            encoding="utf-8",
            quoting=csv.QUOTE_NONE,
            escapechar="\\",
        )
        print(
            f"  ✔ {salida_ips} ({len(grupo)} registros, {len(grupo.columns)} columnas)"
        )
    print("\n✓ CSV por IPS generados.")


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
