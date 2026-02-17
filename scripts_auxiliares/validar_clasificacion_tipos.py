import pandas as pd
import numpy as np

ARCHIVO_EXCEL = "./Procesado_Final.xlsx"

# Las 14 columnas que debería clasificar como TEXTO
INDICES_SUPUESTOS_TEXTO = [3, 20, 35, 40, 42, 61, 70, 78, 79, 80, 119, 122, 123, 125]

# Las 6 que debería clasificar como NUMÉRICA
INDICES_SUPUESTOS_NUMERICOS = [39, 71, 72, 73, 74, 76]

def validar_clasificacion():
    """Valida si la clasificación TEXTO vs NUMÉRICO es correcta"""
    
    print("="*80)
    print("VALIDACIÓN DE CLASIFICACIÓN TEXTO vs NUMÉRICO")
    print("="*80)
    
    df = pd.read_excel(ARCHIVO_EXCEL, header=0)
    encabezados = df.columns.tolist()
    
    print("\n[1] VALIDANDO COLUMNAS CLASIFICADAS COMO 'TEXTO':\n")
    
    for idx_1based in INDICES_SUPUESTOS_TEXTO:
        idx_0based = idx_1based - 1
        col = df.iloc[:, idx_0based]
        nombre = encabezados[idx_0based]
        
        # Obtener tipo pandas
        tipo_pandas = str(col.dtype)
        
        # Intentar convertir a número
        try:
            pd.to_numeric(col.dropna(), errors='coerce')
            numeros_validados = pd.to_numeric(col.dropna(), errors='coerce').count()
            total_valores = col.dropna().count()
            porc_numerico = (numeros_validados / total_valores * 100) if total_valores > 0 else 0
        except:
            porc_numerico = 0
        
        # Ejemplos
        valores_unicos = col.dropna().unique()[:5]
        ejemplos = ", ".join([str(x)[:30] for x in valores_unicos])
        
        print(f"Índice: {idx_1based}")
        print(f"Nombre: {nombre}")
        print(f"Tipo pandas: {tipo_pandas}")
        print(f"% que parecen números: {porc_numerico:.1f}%")
        print(f"Ejemplos: {ejemplos}")
        
        if porc_numerico > 80:
            print("⚠ ALERTA: Podría ser numérica (verifica si es intencional)")
        else:
            print("OK - Clasificación correcta como TEXTO")
        
        print("-" * 80)
    
    print("\n[2] VALIDANDO COLUMNAS CLASIFICADAS COMO 'NUMÉRICA':\n")
    
    for idx_1based in INDICES_SUPUESTOS_NUMERICOS:
        idx_0based = idx_1based - 1
        col = df.iloc[:, idx_0based]
        nombre = encabezados[idx_0based]
        
        tipo_pandas = str(col.dtype)
        
        # Contar valores no-NaN
        valores_no_nulos = col.dropna()
        
        # Intentar detectar si hay texto
        si_es_texto = False
        if col.dtype == 'object':
            si_es_texto = True
        
        ejemplos = valores_no_nulos.unique()[:5]
        ejemplos_str = ", ".join([str(x)[:30] for x in ejemplos])
        
        print(f"Índice: {idx_1based}")
        print(f"Nombre: {nombre}")
        print(f"Tipo pandas: {tipo_pandas}")
        print(f"¿Contiene texto?: {'SI' if si_es_texto else 'NO'}")
        print(f"Ejemplos: {ejemplos_str}")
        
        if si_es_texto:
            print("⚠ ALERTA: Marcada como numérica pero contiene texto")
        else:
            print("OK - Clasificación correcta como NUMÉRICA")
        
        print("-" * 80)

if __name__ == "__main__":
    validar_clasificacion()
