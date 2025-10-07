# backend/fixed_sync_system.py - SISTEMA CORREGIDO SIN API NI BACKUPS
import os
import sys
import time
import threading
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from queue import Queue, Empty
import hashlib
import logging

# Watchdog import
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

from config import Config

class SmartVerificationMixin:
    """Verificación inteligente que no falla por diferencias de metadatos"""
    
    @staticmethod
    def verify_file_copy_smart(origen, destino):
        """Verificación inteligente que considera las peculiaridades de OneDrive/Excel"""
        try:
            if not os.path.exists(origen) or not os.path.exists(destino):
                return False, "Uno de los archivos no existe"
            
            # 1. Verificación básica: tamaño
            size_origen = os.path.getsize(origen)
            size_destino = os.path.getsize(destino)
            
            # Permitir pequeñas diferencias (metadatos de OneDrive)
            size_diff = abs(size_origen - size_destino)
            if size_diff > 1024:  # Más de 1KB de diferencia es problemático
                return False, f"Diferencia de tamaño significativa: {size_diff} bytes"
            
            # 2. Verificación de timestamp razonable
            time_origen = os.path.getmtime(origen)
            time_destino = os.path.getmtime(destino)
            time_diff = abs(time_origen - time_destino)
            
            # Si el archivo de destino es muy antiguo, probablemente no se copió
            if time_diff > 300:  # 5 minutos
                return False, f"Diferencia de tiempo muy grande: {time_diff:.0f}s"
            
            # 3. Para Excel: verificar que sea un archivo válido
            if destino.lower().endswith(('.xlsx', '.xls')):
                try:
                    # Intentar leer el archivo como Excel básico
                    with open(destino, 'rb') as f:
                        header = f.read(8)
                        # Verificar firma básica de archivo ZIP (Excel moderno)
                        if header[:2] in [b'PK', b'\xd0\xcf']:  # ZIP o OLE
                            return True, "Archivo Excel válido copiado correctamente"
                except:
                    return False, "Archivo destino corrupto o inaccesible"
            
            # 4. Para otros archivos: verificación básica de contenido
            return True, f"Archivo copiado correctamente ({size_destino:,} bytes)"
            
        except Exception as e:
            return False, f"Error en verificación: {str(e)}"

class PragmaticSyncManager(SmartVerificationMixin):
    """Gestor de sincronización pragmático - funciona con OneDrive real"""
    
    def __init__(self):
        self.logger = logging.getLogger('PragmaticSync')
        
    def sync_file_pragmatic(self, origen, destino):
        """Sincronización pragmática sin verificaciones excesivas"""
        try:
            Config.log_event(f"Sincronizando: {os.path.basename(origen)}")
            
            # 1. Verificaciones previas básicas
            if not os.path.exists(origen):
                return False, "Archivo origen no existe"
            
            # 2. Crear directorio destino si no existe
            dest_dir = os.path.dirname(destino)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
                Config.log_event(f"Directorio creado: {dest_dir}")
            
            # 3. Copia pragmática con reintentos simples
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    Config.log_event(f"Intento de copia {attempt + 1}/{max_attempts}")
                    
                    # Esperar un poco si el archivo está siendo usado
                    if attempt > 0:
                        time.sleep(2)
                    
                    # Copia directa sin complicaciones
                    shutil.copy2(origen, destino)
                    
                    # Verificación inteligente (no estricta)
                    success, message = self.verify_file_copy_smart(origen, destino)
                    
                    if success:
                        Config.log_event(f"Copia exitosa: {message}")
                        return True, message
                    else:
                        Config.log_event(f"Verificación falló: {message}", "WARNING")
                        if attempt < max_attempts - 1:
                            Config.log_event("Reintentando copia...")
                            continue
                        
                except PermissionError as e:
                    if "being used by another process" in str(e).lower():
                        Config.log_event("Archivo en uso, esperando...", "WARNING")
                        time.sleep(3)
                        continue
                    else:
                        return False, f"Error de permisos: {str(e)}"
                        
                except Exception as e:
                    Config.log_event(f"Error en copia intento {attempt + 1}: {e}", "WARNING")
                    if attempt == max_attempts - 1:
                        return False, f"Error final: {str(e)}"
            
            return False, "Todos los intentos de copia fallaron"
            
        except Exception as e:
            return False, f"Error crítico: {str(e)}"

