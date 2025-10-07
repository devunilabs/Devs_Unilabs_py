# REENVIOCATALOG - Sistema Inteligente de Sincronización con IA

Sistema automatizado de sincronización de archivos Excel entre OneDrive con supervisión de Inteligencia Artificial usando LangChain.

## Arquitectura del Sistema

### Visión General
```
┌─────────────────────────────────────────────────────────────────┐
│                    REENVIOCATALOG SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   IA AGENT      │───▶│  BACKEND CORE   │───▶│   FRONTEND   │ │
│  │  (LangChain)    │    │   (Probado)     │    │   (Flask)    │ │
│  │  - Orquestador  │    │   - Watcher     │    │   - Web UI   │ │
│  │  - Analizador   │    │   - Envío       │    │   - APIs     │ │
│  │  - Notificador  │    │   - Config      │    │   - Logs     │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                     │       │
│           ▼                       ▼                     ▼       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │     EMAILS      │    │   ONEDRIVE      │    │    USERS     │ │
│  │ - Outlook/SMTP  │    │ - Origen/Destino│    │ - Monitoreo  │ │
│  │ - Análisis IA   │    │ - Sync Robusto  │    │ - Control    │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes Principales

#### 1. IA Agent (Nuevo - LangChain)
- **Orquestador**: Inicia y supervisa el sistema automáticamente
- **Analizador**: Analiza cambios con IA y genera insights
- **Notificador**: Envía emails inteligentes con análisis contextual
- **Monitor**: Supervisa logs en tiempo real y toma decisiones

#### 2. Backend Core (Existente - Mejorado)
- **Watcher**: Sincronización cada 2 minutos
- **Envío**: Copia robusta con manejo de archivos abiertos
- **Config**: Configuración optimizada para OneDrive
- **Logs**: Sistema de logging detallado

#### 3. Frontend (Existente)
- **Flask Web UI**: Interfaz web para monitoreo manual
- **APIs REST**: Endpoints para control del sistema
- **Dashboard**: Visualización de métricas y estado

## Estructura de Archivos

```
REENVIOCATALOGIA/
├── backend/                    # Sistema Backend (Core)
│   ├── app.py                 # Servidor Flask
│   ├── envio.py               # Gestor de copia con reintentos
│   ├── config.py              # Configuración OneDrive optimizada
│   ├── watcher.py
|   ├── aggressive_onedrive_sync.py
|   ├── enhanced_sync_with_alerts.py
|   ├── fixed_sync_system.py         
│   └── log.txt                     # Logs del sistema backend
├── frontend/                       # Interfaz Web
│   ├── static/                     # CSS, JS, imágenes
│   └── templates/                  # Templates HTML
├── ia_agent/                       # Sistema IA (Nuevo)
│   ├── orchestrator.py             # Orquestador IA principal       
│   ├── email_notifier.py           # Sistema de notificaciones
│   ├── change_analyzer.py          # Analizador IA con LangChain
│   ├── config/                     # Configuración IA
│   │   ├── agent_config.json               # Config del agente
│   │   └── orchestrator_config.json        # Config del orquestador
│   ├── logs/
|   |   ├── ai_system.log               
│   │   └── orchestrator.log   
|   ├── change_analyzer.py   
│   ├── email_notifier.py  
|   └── orchestrator.py
|                  
├── start_ai_system.py          # Punto de entrada IA (Nuevo)
├── business_dashboard.py       # Dashboard empresarial
├── requirements.txt            # Dependencias backend
├── requirements_agent.txt      # Dependencias IA
├── venv_ia/                   # Entorno virtual
└── start_ai_system_definitivo.py
```

## Flujo de Trabajo del Sistema

### 1. Inicio Automático
```
python start_ai_system.py
    ↓
IA Agent inicia automáticamente backend/watcher.py
    ↓
Sistema funciona 24/7 sin intervención manual
```

### 2. Proceso de Sincronización Inteligente
```
Usuario edita Excel Online
    ↓
OneDrive sincroniza cambios (forzado por IA)
    ↓
Backend detecta cambios cada 2 minutos
    ↓
IA Agent analiza el tipo de cambio
    ↓
Sistema copia archivo con reintentos
    ↓
IA envía email con análisis detallado
    ↓
Todo se registra en logs con contexto IA
```

### 3. Manejo Inteligente de Errores
```
Error detectado en logs
    ↓
IA Agent analiza causa del error
    ↓
Envía email de alerta con análisis
    ↓
Intenta reinicio automático si es necesario
    ↓
Continúa monitoreando hasta resolución
```

## Instalación y Configuración

### Paso 1: Preparar el Entorno

```bash
# Clonar/descargar el proyecto
cd REENVIOCATALOGIA

