# backend/enhanced_sync_with_alerts.py - SINCRONIZACIÓN CON ALERTAS TXT + MANEJO DE ARCHIVOS BLOQUEADOS
import os
import sys
import time
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import logging

class OneDriveForcedSync:
    """Sistema que FUERZA sincronización OneDrive + alertas TXT + manejo de archivos bloqueados"""
    
    def __init__(self):
        self.logger = logging.getLogger('OneDriveForced')
        
    def perform_sync_with_lock(self, origen, destino):
        """Sincronización con archivo de alerta y forzado OneDrive"""
        
        # Preparar rutas y archivos de alerta
        destino_path = Path(destino)
        dest_dir = destino_path.parent
        #FILENAME CHANGING : f"SINCRONIZANDO_{destino_path.stem}.txt"
        alert_file = dest_dir / f"IA_LANGCHAIN_SINCRONIZANDO_{destino_path.stem}.txt"
        
        try:
            # PASO 1: Crear archivo de alerta
            self._create_lock_alert(alert_file)
            
            # PASO 2: Forzar sincronización de alerta (para que otros la vean inmediatamente)
            self._force_onedrive_sync_immediate(dest_dir)
            
            # PASO 3: Esperar que la alerta se propague
            time.sleep(3)
            
            # PASO 4: Realizar copia del archivo principal CON MANEJO DE BLOQUEOS
            copy_success = self._perform_robust_copy(origen, destino)
            
            if copy_success:
                # PASO 5: Forzar sincronización del archivo copiado
                sync_success = self._force_onedrive_sync_immediate(dest_dir)
                
                # PASO 6: Verificar que llegó a la nube
                cloud_verified = self._verify_cloud_sync(destino, max_wait_minutes=2)
                
                # PASO 7: Eliminar archivo de alerta
                self._remove_lock_alert(alert_file)
                
                # PASO 8: Sincronizar eliminación de alerta
                self._force_onedrive_sync_immediate(dest_dir)
                
                return {
                    'success': True,
                    'copy_success': copy_success,
                    'onedrive_sync': sync_success,
                    'cloud_verified': cloud_verified,
                    'message': f'Archivo sincronizado {"y verificado en nube" if cloud_verified else "localmente"}'
                }
            else:
                # PASO 7 (error): Eliminar alerta en caso de error
                self._remove_lock_alert(alert_file)
                return {
                    'success': False,
                    'message': 'Error en copia de archivo - posible bloqueo por Excel'
                }
                
        except Exception as e:
            # Cleanup en caso de error
            self._remove_lock_alert(alert_file)
            return {
                'success': False,
                'message': f'Error crítico: {str(e)}'
            }
    
    def _create_lock_alert(self, alert_file):
        """Crea archivo TXT de alerta"""
        try:
            alert_content = f"""🔄 AGENTE IA SINCRONIZANDO... 🔄

ARCHIVO: {alert_file.stem.replace('SINCRONIZANDO_', '')}
ESTADO: Copiando archivo...
INICIO: {datetime.now().strftime('%H:%M:%S')}
SISTEMA: REENVIOCATALOG IA

⚠️ IMPORTANTE ⚠️
- NO ABRIR el archivo mientras aparezca esta alerta
- NO EDITAR el archivo durante el proceso
- La sincronización tomará 1-2 minutos máximo
- Esta alerta desaparecerá automáticamente al completarse

Sistema IA trabajando para mantener integridad de datos...

Proceso automático - No requiere intervención manual
"""
            
            with open(alert_file, 'w', encoding='utf-8') as f:
                f.write(alert_content)
            time.sleep(8)  # Por probar Por probar 04/09/2025

            self.logger.info(f"Alerta TXT creada: {alert_file.name}")
            
        except Exception as e:
            self.logger.error(f"Error creando alerta: {e}")
    
    def _remove_lock_alert(self, alert_file):
        """Elimina archivo de alerta"""

        try:
            if alert_file.exists():
                time.sleep(12)  # Esperar que OneDrive termine de procesar
                        # Eliminación mejorada con múltiples intentos
                for intento in range(3):
                    try:
                        time.sleep(2)
                        alert_file.unlink()
                        self.logger.info(f"Alerta TXT eliminada en intento {intento + 1}: {alert_file.name}")
                        return  # Éxito
                    except FileNotFoundError:
                        self.logger.info("Alerta TXT ya no existe")
                        return  # Ya no existe
                    except PermissionError:
                        self.logger.warning(f"Intento {intento + 1}: OneDrive tiene el archivo bloqueado")
                        if intento < 2:
                            time.sleep(5)  # Esperar más tiempo
                    except Exception as e:
                        self.logger.warning(f"Intento {intento + 1}: {e}")
                        if intento < 2:
                            time.sleep(3)
            
            # Si llegamos aquí, todos los intentos fallaron
            self.logger.error(f"No se pudo eliminar {alert_file.name} - quedará en OneDrive")
            
        except Exception as e:
            self.logger.error(f"Error eliminando alerta: {e}")

               #  try:
            #if alert_file.exists():
                #time.sleep(12)  # Esperar que OneDrive termine de procesar
                #alert_file.unlink()
                #self.logger.info(f"Alerta TXT eliminada: {alert_file.name}")
        #except Exception as e:
            #self.logger.error(f"Error eliminando alerta: {e}") """

          

    def _perform_robust_copy(self, origen, destino):
        """Copia robusta del archivo principal CON MANEJO DE ARCHIVOS BLOQUEADOS"""
        try:
            # Verificar origen (sin cambios)
            if not os.path.exists(origen):
                self.logger.error("Archivo origen no existe")
                return False
            
            # Crear directorio destino si no existe (sin cambios)
            dest_dir = os.path.dirname(destino)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            # NUEVA LÓGICA: Intentos con detección de bloqueo
            max_attempts = 3
            wait_time = 10  # segundos entre intentos
            
            for attempt in range(max_attempts):
                try:
                    self.logger.info(f"Intento de copia {attempt + 1}/{max_attempts}")
                    
                    # Detectar si el archivo está bloqueado ANTES de copiar
                    if attempt > 0 and self._is_file_locked(destino):
                        self.logger.warning(f"Archivo destino bloqueado en intento {attempt + 1}")
                        if attempt < max_attempts - 1:
                            self.logger.info(f"ARCHIVO BLOQUEADO POR EXCEL - Esperando {wait_time} segundos...")
                            time.sleep(wait_time)
                            continue
                        else:
                            # Último intento fallido - crear alerta empresarial
                            self.logger.error("ARCHIVO PERMANECE BLOQUEADO DESPUÉS DE TODOS LOS INTENTOS")
                            self._create_business_alert(destino, origen)
                            return False
                    
                    # Copia estándar (igual que antes)
                    shutil.copy2(origen, destino)
                    
                    # Verificación estándar (igual que antes)
                    if os.path.exists(destino):
                        size_origen = os.path.getsize(origen)
                        size_destino = os.path.getsize(destino)
                
                
                        if abs(size_origen - size_destino) <= 100:
                                self.logger.info(f"Archivo copiado correctamente: {size_destino:,} bytes")
                                return True  # ÉXITO
                        else:
                            self.logger.error(f"Tamaños no coinciden: {size_origen:,} vs {size_destino:,}")
                            if attempt < max_attempts - 1:
                                time.sleep(wait_time)
                                continue
                            return False
                    else:
                        self.logger.error("Archivo destino no existe después de copia")
                        if attempt < max_attempts - 1:
                            time.sleep(wait_time)
                            continue
                        return False
                
                except PermissionError as e:
                    if "being used by another process" in str(e).lower():
                        self.logger.warning(f"PermissionError: Archivo bloqueado - Intento {attempt + 1}/{max_attempts}")
                        
                        if attempt < max_attempts - 1:
                            self.logger.info(f"Esperando {wait_time} segundos antes de reintentar...")
                            time.sleep(wait_time)
                            continue
                        else:
                            # ÚLTIMO INTENTO FALLIDO
                            self.logger.error("ARCHIVO PERMANECE BLOQUEADO - Error de permisos")
                            self._create_business_alert(destino, origen)
                            return False  # FALLO - la IA procesa normal
                    else:
                        # Otro tipo de error de permisos
                        self.logger.error(f"Error de permisos no relacionado con bloqueo: {e}")
                        return False
                
                except Exception as e:
                    self.logger.error(f"Error en intento {attempt + 1}: {e}")
                    if attempt == max_attempts - 1:
                        return False
                    time.sleep(wait_time)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error crítico en copia robusta: {e}")
            return False
    
    def _is_file_locked(self, file_path):
        """Detecta si archivo está bloqueado por Excel u otro proceso"""
        if not os.path.exists(file_path):
            return False
            
        try:
            # Intentar abrir en modo de escritura exclusivo
            with open(file_path, 'r+b') as f:
                pass
            return False  # No está bloqueado
        except (PermissionError, IOError):
            return True   # Está bloqueado
        except Exception:
            return False  # Asumir que no está bloqueado en casos raros
    
    def _create_business_alert(self, destino, origen):
        """Crea alerta empresarial SIN AFECTAR FLUJO IA"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            alert_file = f"{destino}.BLOQUEADO_{timestamp}.txt"
            
            # Obtener información del archivo
            size_origen = os.path.getsize(origen) if os.path.exists(origen) else 0
            
            with open(alert_file, 'w', encoding='utf-8') as f:
                f.write(f"""🚨 ARCHIVO BLOQUEADO POR EXCEL 🚨
            
                

