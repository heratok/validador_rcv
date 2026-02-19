"""
Tab de creación de copia con encabezados.
"""

import os
import streamlit as st
from crear_con_encabezados_desde_rcv import generar_con_encabezados
from utils_app import guardar_temporal, limpiar_directorio, formatear_mensaje_exito, formatear_mensaje_error
from ui_components import mostrar_info_paso, boton_centrado, crear_columnas_centradas


def mostrar_tab_crear_copia():
    """Renderiza el contenido completo del tab de crear copia"""
    
    mostrar_info_paso(
        1,
        "Crear Copia del Excel Original",
        "Sube el archivo Excel original y genera una copia con encabezados normalizados.",
        "El archivo de salida tendrá el sufijo '_copia.xlsx'"
    )
    
    # Sección de carga de archivo
    col1, col2 = st.columns([2, 1])
    
    with col1:
        archivo_origen = st.file_uploader(
            "📥 Selecciona el archivo Excel original",
            type=["xlsx", "xlsb"],
            key="copia_uploader",
            help="Formatos soportados: .xlsx y .xlsb"
        )
    
    with col2:
        fila_inicio = st.number_input(
            "📍 Fila de inicio de datos",
            min_value=1,
            max_value=50,
            value=4,
            step=1,
            key="copia_fila_inicio",
            help="Número de fila donde comienzan los datos (generalmente fila 4)"
        )

    st.markdown("---")
    
    # Procesamiento
    if not archivo_origen:
        st.warning("⏳ Por favor, sube un archivo Excel para continuar.")
    else:
        temp_dir, ruta_temp = guardar_temporal(archivo_origen, "copia_")
        st.success(formatear_mensaje_exito(archivo_origen.name))

        if boton_centrado("Generar Copia", "🚀"):
            with st.spinner("⏳ Generando copia con encabezados..."):
                salida = generar_con_encabezados(
                    ruta_temp,
                    data_start_row=int(fila_inicio),
                )
            
            if not salida or not os.path.exists(salida):
                st.error(formatear_mensaje_error("generacion"))
            else:
                st.success("✅ ¡Copia generada exitosamente!")
                st.session_state["temp_dir_copia"] = temp_dir
                
                st.markdown("---")
                with open(salida, "rb") as f:
                    col1, col2, col3 = crear_columnas_centradas()
                    with col2:
                        st.download_button(
                            "⬇️ Descargar Copia Generada",
                            f,
                            file_name=os.path.basename(salida),
                            on_click=lambda: limpiar_directorio(st.session_state.get("temp_dir_copia")),
                            use_container_width=True
                        )
