"""
Biblioteca centralizada de normalizadores para columnas específicas.
Cada función recibe un DataFrame y devuelve el DataFrame con las columnas normalizadas.

IMPORTANTE: Todos los índices en este módulo son 0-based (índices pandas).
Para referencia:
  - Columna A (1 en Excel) = índice 0
  - Columna K (11 en Excel) = índice 10
  - Columna M (13 en Excel) = índice 12
"""
import pandas as pd
import unicodedata
import re
import numpy as np


def normalizar_texto(texto):
    """Quita tildes, pasa a minúsculas, elimina espacios extra"""
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.strip()
    return texto


def _aplicar_normalizacion(df, indice, func_normalizar):
    """Función helper para aplicar normalización de forma segura"""
    if indice < 0 or indice >= len(df.columns):
        return df
    
    # Aplicar normalización y convertir a valores numpy para asignación segura
    col_normalizada = df.iloc[:, indice].apply(func_normalizar)
    
    # Asignar usando .values para evitar problemas de dtype
    col_orig = df.columns[indice]
    df[col_orig] = col_normalizada.values
    
    return df


# Índices 0-based de columnas que deben rellenarse con SINDATO cuando estén vacías
INDICES_SINDATO = [2, 19, 34, 39, 41, 60, 69, 77, 78, 79, 118, 121, 122, 124]

# Índices 0-based de columnas de medicamentos (vacíos Y ceros → SINDATO)
INDICES_MEDICAMENTOS = [110, 111, 112, 113, 114, 115, 116]


def normalizar_variantes_sin_dato(df):
    """
    PASO 1 (PRIMERO): Normaliza TODAS las variantes de 'SIN DATO' a 'SINDATO' en TODO el DataFrame.
    
    Convierte:
    - 'SIN DATO' (con espacios simples o múltiples)
    - 'SIN DATOS'
    - 'sin dato', 'SIN_DATO', etc. (mayúsculas/minúsculas)
    
    A: 'SINDATO'
    
    Returns:
        DataFrame con todas las variantes de 'SIN DATO' convertidas a 'SINDATO'
    """
    def convertir_sin_dato(valor):
        if pd.isna(valor):
            return valor
        
        valor_str = str(valor).strip()
        valor_upper = valor_str.upper()
        
        # Normalizar espacios múltiples
        valor_upper = re.sub(r'\s+', ' ', valor_upper)
        
        # Convertir todas las variantes de SIN DATO a SINDATO
        if valor_upper in ('SIN DATO', 'SIN DATOS', 'SIN_DATO', 'SINDATO'):
            return 'SINDATO'
        
        return valor
    
    # Aplicar a todas las columnas
    df_procesado = df.copy()
    for col_idx in range(len(df_procesado.columns)):
        try:
            df_procesado.iloc[:, col_idx] = df_procesado.iloc[:, col_idx].apply(convertir_sin_dato)
        except Exception:
            pass
    
    print("  OK - Variantes de 'SIN DATO' convertidas a 'SINDATO'")
    return df_procesado


def rellenar_sindato_columnas(df, indices_columnnas=None):
    """
    Rellena con "SINDATO" los valores vacíos en columnas de texto especificadas.
    
    Args:
        df: DataFrame a procesar
        indices_columnas: Lista de índices 0-based de columnas a procesar (por defecto INDICES_SINDATO)
    
    Returns:
        DataFrame con SINDATO en valores vacíos
    """
    if indices_columnnas is None:
        indices_columnnas = INDICES_SINDATO
    
    columnas_procesadas = 0
    
    for indice in indices_columnnas:
        if indice < 0 or indice >= len(df.columns):
            continue
        
        try:
            col = df.iloc[:, indice]
            
            # Contar valores vacíos antes de rellenar
            vacios_antes = col.isna().sum()
            vacios_str = (col.astype(str).str.strip() == '').sum() if col.dtype == 'object' else 0
            total_vacios = max(vacios_antes, vacios_str)
            
            # Rellenar NaN con SINDATO
            col_rellena = col.fillna("SINDATO")
            
            # Rellenar cadenas vacías con SINDATO (solo si es de tipo object)
            if col.dtype == 'object':
                col_rellena = col_rellena.astype(str).apply(
                    lambda x: "SINDATO" if x.strip() == '' else x
                )
            
            df[df.columns[indice]] = col_rellena.values
            columnas_procesadas += 1
        except Exception:
            # Si falla, continuar con la siguiente columna
            pass
    
    print(f"  OK - Rellenadas {columnas_procesadas} columnas con SINDATO")
    return df


