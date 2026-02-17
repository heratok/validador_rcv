# Scripts Auxiliares y Utilidades

Esta carpeta contiene scripts de análisis, validación y utilidades que se usan durante el desarrollo y validación del pipeline, pero **NO son parte del proceso principal** de `procesar_general.py`.

## Para usar el pipeline principal

Ejecuta desde la **carpeta raíz**:
```bash
python procesar_general.py
```

Esto procesará automáticamente:
- TRIM de espacios en blanco (91 columnas)
- Relleno de "SINDATO" en valores vacíos (14 columnas)
- Normalización de valores (20+ columnas)
- Procesamiento de fechas (34 columnas)
- Validación contra configuración
- Generación de reportes

---

## Scripts Auxiliares

### Análisis de Datos

| Script | Propósito |
|--------|-----------|
| `analizar_valores_vacios.py` | Identifica qué columnas tienen valores vacíos y sus estadísticas |
| `analizar_sindato_necesario.py` | Clasifica columnas como TEXTO vs NUMÉRICA para determinar cuáles rellenar con SINDATO |
| `validar_clasificacion_tipos.py` | Valida que la clasificación automática de tipos de datos sea correcta |

### Búsqueda y Verificación

| Script | Propósito |
|--------|-----------|
| `buscar_fechas_en_no_fechas.py` | Busca valores de fechas especiales en columnas que NO son fechas |
| `buscar_valores_unicos.py` | Extrae valores únicos de columnas especificadas |
| `buscar_columnas_15_20.py` | Búsqueda específica en columnas 15-20 |
| `verificar_complicaciones.py` | Verifica contenido de la columna COMPLICACIONES |
| `verificar_sindato_rellenado.py` | Verifica que SINDATO se rellenó correctamente en 14 columnas |

### Lectura de Encabezados y Estructura

| Script | Propósito |
|--------|-----------|
| `leer_encabezados_fechas.py` | Lee y lista los encabezados de las columnas de fechas |
| `verificar_indices_columnas.py` | Muestra mapeo: índice 1-based ↔ 0-based ↔ letra Excel |
| `validar_indices_fechas.py` | Valida los índices de columnas de fechas |

### Procesamiento Alternativo (Legacy)

| Script | Propósito |
|--------|-----------|
| `procesar_todas_fechas.py` | Script original de procesamiento de fechas (substituido por fechas_lib.py) |
| `limpiar_columnas_trim.py` | Script original de TRIM (substituido por normalizadores_lib.py) |
| `normalizar_valores_unicos.py` | Normalización alternativa de valores |
| `separar_por_ips_consecutivo.py` | Separación de datos por IPS |
| `regenerar_consecutivo.py` | Regeneración de números consecutivos |

---

## Cómo usar estos scripts

Navega a esta carpeta y ejecuta cualquier script:

```bash
cd scripts_auxiliares
python analizar_valores_vacios.py
python analizar_sindato_necesario.py
python validar_clasificacion_tipos.py
```

Los scripts modifican automáticamente sus rutas de entrada para buscar el archivo en la carpeta raíz (`../Procesado_Final.xlsx` o `../rcv_cesar.xlsx`).

---

## Estructura Recomendada

```
scipt_excel/
├── procesar_general.py          ← EJECUTAR ESTO
├── normalizadores_lib.py         ← Librerías principales
├── fechas_lib.py                 ├─ Librerías principales
├── validar_valores_columna.py    ├─ Librerías principales
├── validaciones_config.json      ← Configuración
├── requirements.txt              ← Dependencias
│
├── scripts_auxiliares/           ← Esta carpeta
│   ├── README.md
│   ├── analizar_valores_vacios.py
│   ├── analizar_sindato_necesario.py
│   └── ... (más scripts de análisis)
│
├── codigos_normalizar/           ← Normalizadores específicos
├── fechas/                       ← Scripts de procesamiento de fechas
├── Reportes_Por_IPS_CSV/         ← Reportes
└── Procesado_Final.xlsx          ← Output principal

```

---

## Troubleshooting

- Si un script de análisis no encuentra el archivo: asegúrate de estar en la carpeta **raíz**
- El archivo `Procesado_Final.xlsx` se crea después de ejecutar `procesar_general.py`
- Los scripts auxiliares generan reportes .xlsx en la carpeta raíz

