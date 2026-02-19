import gc
import os
import shutil
import tempfile

import streamlit as st

from crear_con_encabezados_desde_rcv import generar_con_encabezados
from procesar_general import ejecutar_procesamiento_general
from scripts_auxiliares.separar_por_ips_consecutivo import separar_por_ips
from validar_valores_columna import ejecutar_validacion


st.set_page_config(page_title="Dashboard Excel", layout="centered")

# Selector de tema en el sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    if "tema" not in st.session_state:
        st.session_state.tema = "Claro"
    
    tema = st.radio(
        "Tema de color:",
        ["Claro", "Oscuro"],
        index=0 if st.session_state.tema == "Claro" else 1,
        key="selector_tema"
    )
    st.session_state.tema = tema

# Aplicar CSS según el tema seleccionado
if st.session_state.tema == "Oscuro":
    st.markdown("""
        <style>
        /* Tema Oscuro */
        :root {
            --background-color: #0e1117;
            --secondary-background-color: #262730;
            --text-color: #fafafa;
            --primary-color: #ff4b4b;
        }
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #262730;
        }
        .stTabs [data-baseweb="tab"] {
            color: #fafafa;
        }
        .stSelectbox, .stTextInput, .stNumberInput {
            color: #fafafa;
        }
        div[data-testid="stSidebar"] {
            background-color: #262730;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        /* Tema Claro */
        :root {
            --background-color: #ffffff;
            --secondary-background-color: #f0f2f6;
            --text-color: #262730;
            --primary-color: #1f77b4;
        }
        .stApp {
            background-color: #ffffff;
            color: #262730;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f0f2f6;
        }
        .stTabs [data-baseweb="tab"] {
            color: #262730;
        }
        div[data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
        </style>
    """, unsafe_allow_html=True)

st.title("Dashboard de procesamiento")
st.write("Flujo guiado: 1) crear copia, 2) limpiar, 3) exportar por IPS.")

tab_copia, tab_limpieza, tab_validacion = st.tabs(
    ["1) Crear copia", "2) Limpieza y IPS", "3) Validacion"]
)


def _guardar_temporal(archivo_subido, prefijo):
    temp_dir = tempfile.mkdtemp(prefix=prefijo)
    ruta_temp = os.path.join(temp_dir, archivo_subido.name)
    with open(ruta_temp, "wb") as f:
        f.write(archivo_subido.getbuffer())
    return temp_dir, ruta_temp


def _limpiar_directorio(directorio):
    """Limpia un directorio temporal de forma segura"""
    try:
        if os.path.exists(directorio):
            shutil.rmtree(directorio)
            gc.collect()  # Liberar memoria
    except Exception as e:
        print(f"Error al limpiar {directorio}: {e}")


def _zip_carpeta(carpeta, salida_zip):
    base_name, _ = os.path.splitext(salida_zip)
    return shutil.make_archive(base_name, "zip", carpeta)


with tab_copia:
    st.subheader("Crear copia")
    st.info("Paso 1: sube el Excel original. Paso 2: genera y descarga la copia.")
    st.caption("El archivo de salida termina en '_copia.xlsx'.")
    archivo_origen = st.file_uploader(
        "Archivo Excel original",
        type=["xlsx", "xlsb"],
        key="copia_uploader",
    )
    fila_inicio = st.number_input(
        "Fila de inicio de datos",
        min_value=1,
        max_value=50,
        value=4,
        step=1,
        key="copia_fila_inicio",
    )

    if not archivo_origen:
        st.warning("Espera: sube el archivo para continuar.")
    else:
        temp_dir, ruta_temp = _guardar_temporal(archivo_origen, "copia_")
        st.success(f"Archivo cargado: {archivo_origen.name}")

        if st.button("Generar copia"):
            with st.spinner("Generando copia..."):
                salida = generar_con_encabezados(
                    ruta_temp,
                    data_start_row=int(fila_inicio),
                )
            if not salida or not os.path.exists(salida):
                st.error("No se pudo generar la copia. Revisa la consola.")
            else:
                st.success("Copia generada. Descargala abajo.")
                # Guardar temp_dir para limpiar después
                st.session_state["temp_dir_copia"] = temp_dir
                with open(salida, "rb") as f:
                    st.download_button(
                        "Descargar copia",
                        f,
                        file_name=os.path.basename(salida),
                        on_click=lambda: _limpiar_directorio(st.session_state.get("temp_dir_copia")),
                    )