def rellenar_medicamentos_sindato(df, indices_medicamentos=None):
    """
    Rellena con "SINDATO" los valores vacíos Y valores "0" en columnas de medicamentos.
    
    Args:
        df: DataFrame a procesar
        indices_medicamentos: Lista de índices 0-based de columnas de medicamentos (por defecto INDICES_MEDICAMENTOS)
    
    Returns:
        DataFrame con SINDATO en valores vacíos y ceros
    """
    if indices_medicamentos is None:
        indices_medicamentos = INDICES_MEDICAMENTOS
    
    columnas_procesadas = 0
    total_reemplazos = 0
    
    for indice in indices_medicamentos:
        if indice < 0 or indice >= len(df.columns):
            continue
        
        try:
            col = df.iloc[:, indice]
            
            # Contar valores vacíos
            vacios = col.isna().sum()
            
            # Contar valores que son 0 en diferentes formatos
            cero_mask = (
                col.astype(str)
                .str.strip()
                .str.replace(',', '.')
                .isin(['0', '0.0', '0.00', 'nan'])
            )
            ceros = cero_mask.sum()
            
            # Reemplazar espacios vacíos por NaN
            col_procesada = col.replace(r'^\s*$', pd.NA, regex=True)
            
            # Reemplazar valores cero por NaN
            col_procesada = col_procesada.replace({
                0: pd.NA,
                0.0: pd.NA,
                '0': pd.NA,
                '0.0': pd.NA,
                '0.00': pd.NA,
                '0,0': pd.NA,
                '0,00': pd.NA,
                'nan': pd.NA,
                'NaN': pd.NA,
                'NAN': pd.NA
            })
            
            # Rellenar todos los NaN con SINDATO
            col_procesada = col_procesada.fillna('SINDATO')
            
            df[df.columns[indice]] = col_procesada.values
            columnas_procesadas += 1
            total_reemplazos += vacios + ceros
        except Exception as e:
            # Si falla, continuar con la siguiente columna
            print(f"  ⚠ Error en columna {indice}: {e}")
            pass
    
    print(f"  OK - Rellenadas {columnas_procesadas} columnas de medicamentos con SINDATO ({total_reemplazos} reemplazos)")
    return df


# --- NORMALIZADORES POR COLUMNA ---

def normalizar_columna_k(df, indice=10):
    """Columna K (11): SEXO - Normaliza FEMENINO/MASCULINO a formato title"""
    def normalizar_sexo(valor):
        val = str(valor).strip().upper()
        if val == "FEMENINO":
            return "Femenino"
        if val == "MASCULINO":
            return "Masculino"
        return str(valor)
    
    return _aplicar_normalizacion(df, indice, normalizar_sexo)


def normalizar_columna_m(df, indice=12):
    """Columna M (13): PERTENENCIA ÉTNICA"""
    def normalizar_etnia(valor):
        t = normalizar_texto(str(valor))
        if any(x in t for x in ["negro", "afro", "mulato"]):
            return "Negro (a), Mulato, Afroamericano"
        if "indigena" in t:
            return "Indígena"
        if "rom" in t or "gitano" in t:
            return "ROM (Gitano)"
        if "raizal" in t:
            return "Raizal del Archipielago"
        if "mestizo" in t:
            return "Mestizo"
        if "ninguna" in t or "ningunas" in t:
            return "Ningunas de las Anteriores"
        return "Ningunas de las Anteriores"
    
    return _aplicar_normalizacion(df, indice, normalizar_etnia)


