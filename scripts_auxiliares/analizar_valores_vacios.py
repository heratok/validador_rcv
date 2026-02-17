import pandas as pd
import os

# --- CONFIGURACIÓN ---
ARCHIVO_EXCEL = "./Procesado_Final.xlsx"
NUM_FILAS_A_SALTEAR = 1

def detectar_engine(archivo):
    """Detecta el engine apropiado según la extensión"""
    ext = os.path.splitext(archivo)[1].lower()
    if ext == ".xlsb":
        return "pyxlsb"
    elif ext in [".xlsx", ".xls"]:
        return "openpyxl"
    return None

def leer_encabezados(archivo):
    """Lee los encabezados del archivo"""
    engine = detectar_engine(archivo)
    try:
        df_headers = pd.read_excel(archivo, header=None, skiprows=0, engine=engine, nrows=1)
        return df_headers.iloc[0].tolist()
    except Exception:
        return []

def analizar_valores_vacios(archivo, filas_a_saltar):
    """Analiza qué columnas tienen valores vacíos y muestra estadísticas"""
    
    print("="*80)
    print("ANÁLISIS DE VALORES VACÍOS EN COLUMNAS")
    print("="*80)
    print(f"Archivo: {archivo}\n")
    
    # Leer datos
    engine = detectar_engine(archivo)
    if not engine:
        print(f"Error: No se pudo detectar el tipo de archivo")
        return
    
    try:
        df = pd.read_excel(archivo, header=None, skiprows=filas_a_saltar, engine=engine)
        print(f"OK - Datos cargados: {len(df)} registros, {len(df.columns)} columnas\n")
    except Exception as e:
        print(f"Error al leer archivo: {e}")
        return
    
    # Leer encabezados
    encabezados = leer_encabezados(archivo)
    
    # Analizar cada columna
    columnas_con_vacios = []
    
    for indice in range(len(df.columns)):
        col = df.iloc[:, indice]
        
        # Contar valores vacíos (NaN, None, cadenas vacías)
        vacios = col.isna().sum()
        vacios_str = (col.astype(str).str.strip() == '').sum() if col.dtype == 'object' else 0
        total_vacios = max(vacios, vacios_str)
        
        if total_vacios > 0:
            nombre_col = encabezados[indice] if indice < len(encabezados) else f"Columna_{indice}"
            porcentaje = (total_vacios / len(df)) * 100
            
            # Obtener algunos ejemplos de valores NO vacíos
            valores_no_vacios = col.dropna()
            if len(valores_no_vacios) > 0:
                # Filtrar valores que no sean cadenas vacías
                if col.dtype == 'object':
                    valores_no_vacios = valores_no_vacios[valores_no_vacios.astype(str).str.strip() != '']
                
                ejemplos = valores_no_vacios.unique()[:3]  # Primeros 3 valores únicos
                ejemplos_str = ", ".join([str(x)[:50] for x in ejemplos])
            else:
                ejemplos_str = "TODOS VACÍOS"
            
            # Detectar tipo de datos
            tipo_datos = col.dtype
            
            columnas_con_vacios.append({
                'indice_0based': indice,
                'indice_1based': indice + 1,
                'nombre': nombre_col,
                'vacios': total_vacios,
                'porcentaje': porcentaje,
                'tipo': tipo_datos,
                'ejemplos': ejemplos_str
            })
    
    # Mostrar resultados
    if not columnas_con_vacios:
        print("OK - No se encontraron columnas con valores vacíos")
        return
    
    print(f"Se encontraron {len(columnas_con_vacios)} columnas con valores vacíos:\n")
    print("-"*80)
    
    for col_info in columnas_con_vacios:
        print(f"Índice: {col_info['indice_1based']} (Excel) | {col_info['indice_0based']} (Pandas)")
        print(f"Nombre: {col_info['nombre']}")
        print(f"Vacíos: {col_info['vacios']:,} de {len(df):,} ({col_info['porcentaje']:.2f}%)")
        print(f"Tipo: {col_info['tipo']}")
        print(f"Ejemplos: {col_info['ejemplos']}")
        print("-"*80)
    
    # Resumen
    print(f"\n{'='*80}")
    print("RESUMEN")
    print(f"{'='*80}")
    print(f"Total columnas analizadas: {len(df.columns)}")
    print(f"Columnas con valores vacíos: {len(columnas_con_vacios)}")
    print(f"\nÍndices (1-based) de columnas con vacíos:")
    indices_1based = [str(c['indice_1based']) for c in columnas_con_vacios]
    print(", ".join(indices_1based))
    
    print(f"\nÍndices (0-based) de columnas con vacíos:")
    indices_0based = [str(c['indice_0based']) for c in columnas_con_vacios]
    print(", ".join(indices_0based))
    
    # Guardar reporte detallado
    df_reporte = pd.DataFrame(columnas_con_vacios)
    archivo_reporte = "Reporte_Valores_Vacios.xlsx"
    df_reporte.to_excel(archivo_reporte, index=False)
    print(f"\nOK - Reporte detallado guardado en: {archivo_reporte}")

if __name__ == "__main__":
    analizar_valores_vacios(ARCHIVO_EXCEL, NUM_FILAS_A_SALTEAR)
