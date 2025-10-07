import psycopg2
from tabulate import tabulate
import time
from datetime import datetime

class PostgreSQLMonitor:
    def __init__(self, dbname, user, password, host='172.16.1.34', port='5432'):
        self.connection_params = {
            'dbname': 'production_unilabs',
            'user': 'unilabs',
            'password': 'SEEK@2022#pe',
            'host': '172.16.1.34',
            'port': '5432'
        }
        self.admin_conn = None
    
    def connect(self):
        """Establece conexión como superusuario"""
        try:
            self.admin_conn = psycopg2.connect(**self.connection_params)
            return True
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False
    
    def get_active_sessions(self):
        """Obtiene todas las sesiones activas con su consumo de recursos (versión corregida)"""
        query = """
        SELECT 
            pid AS process_id,
            usename AS username,
            application_name,
            client_addr AS client_ip,
            state,
            query_start,
            query,
            now() - query_start AS duration,
            (SELECT setting FROM pg_settings WHERE name='max_connections') AS max_connections,
            (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') AS active_connections
        FROM 
            pg_stat_activity
        WHERE 
            state = 'active'
        ORDER BY 
            duration DESC;
        """
        
        try:
            with self.admin_conn.cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                return columns, data
        except Exception as e:
            print(f"Error al obtener sesiones: {e}")
            return None, None
    
    def get_resource_consumption(self):
        """Obtiene métricas detalladas de consumo de recursos (versión corregida)"""
        query = """
        SELECT 
            pid,
            usename,
            datname,
            query,
            now() - query_start AS duration,
            (SELECT setting FROM pg_settings WHERE name='max_connections') AS max_connections,
            (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') AS active_connections,
            (SELECT setting FROM pg_settings WHERE name='work_mem') AS work_mem,
            (SELECT setting FROM pg_settings WHERE name='shared_buffers') AS shared_buffers
        FROM 
            pg_stat_activity
        WHERE 
            state = 'active'
        ORDER BY 
            duration DESC;
        """
        
        try:
            with self.admin_conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener consumo: {e}")
            return None
    
    def terminate_session(self, pid):
        """Termina una sesión específica"""
        try:
            with self.admin_conn.cursor() as cursor:
                cursor.execute(f"SELECT pg_terminate_backend({pid});")
                self.admin_conn.commit()
                return True
        except Exception as e:
            print(f"Error al terminar sesión {pid}: {e}")
            return False
    
    def display_dashboard(self, refresh_interval=5):
        """Interfaz de monitoreo en tiempo real"""
        try:
            while True:
                # Limpiar pantalla
                print("\033c", end="")
                
                # Obtener y mostrar sesiones
                columns, sessions = self.get_active_sessions()
                if sessions:
                    print(f"\n{' MONITOR DE CONEXIONES POSTGRESQL ':=^80}")
                    print(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Total de conexiones activas: {len(sessions)}\n")
                    
                    # Mostrar tabla formateada
                    print(tabulate(
                        sessions, 
                        headers=columns, 
                        tablefmt='grid',
                        maxcolwidths=20,
                        showindex=True
                    ))
                    
                    # Mostrar resumen de recursos
                    resource_data = self.get_resource_consumption()
                    if resource_data and len(resource_data) > 0:
                        print(f"\n{' RESUMEN DE RECURSOS ':=^80}")
                        print(f"Conexiones activas/máximas: {resource_data[0][6]}/{resource_data[0][5]}")
                        print(f"Work memory: {resource_data[0][7]}")
                        print(f"Shared buffers: {resource_data[0][8]}")
                
                # Menú de opciones
                print("\nOpciones:")
                print("1. Terminar una sesión")
                print("2. Actualizar datos")
                print("3. Salir")
                
                choice = input("\nSeleccione una opción (1-3): ")
                
                if choice == "1":
                    pid = input("Ingrese el PID de la sesión a terminar: ")
                    if pid.isdigit():
                        if self.terminate_session(int(pid)):
                            print(f"Sesión {pid} terminada exitosamente!")
                            time.sleep(2)
                elif choice == "2":
                    continue
                elif choice == "3":
                    break
                else:
                    print("Opción no válida")
                    time.sleep(1)
                
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\nMonitor detenido por el usuario")
        finally:
            if self.admin_conn:
                self.admin_conn.close()

if __name__ == "__main__":
    # Configuración (cambiar por tus credenciales reales)
    monitor = PostgreSQLMonitor(
        dbname='tu_basedatos',
        user='tu_usuario',
        password='tu_contraseña',
        host='localhost'
    )
    
    if monitor.connect():
        monitor.display_dashboard()
    else:
        print("No se pudo conectar a la base de datos")