def normalizar_columna_n(df, indice=13):
    """Columna N (14): GRUPO POBLACIONAL"""
    def normalizar_grupo(valor):
        t = normalizar_texto(str(valor))
        
        if any(x in t for x in ["comunidades indigenas", "comunidad indigena"]):
            return "Comunidades Indiginas"
        if "discapacitados" in t:
            return "Discapacitados"
        if any(x in t for x in ["victima", "conflicto", "armado"]):
            return "Victimas del Conflicto Armado"
        if "desplazados" in t or "desmovilizados" in t:
            return "Desmovilizados"
        if "adulto mayor" in t:
            return "Adulto Mayor"
        if any(x in t for x in ["madre", "cabeza de hogar", "madres comunitarias"]):
            return "Mujer Cabeza de Hogar"
        if "icbf" in t or "infantil" in t:
            return "Población Infantil a cargo del ICBF"
        if "embarazada" in t:
            return "Mujer Embarazada"
        
        return "Otro Grupo Poblacional"
    
    return _aplicar_normalizacion(df, indice, normalizar_grupo)


def normalizar_columna_o(df, indice=14):
    """Columna O (15): ETNIA"""
    def normalizar_etnia_especifica(valor):
        t = normalizar_texto(str(valor))
        
        if "wayuu" in t or "wayu" in t:
            return "Wayuu"
        if "arhuaco" in t or "ika" in t:
            return "Arhuaco"
        if "wiwa" in t:
            return "Wiwa"
        if "yukpa" in t or "yuko" in t:
            return "Yukpa"
        if "kogui" in t or "kogi" in t:
            return "Kogui"
        if "inga" in t:
            return "Inga"
        if "kankuamo" in t:
            return "Kankuamo"
        if "chimila" in t:
            return "Chimila"
        if "zenu" in t:
            return "Zenu"
        
        return "Sin Etnia"
    
    return _aplicar_normalizacion(df, indice, normalizar_etnia_especifica)


def normalizar_columna_s(df, indice=18):
    """Columna S (19): ZONA DE UBICACIÓN"""
    def normalizar_zona(valor):
        val = str(valor).strip().upper()
        # Convertir abreviaciones y variantes
        if val in ["URBANA", "U"]:
            return "Urbana"
        if val in ["RURAL", "R"]:
            return "Rural"
        return str(valor)
    
    return _aplicar_normalizacion(df, indice, normalizar_zona)


def normalizar_columna_y(df, indice=24):
    """Columna Y (25): FUMA"""
    def normalizar_si_no(valor):
        t = normalizar_texto(str(valor))
        if t in ["si", "s", "1"]:
            return "Si"
        if t in ["no", "n", "0"]:
            return "No"
        return "SINDATO"
    
    return _aplicar_normalizacion(df, indice, normalizar_si_no)


def normalizar_columna_z(df, indice=25):
    """Columna Z (26): CONSUMO DE ALCOHOL"""
    def normalizar_si_no(valor):
        t = normalizar_texto(str(valor))
        if t in ["si", "s", "1"]:
            return "Si"
        if t in ["no", "n", "0"]:
            return "No"
        return "SINDATO"
    
    return _aplicar_normalizacion(df, indice, normalizar_si_no)


def normalizar_columna_aa(df, indice=26):
    """Columna AA (27): DX CONFIRMADO HTA"""
    def normalizar_si_no(valor):
        t = normalizar_texto(str(valor))
        if t in ["si", "s", "1"]:
            return "Si"
        if t in ["no", "n", "0"]:
            return "No"
        return "No"
    
    return _aplicar_normalizacion(df, indice, normalizar_si_no)


def normalizar_columna_ac(df, indice=28):
    """Columna AC (29): DX CONFIRMADO DM"""
    def normalizar_si_no(valor):
        t = normalizar_texto(str(valor))
        if t in ["si", "s", "1"]:
            return "Si"
        if t in ["no", "n", "0"]:
            return "No"
        return "No"
    
    return _aplicar_normalizacion(df, indice, normalizar_si_no)


def normalizar_columna_ae(df, indice=30):
    """Columna AE (31): TIPO DE DM"""
    def normalizar_tipo_dm(valor):
        t = normalizar_texto(str(valor))

        if "tipo 1" in t and "insulino" in t:
            return "Tipo 1 Insulinodependiente"
        if "tipo 2" in t and ("no insulino" in t or "no insulinodep" in t or "no dependiente" in t):
            return "Tipo 2 No Insulinodependiente"
        if "tipo 2" in t and "insulino" in t:
            return "Tipo 2 Insulinodependiente"
        if "no aplica" in t:
            return "No Aplica"

        return "No Aplica"
    
    return _aplicar_normalizacion(df, indice, normalizar_tipo_dm)


