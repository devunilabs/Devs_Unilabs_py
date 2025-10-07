##SEGUIR REVISANDO#

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

    def get_django_sessions(self, date_from=None, search_term=""):
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
                us.created >= %s
            ORDER BY 
                us.created DESC;
        """
        if not date_from:
            date_from = datetime.now().date()

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (date_from,))
                cols = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=cols)
                if search_term:
                    search_term = search_term.lower()
                    mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(search_term).any(), axis=1)
                    df = df[mask]
                return df
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener sesiones Django:\n{str(e)}")
            return pd.DataFrame()

    def get_pg_sessions(self, state_filter="active", search_term=""):
        query = """
            SELECT 
                pid,
                usename AS username,
                datname AS database,
                state,
                NOW() - backend_start AS connection_duration,
                query
            FROM 
                pg_stat_activity
            WHERE 
                datname = current_database()
                AND usename != 'postgres'
        """
        if state_filter != "all":
            query += f" AND state = %s"
        query += " ORDER BY connection_duration DESC;"

        try:
            with self.connection.cursor() as cursor:
                if state_filter != "all":
                    cursor.execute(query, (state_filter,))
                else:
                    cursor.execute(query)
                cols = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=cols)
                if search_term:
                    search_term = search_term.lower()
                    mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(search_term).any(), axis=1)
                    df = df[mask]
                return df
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener sesiones PostgreSQL:\n{str(e)}")
            return pd.DataFrame()

    def terminate_pg_session(self, pid, username):
        confirm = messagebox.askyesno("Confirmar", f"¿Deseas finalizar la sesión de PostgreSQL del usuario '{username}'?")
        if not confirm:
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT pg_terminate_backend(%s);", (pid,))
                self.connection.commit()
                messagebox.showinfo("Éxito", f"Sesión de '{username}' finalizada.")
                self.update_pg_sessions()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo terminar la sesión:\n{str(e)}")

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Monitor de Sesiones Django y PostgreSQL")
        self.root.geometry("1200x700")

        tabControl = ttk.Notebook(self.root)

        # Pestaña Sesiones Django
        tab_django = ttk.Frame(tabControl)
        tabControl.add(tab_django, text='Sesiones Django')

        # Filtros Django
        filter_frame_django = ttk.Frame(tab_django)
        filter_frame_django.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame_django, text="Fecha desde (YYYY-MM-DD):").pack(side=tk.LEFT)
        self.django_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.django_date_entry = ttk.Entry(filter_frame_django, width=12, textvariable=self.django_date_var)
        self.django_date_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame_django, text="Buscar:").pack(side=tk.LEFT, padx=(15, 0))
        self.django_search_var = tk.StringVar()
        self.django_search_entry = ttk.Entry(filter_frame_django, width=20, textvariable=self.django_search_var)
        self.django_search_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(filter_frame_django, text="Buscar / Actualizar", command=self.update_django_sessions).pack(side=tk.LEFT, padx=10)

        self.tree_django = ttk.Treeview(tab_django, columns=("session_id", "user_id", "username", "email", "created"), show="headings")
        for col in self.tree_django["columns"]:
            self.tree_django.heading(col, text=col.replace("_", " ").title())
            self.tree_django.column(col, width=150, anchor='center')
        self.tree_django.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Pestaña Sesiones PostgreSQL
        tab_pg = ttk.Frame(tabControl)
        tabControl.add(tab_pg, text='Sesiones PostgreSQL')

        # Filtros PostgreSQL
        filter_frame_pg = ttk.Frame(tab_pg)
        filter_frame_pg.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame_pg, text="Estado:").pack(side=tk.LEFT)
        self.pg_state_var = tk.StringVar(value="active")
        self.pg_state_combo = ttk.Combobox(filter_frame_pg, textvariable=self.pg_state_var, values=["active", "idle", "all"], width=8)
        self.pg_state_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame_pg, text="Buscar:").pack(side=tk.LEFT, padx=(15, 0))
        self.pg_search_var = tk.StringVar()
        self.pg_search_entry = ttk.Entry(filter_frame_pg, width=20, textvariable=self.pg_search_var)
        self.pg_search_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(filter_frame_pg, text="Buscar / Actualizar", command=self.update_pg_sessions).pack(side=tk.LEFT, padx=10)

        self.tree_pg = ttk.Treeview(tab_pg, columns=("pid", "username", "database", "state", "connection_duration", "query"), show="headings")
        for col in self.tree_pg["columns"]:
            self.tree_pg.heading(col, text=col.replace("_", " ").title())
            self.tree_pg.column(col, width=150 if col != "query" else 500, anchor='center')
        self.tree_pg.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Button(tab_pg, text="🧹 Terminar sesión seleccionada", command=self.terminate_selected_pg_session).pack(pady=5)

        tabControl.pack(expand=1, fill="both")

        # Inicializar con datos
        self.update_django_sessions()
        self.update_pg_sessions()

        self.root.mainloop()

    def update_django_sessions(self):
        try:
            date_from = datetime.strptime(self.django_date_var.get(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido para sesiones Django. Use YYYY-MM-DD.")
            return
        search_term = self.django_search_var.get()
        df = self.get_django_sessions(date_from=date_from, search_term=search_term)
        for row in self.tree_django.get_children():
            self.tree_django.delete(row)
        for _, row in df.iterrows():
            self.tree_django.insert("", "end", values=(
                row["session_id"],
                row["user_id"],
                row["username"],
                row["email"],
                row["created"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(row["created"], datetime) else row["created"]
            ))

    def update_pg_sessions(self):
        state_filter = self.pg_state_var.get()
        search_term = self.pg_search_var.get()
        df = self.get_pg_sessions(state_filter=state_filter, search_term=search_term)
        for row in self.tree_pg.get_children():
            self.tree_pg.delete(row)
        for _, row in df.iterrows():
            self.tree_pg.insert("", "end", values=(
                row["pid"],
                row["username"],
                row["database"],
                row["state"],
                str(row["connection_duration"]),
                row["query"][:100]
            ))

    def terminate_selected_pg_session(self):
        selected = self.tree_pg.selection()
        if not selected:
            messagebox.showinfo("Información", "Selecciona una sesión de PostgreSQL para terminar.")
            return
        item = self.tree_pg.item(selected[0])
        pid = item["values"][0]
        username = item["values"][1]
        self.terminate_pg_session(pid, username)

if __name__ == "__main__":
    db_config = {
        'dbname': 'production_unilabs',
        'user': 'unilabs',
        'password': 'SEEK@2022#pe',
        'host': '172.16.1.34',
        'port': '5432'
    }

    app = DjangoSessionMonitor(db_config)
