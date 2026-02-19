"""
Funciones de utilidad para el dashboard.
Manejo de archivos temporales, limpieza y compresión.
"""

import gc
import os
import shutil
import tempfile


def guardar_temporal(archivo_subido, prefijo):
    """
    Guarda un archivo subido en un directorio temporal.
    
    Args:
        archivo_subido: Objeto UploadedFile de Streamlit
        prefijo: Prefijo para el nombre del directorio temporal
        
    Returns:
        tuple: (ruta_directorio_temporal, ruta_archivo_completa)
    """
    temp_dir = tempfile.mkdtemp(prefix=prefijo)
    ruta_temp = os.path.join(temp_dir, archivo_subido.name)
    with open(ruta_temp, "wb") as f:
        f.write(archivo_subido.getbuffer())
    return temp_dir, ruta_temp


def limpiar_directorio(directorio):
    """
    Limpia un directorio temporal de forma segura.
    
    Args:
        directorio: Ruta del directorio a eliminar
    """
    try:
        if directorio and os.path.exists(directorio):
            shutil.rmtree(directorio)
            gc.collect()  # Liberar memoria
    except Exception as e:
        print(f"Error al limpiar {directorio}: {e}")


def crear_zip(carpeta, salida_zip):
    """
    Crea un archivo ZIP de una carpeta.
    
    Args:
        carpeta: Ruta de la carpeta a comprimir
        salida_zip: Ruta del archivo ZIP de salida
        
    Returns:
        str: Ruta del archivo ZIP creado
    """
    base_name, _ = os.path.splitext(salida_zip)
    return shutil.make_archive(base_name, "zip", carpeta)


def formatear_mensaje_exito(nombre_archivo):
    """
    Formatea un mensaje de éxito con el nombre del archivo.
    
    Args:
        nombre_archivo: Nombre del archivo
        
    Returns:
        str: Mensaje formateado
    """
    return f"✅ Archivo cargado correctamente: **{nombre_archivo}**"


def formatear_mensaje_error(tipo_error="general"):
    """
    Formatea mensajes de error según el tipo.
    
    Args:
        tipo_error: Tipo de error (general, limpieza, exportacion, validacion)
        
    Returns:
        str: Mensaje de error formateado
    """
    mensajes = {
        "general": "❌ Ha ocurrido un error. Por favor, intenta nuevamente.",
        "limpieza": "❌ No se pudo completar la limpieza. Revisa el log de errores.",
        "exportacion": "❌ No se pudo exportar por IPS. Verifica los datos.",
        "validacion": "❌ No se pudo completar la validación. Verifica el archivo y la configuración.",
        "generacion": "❌ No se pudo generar la copia. Revisa la consola o contacta soporte."
    }
    return mensajes.get(tipo_error, mensajes["general"])
