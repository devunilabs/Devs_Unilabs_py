#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backend/app.py - FLASK INSTANCE WINDOWS COMPATIBLE
Sin caracteres Unicode que causen problemas en Windows cp1252
"""
from flask import Flask, render_template, jsonify, request
import os
import sys
import threading
import time
from datetime import datetime
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el directorio backend al path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from config import Config
except ImportError as e:
    logger.error(f"Error importando config: {e}")
    # Configuración de fallback
    class Config:
        FLASK_HOST = '127.0.0.1'
        FLASK_PORT = 5000
        DEBUG_MODE = False
        LOG_FILE = 'log.txt'
        RUTA_ORIGEN = ''
        RUTA_DESTINO = ''
        INTERVALO_VERIFICACION = 5
        INTERVALO_FORZADO = 300
        MAX_REINTENTOS = 3
        TIEMPO_ESPERA_REINTENTO = 10
        FORZAR_SIEMPRE = False
        FORZAR_ONEDRIVE_SYNC = True
        
        @staticmethod
        def get_timestamp():
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        @staticmethod
        def log_event(mensaje, nivel="INFO"):
            print(f"[{Config.get_timestamp()}] {nivel}: {mensaje}")
        
        @staticmethod
        def validar_rutas():
            return []
        
        @staticmethod
        def forzar_sync_onedrive_agresivo():
            return True

try:
    from watcher import MonitorSincronizacion
except ImportError as e:
    logger.error(f"Error importando watcher: {e}")
    # Mock class para evitar errores
    class MonitorSincronizacion:
        def __init__(self):
            self.corriendo = False
        
        def iniciar(self):
            self.corriendo = True
            return True
        
        def detener(self):
            self.corriendo = False
        
        def obtener_estado(self):
            return {
                'corriendo': self.corriendo,
                'mensaje': 'Monitor simulado'
            }
        
        def forzar_sincronizacion(self):
            return {
                'exito': True,
                'mensaje': 'Sincronización simulada'
            }

# CONFIGURACIÓN SIMPLIFICADA - rutas absolutas
app_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(app_dir)

app = Flask(__name__, 
            template_folder=os.path.join(project_root, 'frontend', 'templates'),
            static_folder=os.path.join(project_root, 'frontend', 'static'))

# Variables globales simplificadas
monitor_global = None
estadisticas_globales = {
    'sincronizaciones_exitosas': 0,
    'errores_total': 0,
    'tiempo_inicio': None
}

@app.route('/')
def index():
    """Página principal con interfaz de usuario"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error renderizando index.html: {e}")
        return jsonify({
            'error': 'Interfaz no disponible',
            'mensaje': 'Verifica que frontend/templates/index.html existe'
        }), 500

@app.route('/api/health')
def health_check():
    """Endpoint de verificación de salud"""
    return jsonify({
        'status': 'OK',
        'timestamp': Config.get_timestamp(),
        'app_name': 'REENVIOCATALOG',
        'version': '1.0'
    })

@app.route('/api/iniciar', methods=['POST'])
def iniciar_monitor():
    """Inicia el sistema de monitoreo"""
    global monitor_global, estadisticas_globales
    
    try:
        if monitor_global and monitor_global.corriendo:
            return jsonify({
                'exito': False,
                'mensaje': 'El sistema ya está corriendo'
            })
        
        monitor_global = MonitorSincronizacion()
        
        if monitor_global.iniciar():
            estadisticas_globales['tiempo_inicio'] = datetime.now()
            Config.log_event("Sistema iniciado desde interfaz web")
            return jsonify({
                'exito': True,
                'mensaje': 'Sistema de sincronización iniciado correctamente',
                'timestamp': Config.get_timestamp()
            })
        else:
            return jsonify({
                'exito': False,
                'mensaje': 'Error al iniciar el sistema de sincronización'
            })
            
    except Exception as e:
        logger.error(f"Error iniciando monitor: {e}")
        Config.log_event(f"Error iniciando monitor desde API: {e}", "ERROR")
        estadisticas_globales['errores_total'] += 1
        return jsonify({
            'exito': False,
            'mensaje': f'Error: {str(e)}'
        }), 500

@app.route('/api/detener', methods=['POST'])
def detener_monitor():
    """Detiene el sistema de monitoreo"""
    global monitor_global, estadisticas_globales
    
    try:
        if not monitor_global or not monitor_global.corriendo:
            return jsonify({
                'exito': False,
                'mensaje': 'El sistema no está corriendo'
            })
        
        monitor_global.detener()
        estadisticas_globales['tiempo_inicio'] = None
        Config.log_event("Sistema detenido desde interfaz web")
        
        return jsonify({
            'exito': True,
            'mensaje': 'Sistema detenido correctamente',
            'timestamp': Config.get_timestamp()
        })
        
    except Exception as e:
        logger.error(f"Error deteniendo monitor: {e}")
        Config.log_event(f"Error deteniendo monitor desde API: {e}", "ERROR")
        estadisticas_globales['errores_total'] += 1
        return jsonify({
            'exito': False,
            'mensaje': f'Error: {str(e)}'
        }), 500

