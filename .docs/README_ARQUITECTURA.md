# 📊 Dashboard RCV - Documentación de Estructura

## 🏗️ Arquitectura Refactorizada

El proyecto ha sido completamente refactorizado siguiendo principios de **separación de responsabilidades** y **código limpio**.

### 📁 Estructura de Archivos

```
scipt_excel/
│
├── streamlit_app.py          # 🎯 ARCHIVO PRINCIPAL - Orquestador de la aplicación
├── config_tema.py             # 🎨 Configuración del tema pastel
├── ui_components.py           # 🧩 Componentes reutilizables de UI
├── utils_app.py               # 🛠️ Funciones de utilidad
│
├── tab_crear_copia.py         # 📄 Lógica del Tab 1: Crear Copia
├── tab_limpieza.py            # 🧹 Lógica del Tab 2: Limpieza + IPS
├── tab_validacion.py          # ✅ Lógica del Tab 3: Validación
│
├── crear_con_encabezados_desde_rcv.py  # Generación de copias
├── procesar_general.py                  # Procesamiento y limpieza
├── validar_valores_columna.py           # Validación de datos
│
├── scripts_auxiliares/
│   └── separar_por_ips_consecutivo.py  # Exportación por IPS
│
├── codigos_normalizar/         # Normalizadores por columna
├── fechas/                     # Procesadores de fechas
├── encabezados.json           # Headers persistentes
├── validaciones_config.json   # Configuración de validaciones
└── requirements.txt           # Dependencias
```

## 📖 Descripción de Módulos

### 🎯 `streamlit_app.py` (Archivo Principal)
**Responsabilidad:** Orquestador principal que ensambla todos los componentes.

**Contenido:**
- Configuración de la página
- Aplicación del tema
- Renderizado del header
- Creación y orquestación de tabs

**Líneas de código:** ~40 (reducido de 700+)

---

### 🎨 `config_tema.py`
**Responsabilidad:** Definición y aplicación del tema visual.

**Características:**
- ✨ Tema pastel suave (no satura la vista)
- 🎨 Gradientes suaves beige/azul
- 🔘 Botones con efectos 3D
- 📝 Inputs con bordes redondeados
- 📊 Mensajes con colores pastel distintivos

**Paleta de colores:**
- Fondo: `#fef6f0` → `#f0f4ff`
- Botones: `#a8c5f0` → `#c5b8e0`
- Downloads: `#a8d5ba` → `#c5e8d7`

---

### 🧩 `ui_components.py`
**Responsabilidad:** Componentes reutilizables de interfaz.

**Funciones principales:**
- `mostrar_header()`: Header centralizado
- `mostrar_info_paso()`: Títulos formateados de pasos
- `boton_centrado()`: Botones centrados con iconos
- `crear_columnas_centradas()`: Layout de columnas
- `mostrar_archivos_descarga_duo()`: Descargas en paralelo

**Beneficio:** Consistencia visual en toda la app.

---

### 🛠️ `utils_app.py`
**Responsabilidad:** Funciones de utilidad comunes.

**Funciones principales:**
- `guardar_temporal()`: Manejo de archivos subidos
- `limpiar_directorio()`: Limpieza segura + garbage collection
- `crear_zip()`: Compresión de carpetas
- `formatear_mensaje_exito()`: Mensajes consistentes
- `formatear_mensaje_error()`: Errores categorizados

**Beneficio:** Evita duplicación de código.

---

### 📄 `tab_crear_copia.py`
**Responsabilidad:** Lógica completa del Tab 1.

**Flujo:**
1. Upload del Excel original
2. Configuración de fila de inicio
3. Generación de copia con headers
4. Descarga del archivo `_copia.xlsx`

**Funciones:**
- `mostrar_tab_crear_copia()`: Renderiza todo el contenido

---

### 🧹 `tab_limpieza.py`
**Responsabilidad:** Lógica completa del Tab 2.

**Flujo:**
- **Paso A - Limpieza:**
  1. Upload del archivo copia
  2. Procesamiento (normalización + validación)
  3. Descargas: Excel limpio + reportes

