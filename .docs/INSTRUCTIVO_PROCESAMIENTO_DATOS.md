# INSTRUCTIVO DE PROCESAMIENTO DE DATOS - RCV CESAR

## 1. TRATAMIENTO DE VALORES VACÍOS O NULOS

### Regla General
**Todos los campos vacíos, nulos o con variantes de "SIN DATO" se reemplazan con:** `SINDATO`

### Valores que se convierten a SINDATO:
- Celdas vacías (NaN, null)
- Espacios en blanco (`""`, `"  "`)
- Texto "0", "0.0", "0.00", "0,0", "0,00"
- Valores numéricos: 0, 0.0
- Variantes de "sin dato":
  - `SIN DATO`
  - `SIN DATOS`
  - `SINDATOS`
  - `Sin Dato`
  - `Sin Datos`
  - `sin dato`
  - `sin datos`

### Aplicación:
- Se aplica a **todas las columnas** del archivo
- Incluye las 125 columnas desde CONSECUTIVO hasta OBSERVACIONES
- Garantiza que no haya registros vacíos en los archivos CSV generados

---

## 2. TRATAMIENTO DE FECHAS

### Formato Estandarizado
**Todas las fechas se convierten al formato:** `YYYY/MM/DD` (Año con 4 dígitos / Mes con 2 dígitos / Día con 2 dígitos)

### Columnas de Fechas (32 columnas en total)
Índices de columnas con fechas: 7, 23, 27, 29, 43, 45, 47, 49, 51, 53, 58, 59, 61, 64, 66, 68, 74, 76, 80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 104, 108, 119

### Formatos de Entrada Aceptados:
- **DD/MM/YYYY** → se convierte a YYYY/MM/DD
- **YYYY-MM-DD** → se convierte a YYYY/MM/DD
- **YYYY-MM-DD HH:MM:SS** → se extrae solo la fecha como YYYY/MM/DD
- **Números seriales de Excel** → se convierten a fecha real
- **Objetos datetime/Timestamp de pandas** → se convierten a YYYY/MM/DD

### Fechas Comodín (Valores Especiales)
Ciertas palabras clave se mapean a fechas especiales:

| Texto Original | Fecha Resultante |
|----------------|------------------|
| `NORMAL` | `1800/01/01` |
| `NO APLICA` | `1845/01/01` |
| `SI` | `1845/01/01` |

**Nota:** En las columnas Medicamento, la fecha `1800-01-01` se reemplaza por `SINDATO`

### Corrección de Offset
Las fechas que vienen como números seriales de Excel se corrigen con **-2 días** para ajustar el desfase histórico de Excel.

---

## 3. NORMALIZACIÓN DE VALORES ÚNICOS

### Objetivo
Estandarizar valores que se escriben de diferentes formas pero significan lo mismo.

### Reglas de Normalización:

#### A. Capitalización
- Todos los valores se comparan **sin distinguir mayúsculas/minúsculas**
- Variantes como `SIN DATO`, `Sin Dato`, `sin dato` se unifican a `SINDATO`

#### B. Espacios en Blanco
- Se eliminan espacios al inicio y al final (`.strip()`)
- Detecta valores que parecen diferentes por espacios extras

#### C. Variantes de Texto
Ejemplos de unificación:
- `SIN DATO` = `SIN DATOS` = `SINDATOS` = `Sin Datos` → **SINDATO**
- Valores numéricos cero en diferentes formatos → **SINDATO**

---

## 4. COLUMNAS MEDICAMENTO (7 columnas)

### Columnas Específicas:
- Medicamento (índice 110)
- Medicamento2 (índice 111)
- Medicamento3 (índice 112)
- Medicamento4 (índice 113)
- Medicamento5 (índice 114)
- Medicamento6 (índice 115)
- Medicamento7 (índice 116)

### Reglas Especiales para Medicamentos:

1. **Eliminación de punto y coma (;)**
   - Se eliminan **todos los ";"** dentro de los datos de medicamentos
   - Evita conflictos con el delimitador CSV

2. **Conversión a SINDATO**
   - Valores vacíos → `SINDATO`
   - Valores "0" (texto o número) → `SINDATO`
   - Fecha `1800-01-01` → `SINDATO`

---

## 5. SEPARACIÓN POR IPS (CSV Individuales)

### Configuración de Archivos CSV:

| Parámetro | Valor |
|-----------|-------|
| **Delimitador** | `;` (punto y coma) |
| **Codificación** | ANSI (cp1252) |
| **Encabezados** | Sí (primera fila con nombres de columnas) |
| **Comillas** | No (sin entrecomillar valores) |
| **Columnas Totales** | 125 exactas |

### Proceso de Separación:

1. **Agrupación:** Los registros se agrupan por el campo IPS (columna índice 22)