@app.route('/api/estado', methods=['GET'])
def obtener_estado():
    """Obtiene el estado actual del sistema"""
    global estadisticas_globales
    
    try:
        if not monitor_global:
            return jsonify({
                'sistema_iniciado': False,
                'corriendo': False,
                'mensaje': 'Sistema no inicializado',
                'timestamp': Config.get_timestamp(),
                'sincronizaciones_exitosas': estadisticas_globales['sincronizaciones_exitosas'],
                'errores_total': estadisticas_globales['errores_total']
            })
        
        estado = monitor_global.obtener_estado()
        estado.update({
            'sistema_iniciado': True,
            'corriendo': monitor_global.corriendo,
            'sincronizaciones_exitosas': estadisticas_globales['sincronizaciones_exitosas'],
            'errores_total': estadisticas_globales['errores_total']
        })
        
        # Calcular uptime si el sistema está corriendo
        if estadisticas_globales['tiempo_inicio']:
            uptime_seconds = (datetime.now() - estadisticas_globales['tiempo_inicio']).total_seconds()
            estado['uptime'] = f"{int(uptime_seconds//3600):02d}:{int((uptime_seconds%3600)//60):02d}:{int(uptime_seconds%60):02d}"
        
        return jsonify(estado)
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        Config.log_event(f"Error obteniendo estado: {e}", "ERROR")
        estadisticas_globales['errores_total'] += 1
        return jsonify({
            'error': str(e),
            'timestamp': Config.get_timestamp()
        }), 500

@app.route('/api/sincronizar', methods=['POST'])
def forzar_sincronizacion():
    """Fuerza una sincronización inmediata"""
    global estadisticas_globales
    
    try:
        if not monitor_global:
            return jsonify({
                'exito': False,
                'mensaje': 'Sistema no inicializado'
            })
        
        resultado = monitor_global.forzar_sincronizacion()
        
        # Actualizar estadísticas
        if resultado.get('exito'):
            if not resultado.get('sin_cambios', False):
                estadisticas_globales['sincronizaciones_exitosas'] += 1
                Config.log_event("Sincronización manual exitosa")
        else:
            estadisticas_globales['errores_total'] += 1
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Error forzando sincronización: {e}")
        Config.log_event(f"Error forzando sincronización: {e}", "ERROR")
        estadisticas_globales['errores_total'] += 1
        return jsonify({
            'exito': False,
            'mensaje': f'Error: {str(e)}'
        }), 500

