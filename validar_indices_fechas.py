import pandas as pd
import os
from datetime import datetime

ARCHIVO_ORIGINAL = "limpieza.xlsx"
NUM_FILAS_A_SALTEAR = 2

# Índices a verificar (los que usamos en procesar_todas_fechas.py)
INDICES_A_VERIFICAR = [
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

print(f"Leyendo archivo: {ARCHIVO_ORIGINAL}")
try:
    # Detectar el engine según la extensión
    ext = os.path.splitext(ARCHIVO_ORIGINAL)[1].lower()
    if ext == ".xlsb":
        df = pd.read_excel(
            ARCHIVO_ORIGINAL, header=None, skiprows=NUM_FILAS_A_SALTEAR, engine="pyxlsb"
        )
    else:
        df = pd.read_excel(ARCHIVO_ORIGINAL, header=None, skiprows=NUM_FILAS_A_SALTEAR)

    print(f"Total de columnas en el archivo: {len(df.columns)}")
    print(f"Total de filas: {len(df)}\n")
    print("Validando índices de columnas...\n")

    indices_validos = {}
    indices_invalidos = {}

    for indice in INDICES_A_VERIFICAR:
        if indice >= len(df.columns):
            indices_invalidos[indice] = "ERROR: Índice fuera de rango"
            continue

        col = df[indice]
        primeros_10 = col.head(10)

        # Contar cuántos valores son fechas válidas
        contador_fechas = 0
        tipo_datos = set()

        for valor in primeros_10:
            if pd.isnull(valor):
                continue

            tipo_datos.add(type(valor).__name__)

            if isinstance(valor, (pd.Timestamp, datetime)):
                contador_fechas += 1
            elif isinstance(valor, str):
                val_clean = valor.strip()
                # Verificar fechas especiales
                if val_clean in ("1800-01-01", "1845-01-01", "1845-01-02"):
                    contador_fechas += 1
                # Verificar formato YYYY-MM-DD
                elif len(val_clean) == 10 and "-" in val_clean:
                    try:
                        datetime.strptime(val_clean, "%Y-%m-%d")
                        contador_fechas += 1
                    except:
                        pass

        porcentaje = (
            (contador_fechas / len(primeros_10)) * 100 if len(primeros_10) > 0 else 0
        )

        # Si menos del 50% son fechas, marcar como inválido
        if contador_fechas < 5:  # Menos de 50% de 10
            indices_invalidos[indice] = (
                f"❌ Solo {contador_fechas}/10 son fechas ({porcentaje:.0f}%) - Tipos: {tipo_datos}"
            )
        else:
            valores_no_nulos = col.dropna().shape[0]
            primeros_5 = col.head(5).tolist()
            indices_validos[indice] = {
                "valores_no_nulos": valores_no_nulos,
                "primeros_5": primeros_5,
                "porcentaje_fecha": porcentaje,
                "tipos": tipo_datos,
            }

    print("=" * 80)
    print("✅ ÍNDICES VÁLIDOS (contienen fechas):")
    print("=" * 80)
    for indice in sorted(indices_validos.keys()):
        data = indices_validos[indice]
        print(
            f"\nÍndice {indice}: ✅ {data['valores_no_nulos']} valores no nulos ({data['porcentaje_fecha']:.0f}% fechas)"
        )
        print(f"  Primeros 5: {data['primeros_5']}")
        print(f"  Tipos de datos: {data['tipos']}")

    print("\n" + "=" * 80)
    print("❌ ÍNDICES INVÁLIDOS (NO contienen fechas):")
    print("=" * 80)
    for indice in sorted(indices_invalidos.keys()):
        print(f"Índice {indice}: {indices_invalidos[indice]}")

    print("\n" + "=" * 80)
    print("RESUMEN:")
    print("=" * 80)
    print(f"Total verificados: {len(INDICES_A_VERIFICAR)}")
    print(f"Válidos (con fechas): {len(indices_validos)}")
    print(f"Inválidos (sin fechas): {len(indices_invalidos)}")
    print(f"\n✅ Índices para procesar_todas_fechas.py:")
    print(f"{sorted(indices_validos.keys())}")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
