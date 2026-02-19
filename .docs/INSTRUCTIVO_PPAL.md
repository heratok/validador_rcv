# PROCESAMIENTO DE DATOS - PIPELINE PRINCIPAL

## ⚡ INICIO RÁPIDO

```bash
python procesar_general.py
```

Esto genera: `Procesado_Final.xlsx` y reportes de validación.

---

## 📋 ¿QUÉ HACE EL PIPELINE?

**7 Pasos automáticos:**

1. **Lectura** → Carga `rcv_cesar.xlsx` (3787 registros, 125 columnas)
2. **TRIM** → Elimina espacios inicio/fin en 91 columnas (excluye 34 fechas)
3. **SINDATO** → Rellena con "SINDATO" valores vacíos en 14 columnas de texto
4. **Normalización** → Aplica 20+ reglas específicas por columna
5. **Fechas** → Convierte 34 columnas al formato YYYY/MM/DD
6. **Validación** → Verifica contra configuración JSON
7. **Guardado** → Genera `Procesado_Final.xlsx`

---

## 📊 ARCHIVOS PRINCIPALES

```
raíz/
├── procesar_general.py           ← EJECUTA ESTO (orquestador)
├── normalizadores_lib.py         ← Lógica de normalización
├── fechas_lib.py                 ← Lógica de fechas
├── validar_valores_columna.py    ← Lógica de validación
├── validaciones_config.json      ← Configuración de validaciones
├── requirements.txt              ← Dependencias Python
│
├── rcv_cesar.xlsx                ← ENTRADA (archivo original)
├── Procesado_Final.xlsx          ← SALIDA (archivo procesado)
│
├── codigos_normalizar/           ← Normalizadores por columna
├── fechas/                       ← Scripts de procesamiento de fechas
├── scripts_auxiliares/           ← Scripts de análisis/debug
└── reportes/                     ← Reportes generados
```

---

## 🔧 CONFIGURACIÓN

### `validaciones_config.json`
Define qué valores son válidos para cada columna.

**Ejemplo:**
```json
{
  "indice": 6,
  "nombre": "TIPO DE DM",
  "validos": ["DM TIPO 1", "DM TIPO 2", "SINDATO"]
}
```

**Índices usados: 1-based (como Excel)**
- El script automáticamente convierte a 0-based (pandas)

---

## 📈 CARACTERÍSTICAS

| Característica | Detalles |
|---|---|
| **TRIM** | Elimina espacios inicio/fin, solo en columnas NO-fecha |
| **SINDATO** | Rellena valores vacíos en 14 columnas de texto |
| **Normalización** | 20+ reglas específicas (ej: FEMENINO → Femenino, "SIN DATO" → "SINDATO") |
| **Fechas** | 34 columnas convertidas a YYYY/MM/DD, vacíos → 1800/01/01 |
| **Validación** | Case-insensitive, permite "SIN DATO" → "SINDATO" automáticamente |
| **Reportes** | CSV + Excel con errores de validación |

---

## 🏗️ ESTRUCTURA DE DATOS

### Columnas de Fechas (34 índices 0-based)
```
7, 23, 27, 29, 43, 45, 47, 49, 51, 53, 58, 59, 61, 64, 66, 68,
74, 76, 80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104,
108, 119, 123
```
- **Valores vacíos** → `1800/01/01` (SINDATO)
- **NO aplica** → `1845/01/01` (NO APLICA)
- **Otros formatos** → Convertidos a YYYY/MM/DD

### Columnas para SINDATO (14 índices 0-based)
```
2, 19, 34, 39, 41, 60, 69, 77, 78, 79, 118, 121, 122, 124
```
- **Vacíos** → Rellenados con "SINDATO"
- **Cadenas vacías** → También rellenadas con "SINDATO"

---

## 🧪 SCRIPTS DE ANÁLISIS

En carpeta `scripts_auxiliares/`:

```bash
# Analizar valores vacíos
python scripts_auxiliares/analizar_valores_vacios.py

# Validar clasificación TEXTO vs NUMÉRICO
python scripts_auxiliares/validar_clasificacion_tipos.py

# Verificar SINDATO rellenado
python scripts_auxiliares/verificar_sindato_rellenado.py
```

Ver [scripts_auxiliares/README.md](scripts_auxiliares/README.md) para más detalles.

---

## ⚠️ TROUBLESHOOTING

### "Permission denied" al guardar Procesado_Final.xlsx
**Solución:** Cierra el archivo si está abierto en Excel

### "Archivo no encontrado: rcv_cesar.xlsx"
**Solución:** Asegúrate de que el archivo esté en la misma carpeta que `procesar_general.py`

### Columnas siguen vacías después de SINDATO
**Solución:** Verifica que el índice esté en `INDICES_SINDATO` en `normalizadores_lib.py`

### Fechas no se convirtieron correctamente
**Solución:** Revisa `fechas_lib.py` para ver formatos soportados

---

## 📝 NOTAS

- **Índices JSON:** 1-based (como Excel: A=1, B=2, ..., Z=26)
- **Índices Pandas:** 0-based (A=0, B=1, ..., Z=25)
  - Conversión automática en el código
- **TRIM:** Solo afecta strings, números no se tocan
- **Validación:** Case-insensitive pero preserva mayúsculas en output

---

## 🎯 FLUJO COMPLETO

```
rcv_cesar.xlsx
    ↓
[1] Lectura (3787×125)
    ↓
[2] TRIM (91 columnas)
    ↓
[3] SINDATO (14 columnas)
    ↓
[4] Normalización (20+ reglas)
    ↓
[5] Fechas (34 columnas)
    ↓
[6] Validación (contra JSON)
    ↓
[7] Guardado
    ↓
Procesado_Final.xlsx + Reportes
```

---

**Última actualización:** 2026-02-16
**Versión pipeline:** 2.0 (con SINDATO y TRIM)
