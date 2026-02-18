# Guía de Despliegue en Streamlit Community Cloud

Esta guía te ayudará a desplegar la aplicación de procesamiento de datos BDRUTACCVM en Streamlit Community Cloud de forma gratuita.

## 📋 Requisitos Previos

1. **Cuenta de GitHub**: Necesitas una cuenta en [github.com](https://github.com)
2. **Cuenta de Streamlit**: Crea una cuenta en [share.streamlit.io](https://share.streamlit.io) usando tu cuenta de GitHub
3. **Git instalado**: Asegúrate de tener Git instalado en tu computadora

## 🚀 Paso a Paso para el Despliegue

### Paso 1: Crear un Repositorio en GitHub

1. Ve a [github.com](https://github.com) e inicia sesión
2. Haz clic en el botón **"+"** en la esquina superior derecha y selecciona **"New repository"**
3. Configura el repositorio:
   - **Repository name**: `scipt_excel` (o el nombre que prefieras)
   - **Description**: "Aplicación para procesamiento de datos BDRUTACCVM"
   - **Visibility**: 
     - **Private** si quieres que solo tú tengas acceso al código
     - **Public** si no te importa que el código sea visible (la app puede ser pública o privada independientemente)
   - **NO** marques "Add a README file" (ya tenemos archivos)
4. Haz clic en **"Create repository"**

### Paso 2: Preparar el Proyecto Local

Abre PowerShell o Terminal en la carpeta del proyecto y ejecuta:

```powershell
# Inicializar repositorio Git (si no está ya inicializado)
git init

# Agregar todos los archivos
git add .

# Crear el primer commit
git commit -m "Initial commit: Dashboard de procesamiento BDRUTACCVM"

# Conectar con tu repositorio de GitHub (reemplaza TU_USUARIO y TU_REPO)
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git

# Subir los archivos a GitHub
git branch -M main
git push -u origin main
```

**Nota**: Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub y `TU_REPO` con el nombre de tu repositorio.

### Paso 3: Verificar Archivos Necesarios

Asegúrate de que estos archivos esenciales estén en el repositorio:

- ✅ `streamlit_app.py` (archivo principal de la aplicación)
- ✅ `requirements.txt` (dependencias)
- ✅ `encabezados.json` (headers necesarios)
- ✅ `validaciones_config.json` (configuración de validación)
- ✅ Todos los archivos `.py` de las carpetas `codigos_normalizar/` y `fechas/`
- ✅ `.gitignore` (ignora archivos temporales)
- ✅ `.streamlit/config.toml` (configuración de la app)

### Paso 4: Desplegar en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Haz clic en **"New app"** o **"Create app"**
3. Configura el despliegue:
   - **Repository**: Selecciona tu repositorio (ej: `TU_USUARIO/scipt_excel`)
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
   - **App URL**: Elige un nombre único (ej: `procesamiento-bdrutaccvm`)
4. Haz clic en **"Deploy!"**

### Paso 5: Esperar el Despliegue

- El despliegue toma **2-5 minutos**
- Verás los logs de instalación de dependencias
- Una vez completado, tu app estará disponible en: `https://TU_APP.streamlit.app`

## 🔧 Configuración Adicional

### Límites del Plan Gratuito

- **RAM**: 1 GB
- **CPU**: Compartida
- **Almacenamiento**: Limitado (por eso implementamos limpieza automática)
- **Tiempo de inactividad**: La app se "duerme" después de inactividad, se reactiva al visitarla

### Hacer la App Privada (Opcional)

1. En el dashboard de Streamlit Cloud, selecciona tu app
2. Ve a **Settings** → **Sharing**
3. Cambia de **"Public"** a **"Private"**
4. Solo personas con el link y autorizadas podrán acceder

### Actualizar la Aplicación

Cada vez que hagas cambios en tu código local:

```powershell
# Agregar cambios
git add .

# Crear commit con descripción
git commit -m "Descripción de los cambios"

# Subir a GitHub
git push origin main
```

**Streamlit Cloud detectará automáticamente los cambios y redesplegará la app.**

## 📊 Monitoreo y Logs

1. En el dashboard de Streamlit Cloud, haz clic en tu app
2. Haz clic en **"Manage app"** (tres puntos)
3. Selecciona **"Logs"** para ver errores en tiempo real
4. Selecciona **"Analytics"** para ver estadísticas de uso

## ⚠️ Solución de Problemas

### Error: "requirements.txt not found"
- Asegúrate de que `requirements.txt` esté en la raíz del repositorio

### Error: "Module not found"
- Verifica que todas las dependencias estén en `requirements.txt`
- Asegúrate de que todos los archivos `.py` necesarios estén en el repositorio

### La app se queda cargando
- Revisa los logs en Streamlit Cloud
- Verifica que `encabezados.json` esté en el repositorio
- Asegúrate de que no haya errores de sintaxis

### Archivos muy grandes
- El plan gratuito tiene límite de tamaño de archivos subidos (200 MB por archivo)
- Los archivos procesados se limpian automáticamente para no llenar el espacio

## 🔐 Seguridad

1. **NO subas datos sensibles**: El `.gitignore` ya excluye archivos `.xlsx`, `.xlsb`, `.csv`
2. **Revisa antes de hacer push**: Usa `git status` para ver qué archivos se subirán
3. **Repositorio privado**: Considera hacer tu repositorio privado si contiene lógica de negocio sensible

## 📞 Recursos Adicionales

- [Documentación Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- [Foro de Streamlit](https://discuss.streamlit.io/)
- [Documentación de Git](https://git-scm.com/doc)

## ✅ Checklist Final

Antes de desplegar, verifica:

- [ ] Todos los archivos necesarios están en el repositorio
- [ ] `requirements.txt` está actualizado
- [ ] `.gitignore` excluye archivos sensibles
- [ ] La app funciona localmente (`streamlit run streamlit_app.py`)
- [ ] Has hecho push de todos los cambios a GitHub
- [ ] Has creado la app en Streamlit Cloud

---

**¡Listo!** Tu aplicación estará disponible en `https://tu-app.streamlit.app` 🎉
