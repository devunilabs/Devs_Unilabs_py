# Sincronizador Excel OneDrive v2.0

Sistema avanzado de sincronización automática para archivos Excel compartidos en OneDrive con detección de cambios en tiempo real desde la nube.

## 🚀 Características Principales

- **Detección Híbrida**: Combina file watcher local + verificación periódica en la nube
- **Sincronización Inmediata**: Detecta cambios tanto locales como desde OneDrive web
- **Interfaz Web Moderna**: Panel de control completo con monitoreo en tiempo real
- **Sistema de Logs**: Registro detallado de todas las operaciones
- **Configuración Dinámica**: Ajustes en tiempo real sin reiniciar el sistema
- **Validación de Integridad**: Verificación hash MD5 para garantizar copias correctas
- **Sistema de Reintentos**: Manejo robusto de errores con reintentos automáticos

## 📁 Estructura del Proyecto

```
REENVIOCATALOG/
│
├── backend/
│   ├── app.py                # Servidor Flask principal
│   ├── envio.py              # Gestor de envío de archivos
│   ├── config.py             # Configuración del sistema
│   ├── watcher.py            # Monitor híbrido de cambios
│   └── log.txt               # Registro de eventos
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css    # Estilos modernos con gradientes
│   │   └── js/
│   │       └── script.js     # Lógica de la interfaz
│   └── templates/
│       └── index.html        # Interfaz principal
├── requirements.txt
├── test_onedrive.py
|
└── README.md                 # Esta documentación
```

## 🛠️ Instalación

### 1. Requisitos del Sistema

```bash
# Python 3.7 o superior
python --version

# Pip para instalar dependencias
pip --version
```

### 2. Dependencias de Python

```bash
# Instalar dependencias principales
pip install flask watchdog

# O usando requirements.txt (crear si no existe)
pip install -r requirements.txt
```

**Contenido de requirements.txt:**
```
Flask==2.3.3
watchdog==3.0.0
```

### 3. Configuración Inicial

1. **Editar rutas en `backend/config.py`:**

```python
# Ejemplo para Windows
RUTA_ORIGEN = r"C:\Users\TuUsuario\OneDrive\Documentos\archivo_compartido.xlsx"
RUTA_DESTINO = r"C:\Users\TuUsuario\Desktop\destino\archivo_compartido.xlsx"

# Ejemplo para Linux/Mac
RUTA_ORIGEN = "/home/usuario/OneDrive/Documentos/archivo_compartido.xlsx"
RUTA_DESTINO = "/home/usuario/Desktop/destino/archivo_compartido.xlsx"
```

2. **Verificar permisos de archivos:**
   - Asegurar acceso de lectura al archivo OneDrive
   - Asegurar acceso de escritura al directorio destino

## 🚀 Uso del Sistema

### Inicio Rápido

1. **Ejecutar el servidor:**
```bash
cd backend
python app.py
```

2. **Abrir interfaz web:**
   - Navegar a: `http://localhost:5000`
   - Configurar rutas en el panel de configuración
   - Hacer clic en "Iniciar Monitor"

### Ejecución Solo Backend (Sin interfaz)

```bash
cd backend
python watcher.py
```

## 🔧 Configuración Avanzada

### Parámetros en `config.py`

| Parámetro | Descripción | Valor por Defecto |
|-----------|-------------|-------------------|
| `INTERVALO_VERIFICACION` | Segundos entre verificaciones locales | 5 |
| `INTERVALO_FORZADO` | Segundos entre verificaciones de OneDrive | 60 |
| `MAX_REINTENTOS` | Intentos máximos en caso de error | 3 |
| `TIEMPO_ESPERA_REINTENTO` | Segundos entre reintentos | 2 |
| `FLASK_PORT` | Puerto del servidor web | 5000 |

### Configuración desde la Interfaz Web

La interfaz permite modificar:
- Rutas de origen y destino
- Intervalos de verificación
- Ver estadísticas en tiempo real
- Monitorear logs del sistema

## 📊 Monitoreo y Logs

### Sistema de Logs

- **Ubicación**: `backend/log.txt`
- **Rotación automática**: Cuando supera 1MB
- **Niveles**: INFO, WARNING, ERROR
- **Formato**: `[YYYY-MM-DD HH:MM:SS] NIVEL: Mensaje`

### Métricas en Tiempo Real

- Estado del monitor (activo/inactivo)
- Estado de Watchdog (disponible/activo)
- Información de archivos (tamaño, última modificación)
- Conteo de reintentos fallidos
- Última verificación forzada

## 🔄 Funcionamiento Técnico

### Detección de Cambios (Híbrido)

1. **Watchdog Local**: Detecta cambios instantáneos en carpeta sincronizada
2. **Polling Continuo**: Verifica cada X segundos por si watchdog falla
3. **Verificación Forzada**: Cada Y segundos verifica directamente desde OneDrive

### Proceso de Sincronización

