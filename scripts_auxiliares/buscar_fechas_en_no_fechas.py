import pandas as pd

# --- CONFIGURACIÓN ---
ARCHIVO_EXCEL = "./Procesado_Final.xlsx"
NUM_FILAS_A_SALTEAR = 0  # El procesado ya tiene encabezados

# Índices de columnas DE FECHAS (0-based)
INDICES_FECHAS = [
    7, 23, 27, 29, 43, 45, 47, 49, 51, 53, 58, 59, 61, 64, 66, 68,
    74, 76, 80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104,
    108, 119, 123,
]

def buscar_fechas_en_no_fechas():
    """Busca valores de fechas especiales en columnas que NO son de fechas"""
    
    print("="*80)
    print("BÚSQUEDA DE FECHAS ESPECIALES EN COLUMNAS NO-FECHA")
    print("="*80)
    print(f"Archivo: {ARCHIVO_EXCEL}\n")
    
    # Leer datos
    try:
        df = pd.read_excel(ARCHIVO_EXCEL, header=0, skiprows=NUM_FILAS_A_SALTEAR)
        print(f"OK - Datos cargados: {len(df)} registros, {len(df.columns)} columnas\n")
    except Exception as e:
        print(f"Error al leer archivo: {e}")
        return
    
    encabezados = df.columns.tolist()
    
    # Valores de fechas especiales a buscar
    fechas_buscar = ["1800/01/01", "1845/01/01", "1845/01/02", "1800-01-01", "1845-01-01", "1845-01-02"]
    
    columnas_con_problema = []
    
    # Revisar columnas NO-fecha
    for indice in range(len(df.columns)):
        if indice in INDICES_FECHAS:
            continue  # Saltar columnas de fechas
        
        col = df.iloc[:, indice]
        nombre_col = encabezados[indice] if indice < len(encabezados) else f"Columna_{indice}"
        
        # Buscar valores de fechas especiales
        for fecha_valor in fechas_buscar:
            coincidencias = col.astype(str).str.contains(fecha_valor, case=False, na=False).sum()
            
            if coincidencias > 0:
                # Obtener algunas filas de ejemplo
                filas_ejemplo = df[col.astype(str).str.contains(fecha_valor, case=False, na=False)].index.tolist()[:5]
                
                columnas_con_problema.append({
                    'indice_0based': indice,
                    'indice_1based': indice + 1,
                    'nombre': nombre_col,
                    'fecha_encontrada': fecha_valor,
                    'coincidencias': coincidencias,
                    'filas_ejemplo': filas_ejemplo
                })
    
    # Mostrar resultados
    if not columnas_con_problema:
        print("OK - No se encontraron fechas especiales en columnas NO-fecha")
        return
    
    print(f"Se encontraron {len(columnas_con_problema)} problemas:\n")
    print("-"*80)
    
    for problema in columnas_con_problema:
        print(f"Índice: {problema['indice_1based']} (Excel) | {problema['indice_0based']} (Pandas)")
        print(f"Nombre: {problema['nombre']}")
        print(f"Fecha encontrada: {problema['fecha_encontrada']}")
        print(f"Coincidencias: {problema['coincidencias']}")
        print(f"Filas ejemplo (primeras 5): {problema['filas_ejemplo']}")
        print("-"*80)
    
    # Guardar reporte
    df_reporte = pd.DataFrame(columnas_con_problema)
    archivo_reporte = "Reporte_Fechas_En_No_Fechas.xlsx"
    df_reporte.to_excel(archivo_reporte, index=False)
    print(f"\nOK - Reporte guardado en: {archivo_reporte}")

if __name__ == "__main__":
    buscar_fechas_en_no_fechas()
