import psycopg2 
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime, date

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
        WHERE 
            us.created >= CURRENT_DATE
        ORDER BY 
            us.created DESC;
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

        oldest = df.iloc[-1]  # La más antigua está al final
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
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(
                row["session_id"],
                row["user_id"],
                row["username"],
                row["email"],
                row["created"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(row["created"], datetime) else row["created"]
            ))

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("🔐 Monitor de Sesiones Django")
        self.root.geometry("900x500")
        self.root.configure(bg='#f4f6f9')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#f4f6f9")
        style.configure("TLabel", background="#f4f6f9", font=('Segoe UI', 10))
        style.configure("TButton", font=('Segoe UI', 10))
        style.configure("Treeview", font=('Segoe UI', 9))
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))

        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Button(top_frame, text="🔄 Actualizar", command=self.update_data).pack(side=tk.LEFT, padx=10)
        ttk.Button(top_frame, text="🧹 Terminar sesión más antigua", command=self.terminate_oldest_session).pack(side=tk.LEFT, padx=10)

        columns = ("session_id", "user_id", "username", "email", "created")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("session_id", text="ID Sesión")
        self.tree.heading("user_id", text="ID Usuario")
        self.tree.heading("username", text="Usuario")
        self.tree.heading("email", text="Email")
        self.tree.heading("created", text="Fecha y Hora de Conexión")

        for col in columns:
            self.tree.column(col, anchor="center", width=150)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

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
