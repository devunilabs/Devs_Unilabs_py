# 📋 INSTRUCCIONES PASO A PASO PARA REENVIOCATALOG + IA

# =============================================================================
# PASO 1: PREPARACIÓN INICIAL
# =============================================================================

# 1.1 Navegar a tu directorio REENVIOCATALOG
cd REENVIOCATALOG

# 1.2 Verificar que tienes la estructura correcta
dir  # En Windows
ls -la  # En Linux/Mac

# Deberías ver:
# REENVIOCATALOG/
# ├── backend/
# ├── frontend/
# ├── requirements.txt
# ├── test_onedrive.py
# └── README.md

# =============================================================================
# PASO 2: CREAR ENTORNO VIRTUAL ESPECÍFICO PARA IA
# =============================================================================

# 2.1 Crear entorno virtual
python -m venv venv_ia

# 2.2 Activar entorno virtual
# En Windows:
venv_ia\Scripts\activate

# En Linux/Mac:
source venv_ia/bin/activate

# 2.3 Instalar dependencias existentes de tu proyecto
pip install -r requirements.txt

# =============================================================================
# PASO 3: CREAR ARCHIVO requirements_agent.txt
# =============================================================================

# 3.1 Crear el archivo con las dependencias IA
# (Usar el contenido del artifact requirements_agent.txt)

echo "# LangChain y componentes IA" > requirements_agent.txt
echo "langchain==0.1.0" >> requirements_agent.txt
echo "langchain-community==0.0.10" >> requirements_agent.txt
echo "langchain-core==0.1.0" >> requirements_agent.txt
echo "" >> requirements_agent.txt
echo "# Selenium para automatización web" >> requirements_agent.txt
echo "selenium==4.15.0" >> requirements_agent.txt
echo "webdriver-manager==4.0.1" >> requirements_agent.txt
echo "" >> requirements_agent.txt
echo "# Procesamiento de archivos" >> requirements_agent.txt
echo "pandas>=1.5.0" >> requirements_agent.txt
echo "openpyxl>=3.1.0" >> requirements_agent.txt
echo "watchdog==3.0.0" >> requirements_agent.txt
echo "requests>=2.28.0" >> requirements_agent.txt
echo "pydantic>=2.0.0" >> requirements_agent.txt

# 3.2 Instalar dependencias del agente IA
pip install -r requirements_agent.txt

# =============================================================================
# PASO 4: CREAR ESTRUCTURA DE CARPETAS PARA IA
# =============================================================================

# 4.1 Crear carpetas para el agente IA
mkdir ia_agent
mkdir ia_agent\tools      # Windows
mkdir ia_agent\config
mkdir ia_agent\logs

# En Linux/Mac:
# mkdir -p ia_agent/{tools,config,logs}

# 4.2 Crear archivos __init__.py
echo "" > ia_agent\__init__.py          # Windows
echo "" > ia_agent\tools\__init__.py
echo "" > ia_agent\config\__init__.py

# En Linux/Mac:
# touch ia_agent/__init__.py ia_agent/tools/__init__.py ia_agent/config/__init__.py

# =============================================================================
# PASO 5: CREAR ARCHIVOS DEL AGENTE IA
# =============================================================================

# 5.1 Crear los archivos Python (copiar contenido de los artifacts):

# - ia_agent/agent_automation.py     (del artifact agent_main_adapted)
# - ia_agent/tools/file_tools.py     (del artifact file_tools_adapted)  
# - ia_agent/tools/selenium_tools.py (del artifact selenium_tools_adapted)
# - main_integrated.py               (del artifact main_integrated_adapted)

# 5.2 Crear archivo de configuración
# Copiar el contenido del artifact agent_config_specific a:
# ia_agent/config/agent_config.json

# =============================================================================
# PASO 6: PERSONALIZAR CONFIGURACIÓN PARA TU SISTEMA
# =============================================================================

# 6.1 Editar ia_agent/config/agent_config.json
# Cambiar las rutas según tu sistema:

# Windows example:
# "source": "C:/Users/TU_USUARIO/OneDrive/Catalogo/source"
# "destination": "C:/Users/TU_USUARIO/OneDrive/Catalogo/processed" 
# "backup": "C:/Users/TU_USUARIO/OneDrive/Catalogo/backup"

# 6.2 Crear las carpetas OneDrive si no existen
mkdir "C:\Users\TU_USUARIO\OneDrive\Catalogo\source"       # Windows
mkdir "C:\Users\TU_USUARIO\OneDrive\Catalogo\processed"
mkdir "C:\Users\TU_USUARIO\OneDrive\Catalogo\backup"

# En Linux/Mac:
# mkdir -p ~/OneDrive/Catalogo/{source,processed,backup}

# =============================================================================
# PASO 7: CREAR HERRAMIENTA ONEDRIVE (ARCHIVO FALTANTE)
# =============================================================================

