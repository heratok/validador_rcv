"""
Dashboard RCV - Sistema de Procesamiento de Datos BDRUTACCVM

Archivo principal de la aplicación Streamlit.
Importa y organiza todos los componentes modularizados.
"""

import streamlit as st
from config_tema import aplicar_tema_pastel
from ui_components import mostrar_header
from tab_crear_copia import mostrar_tab_crear_copia
from tab_limpieza import mostrar_tab_limpieza
from tab_validacion import mostrar_tab_validacion


# ========== CONFIGURACIÓN DE LA PÁGINA ==========
st.set_page_config(
    page_title="Dashboard RCV | Procesamiento de Datos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Ocultar sidebar
)

# ========== APLICAR TEMA PASTEL ==========
st.markdown(aplicar_tema_pastel(), unsafe_allow_html=True)

# ========== HEADER PRINCIPAL ==========
mostrar_header()

# ========== TABS PRINCIPALES ==========
tab_copia, tab_limpieza, tab_validacion = st.tabs([
    "📄 Crear Copia",
    "🧹 Limpieza y Exportación IPS",
    "✅ Validación"
])

# ========== CONTENIDO DE CADA TAB ==========
with tab_copia:
    mostrar_tab_crear_copia()

with tab_limpieza:
    mostrar_tab_limpieza()

with tab_validacion:
    mostrar_tab_validacion()
