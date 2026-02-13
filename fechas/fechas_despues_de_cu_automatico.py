import pandas as pd
from datetime import datetime

ARCHIVO_ORIGINAL = "./BD_RCCVM_OCTUBRE _2025_DUSKEPSI.xlsb"
ARCHIVO_SALIDA = "Fechas_despues_de_CU_automatico.xlsx"
NUM_FILAS_A_SALTEAR = 2
INDICE_CU = 98
FECHAS_ESPECIALES = {"1800-01-01", "1845-01-01", "1845-01-02"}


def es_fecha_especial(valor):
    if isinstance(valor, str):
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            return valor in FECHAS_ESPECIALES
        except Exception:
            return False
    return False


def es_valor_fecha(valor):
    if pd.isnull(valor):
        return False
    if isinstance(valor, str):
        val = valor.strip().upper()
        if val in ("NORMAL", "NO APLICA", "SI"):
            return True
        # ¿Parece fecha?
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                _ = datetime.strptime(valor, fmt)
                return True
            except Exception:
                continue
        if valor in FECHAS_ESPECIALES:
            return True
    try:
        # ¿Es número tipo Excel?
        num = float(valor)
        if 20000 < num < 90000:
            return True
    except Exception:
        pass
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
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                fecha = datetime.strptime(valor, fmt)
                return fecha.strftime("%Y/%m/%d")
            except Exception:
                continue
    try:
        num = float(valor)
        fecha = pd.to_datetime(num - 2, unit="D", origin="1900-01-01", errors="raise")
        fecha_str = fecha.strftime("%Y/%m/%d")
        return fecha_str
    except Exception:
        return None


def detectar_columnas_fecha(df, desde_indice):
    columnas_fecha = []
    for idx in range(desde_indice + 1, len(df.columns)):
        col = df[idx]
        # Tomar una muestra de los primeros 30 valores no nulos
        muestra = col.dropna().head(30)
        if len(muestra) == 0:
            continue
        # Si al menos 60% de la muestra parece fecha, la consideramos fecha
        n_fecha = sum(es_valor_fecha(v) for v in muestra)
        if len(muestra) > 0 and n_fecha / len(muestra) >= 0.6:
            columnas_fecha.append(idx)
    return columnas_fecha


def estandarizar_columnas_fecha_automatico(
    archivo_entrada, archivo_salida, indice_cu, filas_a_saltar
):
    print(f"Leyendo archivo: {archivo_entrada}")
    df = pd.read_excel(
        archivo_entrada, header=None, skiprows=filas_a_saltar, engine="pyxlsb"
    )
    print(f"Archivo leído. Columnas totales: {len(df.columns)}")
    columnas_fecha = detectar_columnas_fecha(df, indice_cu)
    print(
        f"Columnas detectadas como fecha después de CU (índice {indice_cu}): {columnas_fecha}"
    )
    df_salida = pd.DataFrame()
    for idx in columnas_fecha:
        print(f"Procesando columna índice {idx}...")
        fechas_final = []
        errores = []
        for i, valor in df[idx].items():
            resultado = convertir_o_dejar(valor)
            # Si es la columna 119 y el valor es None o vacío, poner comodín
            if idx == 119 and (resultado is None or resultado == ""):
                fechas_final.append("1800/01/01")
            elif resultado is None:
                errores.append((i + 1, valor))
                fechas_final.append("")
            else:
                fechas_final.append(resultado)
        if errores:
            print(
                f"Advertencia: No se pudo convertir algunos valores en columna {idx}:"
            )
            for fila, valor in errores:
                print(f"  Fila {fila}: '{valor}'")
        df_salida[f"Col_{idx}_Normalizada"] = fechas_final
    print(f"\nGuardando columnas normalizadas en: {archivo_salida}")
    try:
        df_salida.to_excel(archivo_salida, index=False, header=True)
        print(
            "¡Proceso completado! Archivo de salida creado con columnas normalizadas."
        )
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")


if __name__ == "__main__":
    estandarizar_columnas_fecha_automatico(
        ARCHIVO_ORIGINAL, ARCHIVO_SALIDA, INDICE_CU, NUM_FILAS_A_SALTEAR
    )