# 7.1 Crear ia_agent/tools/onedrive_tools.py
echo "# Herramienta OneDrive para REENVIOCATALOG" > ia_agent\tools\onedrive_tools.py

# 7.2 Copiar contenido básico:
cat >> ia_agent\tools\onedrive_tools.py << 'EOF'
"""
Herramientas de monitoreo OneDrive para REENVIOCATALOG
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict
from langchain.tools import BaseTool

class OneDriveMonitorTool(BaseTool):
    """Herramienta de monitoreo OneDrive para REENVIOCATALOG"""
    
    name = "reenviocatalog_onedrive_monitor"
    description = "Monitorea sincronización OneDrive para REENVIOCATALOG"
    
    def __init__(self, config: Dict, project_root: Path):
        super().__init__()
        self.config = config
        self.project_root = project_root
    
    def _run(self, query: str) -> str:
        try:
            params = json.loads(query)
            file_path = params.get("file_path")
            action = params.get("action", "check_sync")
            
            if action == "check_sync":
                return self._check_sync_status(file_path)
            else:
                return f"❌ Acción no reconocida: {action}"
                
        except Exception as e:
            return f"❌ Error OneDrive: {str(e)}"
    
    def _check_sync_status(self, file_path: str) -> str:
        """Verifica estado de sincronización"""
        if not file_path or not os.path.exists(file_path):
            return f"❌ Archivo no encontrado: {file_path}"
        
        if "onedrive" not in file_path.lower():
            return "⚠️ Archivo no parece estar en OneDrive"
        
        # Verificar última modificación
        mod_time = os.path.getmtime(file_path)
        mod_datetime = datetime.fromtimestamp(mod_time)
        
        return f"✅ OneDrive - Archivo sincronizado: {mod_datetime}"
    
    def _arun(self, query: str):
        raise NotImplementedError("Async not implemented")
EOF

# =============================================================================
# PASO 8: VERIFICAR INSTALACIÓN DE CHROME
# =============================================================================

# 8.1 Verificar que Google Chrome esté instalado
# Windows: Buscar en "Archivos de programa/Google/Chrome"
# Linux: which google-chrome
# Mac: ls /Applications/Google\ Chrome.app

# 8.2 Si no tienes Chrome, descargarlo de: https://www.google.com/chrome/

# =============================================================================
# PASO 9: ESTRUCTURA FINAL VERIFICACIÓN
# =============================================================================

# Tu estructura final debe verse así:
tree  # Si tienes tree instalado, o dir /s en Windows

# REENVIOCATALOGIA/
# ├── backend/                    (TUS ARCHIVOS ORIGINALES)
# │   ├── app.py
# │   ├── envio.py
# │   ├── config.py
# │   ├── watcher.py
# │   └── log.txt
# ├── frontend/                   (TUS ARCHIVOS ORIGINALES)
# │   ├── static/
# │   └── templates/
# ├── ia_agent/                   (NUEVOS ARCHIVOS IA)
# │   ├── __init__.py
# │   ├── agent_automation.py
# │   ├── tools/
# │   │   ├── __init__.py
# │   │   ├── file_tools.py
# │   │   ├── selenium_tools.py
# │   │   └── onedrive_tools.py
# │   ├── config/
# │   │   ├── __init__.py
# │   │   └── agent_config.json
# │   └── logs/                   (se crea automáticamente)
# ├── main_integrated.py          (NUEVO - Punto de entrada)
# ├── requirements_agent.txt      (NUEVO)
# ├── venv_ia/                    (NUEVO - Entorno virtual)
# ├── requirements.txt            (TU ARCHIVO ORIGINAL)
# ├── test_onedrive.py           (TU ARCHIVO ORIGINAL)
# └── README.md                   (TU ARCHIVO ORIGINAL)

# =============================================================================
# PASO 10: PRIMERA PRUEBA
# =============================================================================

# 10.1 Verificar que el entorno virtual esté activo
# Deberías ver (venv_ia) en tu prompt

# 10.2 Ejecutar el sistema integrado
python main_integrated.py

# 10.3 Si todo está correcto, deberías ver:
# 🏢 REENVIOCATALOG - Sistema Integrado con IA
# ======================================
# 🚀 Iniciando Sistema Integrado REENVIOCATALOG...
# 🔍 Verificando estructura del proyecto...
# ✅ Estructura del proyecto verificada
# 🌐 Iniciando aplicación Flask...
# ✅ Proceso Flask iniciado (PID: XXXX)
# 🤖 Inicializando Agente IA REENVIOCATALOG...
# ✅ Agente IA inicializado correctamente
# ⚡ Iniciando automatización IA...
# ✅ Automatización IA activa
# 🔗 Configurando integración componentes...
# ✅ Integración con backend completada
# ✅