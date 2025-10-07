# REENVIOCATALOG con IA - CORREGIDO

Sistema automatizado de procesamiento y reenvío de catálogos con Agente IA.

## INICIO RÁPIDO

### Windows:
```bash
# Ejecutar sistema completo
start_reenviocatalog.bat

# O manualmente:
venv_ia\Scripts\python.exe main_integrated.py
```

### Linux/Mac:
```bash
# Ejecutar sistema completo  
./start_reenviocatalog.sh

# O manualmente:
venv_ia/bin/python main_integrated.py
```

## CARACTERÍSTICAS CORREGIDAS

- ✓ LangChain moderno (v0.1+) compatible
- ✓ Herramientas con esquemas Pydantic correctos  
- ✓ Flask mejorado con múltiples métodos de inicio
- ✓ Procesamiento automático de archivos Excel/CSV
- ✓ Monitoreo inteligente OneDrive
- ✓ Automatización web con Selenium
- ✓ Logs detallados y manejo de errores

## COMANDOS PRINCIPALES

Una vez iniciado el sistema:

- `status` - Ver estado completo
- `process archivo.xlsx` - Procesar archivo específico
- `flask` - Estado de aplicación web
- `restart_flask` - Reiniciar Flask si no responde
- `agent` - Interactuar con IA directamente
- `logs` - Ver registros recientes
- `test` - Ejecutar pruebas del sistema
- `help` - Ayuda completa

## CONFIGURACIÓN

La configuración se encuentra en:
`ia_agent/config/agent_config.json`

Rutas principales configurables:
- `source`: Carpeta origen OneDrive
- `destination`: Carpeta destino OneDrive  
- `backup`: Carpeta backup automático

## SOLUCIÓN DE PROBLEMAS

**Flask no inicia:**
- El sistema funciona solo con IA
- Usar comando `restart_flask` dentro del sistema

**Errores de dependencias:**
- Ejecutar: `venv_ia/Scripts/pip install -r requirements_agent.txt`

**Chrome/Selenium no funciona:**
- Instalar Google Chrome
- El sistema funciona parcialmente sin Selenium

**Rutas OneDrive no accesibles:**  
- Verificar permisos en las carpetas configuradas
- Comprobar sincronización OneDrive activa

## LOGS Y MONITOREO

Logs ubicados en:
- `ia_agent/logs/agent_activity.log` - Actividad general
- `ia_agent/logs/file_events.log` - Eventos de archivos
- `ia_agent/logs/auto_processing.log` - Procesamiento automático
- `backend/log.txt` - Log del backend original

## SOPORTE

El sistema está diseñado para funcionar 24/7 con mínima intervención.
Procesamiento completamente automático de archivos nuevos/modificados.
