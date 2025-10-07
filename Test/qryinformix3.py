import pyodbc
import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class TarifasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Carga Masiva de Tarifas")
        self.root.geometry("800x600")
        
        # Variables
        self.archivo_csv = tk.StringVar()
        self.stats = {
            'total': tk.IntVar(value=0),
            'inserts': tk.IntVar(value=0),
            'updates': tk.IntVar(value=0),
            'errores': tk.IntVar(value=0)
        }
        
        # Crear interfaz
        self.crear_interfaz()
        
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sección de selección de archivo
        file_frame = ttk.LabelFrame(main_frame, text="1. Seleccionar archivo CSV", padding=10)
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="Archivo CSV:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(file_frame, textvariable=self.archivo_csv, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Examinar...", command=self.seleccionar_archivo).grid(row=0, column=2)
        
        # Requisitos del archivo
        req_frame = ttk.Frame(file_frame)
        req_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(req_frame, text="El archivo debe contener las columnas:").pack(anchor=tk.W)
        ttk.Label(req_frame, text="- codigo (Código de cliente)", foreground="blue").pack(anchor=tk.W)
        ttk.Label(req_frame, text="- prueba (Nombre de la prueba)", foreground="blue").pack(anchor=tk.W)
        ttk.Label(req_frame, text="- precio (Precio de la prueba)", foreground="blue").pack(anchor=tk.W)
        
        # Sección de procesamiento
        process_frame = ttk.LabelFrame(main_frame, text="2. Procesar archivo", padding=10)
        process_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(process_frame, text="Cargar Tarifas", command=self.procesar_archivo, 
                  style="Accent.TButton").pack(pady=10)
        
        # Sección de resultados
        results_frame = ttk.LabelFrame(main_frame, text="3. Resultados", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview para mostrar resultados
        self.tree = ttk.Treeview(results_frame, columns=('estado', 'codigo', 'prueba', 'precio', 'mensaje'), 
                               show='headings', height=15)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configurar columnas
        self.tree.heading('estado', text='Estado')
        self.tree.heading('codigo', text='Código')
        self.tree.heading('prueba', text='Prueba')
        self.tree.heading('precio', text='Precio')
        self.tree.heading('mensaje', text='Mensaje')
        
        self.tree.column('estado', width=50, anchor=tk.CENTER)
        self.tree.column('codigo', width=100, anchor=tk.CENTER)
        self.tree.column('prueba', width=250)
        self.tree.column('precio', width=80, anchor=tk.CENTER)
        self.tree.column('mensaje', width=250)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Estadísticas
        stats_frame = ttk.Frame(results_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(stats_frame, text="Total registros:").grid(row=0, column=0, padx=5)
        ttk.Label(stats_frame, textvariable=self.stats['total']).grid(row=0, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(stats_frame, text="INSERTs:").grid(row=0, column=2, padx=5)
        ttk.Label(stats_frame, textvariable=self.stats['inserts'], foreground="green").grid(row=0, column=3, padx=5, sticky=tk.W)
        
        ttk.Label(stats_frame, text="UPDATEs:").grid(row=0, column=4, padx=5)
        ttk.Label(stats_frame, textvariable=self.stats['updates'], foreground="blue").grid(row=0, column=5, padx=5, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Errores:").grid(row=0, column=6, padx=5)
        ttk.Label(stats_frame, textvariable=self.stats['errores'], foreground="red").grid(row=0, column=7, padx=5, sticky=tk.W)
        
        # Botón de salir
        ttk.Button(main_frame, text="Salir", command=self.root.quit).pack(side=tk.RIGHT, pady=10)
        
        # Estilo
        self.root.style = ttk.Style()
        self.root.style.configure("Accent.TButton", foreground='white', background='#4CAF50')
    
    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de tarifas",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
            initialdir=os.getcwd()
        )
        if archivo:
            self.archivo_csv.set(archivo)
            self.limpiar_resultados()
    
    def limpiar_resultados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for stat in self.stats.values():
            stat.set(0)
    
    def validar_formato_csv(self, archivo_csv):
        try:
            with open(archivo_csv, mode='r', encoding='utf-8') as file:
                lector = csv.DictReader(file)
                if not all(col in lector.fieldnames for col in ['codigo', 'prueba', 'precio']):
                    raise ValueError("El archivo CSV debe contener las columnas: codigo, prueba, precio")
        except Exception as e:
            raise ValueError(f"Error validando el archivo CSV: {str(e)}")
    
    def procesar_archivo(self):
        if not self.archivo_csv.get():
            messagebox.showerror("Error", "Por favor seleccione un archivo CSV")
            return
            
        try:
            self.limpiar_resultados()
            archivo = self.archivo_csv.get()
            
            # Validar el archivo primero
            self.validar_formato_csv(archivo)
            
            # Conexión a la base de datos
            conn = pyodbc.connect("DSN=BSD_py;UID=informix;PWD=unipadm")
            cursor = conn.cursor()
            
            # Procesar archivo CSV
            with open(archivo, mode='r', encoding='utf-8') as csvfile:
                lector = csv.DictReader(csvfile)
                
                for fila in lector:
                    self.stats['total'].set(self.stats['total'].get() + 1)
                    
                    try:
                        codigo = fila['codigo'].strip()
                        prueba = fila['prueba'].strip()
                        precio = float(fila['precio'])
                        usuario = 'WQUISPE'
                        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Verificar si existe el registro
                        cursor.execute(
                            "SELECT 1 FROM TARIFAS WHERE codigo = ? AND prueba = ?", 
                            (codigo, prueba)
                        )
                        existe = cursor.fetchone()
                        
                        if existe:
                            # Actualización
                            cursor.execute(
                                "UPDATE TARIFAS SET precio = ?, quien = ?, cuando = ? "
                                "WHERE codigo = ? AND prueba = ?",
                                (precio, usuario, fecha_actual, codigo, prueba))
                            self.stats['updates'].set(self.stats['updates'].get() + 1)
                            estado = "UPDATE"
                            color = "blue"
                        else:
                            # Inserción
                            cursor.execute(
                                "INSERT INTO TARIFAS (codigo, prueba, precio, "
                                "codcli, descli, quien, cuando, modo, tipo) "
                                "VALUES (?, ?, ?, '', '', ?, ?, '-', '')",
                                (codigo, prueba, precio, usuario, fecha_actual))
                            self.stats['inserts'].set(self.stats['inserts'].get() + 1)
                            estado = "INSERT"
                            color = "green"
                        
                        conn.commit()
                        self.tree.insert('', tk.END, values=(estado, codigo, prueba, f"{precio:.2f}", "OK"), tags=(color,))
                        
                    except Exception as e:
                        self.stats['errores'].set(self.stats['errores'].get() + 1)
                        conn.rollback()
                        self.tree.insert('', tk.END, values=("ERROR", codigo, prueba, f"{precio:.2f}", str(e)), tags=("red",))
            
            # Configurar colores
            self.tree.tag_configure('green', foreground='green')
            self.tree.tag_configure('blue', foreground='blue')
            self.tree.tag_configure('red', foreground='red')
            
            messagebox.showinfo("Proceso completado", 
                              f"Archivo procesado con éxito!\n\n"
                              f"Total registros: {self.stats['total'].get()}\n"
                              f"INSERTs: {self.stats['inserts'].get()}\n"
                              f"UPDATEs: {self.stats['updates'].get()}\n"
                              f"Errores: {self.stats['errores'].get()}")
            
        except pyodbc.Error as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = TarifasApp(root)
    root.mainloop()