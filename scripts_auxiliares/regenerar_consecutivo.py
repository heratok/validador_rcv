import pandas as pd
import os
import sys

# --- CONFIGURACIÓN ---
ARCHIVO_EXCEL = "prueba.xlsx"
ARCHIVO_SALIDA = "prueba_consecutivo_regenerado.xlsx"
NUM_FILAS_A_SALTEAR = 1
NOMBRE_COLUMNA_CONSECUTIVO = "CONSECUTIVO"


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


def regenerar_consecutivo(
    archivo_entrada, archivo_salida, nombre_columna, filas_a_saltar
):
    """
    Regenera la columna CONSECUTIVO con números secuenciales desde 1
    """
    print(f"\n{'='*80}")
    print("🔧 REGENERADOR DE COLUMNA CONSECUTIVO")
    print(f"{'='*80}\n")

    print(f"Leyendo archivo: {archivo_entrada}")

    try:
        engine = detectar_engine(archivo_entrada)

        # Leer encabezados
        df_headers = pd.read_excel(
            archivo_entrada, header=None, skiprows=0, nrows=1, engine=engine
        )
        encabezados = df_headers.iloc[0].tolist()

        # Buscar la columna CONSECUTIVO
        indice_consecutivo = None
        for i, enc in enumerate(encabezados):
            if str(enc).strip().upper() == nombre_columna.upper():
                indice_consecutivo = i
                break

        if indice_consecutivo is None:
            print(f"❌ No se encontró la columna '{nombre_columna}'")
            print("\n📋 Encabezados disponibles:")
            for i, enc in enumerate(encabezados):
                print(f"  {i}: {enc}")
            return

        print(f"✓ Columna '{nombre_columna}' encontrada en índice {indice_consecutivo}")

        # Leer todos los datos
        df = pd.read_excel(
            archivo_entrada, header=None, skiprows=filas_a_saltar, engine=engine
        )
        print(f"✓ Datos cargados: {len(df)} registros × {len(df.columns)} columnas")

        # Verificar estado actual de la columna
        columna_actual = df.iloc[:, indice_consecutivo]
        valores_vacios = columna_actual.isna().sum()
        valores_presentes = (~columna_actual.isna()).sum()

        print(f"\nEstado actual de '{nombre_columna}':")
        print(f"  • Registros con valor: {valores_presentes}")
        print(f"  • Registros vacíos: {valores_vacios}")

        # Regenerar consecutivo
        print(f"\n🔄 Regenerando columna con números secuenciales...")
        df.iloc[:, indice_consecutivo] = range(1, len(df) + 1)

        print(f"✓ Columna regenerada: {len(df)} números secuenciales (1 a {len(df)})")

        # Guardar archivo
        print(f"\n💾 Guardando archivo: {archivo_salida}")

        # Crear índices de nombre para las columnas
        nombres_columnas = encabezados
        df.columns = nombres_columnas

        try:
            df.to_excel(archivo_salida, index=False, header=True)
            print(f"\n✓ ¡Archivo generado exitosamente!")
            print(f"  Ubicación: {os.path.abspath(archivo_salida)}")
            print(f"  Registros: {len(df)}")
            print(f"  Columnas: {len(df.columns)}")

            # Mostrar preview
            print(f"\n📋 Preview de la columna '{nombre_columna}' regenerada:")
            print(df[[nombre_columna]].head(10).to_string())
            print(f"  ...")
            print(df[[nombre_columna]].tail(5).to_string())

        except Exception as e:
            print(f"❌ Error al guardar: {e}")
            return

    except FileNotFoundError:
        print(f"❌ Error: El archivo '{archivo_entrada}' no se encontró.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Permite cambiar el archivo mediante argumentos
    if len(sys.argv) > 1:
        archivo_entrada = sys.argv[1]
        archivo_salida = sys.argv[2] if len(sys.argv) > 2 else ARCHIVO_SALIDA
    else:
        archivo_entrada = ARCHIVO_EXCEL
        archivo_salida = ARCHIVO_SALIDA

    regenerar_consecutivo(
        archivo_entrada, archivo_salida, NOMBRE_COLUMNA_CONSECUTIVO, NUM_FILAS_A_SALTEAR
    )
