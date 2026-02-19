"""
Tab de limpieza y exportación por IPS.
"""

import os
import streamlit as st
from procesar_general import ejecutar_procesamiento_general
from scripts_auxiliares.separar_por_ips_consecutivo import separar_por_ips
from utils_app import (guardar_temporal, limpiar_directorio, crear_zip, 
                       formatear_mensaje_exito, formatear_mensaje_error)
from ui_components import (mostrar_info_paso, boton_centrado, crear_columnas_centradas, 
                          mostrar_separador_paso, crear_seccion_archivos)


def mostrar_tab_limpieza():
    """Renderiza el contenido completo del tab de limpieza y exportación"""
    
    mostrar_info_paso(
        2,
        "Limpieza y Exportación por IPS",
        "Primero limpia los datos, luego exporta los archivos CSV separados por IPS.",
        "⏱️ Tiempo estimado: Limpieza 1-3 min | Exportación IPS 1-5 min"
    )
    
    # Carga de archivo
    archivo_con_encabezados = st.file_uploader(
        "📥 Selecciona el archivo copia (generado en Paso 1)",
        type=["xlsx", "xlsb"],
        key="limpieza_uploader",
        help="Usa el archivo '_copia.xlsx' generado en el paso anterior"
    )
    
    st.caption("ℹ️ Configuración: Datos inician en fila 2 | Columna IPS: índice 22")
    st.markdown("---")
    
    if not archivo_con_encabezados:
        st.warning("⏳ Por favor, sube el archivo copia para continuar.")
        return
    
    temp_dir, ruta_temp = guardar_temporal(archivo_con_encabezados, "limpieza_")
    st.success(formatear_mensaje_exito(archivo_con_encabezados.name))
    
    # Paso A: Limpieza
    _mostrar_seccion_limpieza(temp_dir, ruta_temp)
    
    mostrar_separador_paso()
    
    # Paso B: Exportar por IPS
    _mostrar_seccion_exportacion_ips()


def _mostrar_seccion_limpieza(temp_dir, ruta_temp):
    """Muestra la sección de limpieza de datos"""
    st.markdown("#### 🔧 Paso A: Ejecutar Limpieza de Datos")
    
    if boton_centrado("Ejecutar Limpieza", "🧹"):
        # Preparar rutas
        archivos_salida = {
            "excel": os.path.join(temp_dir, "Procesado_Final.xlsx"),
            "log": os.path.join(temp_dir, "Procesamiento_General.log"),
            "reporte_csv": os.path.join(temp_dir, "Reporte_Validacion_Errores.csv"),
            "reporte_excel": os.path.join(temp_dir, "Reporte_Validacion_Errores.xlsx"),
            "totales_csv": os.path.join(temp_dir, "Reporte_Validacion_Errores_Totales.csv"),
            "totales_excel": os.path.join(temp_dir, "Reporte_Validacion_Errores_Totales.xlsx")
        }
        
        with st.spinner("⏳ Procesando... Esto puede tomar 1-3 minutos..."):
            resultado = ejecutar_procesamiento_general(
                ruta_temp,
                archivo_salida=archivos_salida["excel"],
                reporte_errores_csv=archivos_salida["reporte_csv"],
                reporte_errores_excel=archivos_salida["reporte_excel"],
                reporte_errores_totales_csv=archivos_salida["totales_csv"],
                reporte_errores_totales_excel=archivos_salida["totales_excel"],
                log_salida=archivos_salida["log"],
                num_filas_a_saltar=1,
            )
        
        if not resultado:
            st.error(formatear_mensaje_error("limpieza"))
            if os.path.exists(archivos_salida["log"]):
                with open(archivos_salida["log"], "rb") as f:
                    st.download_button(
                        "📄 Descargar Log de Errores",
                        f,
                        file_name="Procesamiento_General.log",
                    )
        else:
            st.success("✅ ¡Limpieza completada exitosamente!")
            st.session_state["limpio_archivo"] = resultado["archivo_salida"]
            st.session_state["limpio_temp_dir"] = temp_dir
            st.session_state["limpieza_completada"] = True
            
            _mostrar_archivos_limpieza(resultado)


