import pandas as pd
import os
import sys

# --- CONFIGURACIÓN ---
ARCHIVO_EXCEL = "prueba.xlsx"
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


def buscar_valores_unicos(archivo, encabezado_buscado, filas_a_saltar):
    """
    Busca una columna por su encabezado y muestra todos los valores únicos
    """
    print(f"Leyendo archivo: {archivo}")

    try:
        # Detectar el engine según la extensión
        ext = os.path.splitext(archivo)[1].lower()
        if ext == ".xlsb":
            try:
                import pyxlsb

                engine = "pyxlsb"
            except ImportError:
                print("Instalando pyxlsb...")
                import subprocess

                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "pyxlsb"]
                )
                engine = "pyxlsb"
        elif ext == ".xlsx":
            engine = "openpyxl"
        else:
            engine = None

        # Leer encabezados (primera fila)
        df_headers = pd.read_excel(
            archivo, header=None, skiprows=0, nrows=1, engine=engine
        )
        encabezados = df_headers.iloc[0].tolist()

        # Buscar el índice de la columna
        indice_columna = None
        for i, enc in enumerate(encabezados):
            if str(enc).strip().upper() == encabezado_buscado.strip().upper():
                indice_columna = i
                break

        if indice_columna is None:
            print(
                f"\n❌ No se encontró la columna con encabezado: '{encabezado_buscado}'"
            )
            print("\n📋 Encabezados disponibles (excluyendo columnas de fechas):")
            for i, enc in enumerate(encabezados):
                if i not in INDICES_FECHAS:
                    print(f"  {i}: {enc}")
            return

        # Verificar que no sea una columna de fecha
        if indice_columna in INDICES_FECHAS:
            print(
                f"\n⚠️  La columna '{encabezados[indice_columna]}' (índice {indice_columna}) es una columna de fechas."
            )
            print(
                "Este script solo busca en columnas NO-fecha para análisis de texto/trim."
            )
            return

        print(
            f"✓ Columna encontrada en índice {indice_columna}: '{encabezados[indice_columna]}'"
        )

        # Leer datos
        df = pd.read_excel(archivo, header=None, skiprows=filas_a_saltar, engine=engine)
        columna = df.iloc[:, indice_columna]

        # Obtener valores únicos (excluyendo NaN)
        valores_unicos = columna.dropna().unique()

        print(f"\n📊 Total de valores únicos: {len(valores_unicos)}")
        print(f"📊 Total de registros en la columna: {len(columna)}")

        # Detectar valores con espacios en blanco al inicio o final
        valores_con_espacios = []
        for valor in valores_unicos:
            valor_str = str(valor)
            if valor_str != valor_str.strip():
                valores_con_espacios.append(valor_str)

        if valores_con_espacios:
            print(
                f"\n⚠️  ATENCIÓN: {len(valores_con_espacios)} valores tienen espacios extras (necesitan TRIM):"
            )
            for val in valores_con_espacios[:10]:
                print(f"    '{val}' (len: {len(val)})")
            if len(valores_con_espacios) > 10:
                print(f"    ... y {len(valores_con_espacios) - 10} más")

        print(f"\n🔍 Valores únicos encontrados:\n")

        for i, valor in enumerate(sorted(valores_unicos.astype(str)), 1):
            cantidad = (columna == valor).sum()
            # Indicar si tiene espacios
            tiene_espacios = "⚠️ " if str(valor) != str(valor).strip() else ""
            print(f"  {i}. {tiene_espacios}'{valor}' → {cantidad} veces")

    except FileNotFoundError:
        print(f"❌ Error: El archivo '{archivo}' no se encontró.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Puedes cambiar el encabezado aquí o pasarlo como argumento
    if len(sys.argv) > 1:
        encabezado = sys.argv[1]
    else:
        encabezado = "TI IDENTIFICIÓN"  # Valor por defecto

    print(f"\n🔎 Buscando columna: '{encabezado}'\n")
    buscar_valores_unicos(ARCHIVO_EXCEL, encabezado, NUM_FILAS_A_SALTEAR)
