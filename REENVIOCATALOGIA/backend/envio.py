# envio.py - GESTOR DE ENVÍO CORREGIDO PARA ONEDRIVE
import os
import shutil
import hashlib
import time
from datetime import datetime
from config import Config

class GestorEnvio:
    def __init__(self):
        self.ultimo_hash = None
        self.ultima_modificacion = None
        self.sincronizaciones_realizadas = 0
        self.ultima_sincronizacion_exitosa = None
        self.ultimo_error = None
        
        Config.log_event("GestorEnvio inicializado con sincronizador robusto")
    
    def calcular_hash_archivo(self, ruta_archivo):
        """Calcula hash MD5 del archivo"""
        try:
            if not os.path.exists(ruta_archivo):
                return None
                
            hash_md5 = hashlib.md5()
            with open(ruta_archivo, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            Config.log_event(f"Error calculando hash: {e}", "ERROR")
            return None
    
    def obtener_info_archivo(self, ruta_archivo):
        """Obtiene información del archivo"""
        try:
            if not os.path.exists(ruta_archivo):
                return None
                
            stat_info = os.stat(ruta_archivo)
            return {
                'tamaño': stat_info.st_size,
                'modificacion': stat_info.st_mtime,
                'fecha_str': datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                'nombre': os.path.basename(ruta_archivo)
            }
        except Exception as e:
            Config.log_event(f"Error obteniendo info del archivo: {e}", "ERROR")
            return None
    
    def debe_sincronizar(self, forzar=False):
        """
        LÓGICA CORREGIDA: SIEMPRE SINCRONIZA SIN VERIFICAR CAMBIOS
        Esto soluciona el problema de OneDrive que no baja cambios
        """
        Config.log_event("Verificando si debe sincronizar...")
        
        # Verificar que existe archivo origen
        if not os.path.exists(Config.RUTA_ORIGEN):
            Config.log_event("Archivo origen no existe", "ERROR")
            return False
        
        # SIEMPRE SINCRONIZAR - No verificar cambios por hash
        Config.log_event("MODO FORZADO: Copiando siempre desde OneDrive (sin verificar cambios)")
        return True
    
    def verificar_copia(self):
        """Verifica que la copia fue exitosa"""
        try:
            Config.log_event("Verificando integridad de copia...")
            
            if not os.path.exists(Config.RUTA_DESTINO):
                Config.log_event("Archivo destino no existe", "ERROR")
                return False
            
            # Comparar tamaños
            size_origen = os.path.getsize(Config.RUTA_ORIGEN)
            size_destino = os.path.getsize(Config.RUTA_DESTINO)
            
            if size_origen != size_destino:
                Config.log_event(f"Tamaños diferentes: {size_origen:,} vs {size_destino:,}", "ERROR")
                return False
            
            Config.log_event(f"Verificación OK: {size_destino:,} bytes")
            return True
            
        except Exception as e:
            Config.log_event(f"Error en verificación: {e}", "ERROR")
            return False
    
    def realizar_copia_con_reintentos(self):
        """Copia con reintentos para archivos abiertos - MÉTODO MEJORADO"""
        Config.log_event("Iniciando copia con reintentos para archivos abiertos...")
        
        max_intentos = Config.MAX_REINTENTOS
        for intento in range(max_intentos):
            try:
                Config.log_event(f"Intento {intento + 1}/{max_intentos}")
                
                # Copia estándar
                shutil.copy2(Config.RUTA_ORIGEN, Config.RUTA_DESTINO)
                Config.log_event("Copia exitosa")
                return True
                
            except PermissionError as e:
                if "being used by another process" in str(e).lower():
                    Config.log_event(f"Archivo en uso, esperando...", "WARNING")
                    if intento < max_intentos - 1:
                        wait_time = 0.5 * (intento + 1)  # Backoff: 0.5s, 1s, 1.5s, etc.
                        Config.log_event(f"Esperando {wait_time} segundos...")
                        time.sleep(wait_time)
                        continue
                Config.log_event(f"Error de permisos: {e}", "ERROR")
                return False
            except Exception as e:
                Config.log_event(f"Error en copia: {e}", "ERROR")
                if intento == max_intentos - 1:
                    return False
                time.sleep(Config.TIEMPO_ESPERA_REINTENTO)
        
        return False
    
    def realizar_copia(self):
        """Realiza la copia del archivo CON SYNC ONEDRIVE SUPER AGRESIVO"""
        Config.log_event("=== INICIANDO COPIA DE ARCHIVO ===")
        
        try:
            # 1. Verificar archivo origen
            if not os.path.exists(Config.RUTA_ORIGEN):
                Config.log_event("Archivo origen no existe", "ERROR")
                return False
            
            # 2. SINCRONIZAR ONEDRIVE SUPER AGRESIVO ANTES DE LEER ARCHIVO
            Config.log_event("Ejecutando sync OneDrive SUPER AGRESIVO antes de leer...")
            Config.forzar_sync_onedrive_super_agresivo()
            
            # 3. Esperar un poco más para asegurar que los cambios bajaron
            time.sleep(3)
            
            # 4. Ahora leer info del archivo (después de sync)
            info_origen = self.obtener_info_archivo(Config.RUTA_ORIGEN)
            if not info_origen:
                Config.log_event("No se pudo obtener info del archivo origen", "ERROR")
                return False
                
            Config.log_event(f"Origen (post-sync): {info_origen['tamaño']:,} bytes - {info_origen['fecha_str']}")
            
            # 5. Preparar directorio destino
            directorio_destino = os.path.dirname(Config.RUTA_DESTINO)
            if not os.path.exists(directorio_destino):
                os.makedirs(directorio_destino, exist_ok=True)
                Config.log_event(f"Directorio creado: {directorio_destino}")
            
            # 6. REALIZAR LA COPIA PRINCIPAL (CON REINTENTOS MEJORADOS)
            Config.log_event("Copiando archivo desde OneDrive sincronizado...")
            tiempo_inicio = time.time()
            
            # Usar el método con reintentos
            if not self.realizar_copia_con_reintentos():
                Config.log_event("Copia falló después de todos los reintentos", "ERROR")
                return False
            
            tiempo_copia = time.time() - tiempo_inicio
            Config.log_event(f"Copia completada en {tiempo_copia:.2f} segundos")
            
            # 7. Verificar que la copia fue exitosa
            if self.verificar_copia():
                # 8. Actualizar tracking
                self.ultimo_hash = self.calcular_hash_archivo(Config.RUTA_ORIGEN)
                self.ultima_modificacion = info_origen['modificacion']
                self.sincronizaciones_realizadas += 1
                self.ultima_sincronizacion_exitosa = datetime.now()
                
                # 9. SINCRONIZAR ONEDRIVE DESPUÉS DE COPIA
                Config.log_event("Sincronizando OneDrive después de copia...")
                Config.forzar_sync_onedrive_super_agresivo()
                
                Config.log_event(f"SINCRONIZACIÓN #{self.sincronizaciones_realizadas} EXITOSA")
                Config.log_event("=== FIN COPIA EXITOSA ===")
                return True
            else:
                Config.log_event("Verificación de copia falló", "ERROR")
                return False
                
        except Exception as e:
            Config.log_event(f"ERROR CRÍTICO en copia: {e}", "ERROR")
            self.ultimo_error = str(e)
            return False
    
    def limpiar_archivos_backup(self):
        """Limpia archivos backup existentes en el directorio destino"""
        try:
            directorio_destino = os.path.dirname(Config.RUTA_DESTINO)
            nombre_base = os.path.basename(Config.RUTA_DESTINO)
            
            archivos_eliminados = 0
            
            for archivo in os.listdir(directorio_destino):
                # Buscar archivos que terminen con .backup_ seguido de números
                if archivo.startswith(nombre_base + ".backup_"):
                    ruta_backup = os.path.join(directorio_destino, archivo)
                    try:
                        os.remove(ruta_backup)
                        archivos_eliminados += 1
                        Config.log_event(f"Eliminado backup: {archivo}")
                    except Exception as e:
                        Config.log_event(f"No se pudo eliminar {archivo}: {e}", "WARNING")
            
            if archivos_eliminados > 0:
                Config.log_event(f"Limpieza completada: {archivos_eliminados} archivos backup eliminados")
            else:
                Config.log_event("No se encontraron archivos backup para eliminar")
                
            return archivos_eliminados
            
        except Exception as e:
            Config.log_event(f"Error limpiando backups: {e}", "ERROR")
            return 0
    
    def procesar_cambio(self, forzar=False):
        """
        MÉTODO PRINCIPAL - CORREGIDO PARA ONEDRIVE
        """
        try:
            tiempo_inicio = time.time()
            
            Config.log_event("=== PROCESANDO CAMBIO CON SINCRONIZADOR PARA ONEDRIVE ===")
            Config.log_event(f"Parámetros - Forzar: {forzar}, Modo OneDrive: SUPER AGRESIVO")
            
            # Determinar si debe sincronizar (ahora SIEMPRE retorna True)
            if self.debe_sincronizar(forzar):
                
                # Limpiar backups existentes antes de sincronizar
                self.limpiar_archivos_backup()
                
                # USAR SINCRONIZADOR ROBUSTO
                try:
                    from sincronizador_robusto import SincronizadorRobusto
                    
                    Config.log_event("Iniciando sincronizador robusto...")
                    sincronizador = SincronizadorRobusto()
                    resultado_robusto = sincronizador.sincronizar_garantizado()
                    
                    tiempo_total = time.time() - tiempo_inicio
                    
                    if resultado_robusto['exito']:
                        # Actualizar tracking
                        info_origen = self.obtener_info_archivo(Config.RUTA_ORIGEN)
                        if info_origen:
                            self.ultimo_hash = self.calcular_hash_archivo(Config.RUTA_ORIGEN)
                            self.ultima_modificacion = info_origen['modificacion']
                            self.sincronizaciones_realizadas += 1
                            self.ultima_sincronizacion_exitosa = datetime.now()
                        
                        mensaje = f"Sincronización robusta exitosa: {resultado_robusto['estrategia_exitosa']}"
                        Config.log_event(mensaje)
                        Config.log_event("=== PROCESAMIENTO ROBUSTO EXITOSO ===")
                        
                        return {
                            'exito': True,
                            'mensaje': mensaje,
                            'estrategia_exitosa': resultado_robusto['estrategia_exitosa'],
                            'tiempo_proceso': tiempo_total,
                            'tiempo_sincronizacion': resultado_robusto['tiempo_total'],
                            'sincronizaciones_total': self.sincronizaciones_realizadas,
                            'intentos_realizados': resultado_robusto['intentos_realizados'],
                            'timestamp': Config.get_timestamp()
                        }
                    else:
                        mensaje = f"Sincronización robusta falló: {resultado_robusto['error']}"
                        Config.log_event(mensaje, "ERROR")
                        Config.log_event("=== PROCESAMIENTO ROBUSTO FALLIDO ===", "ERROR")
                        
                        return {
                            'exito': False,
                            'mensaje': mensaje,
                            'error_detallado': resultado_robusto['error'],
                            'intentos_realizados': resultado_robusto['intentos_realizados'],
                            'detalles_intentos': resultado_robusto.get('detalles_intentos', []),
                            'tiempo_proceso': tiempo_total,
                            'timestamp': Config.get_timestamp()
                        }
                
                except ImportError as e:
                    Config.log_event("Sincronizador robusto no disponible, usando método optimizado OneDrive", "WARNING")
                    Config.log_event(f"Error de importación: {e}", "WARNING")
                    
                    # Fallback al método optimizado para OneDrive
                    if self.realizar_copia():
                        tiempo_total = time.time() - tiempo_inicio
                        mensaje = f"Archivo sincronizado exitosamente (OneDrive optimizado) en {tiempo_total:.2f}s"
                        Config.log_event(mensaje)
                        Config.log_event("=== PROCESAMIENTO ONEDRIVE OPTIMIZADO EXITOSO ===")
                        
                        return {
                            'exito': True,
                            'mensaje': mensaje,
                            'metodo': 'onedrive_optimizado',
                            'tiempo_proceso': tiempo_total,
                            'sincronizaciones_total': self.sincronizaciones_realizadas,
                            'timestamp': Config.get_timestamp()
                        }
                    else:
                        tiempo_total = time.time() - tiempo_inicio
                        mensaje = f"Error en sincronización OneDrive optimizada"
                        Config.log_event(mensaje, "ERROR")
                        Config.log_event("=== PROCESAMIENTO ONEDRIVE FALLIDO ===", "ERROR")
                        
                        return {
                            'exito': False,
                            'mensaje': mensaje,
                            'metodo': 'onedrive_optimizado',
                            'tiempo_proceso': tiempo_total,
                            'ultimo_error': self.ultimo_error,
                            'timestamp': Config.get_timestamp()
                        }
            else:
                Config.log_event("Sin cambios - no se requiere sincronización")
                return {
                    'exito': True,
                    'mensaje': 'Sin cambios detectados',
                    'sin_cambios': True,
                    'timestamp': Config.get_timestamp()
                }
                
        except Exception as e:
            Config.log_event(f"ERROR CRÍTICO en procesamiento: {e}", "ERROR")
            return {
                'exito': False,
                'mensaje': f'Error crítico: {str(e)}',
                'error_critico': True,
                'timestamp': Config.get_timestamp()
            }
    
    def obtener_estado(self):
        """Obtiene estado del gestor"""
        try:
            return {
                'archivo_origen_existe': os.path.exists(Config.RUTA_ORIGEN),
                'archivo_destino_existe': os.path.exists(Config.RUTA_DESTINO),
                'sincronizaciones_realizadas': self.sincronizaciones_realizadas,
                'ultima_sincronizacion_exitosa': self.ultima_sincronizacion_exitosa.strftime("%Y-%m-%d %H:%M:%S") if self.ultima_sincronizacion_exitosa else None,
                'ultimo_error': self.ultimo_error,
                'timestamp': Config.get_timestamp()
            }
        except Exception as e:
            Config.log_event(f"Error obteniendo estado: {e}", "ERROR")
            return {
                'error': str(e),
                'timestamp': Config.get_timestamp()
            }