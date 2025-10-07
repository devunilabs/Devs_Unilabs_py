# backend/watcher.py - VERSIÓN SIMPLIFICADA QUE USA SISTEMA CORREGIDO
import os
import sys
import time
from config import Config

def main():
    """Función principal simplificada"""
    try:
        print("INICIANDO SISTEMA CORREGIDO")
        print("=" * 50)
        
        # Importar sistema corregido
        from fixed_sync_system import get_fixed_system
        
        system = get_fixed_system()
        
        if system.start():
            print("Sistema corregido iniciado correctamente")
            print("Características:")
            print("  - Sin archivos backup")
            print("  - Verificación inteligente")
            print("  - Sin costos de API")
            print("  - Compatible con OneDrive")
            print("Presiona Ctrl+C para detener")
            print("=" * 50)
            
            # Loop principal
            while True:
                time.sleep(1)
        else:
            print("Error al iniciar el sistema")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{'='*50}")
        print("Deteniendo sistema...")
        if 'system' in locals():
            system.stop()
        print("Sistema detenido correctamente")
        print("=" * 50)
    except Exception as e:
        Config.log_event(f"Error crítico: {e}", "ERROR")
        print(f"Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()