1. **Detección**: Cambio detectado por hash MD5 o fecha de modificación
2. **Validación**: Verificar que archivo no esté siendo modificado
3. **Copia**: Usar `shutil.copy2` para preservar metadatos
4. **Verificación**: Comparar tamaños y hashes
5. **Log**: Registrar resultado de la operación

### Manejo de Errores

- **PermissionError**: Reintento con delay
- **FileNotFoundError**: Log y notificación
- **Archivos en uso**: Esperar y reintentar
- **Errores de red**: Continuar con verificación local

## 🌐 API REST

### Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Interfaz principal |
| POST | `/api/iniciar` | Iniciar monitor |
| POST | `/api/detener` | Detener monitor |
| POST | `/api/sincronizar` | Forzar sincronización |
| GET | `/api/estado` | Estado del sistema |
| GET/POST | `/api/configuracion` | Obtener/actualizar config |
| GET | `/api/logs` | Obtener logs |
| POST | `/api/limpiar-logs` | Limpiar logs |

### Ejemplo de Uso de API

```python
import requests

# Iniciar monitor
response = requests.post('http://localhost:5000/api/iniciar')
print(response.json())

# Obtener estado
response = requests.get('http://localhost:5000/api/estado')
estado = response.json()
print(f"Monitor activo: {estado['monitor_activo']}")
```

## 🔒 Seguridad y Consideraciones

### Permisos de Archivos

- El sistema necesita permisos de lectura en OneDrive
- Requiere permisos de escritura en directorio destino
- No modifica el archivo original, solo lee

### Limitaciones de OneDrive

- Los cambios desde OneDrive web pueden tardar en sincronizar localmente
- La API de OneDrive requiere autenticación adicional (no implementada)
- El sistema depende de la sincronización local de OneDrive

### Recomendaciones de Seguridad

- Ejecutar con usuario con permisos mínimos necesarios
- Monitorear logs regularmente
- Hacer respaldos del archivo destino
- No compartir rutas sensibles en la configuración

## 🐛 Solución de Problemas

### Problemas Comunes

**1. "Archivo origen no encontrado"**
- Verificar que OneDrive esté sincronizado
- Comprobar la ruta en `config.py`
- Verificar permisos del usuario

**2. "Error de permisos"**
- Ejecutar como administrador (Windows) o sudo (Linux)
- Verificar permisos del directorio destino
- Comprobar que el archivo no esté abierto en Excel

**3. "Watchdog no disponible"**
- Instalar: `pip install watchdog`
- Sistema funcionará solo con polling

**4. "Cambios no detectados desde OneDrive web"**
- Normal, esperar `INTERVALO_FORZADO` segundos
- Verificar sincronización local de OneDrive
- Usar "Sincronizar Ahora" en la interfaz

### Logs de Depuración

Para debug avanzado, modificar en `config.py`:
```python
DEBUG_MODE = True
```

Esto habilitará logs más detallados en la consola.

## 📈 Rendimiento

### Optimizaciones Implementadas

- **Hash caching**: Evita recalcular hash si no cambió la fecha
- **Debouncing**: Evita múltiples eventos de un solo cambio
- **Verificación inteligente**: Solo calcula hash cuando es necesario
- **Threading**: Operaciones no bloquean la interfaz

### Uso de Recursos

- **CPU**: Mínimo en reposo, picos durante verificaciones
- **Memoria**: ~10-20MB dependiendo del tamaño de logs
- **Disco**: Lecturas periódicas del archivo origen
- **Red**: No usa red (depende de OneDrive local)

## 🔄 Actualizaciones y Mantenimiento

### Mantenimiento Rutinario

- Limpiar logs antiguos periódicamente
- Verificar espacio en disco del destino
- Actualizar dependencias de Python
- Monitorear errores en logs

### Respaldo de Configuración

La configuración se puede exportar desde la interfaz web o copiando `config.py`.

## 📋 Changelog

### v2.0 (Actual)
- ✅ Sistema híbrido de detección (watchdog + polling + forzado)
- ✅ Interfaz web completa con monitoreo en tiempo real
- ✅ API REST para integración
- ✅ Sistema de logs avanzado
- ✅ Validación de integridad con MD5
- ✅ Configuración dinámica
- ✅ Manejo robusto de errores

### v1.0 (Anterior)
- Detección básica por polling
- Configuración estática
- Sin interfaz web

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork del repositorio
2. Crear rama de feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📞 Soporte

Para reportar problemas o solicitar características:

1. Revisar logs en `backend/log.txt`
2. Verificar configuración en `backend/config.py`
3. Comprobar permisos de archivos
4. Documentar pasos para reproducir el problema

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE para más detalles.

---

**¡Sistema listo para usar!** 🎉

El sincronizador está diseñado para funcionar de manera autónoma y confiable, detectando cambios tanto locales como desde OneDrive web para mantener tus archivos siempre actualizados.