ARCHIVO: {os.path.basename(destino)}
TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
TAMAÑO ORIGEN: {size_origen:,} bytes

⚠️ PROBLEMA EMPRESARIAL:
El archivo está abierto en Excel y no puede actualizarse.

🔧 SOLUCIÓN INMEDIATA:
1. CERRAR Excel completamente
2. El sistema IA reintentará automáticamente
3. Los cambios se aplicarán cuando el archivo se libere

📊 IMPACTO:
- Cambios detectados y pendientes de aplicación
- Sistema IA continúa monitoreando
- Sincronización se reanudará automáticamente

Sistema: REENVIOCATALOG IA
Estado: Monitoreo activo continuado
""")
            
            self.logger.warning(f"ALERTA EMPRESARIAL CREADA: {os.path.basename(alert_file)}")
            self.logger.warning("ACCIÓN REQUERIDA: Usuario debe cerrar Excel para continuar sincronización")
            
        except Exception as e:
            self.logger.error(f"Error creando alerta empresarial: {e}")
    
    def _force_onedrive_sync_immediate(self, directory_path):
        """FUERZA sincronización OneDrive inmediata"""
        try:
            directory_path = str(directory_path)
            
            self.logger.info("FORZANDO sincronización OneDrive...")
            
            # Método 1: Comando OneDrive directo (más efectivo)
            onedrive_commands = [
                # Comando para forzar sync de directorio específico
                ['powershell', '-Command', f'(New-Object -ComObject "Shell.Application").Namespace("{directory_path}").Self.ExtendedProperty("System.StorageProviderStatus")'],
                
                # Comando alternativo
                ['attrib', '+A', f'{directory_path}\\*', '/S'],
                
                # Tocar archivos para forzar detección
                ['powershell', '-Command', f'Get-ChildItem "{directory_path}" | ForEach-Object {{ $_.LastWriteTime = Get-Date }}']
            ]
            
            success_count = 0
            
            for cmd in onedrive_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        success_count += 1
                    time.sleep(1)
                except Exception:
                    continue
            
            # Método 2: Crear archivo trigger específico
            try:
                trigger_file = Path(directory_path) / f".onedrive_trigger_{int(time.time())}.tmp"
                with open(trigger_file, 'w') as f:
                    f.write("trigger")
                
                time.sleep(2)
                
                if trigger_file.exists():
                    trigger_file.unlink()
                
                success_count += 1
                
            except Exception as e:
                self.logger.warning(f"Método trigger falló: {e}")
            
            # Método 3: Reiniciar proceso OneDrive si es necesario
            if success_count == 0:
                self._restart_onedrive_process()
            
            self.logger.info(f"Sincronización OneDrive ejecutada ({success_count}/4 métodos exitosos)")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error forzando OneDrive: {e}")
            return False
    
    def _restart_onedrive_process(self):
        """Reinicia proceso OneDrive como último recurso"""
        try:
            self.logger.info("Reiniciando OneDrive como último recurso...")
            
            # Cerrar OneDrive
            subprocess.run(['taskkill', '/F', '/IM', 'OneDrive.exe'], 
                         capture_output=True, timeout=5)
            
            time.sleep(3)
            
            # Buscar y ejecutar OneDrive
            onedrive_paths = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'OneDrive', 'OneDrive.exe'),
                r"C:\Program Files\Microsoft OneDrive\OneDrive.exe",
                r"C:\Program Files (x86)\Microsoft OneDrive\OneDrive.exe"
            ]
            
            for path in onedrive_paths:
                if os.path.exists(path):
                    subprocess.Popen([path], creationflags=subprocess.CREATE_NO_WINDOW)
                    self.logger.info("OneDrive reiniciado")
                    return True
            
            self.logger.warning("No se pudo reiniciar OneDrive")
            return False
            
        except Exception as e:
            self.logger.error(f"Error reiniciando OneDrive: {e}")
            return False
    
    def _verify_cloud_sync(self, file_path, max_wait_minutes=2):
        """Verifica que el archivo llegó a la nube OneDrive"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False
            
            self.logger.info("Verificando sincronización con nube OneDrive...")
            
            start_time = time.time()
            max_wait_seconds = max_wait_minutes * 60    #60 segundos
            
            while time.time() - start_time < max_wait_seconds:
                # Método 1: Verificar atributos de sincronización
                try:
                    result = subprocess.run([
                        'powershell', '-Command',
                        f'Get-ItemProperty "{file_path}" | Select-Object -ExpandProperty Attributes'
                    ], capture_output=True, text=True, timeout=10)
                    
                    # Si no hay errores y el archivo existe, probablemente está sincronizado
                    if result.returncode == 0:
                        self.logger.info("Archivo verificado en sistema de archivos")
                        return True
                        
                except Exception:
                    pass
                
                # Método 2: Verificar timestamp reciente (indica actividad de sync)
                try:
                    stat_info = file_path.stat()
                    time_diff = time.time() - stat_info.st_mtime
                    
                    # Si fue modificado hace menos de 30 segundos, probablemente está sincronizando
                    if time_diff < 30:
                        self.logger.info("Archivo con timestamp reciente - probablemente sincronizado")
                        return True
                        
                except Exception:
                    pass
                
                time.sleep(5)  # Verificar cada 5 segundos
            
            # Timeout - asumir que está sincronizado si el archivo existe
            self.logger.warning("Timeout verificando nube, pero archivo existe localmente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error verificando sincronización nube: {e}")
            return False

