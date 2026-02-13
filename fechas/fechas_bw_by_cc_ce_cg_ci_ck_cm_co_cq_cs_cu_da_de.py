import pandas as pd
from datetime import datetime

ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Fechas_BW_BY_CC_CE_CG_CI_CK_CM_CO_CQ_CS_CU_DA_DE_Estandarizadas.xlsx"
COLUMNAS = {
    "BW": 74,
    "BY": 76,
    "CC": 80,
    "CE": 82,
    "CG": 84,
    "CI": 86,
    "CK": 88,
    "CM": 90,
    "CO": 92,
    "CQ": 94,
    "CS": 96,
    "CU": 98,
    "DA": 100,
    "DE": 104,
}
NUM_FILAS_A_SALTEAR = 2
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
    # Si es fecha especial, devolver con '/' como separador
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


def estandarizar_varias_columnas_fechas(
    archivo_entrada, archivo_salida, columnas, filas_a_saltar
):
    print(f"Iniciando la lectura del archivo: {archivo_entrada}")
    df = pd.read_excel(
        archivo_entrada, header=None, skiprows=filas_a_saltar, engine="pyxlsb"
    )
    print(f"Datos cargados correctamente. Registros: {len(df)}")
    df_salida = pd.DataFrame()
    for col_letra, col_idx in columnas.items():
        print(f"Procesando columna {col_letra} (índice {col_idx})...")
        columna = df[col_idx]
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
        print(
            "¡Proceso completado! Archivo de salida creado con todas las columnas normalizadas."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


if __name__ == "__main__":
    estandarizar_varias_columnas_fechas(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, COLUMNAS, NUM_FILAS_A_SALTEAR
    )
