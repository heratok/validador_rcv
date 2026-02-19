"""
Tab de validación de columnas.
"""

import os
import streamlit as st
from validar_valores_columna import ejecutar_validacion
from utils_app import guardar_temporal, limpiar_directorio, formatear_mensaje_exito, formatear_mensaje_error
from ui_components import mostrar_info_paso, boton_centrado


def mostrar_tab_validacion():
    """Renderiza el contenido completo del tab de validación"""
    
    mostrar_info_paso(
        3,
        "Validación de Columnas",
        "Valida los datos del Excel sin aplicar limpieza.",
        "Genera reportes de errores de validación sin modificar el archivo original"
    )
    
    # Carga de archivo
    col1, col2 = st.columns([2, 1])
    
    with col1:
        archivo_subido = st.file_uploader(
            "📥 Selecciona el archivo Excel con encabezados",
            type=["xlsx", "xlsb"],
            key="validacion_uploader",
            help="Archivo Excel para validar columnas"
        )
    
    with col2:
        filas_a_saltar = st.number_input(
            "📍 Filas a saltar (header)",
            min_value=0,
            max_value=20,
            value=1,
            step=1,
            key="validacion_filas",
            help="Número de filas de encabezado a ignorar"
        )

    st.markdown("---")
    
    # Procesamiento
    if not archivo_subido:
        st.warning("⏳ Por favor, sube un archivo Excel para continuar.")
    else:
        temp_dir, ruta_temp = guardar_temporal(archivo_subido, "validacion_")
        st.success(formatear_mensaje_exito(archivo_subido.name))

        if boton_centrado("Ejecutar Validación", "✅"):
            log_path = os.path.join(temp_dir, "Validacion_Columnas.log")
            csv_path = os.path.join(temp_dir, "Validacion_Errores.csv")

            with st.spinner("⏳ Ejecutando validación..."):
                resultado = ejecutar_validacion(
                    ruta_temp,
                    log_salida=log_path,
                    num_filas_a_saltar=int(filas_a_saltar),
                    csv_salida=csv_path,
                )

            if not resultado:
                st.error(formatear_mensaje_error("validacion"))
            else:
                st.success("✅ ¡Validación completada exitosamente!")
                st.session_state["temp_dir_validacion"] = temp_dir

                st.markdown("#### 📦 Archivos de Validación")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📄 Log de Validación:**")
                    with open(resultado["log"], "rb") as f:
                        st.download_button(
                            "⬇️ Descargar Log",
                            f,
                            file_name="Validacion_Columnas.log",
                            use_container_width=True
                        )

                with col2:
                    st.markdown("**📊 Reporte CSV:**")
                    if resultado["csv"] and os.path.exists(resultado["csv"]):
                        with open(resultado["csv"], "rb") as f:
                            st.download_button(
                                "⬇️ Descargar CSV",
                                f,
                                file_name="Validacion_Errores.csv",
                                on_click=lambda: limpiar_directorio(st.session_state.get("temp_dir_validacion")),
                                use_container_width=True
                            )
