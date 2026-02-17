"""
Script para verificar los índices de las columnas y confirmar la correspondencia
entre números de columna Excel (1-based) e índices pandas (0-based).

Uso:
    python verificar_indices_columnas.py
"""
import pandas as pd
import os

ARCHIVO = "rcv_cesar.xlsx"
NUM_FILAS_A_SALTEAR = 1


def detectar_engine(archivo):
    ext = os.path.splitext(archivo)[1].lower()
    if ext == ".xlsb":
        try:
            import pyxlsb  # noqa: F401
            return "pyxlsb"
        except ImportError:
            print("Falta pyxlsb. Instalar con: pip install pyxlsb")
            return None
    if ext == ".xlsx":
        return "openpyxl"
    return None


def leer_encabezados(archivo):
    engine = detectar_engine(archivo)
    if not engine:
        return []
    try:
        df_headers = pd.read_excel(
            archivo, header=None, skiprows=0, nrows=1, engine=engine
        )
        return df_headers.iloc[0].tolist()
    except Exception as e:
        print(f"Error al leer encabezados: {e}")
        return []


def numero_a_letra_columna(n):
    """Convierte número de columna (1-based) a letra de Excel (A, B, C, ...)"""
    resultado = ""
    while n > 0:
        n -= 1
        resultado = chr(65 + (n % 26)) + resultado
        n //= 26
    return resultado


def main():
    print("=" * 100)
    print("VERIFICACIÓN DE ÍNDICES DE COLUMNAS")
    print("=" * 100)
    print()
    
    encabezados = leer_encabezados(ARCHIVO)
    if not encabezados:
        print("No se pudieron leer los encabezados.")
        return
    
    print(f"Total de columnas: {len(encabezados)}")
    print()
    print(f"{'Excel':>6} | {'1-based':>8} | {'0-based':>8} | {'Letra':>6} | Nombre del encabezado")
    print("-" * 100)
    
    for idx, nombre in enumerate(encabezados):
        col_excel = idx + 1  # 1-based
        col_pandas = idx     # 0-based
        letra = numero_a_letra_columna(col_excel)
        nombre_str = str(nombre).strip() if nombre else "(vacío)"
        
        print(f"{col_excel:6d} | {col_excel:8d} | {col_pandas:8d} | {letra:>6} | {nombre_str}")
    
    print()
    print("=" * 100)
    print("EXPLICACIÓN:")
    print("  - 1-based: número de columna contando desde 1 (A=1, B=2, ..., usado en el JSON)")
    print("  - 0-based: índice pandas (A=0, B=1, ..., usado internamente en Python)")
    print("  - Para usar en validaciones_config.json: usar valor '1-based'")
    print("  - El código Python restará 1 automáticamente para acceder a la columna correcta")
    print()


if __name__ == "__main__":
    main()