# Crear entorno virtual
python -m venv venv_ia

# Activar entorno virtual
# Windows:
venv_ia\Scripts\activate
# Linux/Mac:
source venv_ia/bin/activate
```

### Paso 2: Instalar Dependencias

```bash
# Instalar dependencias backend
pip install -r requirements.txt

# Instalar dependencias IA
pip install -r requirements_agent.txt

# Verificar instalación
pip list | grep -i langchain
pip list | grep -i flask
```

### Paso 3: Configurar Rutas de Archivos

Editar `backend/config.py`:

```python
# Cambiar estas rutas por las tuyas:
RUTA_ORIGEN = r"C:\Users\tuusuario\Unilabs Group Services\Moisés Rojas - Catalogos\Catalogo_2025_IVD.xlsx"
RUTA_DESTINO = r"C:\Users\tuusuario\OneDrive - Unilabs Group Services\Archivos de Abigail Caceres\Catalogo_2025_IVD.xlsx"
```

### Paso 4: Configurar Notificaciones por Email

Al ejecutar por primera vez, se creará automáticamente:
`ia_agent/config/orchestrator_config.json`

Editar este archivo:

```json
{
    "email": {
        "provider": "outlook",
        "smtp_server": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "username": "tu_email@empresa.com",
        "password": "tu_password_o_app_password",
        "from_email": "tu_email@empresa.com",
        "to_email": "destinatario@empresa.com",
        "use_corporate_smtp": false,
        "corporate_smtp": {
            "server": "mail.empresa.com",
            "port": 587,
            "auth_required": true
        }
    }
}
```

#### Configuración SMTP Corporativo

Si usas SMTP corporativo, cambiar:

```json
{
    "email": {
        "provider": "corporate",
        "use_corporate_smtp": true,
        "corporate_smtp": {
            "server": "mail.tuempresa.com",
            "port": 587,
            "auth_required": true
        },
        "username": "tu_usuario_corporativo",
        "password": "tu_password_corporativo"
    }
}
```

### Paso 5: Configurar LangChain (Opcional)

Para análisis IA avanzado, agregar API key de OpenAI:

```json
{
    "langchain": {
        "provider": "openai",
        "openai_api_key": "sk-tu-api-key-aqui",
        "model": "gpt-3.5-turbo",
        "temperature": 0.1,
        "fallback_enabled": true
    }
}
```

**Nota**: Si no configuras OpenAI, el sistema usa análisis básico automáticamente.

## Ejecución del Sistema

### Opción 1: Sistema IA Completo (Recomendado)

```bash
# Activar entorno virtual
venv_ia\Scripts\activate

# Ejecutar sistema IA automático
python start_ai_system.py
```

**Resultado esperado:**
- Sistema completamente automático
- Backend inicia automáticamente
- Notificaciones por email configuradas
- Análisis IA de cambios activo
- Funciona 24/7 sin intervención

### Opción 2: Solo Backend Tradicional

```bash
# Solo para pruebas o debugging
cd backend
python watcher.py
```

### Opción 3: Sistema Integrado Complejo

```bash
# Para desarrollo o debugging avanzado
python main_integrated.py
```

### Opción 4: Dashboard de Demostración

```bash
# Para presentación empresarial
python business_dashboard.py
```

## Monitoreo y Logs

### Logs del Sistema

1. **Backend Logs**: `backend/log.txt`
   - Sincronizaciones cada 2 minutos
   - Detalles de OneDrive sync
   - Errores de copia

2. **IA Logs**: `ia_agent/logs/orchestrator.log`
   - Decisiones del IA Agent
   - Análisis de cambios
   - Estado del orquestador

3. **Flask Logs**: Consola web
   - Requests HTTP
   - Estado de APIs
   - Errores de interfaz

### Interfaz Web

Acceder a: http://localhost:5000

- **Estado del Sistema**: Métricas en tiempo real
- **Logs Recientes**: Últimas 50 líneas de log
- **Control Manual**: Forzar sincronización
- **Configuración**: Cambiar intervalos

## Funcionamiento y Características

### Sincronización Automática

- **Intervalo**: Cada 2 minutos
- **Detección**: Cambios en Excel Online
- **Copia**: Robusta con reintentos para archivos abiertos
- **Verificación**: Integridad de datos por hash MD5
- **OneDrive**: Sincronización forzada antes y después

### Inteligencia Artificial

- **Orquestación**: Inicia y supervisa automáticamente
- **Análisis**: Detecta tipo de cambios (nuevos datos, modificaciones)
- **Decisiones**: Determina importancia y acciones necesarias
- **Notificaciones**: Emails contextuales con análisis IA
- **Recuperación**: Reinicio automático en caso de errores

### Notificaciones Inteligentes

#### Email de Inicio del Sistema
- Confirmación de inicio automático
- Estado de todos los componentes
- Configuración activa

#### Email de Sincronización Exitosa
- Número de sincronización
- Análisis IA del cambio detectado
- Tiempo de procesamiento
- Próxima verificación

#### Email de Error
- Tipo de error con análisis IA
- Severidad y recomendaciones
- Acciones automáticas tomadas
- Estado de recuperación

## Resolución de Problemas

### Problema: Sistema no inicia

**Verificar:**
```bash
# Entorno virtual activo
venv_ia\Scripts\activate