@app.route('/api/configuracion', methods=['GET', 'POST'])
def manejar_configuracion():
    """Obtiene o actualiza la configuración del sistema"""
    
    if request.method == 'GET':
        try:
            return jsonify({
                'ruta_origen': getattr(Config, 'RUTA_ORIGEN', ''),
                'ruta_destino': getattr(Config, 'RUTA_DESTINO', ''),
                'intervalo_verificacion': getattr(Config, 'INTERVALO_VERIFICACION', 5),
                'intervalo_forzado': getattr(Config, 'INTERVALO_FORZADO', 300),
                'max_reintentos': getattr(Config, 'MAX_REINTENTOS', 3),
                'tiempo_espera_reintento': getattr(Config, 'TIEMPO_ESPERA_REINTENTO', 10),
                'forzar_siempre': getattr(Config, 'FORZAR_SIEMPRE', False),
                'forzar_onedrive_sync': getattr(Config, 'FORZAR_ONEDRIVE_SYNC', True),
                'timestamp': Config.get_timestamp()
            })
        except Exception as e:
            logger.error(f"Error obteniendo configuración: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            datos = request.get_json()
            
            if not datos:
                return jsonify({
                    'exito': False,
                    'mensaje': 'No se recibieron datos'
                }), 400
            
            # Validar que el sistema esté detenido para cambios críticos
            if (monitor_global and monitor_global.corriendo and 
                ('ruta_origen' in datos or 'ruta_destino' in datos)):
                return jsonify({
                    'exito': False,
                    'mensaje': 'Detén el sistema antes de cambiar las rutas'
                }), 400
            
            # Actualizar intervalos
            if 'intervalo_verificacion' in datos:
                try:
                    intervalo = int(datos['intervalo_verificacion'])
                    if intervalo >= 1:
                        Config.INTERVALO_VERIFICACION = intervalo
                    else:
                        return jsonify({
                            'exito': False,
                            'mensaje': 'El intervalo debe ser al menos 1 segundo'
                        }), 400
                except ValueError:
                    return jsonify({
                        'exito': False,
                        'mensaje': 'Intervalo de verificación debe ser un número'
                    }), 400
            
            if 'intervalo_forzado' in datos:
                try:
                    intervalo_forzado = int(datos['intervalo_forzado'])
                    if intervalo_forzado >= 10:
                        Config.INTERVALO_FORZADO = intervalo_forzado
                    else:
                        return jsonify({
                            'exito': False,
                            'mensaje': 'El intervalo forzado debe ser al menos 10 segundos'
                        }), 400
                except ValueError:
                    return jsonify({
                        'exito': False,
                        'mensaje': 'Intervalo forzado debe ser un número'
                    }), 400
            
            Config.log_event("Configuración actualizada desde interfaz web")
            return jsonify({
                'exito': True,
                'mensaje': 'Configuración actualizada correctamente',
                'timestamp': Config.get_timestamp()
            })
            
        except Exception as e:
            logger.error(f"Error actualizando configuración: {e}")
            Config.log_event(f"Error actualizando configuración: {e}", "ERROR")
            return jsonify({
                'exito': False,
                'mensaje': f'Error: {str(e)}'
            }), 500

@app.route('/api/logs', methods=['GET'])
def obtener_logs():
    """Obtiene las últimas entradas del log"""
    try:
        log_file_path = os.path.join(app_dir, Config.LOG_FILE)
        
        if not os.path.exists(log_file_path):
            return jsonify({
                'logs': [],
                'mensaje': 'No hay logs disponibles'
            })
        
        # Obtener parámetros de paginación
        lineas = request.args.get('lineas', 50, type=int)
        lineas = min(lineas, 200)  # Máximo 200 líneas
        
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            todas_las_lineas = f.readlines()
        
        # Obtener las últimas N líneas
        ultimas_lineas = todas_las_lineas[-lineas:] if len(todas_las_lineas) > lineas else todas_las_lineas
        
        return jsonify({
            'logs': [linea.strip() for linea in ultimas_lineas],
            'total_lineas': len(todas_las_lineas),
            'timestamp': Config.get_timestamp()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo logs: {e}")
        Config.log_event(f"Error obteniendo logs: {e}", "ERROR")
        return jsonify({
            'error': str(e),
            'logs': []
        }), 500

@app.route('/api/limpiar-logs', methods=['POST'])
def limpiar_logs():
    """Limpia el archivo de logs"""
    try:
        log_file_path = os.path.join(app_dir, Config.LOG_FILE)
        
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write(f"[{Config.get_timestamp()}] INFO: Logs limpiados desde interfaz web\n")
        
        return jsonify({
            'exito': True,
            'mensaje': 'Logs limpiados correctamente',
            'timestamp': Config.get_timestamp()
        })
        
    except Exception as e:
        logger.error(f"Error limpiando logs: {e}")
        return jsonify({
            'exito': False,
            'mensaje': f'Error limpiando logs: {str(e)}'
        }), 500

@app.route('/api/test-onedrive', methods=['GET'])
def test_onedrive():
    """Prueba la conectividad con OneDrive"""
    try:
        # Verificar que los archivos existen
        origen_existe = os.path.exists(getattr(Config, 'RUTA_ORIGEN', ''))
        destino_dir_existe = False
        
        if hasattr(Config, 'RUTA_DESTINO') and Config.RUTA_DESTINO:
            destino_dir_existe = os.path.exists(os.path.dirname(Config.RUTA_DESTINO))
        
        # Probar permisos de escritura
        permisos_ok = False
        try:
            if hasattr(Config, 'RUTA_DESTINO') and Config.RUTA_DESTINO:
                test_file = os.path.join(os.path.dirname(Config.RUTA_DESTINO), '.test_write.tmp')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                permisos_ok = True
        except Exception as e:
            logger.warning(f"Error probando permisos: {e}")
            Config.log_event(f"Error probando permisos: {e}", "WARNING")
        
        # Probar sincronización OneDrive
        try:
            sync_result = Config.forzar_sync_onedrive_agresivo()
        except Exception as e:
            sync_result = False
            logger.warning(f"Error probando sync OneDrive: {e}")
            Config.log_event(f"Error probando sync OneDrive: {e}", "WARNING")
        
        return jsonify({
            'origen_existe': origen_existe,
            'destino_accesible': destino_dir_existe,
            'permisos_escritura': permisos_ok,
            'onedrive_sync': sync_result,
            'estado': 'OK' if all([origen_existe, destino_dir_existe, permisos_ok, sync_result]) else 'WARNING',
            'mensaje': 'Sistema OneDrive funcionando correctamente' if all([origen_existe, destino_dir_existe, permisos_ok, sync_result]) else 'Sistema funcional con algunas limitaciones'
        })
        
    except Exception as e:
        logger.error(f"Error test OneDrive: {e}")
        return jsonify({
            'error': str(e),
            'estado': 'ERROR'
        }), 500

@app.errorhandler(404)
def no_encontrado(error):
    return jsonify({
        'error': 'Endpoint no encontrado',
        'mensaje': 'La ruta solicitada no existe'
    }), 404

@app.errorhandler(500)
def error_servidor(error):
    logger.error(f"Error 500: {str(error)}")
    Config.log_event(f"Error 500: {str(error)}", "ERROR")
    return jsonify({
        'error': 'Error interno del servidor',
        'mensaje': 'Ocurrió un error inesperado'
    }), 500

def verificar_estructura():
    """Verifica que la estructura del proyecto sea correcta"""
    template_dir = app.template_folder
    static_dir = app.static_folder
    
    errores = []
    
    if not os.path.exists(template_dir):
        errores.append(f"No se encuentra la carpeta de templates: {template_dir}")
    
    if not os.path.exists(static_dir):
        errores.append(f"No se encuentra la carpeta static: {static_dir}")
    
    index_file = os.path.join(template_dir, 'index.html')
    if not os.path.exists(index_file):
        errores.append(f"No se encuentra index.html en: {index_file}")
    
    return errores

def inicializar_sistema():
    """Inicialización del sistema al arrancar"""
    Config.log_event("=== INICIANDO SERVIDOR FLASK ===")
    logger.info("Iniciando sistema Flask REENVIOCATALOG")
    
    # Verificar estructura
    errores = verificar_estructura()
    
    if errores:
        logger.warning("Problemas de estructura encontrados:")
        for error in errores:
            logger.warning(f"  - {error}")
        print("ADVERTENCIA: Problemas de estructura:")
        for error in errores:
            print(f"   * {error}")
        print("SOLUCION: Verifica que las carpetas frontend/templates y frontend/static existen")
        
        # No fallar completamente, permitir que Flask arranque para mostrar errores
        return True
    
    logger.info(f"Templates encontrados en: {app.template_folder}")
    logger.info(f"Static encontrado en: {app.static_folder}")
    
    # Validar configuración inicial
    try:
        errores_config = Config.validar_rutas()
        if errores_config:
            Config.log_event(f"Advertencias de configuración: {errores_config}", "WARNING")
            logger.warning(f"Advertencias de configuración: {errores_config}")
    except Exception as e:
        logger.warning(f"No se pudo validar configuración: {e}")
    
    # Crear archivo de log si no existe
    log_file_path = os.path.join(app_dir, Config.LOG_FILE)
    if not os.path.exists(log_file_path):
        Config.log_event("Sistema inicializado correctamente")
    
    return True

def run_app():
    """Función para ejecutar la aplicación Flask"""
    try:
        if not inicializar_sistema():
            logger.error("Error en la inicialización")
            return False
        
        host = getattr(Config, 'FLASK_HOST', '127.0.0.1')
        port = getattr(Config, 'FLASK_PORT', 5000)
        debug = getattr(Config, 'DEBUG_MODE', False)
        
        logger.info(f"Iniciando servidor en http://{host}:{port}")
        print("=" * 50)
        print("REENVIOCATALOG FLASK SERVER")
        print("=" * 50)
        print(f">> Iniciando servidor en http://{host}:{port}")
        print(">> Monitoreando:")
        print(f"   - Origen: {getattr(Config, 'RUTA_ORIGEN', 'No configurado')}")
        print(f"   - Destino: {getattr(Config, 'RUTA_DESTINO', 'No configurado')}")
        print(">> Configuracion:")
        print(f"   - Verificacion cada: {getattr(Config, 'INTERVALO_VERIFICACION', 5)} segundos")
        print(f"   - Sincronizacion forzada cada: {getattr(Config, 'INTERVALO_FORZADO', 300)} segundos")
        print("\n>> Presiona Ctrl+C para detener")
        print("=" * 50)
        
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=False  # Evitar problemas con múltiples inicios
        )
        
        return True
        
    except KeyboardInterrupt:
        print("\n>> Deteniendo servidor...")
        if monitor_global:
            monitor_global.detener()
        print(">> Servidor detenido correctamente")
        return True
    except Exception as e:
        logger.error(f"Error crítico en servidor: {e}")
        Config.log_event(f"Error crítico en servidor: {e}", "ERROR")
        print(f"ERROR CRITICO: {e}")
        if monitor_global:
            monitor_global.detener()
        return False

if __name__ == '__main__':
    run_app()