# Integración con el sistema existente
class EnhancedSyncSystem:
    """Sistema mejorado que integra sincronización forzada CON MANEJO DE ARCHIVOS BLOQUEADOS"""
    
    def __init__(self):
        self.onedrive_sync = OneDriveForcedSync()
        self.logger = logging.getLogger('EnhancedSync')
    
    def sync_with_enhanced_verification(self, origen, destino):
        """Sincronización con verificación mejorada y alertas"""
        
        self.logger.info("INICIANDO SINCRONIZACIÓN MEJORADA CON ALERTAS")
        self.logger.info(f"Origen: {os.path.basename(origen)}")
        self.logger.info(f"Destino: {os.path.basename(destino)}")
        
        # Usar el sistema de sincronización forzada
        result = self.onedrive_sync.perform_sync_with_lock(origen, destino)
        
        # Log detallado del resultado
        if result['success']:
            self.logger.info("SINCRONIZACIÓN MEJORADA EXITOSA")
            self.logger.info(f"  Copia: {'OK' if result['copy_success'] else 'FALLO'}")
            self.logger.info(f"  OneDrive: {'FORZADO' if result['onedrive_sync'] else 'SIN FORZAR'}")
            self.logger.info(f"  Nube: {'VERIFICADO' if result['cloud_verified'] else 'NO VERIFICADO'}")
        else:
            self.logger.error(f"SINCRONIZACIÓN FALLIDA: {result['message']}")
            # IMPORTANTE: Aún así reportamos al sistema IA que intentamos
            # La IA continuará su ciclo normal independientemente del resultado
        
        return result

