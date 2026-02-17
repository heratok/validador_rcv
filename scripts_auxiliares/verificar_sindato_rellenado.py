import pandas as pd

ARCHIVO_EXCEL = "./Procesado_Final.xlsx"

# Las 14 columnas que deberían haber sido rellenadas con SINDATO
INDICES_SINDATO = [2, 19, 34, 39, 41, 60, 69, 77, 78, 79, 118, 121, 122, 124]

df = pd.read_excel(ARCHIVO_EXCEL, header=0)
encabezados = df.columns.tolist()

print("="*80)
print("VERIFICACIÓN: COLUMNAS RELLENADAS CON SINDATO")
print("="*80)
print()

for idx_0based in INDICES_SINDATO:
    idx_1based = idx_0based + 1
    col = df.iloc[:, idx_0based]
    nombre = encabezados[idx_0based]
    
    # Contar SINDATO
    count_sindato = (col == "SINDATO").sum()
    count_vacios = col.isna().sum()
    total = len(df)
    
    # Otros valores
    otros_valores = col[col != "SINDATO"].dropna().unique()[:3]
    otros_str = ", ".join([str(x)[:30] for x in otros_valores])
    
    print(f"[{idx_1based:3d}] {nombre[:50]}")
    print(f"      SINDATO: {count_sindato:,} | Vacíos (NaN): {count_vacios} | Total: {total:,}")
    print(f"      Otros valores: {otros_str if len(otros_valores) > 0 else '(solo SINDATO)'}")
    print()

print("="*80)
print("OK - Verificación completada")
print("="*80)