2. **Consecutivo:** 
   - Si existe la columna CONSECUTIVO en las 125 originales, se actualiza
   - El consecutivo se reinicia desde 1 para cada archivo IPS
   - NO se crean columnas adicionales (mantener exactamente 125)

3. **Nombres de Archivo:**
   - Formato: `[NOMBRE_IPS].csv`
   - Caracteres `/` y `\` se reemplazan por `-`
   - Ubicación: carpeta `Reportes_Por_IPS_CSV/`

4. **Validación:**
   - Cada archivo debe tener exactamente **125 columnas**
   - La última columna debe ser **OBSERVACIONES**
   - Primera columna: **CONSECUTIVO** (si existe en el original)

---

## 6. ARCHIVO MEDICAMENTOS_SINDATO.xlsx

### Propósito:
Generar un archivo Excel que contenga **únicamente las 7 columnas de Medicamento** con datos limpios.

### Contenido:
- 7 columnas: Medicamento hasta Medicamento7
- 3787 filas de datos (sin contar encabezado)
- Valores vacíos, ceros y "1800-01-01" convertidos a `SINDATO`

### Uso:
Archivo de referencia para validar que los medicamentos estén correctamente normalizados antes de enviar a producción.

---

## 7. SCRIPTS PRINCIPALES

### `procesar_todas_fechas.py`
- **Función:** Normaliza las 32 columnas de fechas
- **Entrada:** `limpieza.xlsx`
- **Salida:** `Todas_Fechas_Estandarizadas.xlsx`
- **Formato salida:** YYYY/MM/DD

### `separar_por_ips_consecutivo.py`
- **Función:** Genera archivos CSV individuales por IPS
- **Entrada:** `rcv_cesar.xlsx`
- **Salida:** Múltiples CSV en `Reportes_Por_IPS_CSV/`
- **Características:** Delimitador ";", ANSI, sin comillas, 125 columnas

### `buscar_columnas_15_20.py`
- **Función:** Extrae y limpia columnas Medicamento
- **Entrada:** `rcv_cesar.xlsx`
- **Salida:** `Medicamentos_SINDATO.xlsx`
- **Características:** Solo 7 columnas, valores normalizados a SINDATO

### `limpiar_columnas_trim.py`
- **Función:** Detecta y limpia espacios en blanco innecesarios
- **Interactivo:** Menú para analizar columnas específicas o todas
- **Salida:** `Columnas_Con_Trim.xlsx` (opcional)

### `regenerar_consecutivo.py`
- **Función:** Renumera la columna CONSECUTIVO desde 1 hasta n
- **Uso:** Cuando se necesita regenerar el orden secuencial

---

## 8. FLUJO COMPLETO DE PROCESAMIENTO

```
1. Archivo Original (rcv_cesar.xlsx)
   ↓
2. Normalización de Fechas (procesar_todas_fechas.py)
   ↓
3. Limpieza de Espacios/TRIM (limpiar_columnas_trim.py)
   ↓
4. Extracción Medicamentos (buscar_columnas_15_20.py)
   ↓
5. Separación por IPS (separar_por_ips_consecutivo.py)
   ↓
6. Archivos CSV Finales (delimitador ";", ANSI, 125 columnas)
```

---

## 9. VALIDACIONES FINALES

### Antes de Enviar los CSV:

✅ **Verificar:**
1. Todos los archivos CSV tienen exactamente 125 columnas
2. No hay valores vacíos (todos deben ser SINDATO si no tienen dato)
3. Las fechas están en formato YYYY/MM/DD
4. No hay caracteres ";" en las columnas Medicamento
5. Codificación es ANSI (cp1252)
6. Delimitador es ";" (punto y coma)
7. Primera fila contiene encabezados
8. Última columna es OBSERVACIONES

### Herramientas de Validación:
- Los scripts muestran advertencias si detectan columnas incorrectas
- Se reporta el número de reemplazos realizados (vacíos, ceros, fechas)
- Se muestra el total de registros y columnas por archivo

---

## 10. NOTAS IMPORTANTES

⚠️ **Configuración de Archivos:**
- `NUM_FILAS_A_SALTEAR = 1` → Siempre salta 1 fila (el encabezado original)
- Los encabezados se leen por separado y se asignan manualmente a las columnas

⚠️ **Valores Especiales:**
- La fecha `1800-01-01` es un comodín que en Medicamentos se convierte a SINDATO
- Las fechas `1845-01-01` y `1845-01-02` son válidas (representan "NO APLICA" y "SI")

⚠️ **Columnas:**
- Total en archivo original: 125 columnas (A hasta DU en Excel)
- Índice en Python: 0 a 124
- Primera columna (índice 0): CONSECUTIVO
- Última columna (índice 124): OBSERVACIONES

---

**Fecha de última actualización:** Diciembre 2025  
**Versión:** 2.0
