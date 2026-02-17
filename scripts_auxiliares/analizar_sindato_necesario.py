import pandas as pd

# --- CONFIGURACIÓN ---
ARCHIVO_EXCEL = "./Procesado_Final.xlsx"

# Índices de columnas DE FECHAS (0-based)
INDICES_FECHAS = [
    7, 23, 27, 29, 43, 45, 47, 49, 51, 53, 58, 59, 61, 64, 66, 68,
    74, 76, 80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104,
    108, 119, 123,
]

def analizar_columnas_para_sindato():
    """Analiza qué columnas NO-fecha deberían rellenarse con SINDATO"""
    
    print("="*80)
    print("ANÁLISIS: COLUMNAS PARA RELLENAR CON 'SINDATO'")
    print("="*80)
    print(f"Archivo: {ARCHIVO_EXCEL}\n")
    
    # Leer datos
    try:
        df = pd.read_excel(ARCHIVO_EXCEL, header=0)
        print(f"OK - Datos cargados: {len(df)} registros, {len(df.columns)} columnas\n")
    except Exception as e:
        print(f"Error al leer archivo: {e}")
        return
    
    encabezados = df.columns.tolist()
    
    columnas_para_sindato = []
    columnas_numericas_vacias = []
    
    # Revisar todas las columnas NO-fecha
    print("Analizando columnas NO-fecha...\n")
    
    for indice in range(len(df.columns)):
        if indice in INDICES_FECHAS:
            continue  # Saltar columnas de fechas
        
        col = df.iloc[:, indice]
        nombre_col = encabezados[indice] if indice < len(encabezados) else f"Columna_{indice}"
        
        # Contar valores vacíos
        vacios = col.isna().sum()
        vacios_str = (col.astype(str).str.strip() == '').sum() if col.dtype == 'object' else 0
        total_vacios = max(vacios, vacios_str)
        
        if total_vacios > 0:
            porcentaje = (total_vacios / len(df)) * 100
            tipo_datos = str(col.dtype)
            
            # Clasificar
            if col.dtype == 'object' or col.dtype == 'str':
                # Columna de TEXTO
                columnas_para_sindato.append({
                    'indice_0based': indice,
                    'indice_1based': indice + 1,
                    'nombre': nombre_col,
                    'vacios': total_vacios,
                    'porcentaje': porcentaje,
                    'tipo': 'TEXTO',
                    'recomendacion': 'SI - Rellenar con SINDATO'
                })
            else:
                # Columna NUMÉRICA
                columnas_numericas_vacias.append({
                    'indice_0based': indice,
                    'indice_1based': indice + 1,
                    'nombre': nombre_col,
                    'vacios': total_vacios,
                    'porcentaje': porcentaje,
                    'tipo': tipo_datos,
                    'recomendacion': 'NO - Dejar como NaN (número vacío)'
                })
    
    # Mostrar resultados
    if columnas_para_sindato:
        print("=" * 80)
        print("COLUMNAS DE TEXTO CON VACÍOS - CANDIDATAS PARA SINDATO")
        print("=" * 80)
        print()
        
        for col_info in columnas_para_sindato:
            print(f"[TEXTO] Índice {col_info['indice_1based']} (1-based) | {col_info['indice_0based']} (0-based)")
            print(f"Nombre: {col_info['nombre']}")
            print(f"Vacíos: {col_info['vacios']:,} de {len(df):,} ({col_info['porcentaje']:.2f}%)")
            print(f"Recomendacion: {col_info['recomendacion']}")
            print("-" * 80)
    
    if columnas_numericas_vacias:
        print("\n" + "=" * 80)
        print("COLUMNAS NUMÉRICAS CON VACÍOS - NO RELLENAR CON SINDATO")
        print("=" * 80)
        print()
        
        for col_info in columnas_numericas_vacias:
            print(f"[{col_info['tipo']}] Índice {col_info['indice_1based']} (1-based) | {col_info['indice_0based']} (0-based)")
            print(f"Nombre: {col_info['nombre']}")
            print(f"Vacíos: {col_info['vacios']:,} de {len(df):,} ({col_info['porcentaje']:.2f}%)")
            print(f"Recomendacion: {col_info['recomendacion']}")
            print("-" * 80)
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"Columnas de TEXTO con vacíos: {len(columnas_para_sindato)}")
    if columnas_para_sindato:
        indices = [str(c['indice_1based']) for c in columnas_para_sindato]
        print(f"Índices (1-based): {', '.join(indices)}")
    
    print(f"\nColumnas NUMÉRICAS con vacíos: {len(columnas_numericas_vacias)}")
    if columnas_numericas_vacias:
        indices = [str(c['indice_1based']) for c in columnas_numericas_vacias]
        print(f"Índices (1-based): {', '.join(indices)}")
    
    # Guardar reporte
    todas_columnas = columnas_para_sindato + columnas_numericas_vacias
    if todas_columnas:
        df_reporte = pd.DataFrame(todas_columnas)
        archivo_reporte = "Reporte_Columnas_Para_SINDATO.xlsx"
        df_reporte.to_excel(archivo_reporte, index=False)
        print(f"\nOK - Reporte guardado en: {archivo_reporte}")

if __name__ == "__main__":
    analizar_columnas_para_sindato()