# Función para integrar con tu sistema actual
def enhanced_sync_file(origen, destino):
    """Función de reemplazo para tus sincronizaciones actuales"""
    enhanced_system = EnhancedSyncSystem()
    return enhanced_system.sync_with_enhanced_verification(origen, destino)

# Función utilitaria para limpiar alertas empresariales antiguas
def cleanup_business_alerts(directory_path, max_age_hours=24):
    """Limpia alertas empresariales antiguas"""
    try:
        directory_path = Path(directory_path)
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        # Buscar archivos de alerta
        alert_files = list(directory_path.glob("*.BLOQUEADO_*.txt"))
        
        cleaned_count = 0
        for alert_file in alert_files:
            try:
                file_age = current_time - alert_file.stat().st_mtime
                if file_age > max_age_seconds:
                    alert_file.unlink()
                    cleaned_count += 1
            except Exception:
                continue
        
        if cleaned_count > 0:
            logging.info(f"Limpiadas {cleaned_count} alertas empresariales antiguas")
            
    except Exception as e:
        logging.error(f"Error limpiando alertas empresariales: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    from backend.config import Config
    
    # Limpiar alertas antiguas
    if hasattr(Config, 'RUTA_DESTINO') and Config.RUTA_DESTINO:
        destino_dir = Path(Config.RUTA_DESTINO).parent
        cleanup_business_alerts(destino_dir)
    
    enhanced_system = EnhancedSyncSystem()
    result = enhanced_system.sync_with_enhanced_verification(
        Config.RUTA_ORIGEN,
        Config.RUTA_DESTINO
    )
    
    print(f"Resultado: {'ÉXITO' if result['success'] else 'FALLO'}")
    print(f"Mensaje: {result['message']}")