# Dependencias instaladas
pip list | grep langchain

# Configuración de rutas
python -c "from backend.config import Config; print(Config.RUTA_ORIGEN)"
```

### Problema: Emails no se envían

**Verificar:**
1. Credenciales en `orchestrator_config.json`
2. Configuración SMTP correcta
3. Password de aplicación (no password normal)
4. Firewall/antivirus bloqueando SMTP

### Problema: OneDrive no sincroniza

**Verificar:**
1. OneDrive ejecutándose en Windows
2. Archivos no bloqueados por permisos
3. Espacio suficiente en OneDrive
4. Internet estable

### Problema: IA no analiza cambios

**Verificar:**
1. API key de OpenAI válida (opcional)
2. `fallback_enabled: true` en config
3. Logs de IA en `ia_agent/logs/orchestrator.log`

## Dependencias del Proyecto

### Backend (requirements.txt)
```
Flask==2.3.3
requests==2.31.0
Werkzeug==2.3.7
```

### IA Agent (requirements_agent.txt)
```
langchain==0.1.0
langchain-openai==0.0.5
langchain-community==0.0.13
openai==1.12.0
pydantic==2.5.3
```

### Sistema
- Python 3.8+
- Windows 10+ (para OneDrive)
- OneDrive sincronizado
- Conexión a internet

## Configuración Avanzada

### Personalizar Intervalos

En `backend/config.py`:
```python
INTERVALO_FORZADO = 120  # 2 minutos (por defecto)
INTERVALO_VERIFICACION = 30  # Verificación interna
MAX_REINTENTOS = 5  # Reintentos para archivos abiertos
```

### Personalizar Análisis IA

En `orchestrator_config.json`:
```json
{
    "notifications": {
        "sync_success": true,    # Email por cada sync exitosa
        "sync_failure": true,    # Email por cada error
        "system_start": true,    # Email al iniciar sistema
        "error_threshold": 3,    # Reiniciar después de N errores
        "detailed_analysis": true # Análisis IA detallado
    }
}
```

### Configuración de Reinicio Automático

```json
{
    "backend_integration": {
        "restart_on_failure": true,      # Reiniciar automáticamente
        "max_restart_attempts": 3        # Máximo 3 reintentos
    }
}
```

## Seguridad y Consideraciones

### Credenciales
- Usar passwords de aplicación, no passwords normales
- No compartir archivos de configuración con credenciales
- Considerar variables de entorno para producción

### Permisos
- Verificar permisos de lectura/escritura en OneDrive
- Ejecutar como administrador si es necesario
- Configurar excepciones en antivirus

### Monitoreo
- Revisar logs regularmente
- Configurar alertas para errores críticos
- Mantener backups de configuraciones

## Soporte y Mantenimiento

### Logs para Soporte
Incluir estos archivos al reportar problemas:
- `backend/log.txt`
- `ia_agent/logs/orchestrator.log`
- `ia_agent/config/orchestrator_config.json` (sin credenciales)

### Actualizaciones
1. Hacer backup de configuraciones
2. Actualizar dependencias: `pip install -r requirements_agent.txt --upgrade`
3. Revisar cambios en configuración
4. Probar en entorno de desarrollo primero

### Mantenimiento Regular
- Limpiar logs antiguos mensualmente
- Verificar espacio en disco
- Actualizar API keys si vencen
- Revisar configuración de email

---

## Licencia y Créditos

Sistema desarrollado para automatización empresarial de sincronización de archivos con supervisión de Inteligencia Artificial.

**Componentes principales:**
- Backend: Sistema de sincronización robusto
- IA Agent: LangChain + OpenAI para análisis inteligente
- Frontend: Flask para interfaz web
- Notificaciones: SMTP/Outlook para alertas automáticas

---

**Versión**: 2.0  
**Última actualización**: 2025-08-28  
**Compatibilidad**: Windows 10+, Python 3.8+