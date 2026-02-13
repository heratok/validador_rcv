import pandas as pd
import os

ARCHIVO_EXCEL = "rcv_cesar.xlsx"
ARCHIVO_SALIDA = "Medicamentos_SINDATO.xlsx"
NUM_FILAS_A_SALTEAR = 1


def detectar_engine(archivo):
    ext = os.path.splitext(archivo)[1].lower()
    if ext == ".xlsb":
        try:
            import pyxlsb

            return "pyxlsb"
        except ImportError:
            print("Instalando pyxlsb...")
            import subprocess
            import sys

            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyxlsb"])
            return "pyxlsb"
    elif ext == ".xlsx":
        return "openpyxl"
    return None


def buscar_columnas_rango(archivo):
    print(f"Leyendo encabezados de: {archivo}\n")

    engine = detectar_engine(archivo)

    # Leer encabezados
    df_headers = pd.read_excel(archivo, header=None, skiprows=0, nrows=1, engine=engine)
    encabezados = df_headers.iloc[0].tolist()

    # Información general del archivo
    print(f"📊 INFORMACIÓN DEL ARCHIVO")
    print("=" * 80)
    print(f"Total de columnas en el archivo: {len(encabezados)}")
    print(f"Última columna (índice {len(encabezados)-1}): '{encabezados[-1]}'")
    print("=" * 80)
    print()

    # Buscar columnas que empiecen con "Medicamento"
    columnas_encontradas = []

    print("Buscando columnas con encabezados 'Medicamento', 'Medicamento2', etc...")
    print("=" * 80)

    for i, encabezado in enumerate(encabezados):
        enc_str = str(encabezado).strip()
        # Buscar columnas que empiecen con "Medicamento"
        if enc_str.lower().startswith("medicamento"):
            columnas_encontradas.append({"indice": i, "nombre": enc_str})
            print(f"✓ Encontrada en índice {i}: '{encabezado}'")

    print("=" * 80)
    print(f"\nTotal de columnas 'Medicamento' encontradas: {len(columnas_encontradas)}")

    if columnas_encontradas:
        # Ordenar por índice
        columnas_encontradas.sort(key=lambda x: x["indice"])

        print("\nResumen de columnas encontradas:")
        for col_info in columnas_encontradas:
            print(f"  Índice {col_info['indice']}: {col_info['nombre']}")

        # Extraer las columnas del DataFrame completo
        print("\n" + "=" * 80)
        print("PROCESANDO COLUMNAS MEDICAMENTO...")
        print("=" * 80)

        indices = [col_info["indice"] for col_info in columnas_encontradas]

        # Leer el archivo completo con datos
        print(f"\nLeyendo archivo completo: {ARCHIVO_EXCEL}")
        if ARCHIVO_EXCEL.endswith(".xlsb"):
            df = pd.read_excel(
                ARCHIVO_EXCEL,
                engine="pyxlsb",
                skiprows=NUM_FILAS_A_SALTEAR,
                header=None,
            )
        else:
            df = pd.read_excel(
                ARCHIVO_EXCEL,
                engine="openpyxl",
                skiprows=NUM_FILAS_A_SALTEAR,
                header=None,
            )

        print(f"Total de filas leídas del archivo original: {len(df)}")
        print(
            f"(Sin contar la fila {NUM_FILAS_A_SALTEAR} que se saltó como encabezado)"
        )

        # Seleccionar solo las columnas Medicamento
        df_medicamentos = df.iloc[:, indices].copy()

        # Renombrar las columnas con los nombres encontrados
        nombres_columnas = [col_info["nombre"] for col_info in columnas_encontradas]
        df_medicamentos.columns = nombres_columnas

        print(
            f"Datos extraídos: {len(df_medicamentos)} filas, {len(df_medicamentos.columns)} columnas"
        )

        # Procesar cada columna: reemplazar vacíos y ceros con "SINDATO"
        print("\nReemplazando valores vacíos y ceros con 'SINDATO'...")

        for columna in df_medicamentos.columns:
            serie_original = df_medicamentos[columna]

            # Contar valores vacíos antes
            vacios_antes = serie_original.isna().sum()

            # Contar valores que son 0 en diferentes formatos (numérico o texto)
            cero_like_mask = (
                serie_original.astype(str)
                .str.strip()
                .str.replace(",", ".")
                .isin(["0", "0.0", "0.00"])
            )
            ceros_antes = cero_like_mask.sum()

            # Reemplazar espacios vacíos, variantes de cero y fecha comodín por NaN
            df_medicamentos[columna] = serie_original.replace(
                r"^\s*$", pd.NA, regex=True
            )
            df_medicamentos[columna] = df_medicamentos[columna].replace(
                {
                    0: pd.NA,
                    0.0: pd.NA,
                    "0": pd.NA,
                    "0.0": pd.NA,
                    "0.00": pd.NA,
                    "0,0": pd.NA,
                    "0,00": pd.NA,
                    "1800-01-01": pd.NA,
                }
            )

            # Llenar cualquier NaN resultante con la marca
            df_medicamentos[columna] = df_medicamentos[columna].fillna("SINDATO")

            total_reemplazos = vacios_antes + ceros_antes
            if total_reemplazos > 0:
                print(
                    f"  {columna}: {vacios_antes} vacíos + {ceros_antes} ceros = {total_reemplazos} reemplazos"
                )

        # Guardar el archivo de salida
        print(f"\nGuardando archivo: {ARCHIVO_SALIDA}")
        df_medicamentos.to_excel(ARCHIVO_SALIDA, index=False, engine="openpyxl")

        print(f"\n✓ Archivo generado exitosamente: {ARCHIVO_SALIDA}")
        print(f"  - Columnas incluidas: {len(df_medicamentos.columns)}")
        print(f"  - Total de filas: {len(df_medicamentos)}")
    else:
        print("\n⚠ No se encontraron columnas 'Medicamento'")


if __name__ == "__main__":
    buscar_columnas_rango(ARCHIVO_EXCEL)