def normalizar_columna_af(df, indice=31):
    """Columna AF (32): ETIOLOGÍA DE LA ERC"""
    def normalizar_etiologia(valor):
        t = normalizar_texto(str(valor))
        
        if "hta" in t or "dm" in t or "diabetes" in t or "hipertension" in t:
            return "HTA o DM"
        if "autoinmune" in t:
            return "Autoinmune"
        if "obstructiv" in t or "nefropatia obstructiva" in t:
            return "Nefropatía Obstructiva"
        if "poliquistic" in t:
            return "Enfermedad Poliquistica"
        if "no tiene" in t or "sin erc" in t:
            return "No tiene ERC"
        
        return "Otras"
    
    return _aplicar_normalizacion(df, indice, normalizar_etiologia)


def normalizar_columna_ay(df, indice=50):
    """Columna AY (51): PARCIAL DE ORINA"""
    def normalizar_orina(valor):
        t = normalizar_texto(str(valor))
        
        if "normal" in t:
            return "Normal"
        if "patologic" in t or "anormal" in t:
            return "Patologico"
        
        return "SINDATO"
    
    return _aplicar_normalizacion(df, indice, normalizar_orina)


def normalizar_columna_bk(df, indice=62):
    """Columna BK (63): DM CONTROLADA"""
    def normalizar_si_no(valor):
        t = normalizar_texto(str(valor))
        if t in ["si", "s", "1"]:
            return "Si"
        if t in ["no", "n", "0"]:
            return "No"
        return "No"
    
    return _aplicar_normalizacion(df, indice, normalizar_si_no)


def normalizar_columna_reporte_ekg(df, indice=65):
    """Columna BN (66): REPORTE DE EKG"""
    def normalizar_ekg(valor):
        t = normalizar_texto(str(valor))
        
        if "normal" in t:
            return "Normal"
        if "anormal" in t or "patologic" in t:
            return "Anormal"
        
        return "SINDATO"
    
    return _aplicar_normalizacion(df, indice, normalizar_ekg)


def normalizar_columna_ecocardiograma(df, indice=67):
    """Columna BP (68): ECOCARDIOGRAMA"""
    def normalizar_eco(valor):
        # Si es 0 o vacío, convertir a SINDATO
        if pd.isna(valor) or str(valor).strip() in ['', '0', '0.0']:
            return "SINDATO"
            
        t = normalizar_texto(str(valor))
        
        if "normal" in t:
            return "Normal"
        if "anormal" in t or "patologic" in t or "alterado" in t:
            return "Anormal"
        
        # Para textos descriptivos médicos, convertir a "Anormal" (contiene hallazgos)
        return "Anormal"
    
    return _aplicar_normalizacion(df, indice, normalizar_eco)


def normalizar_columna_dn(df, indice=109):
    """Columna DF (110): HTA CONTROLADA"""
    def normalizar_si_no(valor):
        t = normalizar_texto(str(valor))
        if t in ["si", "s", "1"]:
            return "Si"
        if t in ["no", "n", "0"]:
            return "No"
        return "No"
    
    return _aplicar_normalizacion(df, indice, normalizar_si_no)


def normalizar_columna_w(df, indice=22):
    """Columna W (23): NOMBRE DE LA IPS QUE HACE SEGUIMIENTO - No requiere normalización específica"""
    # Esta columna contiene nombres de texto (ej: "IPSI DUSAKAWI")
    # Solo se aplica TRIM general, sin normalización adicional
    return df


def normalizar_columnas_aq_as(df, indices=[42, 44]):
    """Columnas AQ (43), AS (45) - CLASIFICACION RCV"""
    def normalizar_rcv(valor):
        t = normalizar_texto(str(valor))
        
        if "alto" in t:
            return "Riesgo Alto"
        if "bajo" in t:
            return "Riesgo Bajo"
        if "moderado" in t or "medio" in t:
            return "Riesgo Moderado"
        
        return "No se Clasifico"
    
    for indice in indices:
        df = _aplicar_normalizacion(df, indice, normalizar_rcv)
    
    return df


