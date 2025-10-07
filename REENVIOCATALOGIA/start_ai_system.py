# ==============================================================================
# 4. start_ai_system.py - NUEVO PUNTO DE ENTRADA AUTOMÁTICO
# ==============================================================================

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
start_ai_system.py - SISTEMA CORREGIDO SIN API Y SIN BACKUPS
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime
from pathlib import Path

# Configurar paths
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

def setup_logging():
    """Configura logging del sistema corregido"""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "system.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

class CorrectedSystemManager:
    """Gestor del sistema corregido"""
    
    def __init__(self):
        self.fixed_sync_system = None
        self.running = False
        self.logger = logging.getLogger(__name__)
        
    def start_system(self):
        """Inicia el sistema corregido"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("INICIANDO SISTEMA CORREGIDO - SIN API, SIN BACKUPS")
            self.logger.info("=" * 60)
            
            # Validar configuración básica
            if not self._validate_basic_config():
                return False
            
            # Iniciar sistema de sincronización corregido
            if not self._start_fixed_sync():
                return False
            
            # Configurar manejo de señales
            self._setup_signal_handlers()
            
            self.running = True
            self.logger.info("SISTEMA CORREGIDO COMPLETAMENTE OPERATIVO")
            self.logger.info("Características:")
            self.logger.info("  - Verificación inteligente (no estricta)")
            self.logger.info("  - Sin archivos backup")
            self.logger.info("  - Análisis por reglas (sin costo API)")
            self.logger.info("  - Compatible con OneDrive real")
            self.logger.info("Presiona Ctrl+C para detener")
            self.logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error crítico iniciando sistema: {e}")
            return False
    
    def _validate_basic_config(self):
        """Valida configuración básica"""
        try:
            from backend.config import Config
            
            if not os.path.exists(Config.RUTA_ORIGEN):
                self.logger.error(f"Archivo origen no existe: {Config.RUTA_ORIGEN}")
                return False
            
            # Verificar/crear directorio destino
            dest_dir = os.path.dirname(Config.RUTA_DESTINO)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
                self.logger.info(f"Directorio destino creado: {dest_dir}")
            
            self.logger.info("Configuración básica validada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando configuración: {e}")
            return False
    
    def _start_fixed_sync(self):
        """Inicia el sistema de sincronización corregido"""
        try:
            from backend.fixed_sync_system import get_fixed_system
            
            self.fixed_sync_system = get_fixed_system()
            
            if self.fixed_sync_system.start():
                self.logger.info("Sistema de sincronización corregido iniciado")
                return True
            else:
                self.logger.error("Error iniciando sistema corregido")
                return False
                
        except ImportError as e:
            self.logger.error(f"Error importando sistema corregido: {e}")
            self.logger.error("Asegúrate de que backend/fixed_sync_system.py existe")
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado: {e}")
            return False
    
    def _setup_signal_handlers(self):
        """Configura manejo de señales"""
        def signal_handler(signum, frame):
            self.logger.info("Señal de interrupción recibida")
            self.stop_system()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run_main_loop(self):
        """Loop principal simplificado"""
        if not self.running:
            return False
        
        try:
            last_status = 0
            
            while self.running:
                current_time = time.time()
                
                # Log status cada 5 minutos
                if current_time - last_status > 300:
                    if self.fixed_sync_system:
                        status = self.fixed_sync_system.get_status()
                        stats = status['stats']
                        self.logger.info(
                            f"STATUS - Detecciones: {stats['detections']}, "
                            f"Éxitos: {stats['successful_syncs']}, "
                            f"Fallos: {stats['failed_syncs']}"
                        )
                    last_status = current_time
                
                time.sleep(10)
                
        except KeyboardInterrupt:
            self.logger.info("Interrupción por teclado")
        except Exception as e:
            self.logger.error(f"Error en loop principal: {e}")
        
        return True
    
    def force_sync(self):
        """Fuerza sincronización"""
        if self.fixed_sync_system:
            return self.fixed_sync_system.force_sync()
        return False
    
    def get_status(self):
        """Estado del sistema"""
        status = {
            'running': self.running,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.fixed_sync_system:
            status['sync_system'] = self.fixed_sync_system.get_status()
        
        return status
    
    def stop_system(self):
        """Detiene el sistema"""
        self.logger.info("Deteniendo sistema corregido...")
        self.running = False
        
        if self.fixed_sync_system:
            self.fixed_sync_system.stop()
        
        self.logger.info("Sistema detenido correctamente")

def main():
    """Función principal"""
    print("SISTEMA CORREGIDO - Sin API, Sin Backups, Verificación Inteligente")
    print("=" * 70)
    
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Verificar directorio
    if not (project_root / "backend").exists():
        logger.error("Error: directorio backend no encontrado")
        return 1
    
    # Crear y ejecutar sistema
    system = CorrectedSystemManager()
    
    try:
        if system.start_system():
            system.run_main_loop()
        else:
            logger.error("Error iniciando sistema")
            return 1
            
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        return 1
    finally:
        system.stop_system()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())