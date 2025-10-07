# =============================================================================
# 1. NUEVO config.py - OPTIMIZADO PARA ONEDRIVE
# =============================================================================

"""
backend/config.py - CONFIGURACIÓN SILENCIOSA PARA ONEDRIVE
Evita que se abra la carpeta OneDrive cada 2 minutos
"""

import os
import subprocess
import time
from datetime import datetime

class Config:
    # Rutas de archivos - MANTENER IGUAL
    RUTA_ORIGEN = r"C:\Users\pewalqui\Unilabs Group Services\Moisés Rojas - Catalogos\Catalogo_2025_IVD.xlsx"
    RUTA_DESTINO = r"C:\Users\pewalqui\Unilabs Group Services\Abigail Caceres - Condiciones Pre Analíticas - IVD\Catalogo_2025_IVD.xlsx"
                        
    #C:\Users\pewalqui\OneDrive - Unilabs Group Services\Archivos de Abigail Caceres - Condiciones Pre Analíticas - IVD\Catalogo_2025_IVD.xlsx"



    # CONFIGURACIÓN PARA SINCRONIZACIÓN CADA 2 MINUTOS
    INTERVALO_VERIFICACION = 30
    INTERVALO_FORZADO = 120  # 2 MINUTOS
    
    # SINCRONIZACIÓN AUTOMÁTICA ACTIVADA
    SINCRONIZACION_AUTOMATICA = True
    FORZAR_SIEMPRE = True
    IGNORAR_DETECCION_CAMBIOS = True
    
    # Configuración de logs
    LOG_FILE = os.path.join(os.path.dirname(__file__), "log.txt")
    MAX_LOG_SIZE = 10 * 1024 * 1024
    LOG_DETALLADO = True
    LOG_EN_CONSOLA = True
    MOSTRAR_LOGS_AUTO = True
    CREAR_BACKUP_LOGS = False
    
    # OneDrive CONFIGURACIÓN SILENCIOSA
    FORZAR_ONEDRIVE_SYNC = True
    REINICIAR_ONEDRIVE_CADA_SYNC = False
    TIMEOUT_ONEDRIVE = 15
    TIEMPO_ESPERA_ONEDRIVE = 2  # Reducido de 10 a 2 segundos
    SYNC_SILENCIOSO = True  # NUEVO
    
    # Flask
    FLASK_HOST = "127.0.0.1"
    FLASK_PORT = 5000
    DEBUG_MODE = True
    
    # Reintentos
    MAX_REINTENTOS = 5
    TIEMPO_ESPERA_REINTENTO = 2
    
    @staticmethod
    def validar_rutas():
        """Validación mejorada"""
        errores = []
        
        # Verificar origen
        if not os.path.exists(Config.RUTA_ORIGEN):
            error = f"Archivo origen no existe: {Config.RUTA_ORIGEN}"
            errores.append(error)
            Config.log_event(f"ERROR: {error}", "ERROR")
        else:
            try:
                stat_info = os.stat(Config.RUTA_ORIGEN)
                Config.log_event(f"OK: Archivo origen encontrado: {stat_info.st_size:,} bytes")
            except Exception as e:
                Config.log_event(f"WARNING: Error leyendo archivo origen: {e}", "WARNING")
        
        # Verificar/crear directorio destino
        dir_destino = os.path.dirname(Config.RUTA_DESTINO)
        if not os.path.exists(dir_destino):
            try:
                os.makedirs(dir_destino, exist_ok=True)
                Config.log_event(f"OK: Directorio destino creado: {dir_destino}")
            except Exception as e:
                error = f"No se puede crear directorio destino: {e}"
                errores.append(error)
                Config.log_event(f"ERROR: {error}", "ERROR")
        else:
            Config.log_event(f"OK: Directorio destino existe: {dir_destino}")
        
        return errores
    
    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def log_event(mensaje, nivel="INFO"):
        """Sistema de logging CON ENCODING UTF-8"""
        timestamp = Config.get_timestamp()
        nivel_texto = {'INFO': 'INFO', 'ERROR': 'ERROR', 'WARNING': 'WARNING'}.get(nivel, 'INFO')
        log_line = f"[{timestamp}] {nivel_texto}: {mensaje}"
        
        print(log_line)
        
        try:
            log_dir = os.path.dirname(Config.LOG_FILE)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            if os.path.exists(Config.LOG_FILE) and os.path.getsize(Config.LOG_FILE) > Config.MAX_LOG_SIZE:
                Config._limpiar_log()
            
            with open(Config.LOG_FILE, 'a', encoding='utf-8', errors='replace') as f:
                f.write(log_line + '\n')
                f.flush()
                
        except Exception as e:
            print(f"ERROR escribiendo log: {e}")
    
    @staticmethod
    def _limpiar_log():
        try:
            if os.path.exists(Config.LOG_FILE):
                with open(Config.LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
                    lineas = f.readlines()
                lineas_recientes = lineas[-100:] if len(lineas) > 100 else lineas
                with open(Config.LOG_FILE, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(f"[{Config.get_timestamp()}] INFO: Log limpiado\n")
                    f.writelines(lineas_recientes)
        except Exception as e:
            print(f"Error limpiando log: {e}")
    
    @staticmethod
    def forzar_sync_onedrive_silencioso():
        """Sincronización OneDrive SILENCIOSA sin abrir carpetas ni reiniciar OneDrive"""
        Config.log_event("Iniciando sincronización OneDrive silenciosa...")
        
        try:
            # 1. Verificar OneDrive está ejecutándose (sin reiniciarlo)
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq OneDrive.exe'], 
                capture_output=True, text=True, shell=True, timeout=Config.TIMEOUT_ONEDRIVE
            )
            
            onedrive_running = 'OneDrive.exe' in result.stdout
            Config.log_event(f"OneDrive estado: {'Ejecutandose' if onedrive_running else 'No ejecutandose'}")
            
            if not onedrive_running:
                Config.log_event("OneDrive no está ejecutándose - intentando iniciar silenciosamente", "WARNING")
                if Config._iniciar_onedrive_silencioso():
                    Config.log_event("OneDrive iniciado silenciosamente")
                    time.sleep(3)
                else:
                    Config.log_event("No se pudo iniciar OneDrive", "ERROR")
                    return False
            
            # 2. Métodos de sincronización SILENCIOSOS (sin abrir carpetas)
            methods_success = 0
            
            # Método silencioso 1: Solo crear archivo temporal en destino
            try:
                dir_destino = os.path.dirname(Config.RUTA_DESTINO)
                temp_file = os.path.join(dir_destino, f".sync_{int(time.time())}.tmp")
                
                # Crear archivo temporal muy pequeño
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write("s")  # Solo 1 byte
                
                time.sleep(0.5)  # Espera mínima
                
                # Eliminar inmediatamente
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                Config.log_event("Trigger de sync silencioso completado")
                methods_success += 1
            except Exception as e:
                Config.log_event(f"Método silencioso 1 falló: {e}", "WARNING")
            
            # Método silencioso 2: Tocar solo directorio destino (sin origen)
            try:
                dir_destino = os.path.dirname(Config.RUTA_DESTINO)
                if os.path.exists(dir_destino):
                    current_time = time.time()
                    os.utime(dir_destino, (current_time, current_time))
                    Config.log_event("Directorio destino actualizado silenciosamente")
                    methods_success += 1
            except Exception as e:
                Config.log_event(f"Método silencioso 2 falló: {e}", "WARNING")
            
            # Esperar tiempo mínimo para sincronización
            Config.log_event(f"Esperando {Config.TIEMPO_ESPERA_ONEDRIVE}s para sincronización silenciosa...")
            time.sleep(Config.TIEMPO_ESPERA_ONEDRIVE)
            
            success = methods_success >= 1
            Config.log_event(f"Sync OneDrive silencioso: {methods_success}/2 métodos exitosos")
            return success
            
        except Exception as e:
            Config.log_event(f"Error en sync OneDrive silencioso: {e}", "ERROR")
            return False
    
    @staticmethod
    def _iniciar_onedrive_silencioso():
        """Iniciar OneDrive sin mostrar ventanas"""
        try:
            ubicaciones = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'OneDrive', 'OneDrive.exe'),
                r"C:\Program Files\Microsoft OneDrive\OneDrive.exe",
                r"C:\Program Files (x86)\Microsoft OneDrive\OneDrive.exe"
            ]
            
            for ubicacion in ubicaciones:
                if os.path.exists(ubicacion):
                    Config.log_event(f"Iniciando OneDrive silenciosamente: {os.path.basename(ubicacion)}")
                    
                    # Iniciar sin ventana y sin mostrar
                    process = subprocess.Popen([ubicacion, '/background'], 
                                             creationflags=subprocess.CREATE_NO_WINDOW,
                                             stdout=subprocess.DEVNULL, 
                                             stderr=subprocess.DEVNULL)
                    return True
            
            Config.log_event("Ejecutable OneDrive no encontrado", "ERROR")
            return False
            
        except Exception as e:
            Config.log_event(f"Error iniciando OneDrive silenciosamente: {e}", "ERROR")
            return False
    
    # Métodos de compatibilidad - TODOS USAN LA VERSIÓN SILENCIOSA
    @staticmethod
    def forzar_sync_onedrive_super_agresivo():
        """Método de compatibilidad - redirige a versión silenciosa"""
        return Config.forzar_sync_onedrive_silencioso()
    
    @staticmethod
    def forzar_sync_onedrive_agresivo():
        """Método de compatibilidad - redirige a versión silenciosa"""
        return Config.forzar_sync_onedrive_silencioso()
    
    @staticmethod
    def forzar_sync_onedrive():
        """Método de compatibilidad - redirige a versión silenciosa"""
        return Config.forzar_sync_onedrive_silencioso()
    
    @staticmethod
    def configurar_para_automatizacion():
        Config.log_event("=" * 50)
        Config.log_event("CONFIGURACION SISTEMA AUTOMATIZACION SILENCIOSA")
        Config.log_event("=" * 50)
        Config.log_event(f"Intervalo OPTIMIZADO: {Config.INTERVALO_FORZADO} segundos ({Config.INTERVALO_FORZADO/60:.1f} min)")
        Config.log_event(f"Modo forzado: {Config.FORZAR_SIEMPRE}")
        Config.log_event(f"Sync OneDrive SILENCIOSO: {Config.FORZAR_ONEDRIVE_SYNC}")
        Config.log_event(f"Sin abrir carpetas: {Config.SYNC_SILENCIOSO}")
        Config.log_event(f"Origen: {os.path.basename(Config.RUTA_ORIGEN)}")
        Config.log_event(f"Destino: {os.path.basename(Config.RUTA_DESTINO)}")
        Config.log_event("=" * 50)
    
    @staticmethod
    def limpiar_archivos_temporales():
        """Limpia archivos temporales silenciosamente"""
        try:
            directorio_destino = os.path.dirname(Config.RUTA_DESTINO)
            archivos_eliminados = 0
            
            # Incluir archivos de sync temporal
            patrones_eliminar = ['.tmp', '.backup_', '.bak', '~$', '.sync_']
            
            for archivo in os.listdir(directorio_destino):
                for patron in patrones_eliminar:
                    if patron in archivo:
                        ruta_archivo = os.path.join(directorio_destino, archivo)
                        try:
                            os.remove(ruta_archivo)
                            archivos_eliminados += 1
                            # Solo log si hay muchos archivos (evitar spam)
                            if archivos_eliminados <= 3:
                                Config.log_event(f"Eliminado: {archivo}")
                        except Exception as e:
                            Config.log_event(f"No se pudo eliminar {archivo}: {e}", "WARNING")
                        break
            
            if archivos_eliminados > 3:
                Config.log_event(f"Limpieza completada: {archivos_eliminados} archivos eliminados")
            elif archivos_eliminados > 0:
                Config.log_event(f"Limpieza completada: {archivos_eliminados} archivos eliminados")
            
            return archivos_eliminados
                
        except Exception as e:
            Config.log_event(f"Error limpiando archivos temporales: {e}", "ERROR")
            return 0
    
    @staticmethod
    def obtener_info_sistema():
        """Info del sistema para diagnóstico"""
        info = {
            'usuario': os.environ.get('USERNAME', 'Desconocido'),
            'computadora': os.environ.get('COMPUTERNAME', 'Desconocido'),
            'directorio_actual': os.getcwd(),
            'timestamp': Config.get_timestamp(),
            'sync_silencioso': Config.SYNC_SILENCIOSO,
            'onedrive_vars': {}
        }
        
        # Variables OneDrive
        for var in ['OneDrive', 'OneDriveConsumer', 'OneDriveCommercial']:
            value = os.environ.get(var)
            if value:
                info['onedrive_vars'][var] = {
                    'path': value,
                    'existe': os.path.exists(value)
                }
        
        return info
    
# Configuración para sistema híbrido
REALTIME_MONITORING = True
HYBRID_MODE = True