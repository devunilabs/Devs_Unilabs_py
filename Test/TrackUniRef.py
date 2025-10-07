import sys
import psycopg2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QTableWidget, QTableWidgetItem, QTabWidget, QLabel)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

class PostgreSQLMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PostgreSQL Monitor")
        self.setGeometry(100, 100, 1000, 800)
        
        # Configuración de la conexión a PostgreSQL
        self.connection_params = {
            'host': '172.16.1.34',
            'database': 'production_unilabs',
            'user': 'unilabs',
            'password': 'SEEK@2022#pe',
            'port': '5432'
        }
        
        self.initUI()
        self.load_data()
        
    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        
        # Pestaña de sesiones activas
        self.sessions_tab = QWidget()
        self.sessions_layout = QVBoxLayout()
        
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(6)
        self.sessions_table.setHorizontalHeaderLabels([
            "Usuario", "Dirección IP", "Aplicación", "Estado", "Consulta", "Duración"
        ])
        
        self.sessions_layout.addWidget(QLabel("Sesiones Activas"))
        self.sessions_layout.addWidget(self.sessions_table)
        self.sessions_tab.setLayout(self.sessions_layout)
        
        # Pestaña de consumo de recursos
        self.resources_tab = QWidget()
        self.resources_layout = QVBoxLayout()
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        self.resources_layout.addWidget(QLabel("Consumo de Recursos por Usuario"))
        self.resources_layout.addWidget(self.canvas)
        self.resources_tab.setLayout(self.resources_layout)
        
        self.tab_widget.addTab(self.sessions_tab, "Sesiones")
        self.tab_widget.addTab(self.resources_tab, "Consumo")
        
        self.layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(self.layout)
        
    def load_data(self):
        try:
            conn = psycopg2.connect(**self.connection_params)
            
            # Obtener sesiones activas
            sessions_query = """
            SELECT 
                usename, 
                client_addr::text, 
                application_name, 
                state, 
                query, 
                now() - query_start as duration
            FROM pg_stat_activity 
            WHERE state = 'active' 
            ORDER BY duration DESC;
            """
            
            sessions_df = pd.read_sql(sessions_query, conn)
            self.display_sessions(sessions_df)
            
            # Obtener consumo por usuario
            consumption_query = """
            SELECT 
                usename,
                COUNT(*) as total_connections,
                SUM(CASE WHEN state = 'active' THEN 1 ELSE 0 END) as active_connections,
                SUM(EXTRACT(EPOCH FROM (now() - query_start))) as total_query_time
            FROM pg_stat_activity
            GROUP BY usename
            ORDER BY total_query_time DESC;
            """
            
            consumption_df = pd.read_sql(consumption_query, conn)
            self.plot_consumption(consumption_df)
            
            conn.close()
            
        except Exception as e:
            print(f"Error: {e}")
    
    def display_sessions(self, df):
        self.sessions_table.setRowCount(len(df))
        
        for row in range(len(df)):
            for col in range(6):
                self.sessions_table.setItem(row, col, QTableWidgetItem(str(df.iat[row, col])))
    
    def plot_consumption(self, df):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not df.empty:
            df.plot(kind='bar', x='usename', y='total_query_time', ax=ax, legend=False)
            ax.set_ylabel('Tiempo Total de Consulta (segundos)')
            ax.set_title('Consumo de Recursos por Usuario')
            ax.tick_params(axis='x', rotation=45)
        
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PostgreSQLMonitor()
    window.show()
    sys.exit(app.exec_())