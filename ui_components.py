"""
Componentes reutilizables de la interfaz de usuario.
"""

import streamlit as st


def mostrar_header():
    """Muestra el header principal del dashboard"""
    st.markdown("""
        <div style='text-align: center; padding: 30px 0 20px 0;'>
            <h1 style='margin: 0; font-size: 2.8em; color: #1f2937;'>📊 Dashboard RCV</h1>
            <p style='font-size: 1.3em; margin: 15px 0; color: #6b7280;'>
                Sistema de Procesamiento de Datos BDRUTACCVM
            </p>
            <p style='font-size: 0.95em; color: #9ca3af; margin-top: 10px;'>
                Flujo completo: Crear Copia → Limpieza → Exportación IPS → Validación
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")


def crear_columnas_centradas(num_columnas=3):
    """
    Crea columnas centradas para botones.
    
    Args:
        num_columnas: Número de columnas (default: 3 para centrar)
        
    Returns:
        tuple: Columnas de Streamlit
    """
    return st.columns([1] * num_columnas)


def mostrar_info_paso(numero_paso, titulo, descripcion, info_adicional=None):
    """
    Muestra información formateada de un paso del proceso.
    
    Args:
        numero_paso: Número del paso
        titulo: Título del paso
        descripcion: Descripción del paso
        info_adicional: Información adicional opcional
    """
    iconos_pasos = {
        1: "📄",
        2: "🧹", 
        3: "✅"
    }
    icono = iconos_pasos.get(numero_paso, "📌")
    
    st.markdown(f"### {icono} Paso {numero_paso}: {titulo}")
    st.info(f"🔹 **Instrucciones:** {descripcion}")
    if info_adicional:
        st.caption(f"📌 {info_adicional}")
    st.markdown("---")


def crear_seccion_archivos(titulo, columnas_config):
    """
    Crea una sección de descargas de archivos.
    
    Args:
        titulo: Título de la sección
        columnas_config: Configuración de columnas (número)
    """
    st.markdown(f"#### 📦 {titulo}")
    return st.columns(columnas_config)


def boton_centrado(texto, icono="", **kwargs):
    """
    Crea un botón centrado con icono.
    
    Args:
        texto: Texto del botón
        icono: Emoji/icono del botón
        **kwargs: Argumentos adicionales para st.button
        
    Returns:
        bool: True si el botón fue presionado
    """
    col1, col2, col3 = crear_columnas_centradas()
    with col2:
        texto_completo = f"{icono} {texto}" if icono else texto
        return st.button(texto_completo, use_container_width=True, **kwargs)


def mostrar_separador_paso():
    """Muestra un separador visual entre pasos"""
    st.markdown("---")


def mostrar_archivos_descarga_duo(archivo_izq, nombre_izq, titulo_izq,
                                   archivo_der, nombre_der, titulo_der,
                                   callback_izq=None, callback_der=None):
    """
    Muestra dos archivos para descargar en columnas paralelas.
    
    Args:
        archivo_izq: Ruta del archivo izquierdo
        nombre_izq: Nombre para descargar archivo izquierdo
        titulo_izq: Título del botón izquierdo
        archivo_der: Ruta del archivo derecho
        nombre_der: Nombre para descargar archivo derecho
        titulo_der: Título del botón derecho
        callback_izq: Callback opcional para el botón izquierdo
        callback_der: Callback opcional para el botón derecho
    """
    col1, col2 = st.columns(2)
    
    with col1:
        if archivo_izq:
            with open(archivo_izq, "rb") as f:
                st.download_button(
                    titulo_izq,
                    f,
                    file_name=nombre_izq,
                    use_container_width=True,
                    on_click=callback_izq
                )
    
    with col2:
        if archivo_der:
            with open(archivo_der, "rb") as f:
                st.download_button(
                    titulo_der,
                    f,
                    file_name=nombre_der,
                    use_container_width=True,
                    on_click=callback_der
                )
