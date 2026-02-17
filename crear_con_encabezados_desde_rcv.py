import os
import pandas as pd

# --- CONFIGURACION ---
BASE_DIR = "."
ARCHIVO_ENCABEZADOS = "rcv_cesar.xlsx"
DATA_START_ROW = 4  # 1-based; datos empiezan en fila 4


def detectar_engine(archivo):
    ext = os.path.splitext(archivo)[1].lower()
    if ext == ".xlsb":
        return "pyxlsb"
    if ext in [".xlsx", ".xls"]:
        return "openpyxl"
    return None


def leer_encabezados(archivo):
    engine = detectar_engine(archivo)
    if not engine:
        raise ValueError(f"Formato no soportado para encabezados: {archivo}")
    df_headers = pd.read_excel(archivo, header=None, skiprows=0, nrows=1, engine=engine)
    return df_headers.iloc[0].tolist()


def procesar_archivo(ruta_archivo, encabezados):
    engine = detectar_engine(ruta_archivo)
    if not engine:
        print(f"Saltando (formato no soportado): {ruta_archivo}")
        return

    # Leer datos desde fila 4 (skiprows=3), sin encabezados
    df = pd.read_excel(ruta_archivo, header=None, skiprows=DATA_START_ROW - 1, engine=engine)

    # Ajustar encabezados al numero de columnas reales
    if len(df.columns) <= len(encabezados):
        columnas = encabezados[: len(df.columns)]
    else:
        columnas = encabezados
        df = df.iloc[:, : len(encabezados)]
        print(
            f"Aviso: {os.path.basename(ruta_archivo)} tiene {len(df.columns)} columnas, "
            f"encabezados base {len(encabezados)}. Se recortan columnas extra."
        )

    df_salida = pd.DataFrame(df.values, columns=columnas)

    # Guardar como .xlsx con sufijo
    base, _ = os.path.splitext(ruta_archivo)
    salida = f"{base}_con_encabezados.xlsx"
    df_salida.to_excel(salida, index=False)

    print(f"OK - Generado: {salida}")


def main():
    encabezados = leer_encabezados(ARCHIVO_ENCABEZADOS)
    if not encabezados:
        print("No se pudieron leer encabezados.")
        return

    for root, dirs, files in os.walk(BASE_DIR):
        # Evitar procesar la carpeta scripts_auxiliares y reportes
        if os.path.basename(root).lower() in ["scripts_auxiliares", "reportes", "__pycache__", ".git"]:
            continue

        for nombre in files:
            if nombre.startswith("~$"):
                continue
            if not nombre.lower().endswith(".xlsb"):
                continue
            ruta = os.path.join(root, nombre)
            # Evitar el archivo de encabezados si es xlsb
            if os.path.abspath(ruta) == os.path.abspath(ARCHIVO_ENCABEZADOS):
                continue
            procesar_archivo(ruta, encabezados)


if __name__ == "__main__":
    main()