def _mostrar_archivos_limpieza(resultado):
    """Muestra los archivos generados por la limpieza"""
    st.markdown("#### 📦 Archivos Generados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Archivo Principal:**")
        if os.path.exists(resultado["archivo_salida"]):
            with open(resultado["archivo_salida"], "rb") as f:
                st.download_button(
                    "⬇️ Excel Limpio",
                    f,
                    file_name="Procesado_Final.xlsx",
                    use_container_width=True
                )

    with col2:
        st.markdown("**📈 Reportes de Validación:**")
        if os.path.exists(resultado["reporte_errores_csv"]):
            with open(resultado["reporte_errores_csv"], "rb") as f:
                st.download_button(
                    "⬇️ Reporte CSV",
                    f,
                    file_name="Reporte_Validacion_Errores.csv",
                    use_container_width=True
                )

    col1, col2 = st.columns(2)
    
    with col1:
        if os.path.exists(resultado["reporte_errores_excel"]):
            with open(resultado["reporte_errores_excel"], "rb") as f:
                st.download_button(
                    "⬇️ Reporte Excel",
                    f,
                    file_name="Reporte_Validacion_Errores.xlsx",
                    use_container_width=True
                )

    with col2:
        if os.path.exists(resultado["reporte_errores_totales_csv"]):
            with open(resultado["reporte_errores_totales_csv"], "rb") as f:
                st.download_button(
                    "⬇️ Reporte Total CSV",
                    f,
                    file_name="Reporte_Validacion_Errores_Totales.csv",
                    use_container_width=True
                )
    
    if os.path.exists(resultado["reporte_errores_totales_excel"]):
        with open(resultado["reporte_errores_totales_excel"], "rb") as f:
            st.download_button(
                "⬇️ Reporte Total Excel",
                f,
                file_name="Reporte_Validacion_Errores_Totales.xlsx",
            )


def _mostrar_seccion_exportacion_ips():
    """Muestra la sección de exportación por IPS"""
    archivo_limpio = st.session_state.get("limpio_archivo")
    temp_dir_limpio = st.session_state.get("limpio_temp_dir")
    limpieza_completada = st.session_state.get("limpieza_completada", False)
    
    puede_exportar = (
        archivo_limpio
        and os.path.exists(archivo_limpio)
        and temp_dir_limpio
        and os.path.exists(temp_dir_limpio)
        and limpieza_completada
    )

    st.markdown("#### 📤 Paso B: Exportar Archivos por IPS")
    
    if not puede_exportar:
        st.info("ℹ️ Primero debes ejecutar la limpieza de datos en el Paso A")
    
    if boton_centrado("Exportar por IPS", "📤", disabled=not puede_exportar):
        if not puede_exportar:
            st.error(formatear_mensaje_error("exportacion"))
        else:
            carpeta_base = os.path.join(temp_dir_limpio, "Reportes_Por_IPS_CSV")
            
            with st.spinner("⏳ Generando archivos CSV por IPS... Esto puede tomar 1-5 minutos..."):
                carpeta_salida = separar_por_ips(
                    archivo_limpio,
                    carpeta_salida_base=carpeta_base,
                    num_filas_a_saltar=1,
                    indice_ips=22,
                )
            
            if not carpeta_salida or not os.path.exists(carpeta_salida):
                st.error(formatear_mensaje_error("exportacion"))
            else:
                zip_path = os.path.join(temp_dir_limpio, "Reportes_Por_IPS_CSV.zip")
                zip_final = crear_zip(carpeta_base, zip_path)
                st.success("✅ ¡Archivos CSV por IPS generados exitosamente!")
                st.session_state["ips_descargado"] = False
                
                st.markdown("---")
                col1, col2, col3 = crear_columnas_centradas()
                with col2:
                    with open(zip_final, "rb") as f:
                        st.download_button(
                            "📦 Descargar ZIP Completo de IPS",
                            f,
                            file_name="Reportes_Por_IPS_CSV.zip",
                            on_click=lambda: st.session_state.update({"ips_descargado": True}),
                            use_container_width=True
                        )
                
                if st.session_state.get("ips_descargado", False):
                    st.info("✅ Descarga completada. Puedes cargar una nueva copia arriba para continuar.")
                    if boton_centrado("Limpiar y Procesar Nuevo Archivo", "🔄"):
                        limpiar_directorio(st.session_state.get("limpio_temp_dir"))
                        st.session_state["limpio_archivo"] = None
                        st.session_state["limpio_temp_dir"] = None
                        st.session_state["limpieza_completada"] = False
                        st.session_state["ips_descargado"] = False
                        st.rerun()