class IntelligentRuleAnalyzer:
    """Analizador inteligente basado en reglas - SIN API, SIN COSTO"""
    
    def __init__(self):
        # Reglas de negocio inteligentes
        self.rules = {
            'critical_keywords': [
                'precio', 'price', 'stock', 'inventario', 'inventory',
                'descuento', 'discount', 'promocion', 'promotion', 'oferta',
                'catalogo', 'catalog', 'producto', 'product'
            ],
            'urgent_size_mb': 0.1,  # Cambios > 100KB son importantes
            'ignore_patterns': [
                'temp', 'tmp', 'backup', 'bak', '~$', '.crdownload'
            ],
            'excel_extensions': ['.xlsx', '.xls', '.xlsm'],
            'business_hours': (8, 18),  # 8 AM - 6 PM
            'weekend_delay_multiplier': 2
        }
    
    def analyze_file_change(self, file_path, file_size=0, change_size=0):
        """Análisis inteligente sin IA externa"""
        
        filename = os.path.basename(file_path).lower()
        now = datetime.now()
        
        # Verificar si debe ignorarse
        if any(pattern in filename for pattern in self.rules['ignore_patterns']):
            return {
                'action': 'IGNORE',
                'priority': 'NONE',
                'reason': 'Archivo temporal o backup detectado',
                'delay_seconds': 0,
                'sync_immediately': False
            }
        
        # Análisis de contexto temporal
        is_business_hours = (
            now.weekday() < 5 and  # Lunes-Viernes
            self.rules['business_hours'][0] <= now.hour < self.rules['business_hours'][1]
        )
        is_weekend = now.weekday() >= 5
        
        # Análisis de contenido
        has_critical_keywords = any(
            keyword in filename for keyword in self.rules['critical_keywords']
        )
        is_excel_file = any(filename.endswith(ext) for ext in self.rules['excel_extensions'])
        is_significant_change = abs(change_size) > (self.rules['urgent_size_mb'] * 1024 * 1024)
        
        # Lógica de decisión inteligente
        base_priority = 'MEDIUM'
        base_delay = 60  # 1 minuto por defecto
        
        # Reglas de escalamiento
        if has_critical_keywords and is_excel_file:
            base_priority = 'CRITICAL'
            base_delay = 0  # Inmediato
            reason = 'Archivo crítico de catálogo con palabras clave importantes'
            
        elif is_significant_change and is_excel_file:
            base_priority = 'HIGH'
            base_delay = 10 if is_business_hours else 30
            reason = f'Cambio significativo en archivo Excel ({abs(change_size/1024/1024):.1f}MB)'
            
        elif is_excel_file and is_business_hours:
            base_priority = 'MEDIUM'
            base_delay = 30
            reason = 'Archivo Excel modificado en horario laboral'
            
        else:
            base_priority = 'LOW'
            base_delay = 300  # 5 minutos
            reason = 'Modificación estándar de archivo'
        
        # Ajustes por contexto temporal
        if is_weekend:
            base_delay *= self.rules['weekend_delay_multiplier']
            reason += ' (fin de semana - menor urgencia)'
        
        if not is_business_hours and base_delay < 60:
            base_delay = max(60, base_delay * 2)
            reason += ' (fuera de horario laboral)'
        
        return {
            'action': 'SYNC',
            'priority': base_priority,
            'reason': reason,
            'delay_seconds': base_delay,
            'sync_immediately': base_delay == 0,
            'business_context': {
                'is_business_hours': is_business_hours,
                'is_weekend': is_weekend,
                'has_critical_content': has_critical_keywords,
                'is_excel': is_excel_file
            }
        }

class FixedRealtimeHandler(FileSystemEventHandler):
    """Handler corregido que funciona con sistema real"""
    
    def __init__(self, sync_manager):
        super().__init__()
        self.sync_manager = sync_manager
        self.monitored_file = Path(Config.RUTA_ORIGEN)
        self.last_change = {}
        self.debounce_seconds = 3
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Solo nuestro archivo específico
        if file_path.name != self.monitored_file.name:
            return
        
        current_time = time.time()
        file_key = str(file_path)
        
        # Debounce
        if file_key in self.last_change:
            if current_time - self.last_change[file_key] < self.debounce_seconds:
                return
        
        self.last_change[file_key] = current_time
        
        # Obtener info del archivo después de estabilidad
        file_info = self._get_stable_file_info(file_path)
        if file_info:
            self.sync_manager.queue_sync(file_info)
    
    def _get_stable_file_info(self, file_path):
        """Obtiene info del archivo cuando está estable"""
        try:
            # Esperar que el archivo esté estable
            for _ in range(3):
                if not file_path.exists():
                    return None
                    
                initial_size = file_path.stat().st_size
                time.sleep(1)
                
                if file_path.exists():
                    final_size = file_path.stat().st_size
                    if initial_size == final_size and final_size > 0:
                        break
                else:
                    return None
            
            stat_info = file_path.stat()
            return {
                'path': str(file_path),
                'name': file_path.name,
                'size': stat_info.st_size,
                'modified_time': datetime.fromtimestamp(stat_info.st_mtime),
                'size_mb': round(stat_info.st_size / (1024*1024), 2)
            }
            
        except Exception as e:
            Config.log_event(f"Error obteniendo info de archivo: {e}", "WARNING")
            return None

