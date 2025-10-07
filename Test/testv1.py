import psycopg2 
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime

class DjangoSessionMonitor:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None

        if self.connect_db():
            self.setup_ui()
        else:
            messagebox.showerror("Error", "No se pudo iniciar la aplicación por fallo en la conexión.")

    def connect_db(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
            return True
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos:\n{str(e)}")
            return False

    def get_sessions(self):
        if not self.connection:
            messagebox.showerror("Error", "No hay conexión a la base de datos.")
            return pd.DataFrame()

        query = """
        SELECT 
            us.id AS session_id,
            us.created,
            u.id AS user_id,
            u.username,
            u.email
        FROM 
            users_usersession us
        JOIN 
            users_user u ON us.user_id = u.id
        ORDER BY 
            us.created ASC;
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                return pd.DataFrame(data, columns=columns)
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener sesiones:\n{str(e)}")
            return pd.DataFrame()

    def terminate_oldest_session(self):
        df = self.get_sessions()
        if df.empty:
            messagebox.showinfo("Sin sesiones", "No hay sesiones activas para finalizar.")
            return

        oldest = df.iloc[0]
        session_id = oldest["session_id"]
        username = oldest["username"]
        confirm = messagebox.askyesno("Confirmar", f"¿Deseas terminar la sesión más antigua del usuario '{username}'?")
        if confirm:
            if self.terminate_session(session_id):
                messagebox.showinfo("Éxito", f"Sesión del usuario '{username}' finalizada.")
                self.update_data()
            else:
                messagebox.showerror("Error", f"No se pudo finalizar la sesión del usuario '{username}'.")

    def terminate_session(self, session_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM users_usersession WHERE id = %s", (session_id,))
                self.connection.commit()
                return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo terminar la sesión:\n{str(e)}")
            return False

    def update_data(self):
        df = self.get_sessions()
        if df.empty:
            messagebox.showinfo("Actualización", "No hay sesiones activas para mostrar.")
        else:
            print("Sesiones actuales:")
            print(df.head())

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("🔐 Monitor de Sesiones Django")
        self.root.geometry("800x400")
        self.root.configure(bg='#f4f6f9')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#f4f6f9")
        style.configure("TLabel", background="#f4f6f9", font=('Segoe UI', 10))
        style.configure("TButton", font=('Segoe UI', 10))

        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Button(top_frame, text="🔄 Actualizar", command=self.update_data).pack(side=tk.LEFT, padx=10)
        ttk.Button(top_frame, text="🧹 Terminar sesión más antigua", command=self.terminate_oldest_session).pack(side=tk.LEFT, padx=10)

        self.root.mainloop()

if __name__ == "__main__":
    db_config = {
        'dbname': 'production_unilabs',
        'user': 'unilabs',
        'password': 'SEEK@2022#pe',
        'host': '172.16.1.34',
        'port': '5432'
    }

    app = DjangoSessionMonitor(db_config)













##########################################################3



##########################################################3




#######################################################33



 