with tab_limpieza:
    st.subheader("Limpiar Excel y exportar por IPS")
    st.info("Paso 1: sube la copia. Paso 2: limpia. Paso 3: exporta por IPS.")
    st.caption("Tiempo estimado: limpieza 1-3 min; exportar por IPS 1-5 min.")
    archivo_con_encabezados = st.file_uploader(
        "Archivo copia",
        type=["xlsx", "xlsb"],
        key="limpieza_uploader",
    )
    st.caption("Datos inician en fila 2. IPS usa el indice fijo 22 (0-based).")

    if not archivo_con_encabezados:
        st.warning("Espera: sube el archivo para continuar.")
    else:
        temp_dir, ruta_temp = _guardar_temporal(archivo_con_encabezados, "limpieza_")
        st.success(f"Archivo cargado: {archivo_con_encabezados.name}")

        if st.button("Ejecutar limpieza"):
            salida_excel = os.path.join(temp_dir, "Procesado_Final.xlsx")
            log_path = os.path.join(temp_dir, "Procesamiento_General.log")
            reporte_csv = os.path.join(temp_dir, "Reporte_Validacion_Errores.csv")
            reporte_xlsx = os.path.join(temp_dir, "Reporte_Validacion_Errores.xlsx")
            reporte_totales_csv = os.path.join(
                temp_dir, "Reporte_Validacion_Errores_Totales.csv"
            )
            reporte_totales_xlsx = os.path.join(
                temp_dir, "Reporte_Validacion_Errores_Totales.xlsx"
            )

            with st.spinner("Limpiando archivo..."):
                resultado = ejecutar_procesamiento_general(
                    ruta_temp,
                    archivo_salida=salida_excel,
                    reporte_errores_csv=reporte_csv,
                    reporte_errores_excel=reporte_xlsx,
                    reporte_errores_totales_csv=reporte_totales_csv,
                    reporte_errores_totales_excel=reporte_totales_xlsx,
                    log_salida=log_path,
                    num_filas_a_saltar=1,
                )

            if not resultado:
                st.error("No se pudo completar la limpieza. Revisa el log.")
                if os.path.exists(log_path):
                    with open(log_path, "rb") as f:
                        st.download_button(
                            "Descargar log de limpieza",
                            f,
                            file_name="Procesamiento_General.log",
                        )
            else:
                st.success("Limpieza terminada. Descarga el Excel limpio abajo.")
                st.session_state["limpio_archivo"] = resultado["archivo_salida"]
                st.session_state["limpio_temp_dir"] = temp_dir
                st.session_state["limpieza_completada"] = True

                if os.path.exists(resultado["archivo_salida"]):
                    with open(resultado["archivo_salida"], "rb") as f:
                        st.download_button(
                            "Descargar Excel limpio",
                            f,
                            file_name="Procesado_Final.xlsx",
                        )

                if os.path.exists(resultado["reporte_errores_csv"]):
                    with open(resultado["reporte_errores_csv"], "rb") as f:
                        st.download_button(
                            "Descargar reporte CSV",
                            f,
                            file_name="Reporte_Validacion_Errores.csv",
                        )

                if os.path.exists(resultado["reporte_errores_excel"]):
                    with open(resultado["reporte_errores_excel"], "rb") as f:
                        st.download_button(
                            "Descargar reporte Excel",
                            f,
                            file_name="Reporte_Validacion_Errores.xlsx",
                        )

                if os.path.exists(resultado["reporte_errores_totales_csv"]):
                    with open(resultado["reporte_errores_totales_csv"], "rb") as f:
                        st.download_button(
                            "Descargar reporte CSV total",
                            f,
                            file_name="Reporte_Validacion_Errores_Totales.csv",
                        )

                if os.path.exists(resultado["reporte_errores_totales_excel"]):
                    with open(resultado["reporte_errores_totales_excel"], "rb") as f:
                        st.download_button(
                            "Descargar reporte Excel total",
                            f,
                            file_name="Reporte_Validacion_Errores_Totales.xlsx",
                        )

        st.divider()

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

        st.write("**Paso 3: Exportar por IPS**")
        if st.button("Exportar por IPS", disabled=not puede_exportar):
            if not puede_exportar:
                st.error("Primero ejecuta la limpieza arriba.")
            else:
                carpeta_base = os.path.join(temp_dir_limpio, "Reportes_Por_IPS_CSV")
                with st.spinner("Generando CSV por IPS..."):
                    carpeta_salida = separar_por_ips(
                        archivo_limpio,
                        carpeta_salida_base=carpeta_base,
                        num_filas_a_saltar=1,
                        indice_ips=22,
                    )
                if not carpeta_salida or not os.path.exists(carpeta_salida):
                    st.error("No se pudo exportar por IPS.")
                else:
                    zip_path = os.path.join(temp_dir_limpio, "Reportes_Por_IPS_CSV.zip")
                    zip_final = _zip_carpeta(carpeta_base, zip_path)
                    st.success("CSV por IPS generados. Descarga el ZIP abajo.")
                    st.session_state["ips_descargado"] = False
                    with open(zip_final, "rb") as f:
                        st.download_button(
                            "Descargar ZIP de IPS",
                            f,
                            file_name="Reportes_Por_IPS_CSV.zip",
                            on_click=lambda: st.session_state.update({"ips_descargado": True}),
                        )
                    
                    if st.session_state.get("ips_descargado", False):
                        st.info("✅ Descarga completada. Puedes cargar una nueva copia arriba para continuar.")
                        if st.button("Limpiar y preparar para nuevo archivo"):
                            _limpiar_directorio(st.session_state.get("limpio_temp_dir"))
                            st.session_state["limpio_archivo"] = None
                            st.session_state["limpio_temp_dir"] = None
                            st.session_state["limpieza_completada"] = False
                            st.session_state["ips_descargado"] = False
                            st.rerun()