- **Paso B - Exportación IPS:**
  1. Separación por IPS
  2. Generación de CSVs
  3. Compresión en ZIP
  4. Descarga + limpieza opcional

**Funciones:**
- `mostrar_tab_limpieza()`: Orquestador principal
- `_mostrar_seccion_limpieza()`: Paso A
- `_mostrar_archivos_limpieza()`: Descargas paso A
- `_mostrar_seccion_exportacion_ips()`: Paso B

---

### ✅ `tab_validacion.py`
**Responsabilidad:** Lógica completa del Tab 3.

**Flujo:**
1. Upload del Excel
2. Configuración de filas a saltar
3. Validación sin limpieza
4. Descargas: Log + CSV de errores

**Funciones:**
- `mostrar_tab_validacion()`: Renderiza todo el contenido

---

## 🎯 Ventajas de la Refactorización

### ✅ Mantenibilidad
- Cada archivo tiene una responsabilidad única
- Fácil localizar y modificar funcionalidades
- Cambios aislados no afectan otros módulos

### ✅ Reutilización
- Componentes de UI reutilizables
- Funciones de utilidad centralizadas
- Evita duplicación de código

### ✅ Legibilidad
- Código organizado y documentado
- Nombres descriptivos
- Flujo lógico claro

### ✅ Escalabilidad
- Fácil agregar nuevos tabs
- Extender componentes existentes
- Modificar tema sin tocar lógica

### ✅ Testing
- Funciones aisladas fáciles de probar
- Mockeo simplificado
- Debugging más rápido

---

## 🚀 Cómo Ejecutar

```bash
# Activar entorno virtual
.venv\Scripts\Activate.ps1

# Ejecutar aplicación
streamlit run streamlit_app.py
```

---

## 🎨 Tema Visual

### Diseño Pastel Suave
El tema ha sido diseñado para **no saturar la vista**:

- ✨ Colores pastel suaves (no brillantes)
- 🌈 Gradientes sutiles
- 📝 Alto contraste para legibilidad
- 🔘 Elementos con bordes redondeados
- 💫 Transiciones suaves
- 👁️ Sin sidebar (más espacio)

### Sin Cambio de Tema Manual
- No hay selector de tema en sidebar
- Tema único optimizado para uso prolongado
- Basado en principios de diseño UI/UX modernos

---

## 📦 Despliegue

El código refactorizado es compatible con Streamlit Cloud:

```bash
git add .
git commit -m "Refactor: Modular architecture with pastel theme"
git push origin main
```

**Streamlit Cloud detectará automáticamente** `streamlit_app.py` como punto de entrada.

---

## 🔧 Personalización

### Cambiar Colores del Tema
Edita `config_tema.py` y modifica los valores en la función `aplicar_tema_pastel()`.

### Agregar Nuevo Tab
1. Crea `tab_nuevo.py`
2. Define `mostrar_tab_nuevo()`
3. Importa en `streamlit_app.py`
4. Agrega en la lista de tabs

### Modificar Componentes UI
Edita funciones en `ui_components.py` para cambiar apariencia global.

---

## 📚 Dependencias

Ver `requirements.txt` para lista completa.

**Core:**
- streamlit >= 1.41.0
- pandas >= 2.0.0, < 3.0.0
- openpyxl >= 3.1.0
- pyxlsb >= 1.0.10

---

## 👨‍💻 Mantenimiento

### Convenciones de Código
- Nombres descriptivos en español
- Docstrings en todas las funciones
- Emojis para mejorar legibilidad visual
- Type hints donde sea posible

### Git Workflow
```bash
git add archivo_modificado.py
git commit -m "tipo: descripción breve"
git push origin main
```

**Tipos de commit:**
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bugs
- `refactor:` Refactorización de código
- `style:` Cambios de estilo/formato
- `docs:` Documentación

---

**Última actualización:** Febrero 2026  
**Versión:** 2.0 (Refactorizada)
