import pandas as pd

ARCHIVO_EXCEL = "./Procesado_Final.xlsx"

df = pd.read_excel(ARCHIVO_EXCEL, header=0)

# Buscar la columna COMPLICACIONES
for idx, col_name in enumerate(df.columns):
    if "COMPLICACION" in str(col_name).upper():
        print(f"Índice {idx} (0-based) | Índice {idx+1} (1-based)")
        print(f"Nombre: {col_name}")
        print(f"\nPrimeros 20 valores únicos:")
        print(df.iloc[:, idx].value_counts().head(20))
        print(f"\n¿Contiene '1800'?")
        print(df.iloc[:, idx].astype(str).str.contains("1800", na=False).sum())
        break
