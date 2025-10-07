
from sqlalchemy import create_engine, text  # Importa text de SQLAlchemy
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError

def configurar_conexion():
    """Configura y retorna una conexión a la base de datos"""
    # Parámetros de configuración (modifica estos valores)
    configuracion_db = {
        'drivername': 'postgresql',  # Cambia según tu DB (mysql, oracle, etc)
        'username': 'unilabs',
        'password': 'SEEK@2022#pe',
        'host': '172.16.1.34',
        'database': 'production_unilabs',
        'port': '5432',  # 3306 para MySQL
    }
    
    try:
        # 1. Crear URL de conexión base
        url_conexion = URL.create(**configuracion_db)
        
        # 2. Configurar motor con parámetros adicionales
        motor_db = create_engine(
            url_conexion,
            connect_args={
                'options': '-c client_encoding=utf8'  # Configura encoding aquí
            },
            echo=False  # Cambia a True para ver logs de SQL
        )
        
        return motor_db
        
    except Exception as e:
        raise RuntimeError(f"Error al configurar conexión: {str(e)}")

def probar_conexion():
    """Prueba la conexión a la base de datos"""
    try:
        motor = configurar_conexion()
        
        # Intentar conexión
        with motor.connect() as conexion:
            print("✅ ¡Conexión exitosa a la base de datos!")
            # Ejecutar consulta usando text() para preparar la sentencia SQL
            resultado = conexion.execute(text("SELECT version()"))  # Envuelve en text()
            print(f"Versión del servidor: {resultado.scalar()}")
            
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Error al conectar a la base de datos: {str(e)}")
        return False
    except RuntimeError as e:
        print(f"❌ Error de configuración: {str(e)}")
        return False

# Ejecutar prueba de conexión al ejecutar el script
if __name__ == "__main__":
    probar_conexion()