def normalizar_columnas_control_realizado_por(df, indices=None):
    """
    Normaliza columnas de CONTROL REALIZADO POR (82,84,86,88,90,92,94,96,98,100,102,104)
    """
    if indices is None:
        indices = [81, 83, 85, 87, 89, 91, 93, 95, 97, 99, 101, 103]  # 0-indexed
    
    def normalizar_control(valor):
        t = normalizar_texto(str(valor))
        
        if "enfermeria" in t and "medico" in t:
            return "MEDICO Y ENFERMERIA"
        if "medico" in t and "internista" in t:
            return "MEDICO INTERNISTA"
        if "medico" in t and "general" in t:
            return "MEDICO GENERAL"
        if "enfermeria" in t:
            return "ENFERMERIA"
        if "nutricionista" in t or "nutricion" in t:
            return "NUTRICIONISTA"
        if "psicolog" in t:
            return "PSICOLOGIA"
        if "no aplica" in t or "n/a" in t:
            return "NO APLICA"
        
        return "SINDATO"
    
    for indice in indices:
        df = _aplicar_normalizacion(df, indice, normalizar_control)
    
    return df


def normalizar_adherencia_tratamiento(df, indice=117):
    """Columna DN (118): ADHERENCIA AL TRATAMIENTO FARMACOLOGICO"""
    def normalizar_adherencia(valor):
        t = normalizar_texto(str(valor))
        if t in ["si", "s", "1", "adherente"]:
            return "Si"
        if t in ["no", "n", "0", "no adherente"]:
            return "No"
        return "SINDATO"
    
    return _aplicar_normalizacion(df, indice, normalizar_adherencia)


# --- FUNCIÓN ORQUESTADORA ---

def aplicar_trim_general(df, indices_excluir=None):
    """
    Aplica TRIM (strip) a TODAS las columnas de tipo texto/objeto excepto las excluidas.
    
    Args:
        df: DataFrame a procesar
        indices_excluir: Lista de índices de columnas a excluir del TRIM (ej: columnas de fechas)
    
    Returns:
        DataFrame con TRIM aplicado
    """
    if indices_excluir is None:
        indices_excluir = set()
    else:
        indices_excluir = set(indices_excluir)
    
    columnas_procesadas = 0
    columnas_excluidas = len(indices_excluir)
    
    for indice in range(len(df.columns)):
        if indice in indices_excluir:
            continue
        
        try:
            col = df.iloc[:, indice]
            # Aplicar TRIM a todas las columnas (pandas mantendrá el tipo original)
            # Solo hacemos strip si el valor es string
            def safe_strip(x):
                if pd.isna(x):
                    return x
                if isinstance(x, str):
                    return x.strip()
                return x
            
            col_trimmed = col.apply(safe_strip)
            df[df.columns[indice]] = col_trimmed.values
            columnas_procesadas += 1
        except Exception:
            # Si falla, continuar con la siguiente columna
            pass
    
    print(f"  ✓ TRIM aplicado a {columnas_procesadas} columnas (excluidas {columnas_excluidas} fechas)")
    return df


def aplicar_todos_normalizadores(df):
    """
    Aplica todos los normalizadores conocidos al DataFrame.
    Se ejecutan en orden según las columnas.
    """
    print("Aplicando normalizadores específicos...")
    
    df = normalizar_columna_k(df, 10)
    df = normalizar_columna_m(df, 12)
    df = normalizar_columna_n(df, 13)
    df = normalizar_columna_o(df, 14)
    df = normalizar_columna_s(df, 18)
    df = normalizar_columna_w(df, 22)
    df = normalizar_columna_y(df, 24)
    df = normalizar_columna_z(df, 25)
    df = normalizar_columna_aa(df, 26)
    df = normalizar_columna_ac(df, 28)
    df = normalizar_columna_ae(df, 30)
    df = normalizar_columna_af(df, 31)
    df = normalizar_columnas_aq_as(df, [42, 44])
    df = normalizar_columna_ay(df, 50)
    df = normalizar_columna_bk(df, 62)
    df = normalizar_columna_reporte_ekg(df, 65)
    df = normalizar_columna_ecocardiograma(df, 67)
    df = normalizar_columnas_control_realizado_por(df, [81, 83, 85, 87, 89, 91, 93, 95, 97, 99, 101, 103])
    df = normalizar_columna_dn(df, 109)
    df = normalizar_adherencia_tratamiento(df, 117)
    
    print("✓ Normalizadores específicos aplicados")
    return df