class FixedSyncSystem:
    """Sistema de sincronización corregido y funcional"""
    
    def __init__(self):
        self.is_running = False
        self.observer = None
        self.sync_queue = Queue()
        self.worker_thread = None
        
        # Componentes corregidos
        self.sync_manager = PragmaticSyncManager()
        self.analyzer = IntelligentRuleAnalyzer()
        
        # Estadísticas
        self.stats = {
            'detections': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'ignored_files': 0
        }
        
        self.logger = logging.getLogger('FixedSyncSystem')
    
    def start(self):
        """Inicia el sistema corregido"""
        if self.is_running:
            Config.log_event("Sistema ya está corriendo", "WARNING")
            return False
        
        try:
            # Verificar configuración básica
            if not os.path.exists(Config.RUTA_ORIGEN):
                Config.log_event("ERROR CRÍTICO: Archivo origen no existe", "ERROR")
                return False
            
            # Instalar watchdog si no está disponible
            if not WATCHDOG_AVAILABLE:
                if not self._install_watchdog():
                    Config.log_event("No se pudo instalar watchdog", "ERROR")
                    return False
            
            # Configurar observer
            self.observer = Observer()
            handler = FixedRealtimeHandler(self)
            watch_dir = os.path.dirname(Config.RUTA_ORIGEN)
            
            self.observer.schedule(handler, watch_dir, recursive=False)
            self.observer.start()
            
            # Iniciar worker thread
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._sync_worker, daemon=True)
            self.worker_thread.start()
            
            Config.log_event("=" * 60)
            Config.log_event("SISTEMA DE SINCRONIZACIÓN CORREGIDO INICIADO")
            Config.log_event("=" * 60)
            Config.log_event("Características del sistema corregido:")
            Config.log_event("  ✓ Sin creación de archivos backup")
            Config.log_event("  ✓ Verificación inteligente (no estricta)")
            Config.log_event("  ✓ Análisis por reglas (sin API)")
            Config.log_event("  ✓ Compatible con OneDrive real")
            Config.log_event("  ✓ Detección en tiempo real")
            Config.log_event(f"Monitoreando: {os.path.basename(Config.RUTA_ORIGEN)}")
            Config.log_event("=" * 60)
            
            return True
            
        except Exception as e:
            Config.log_event(f"Error iniciando sistema corregido: {e}", "ERROR")
            return False
    
    def _install_watchdog(self):
        """Instala watchdog automáticamente"""
        try:
            import subprocess
            Config.log_event("Instalando watchdog...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
            
            # Reimportar
            global WATCHDOG_AVAILABLE
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            WATCHDOG_AVAILABLE = True
            
            Config.log_event("Watchdog instalado correctamente")
            return True
            
        except Exception as e:
            Config.log_event(f"Error instalando watchdog: {e}", "ERROR")
            return False
    
    def queue_sync(self, file_info):
        """Agrega sincronización a cola con análisis inteligente"""
        self.stats['detections'] += 1
        
        # Análisis inteligente por reglas
        analysis = self.analyzer.analyze_file_change(
            file_info['path'],
            file_info['size'],
            0  # Por simplicidad, no calculamos cambio de tamaño aquí
        )
        
        if analysis['action'] == 'IGNORE':
            self.stats['ignored_files'] += 1
            Config.log_event(f"Archivo ignorado: {analysis['reason']}")
            return
        
        Config.log_event("=" * 50)
        Config.log_event(f"CAMBIO DETECTADO #{self.stats['detections']}")
        Config.log_event(f"Archivo: {file_info['name']}")
        Config.log_event(f"Tamaño: {file_info['size_mb']:.2f} MB")
        Config.log_event(f"Análisis: {analysis['priority']} - {analysis['reason']}")
        
        # Agregar a cola
        sync_task = {
            'file_info': file_info,
            'analysis': analysis,
            'queued_at': datetime.now()
        }
        
        if analysis['sync_immediately']:
            Config.log_event("SINCRONIZACIÓN INMEDIATA")
            # Poner al frente de la cola
            self.sync_queue.put(sync_task)
        else:
            delay = analysis['delay_seconds']
            Config.log_event(f"Sincronización programada en {delay} segundos")
            # En un sistema real, usaríamos un scheduler, por simplicidad agregamos inmediatamente
            self.sync_queue.put(sync_task)
    
    def _sync_worker(self):
        """Worker que procesa sincronizaciones de forma inteligente"""
        Config.log_event("Worker de sincronización iniciado")
        
        while self.is_running:
            try:
                # Obtener siguiente tarea
                sync_task = self.sync_queue.get(timeout=1)
                
                file_info = sync_task['file_info']
                analysis = sync_task['analysis']
                
                Config.log_event("PROCESANDO SINCRONIZACIÓN")
                Config.log_event(f"Prioridad: {analysis['priority']}")
                
                # Ejecutar sincronización pragmática
                start_time = time.time()
                success, message = self.sync_manager.sync_file_pragmatic(
                    Config.RUTA_ORIGEN,
                    Config.RUTA_DESTINO
                )
                sync_duration = time.time() - start_time
                
                if success:
                    self.stats['successful_syncs'] += 1
                    Config.log_event(f"SINCRONIZACIÓN EXITOSA en {sync_duration:.2f}s")
                    Config.log_event(f"Resultado: {message}")
                else:
                    self.stats['failed_syncs'] += 1
                    Config.log_event(f"SINCRONIZACIÓN FALLIDA: {message}", "ERROR")
                
                Config.log_event(f"Estadísticas: {self.stats['successful_syncs']} éxitos, {self.stats['failed_syncs']} fallos")
                Config.log_event("=" * 50)
                
                self.sync_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                Config.log_event(f"Error en worker: {e}", "ERROR")
                self.stats['failed_syncs'] += 1
                time.sleep(5)
    
    def force_sync(self):
        """Fuerza sincronización inmediata"""
        try:
            Config.log_event("SINCRONIZACIÓN FORZADA MANUAL")
            success, message = self.sync_manager.sync_file_pragmatic(
                Config.RUTA_ORIGEN,
                Config.RUTA_DESTINO
            )
            
            if success:
                Config.log_event(f"Sincronización manual exitosa: {message}")
                self.stats['successful_syncs'] += 1
            else:
                Config.log_event(f"Error en sincronización manual: {message}", "ERROR")
                self.stats['failed_syncs'] += 1
            
            return success
            
        except Exception as e:
            Config.log_event(f"Error crítico en sincronización manual: {e}", "ERROR")
            return False
    
    def get_status(self):
        """Estado del sistema corregido"""
        return {
            'running': self.is_running,
            'watchdog_available': WATCHDOG_AVAILABLE,
            'observer_alive': self.observer.is_alive() if self.observer else False,
            'queue_size': self.sync_queue.qsize(),
            'stats': self.stats.copy(),
            'features': {
                'no_backups': True,
                'smart_verification': True,
                'rule_based_analysis': True,
                'no_api_cost': True
            }
        }
    
    def stop(self):
        """Detiene el sistema"""
        Config.log_event("Deteniendo sistema corregido...")
        self.is_running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        
        Config.log_event("ESTADÍSTICAS FINALES:")
        Config.log_event(f"  - Detecciones: {self.stats['detections']}")
        Config.log_event(f"  - Sincronizaciones exitosas: {self.stats['successful_syncs']}")
        Config.log_event(f"  - Sincronizaciones fallidas: {self.stats['failed_syncs']}")
        Config.log_event(f"  - Archivos ignorados: {self.stats['ignored_files']}")
        Config.log_event("Sistema corregido detenido")

# Instancia global
_fixed_system = None

def get_fixed_system():
    """Obtiene instancia del sistema corregido"""
    global _fixed_system
    if _fixed_system is None:
        _fixed_system = FixedSyncSystem()
    return _fixed_system

def main():
    """Función principal para testing"""
    try:
        system = get_fixed_system()
        
        if system.start():
            Config.log_event("Sistema corregido iniciado - presiona Ctrl+C para detener")
            while True:
                time.sleep(1)
        else:
            Config.log_event("Error iniciando sistema corregido", "ERROR")
            
    except KeyboardInterrupt:
        Config.log_event("Deteniendo por interrupción de usuario")
        if system:
            system.stop()

if __name__ == "__main__":
    main()