with tab_validacion:
    st.subheader("Validar columnas (sin limpiar)")
    st.info("Sube el Excel y genera el log/CSV de validacion.")
    archivo_subido = st.file_uploader(
        "Archivo Excel con encabezados",
        type=["xlsx", "xlsb"],
        key="validacion_uploader",
    )
    filas_a_saltar = st.number_input(
        "Filas a saltar (header original)",
        min_value=0,
        max_value=20,
        value=1,
        step=1,
        key="validacion_filas",
    )

    if not archivo_subido:
        st.warning("Espera: sube el archivo para continuar.")
    else:
        temp_dir, ruta_temp = _guardar_temporal(archivo_subido, "validacion_")
        st.success(f"Archivo cargado: {archivo_subido.name}")

        if st.button("Ejecutar validacion"):
            log_path = os.path.join(temp_dir, "Validacion_Columnas.log")
            csv_path = os.path.join(temp_dir, "Validacion_Errores.csv")

            with st.spinner("Validando..."):
                resultado = ejecutar_validacion(
                    ruta_temp,
                    log_salida=log_path,
                    num_filas_a_saltar=int(filas_a_saltar),
                    csv_salida=csv_path,
                )

            if not resultado:
                st.error("No se pudo completar la validacion. Revisa la consola.")
            else:
                st.success("Validacion terminada.")
                # Guardar temp_dir para limpiar después
                st.session_state["temp_dir_validacion"] = temp_dir

                with open(resultado["log"], "rb") as f:
                    st.download_button(
                        "Descargar log",
                        f,
                        file_name="Validacion_Columnas.log",
                    )

                if resultado["csv"] and os.path.exists(resultado["csv"]):
                    with open(resultado["csv"], "rb") as f:
                        st.download_button(
                            "Descargar CSV",
                            f,
                            file_name="Validacion_Errores.csv",
                            on_click=lambda: _limpiar_directorio(st.session_state.get("temp_dir_validacion")),
                        )
