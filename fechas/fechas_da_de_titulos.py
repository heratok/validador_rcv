import pandas as pd
from datetime import datetime

ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Fechas_DA_DE_TITULOS_Estandarizadas.xlsx"
TITULO_DA = "FECHA DE PROXIMO CONTROL"
TITULO_DE = "FECHA DE LA ULTIMA TOMA DE PRESION ARTERIAL REPORTADO EN HISTORIA CLÍNICA"
NUM_FILAS_A_SALTEAR = 1  # Asumimos que la fila 2 tiene los títulos
FECHAS_ESPECIALES = {"1800-01-01", "1845-01-01", "1845-01-02"}


def es_fecha_especial(valor):
    if isinstance(valor, str):
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            return valor in FECHAS_ESPECIALES
        except Exception:
            return False
    return False


def convertir_o_dejar(valor):
    if pd.isnull(valor):
        return ""
    if isinstance(valor, str):
        val = valor.strip().upper()
        if val == "NORMAL":
            return "1800/01/01"
        if val in ("NO APLICA", "SI"):
            return "1845/01/01"
    if es_fecha_especial(valor):
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            return fecha.strftime("%Y/%m/%d")
        except Exception:
            if isinstance(valor, str) and valor in FECHAS_ESPECIALES:
                return valor.replace("-", "/")
            return valor
    if isinstance(valor, str):
        try:
            fecha = datetime.strptime(valor, "%d/%m/%Y")
            return fecha.strftime("%Y/%m/%d")
        except Exception:
            pass
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            return fecha.strftime("%Y/%m/%d")
        except Exception:
            pass
    try:
        num = float(valor)
        fecha = pd.to_datetime(num - 2, unit="D", origin="1900-01-01", errors="raise")
        fecha_str = fecha.strftime("%Y/%m/%d")
        return fecha_str
    except Exception:
        return None


def estandarizar_columnas_da_de_por_titulo(
    archivo_entrada, archivo_salida, titulo_da, titulo_de, filas_a_saltar
):
    print(f"Iniciando la lectura del archivo: {archivo_entrada}")
    df = pd.read_excel(
        archivo_entrada, header=0, skiprows=filas_a_saltar, engine="pyxlsb"
    )
    print(f"Datos cargados correctamente. Registros: {len(df)}")
    if titulo_da not in df.columns or titulo_de not in df.columns:
        print("No se encontraron los títulos DA o DE en el archivo.")
        return
    columnas = {"DA": titulo_da, "DE": titulo_de}
    df_salida = pd.DataFrame()
    for col_letra, col_titulo in columnas.items():
        print(f"Procesando columna {col_letra} (título '{col_titulo}')...")
        columna = df[col_titulo]
        fechas_final = []
        errores = []
        for idx, valor in columna.items():
            resultado = convertir_o_dejar(valor)
            if resultado is None:
                errores.append((idx + 1, valor))
                fechas_final.append("")
            else:
                fechas_final.append(resultado)
        if errores:
            print(
                f"Advertencia: No se pudo convertir los siguientes valores en columna {col_letra}:"
            )
            for fila, valor in errores:
                print(f"  Fila {fila}: '{valor}'")
        else:
            print(
                f"Todas las fechas de {col_letra} fueron convertidas correctamente o son especiales."
            )
        df_salida[f"{col_letra}_Normalizada"] = fechas_final
    print(f"\nGuardando columnas normalizadas en: {archivo_salida}")
    try:
        df_salida.to_excel(archivo_salida, index=False, header=True)
        print("¡Proceso completado! Archivo de salida creado con DA y DE normalizadas.")
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


if __name__ == "__main__":
    estandarizar_columnas_da_de_por_titulo(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, TITULO_DA, TITULO_DE, NUM_FILAS_A_SALTEAR
    )
