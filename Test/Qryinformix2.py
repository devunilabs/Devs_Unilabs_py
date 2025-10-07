import pyodbc
import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import logging

class TarifasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Carga Masiva de Tarifas - Informix")
        self.root.geometry("1200x800")
        
        # Configurar logging
        logging.basicConfig(
            filename='tarifas_app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Variables
        self.archivo_csv = tk.StringVar()
        self.stats = {
            'total': tk.IntVar(value=0),
            'inserts': tk.IntVar(value=0),
            'updates': tk.IntVar(value=0),
            'errores': tk.IntVar(value=0),
            'clientes_procesados': tk.IntVar(value=0)
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
        ttk.Entry(file_frame, textvariable=self.archivo_csv, width=70).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Examinar...", command=self.seleccionar_archivo).grid(row=0, column=2)
        
        # Requisitos del archivo
        req_frame = ttk.Frame(file_frame)
        req_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(req_frame, text="El archivo debe contener las columnas:").pack(anchor=tk.W)
        ttk.Label(req_frame, text="- codigo (Código de tarifa, ej: T_2_2_009)", foreground="blue").pack(anchor=tk.W)
        ttk.Label(req_frame, text="- prueba (Nombre de la prueba, ej: OH17_KETO)", foreground="blue").pack(anchor=tk.W)
        ttk.Label(req_frame, text="- precio (Precio de la prueba, formatos: 1500.50 o 1,500.50)", foreground="blue").pack(anchor=tk.W)
        
        # Sección de procesamiento
        process_frame = ttk.LabelFrame(main_frame, text="2. Procesar archivo", padding=10)
        process_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(process_frame, text="Cargar Tarifas", command=self.procesar_archivo, 
                  style="Accent.TButton").pack(pady=10)
        
        # Sección de verificación en BD
        verify_frame = ttk.LabelFrame(main_frame, text="3. Verificar en Base de Datos (Informix)", padding=10)
        verify_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(verify_frame, text="Verificar Registro", command=self.verificar_registro).pack(side=tk.LEFT, padx=5)
        self.codigo_verify = ttk.Entry(verify_frame, width=20)
        self.codigo_verify.pack(side=tk.LEFT, padx=5)
        ttk.Label(verify_frame, text="Código:").pack(side=tk.LEFT)
        
        self.prueba_verify = ttk.Entry(verify_frame, width=40)
        self.prueba_verify.pack(side=tk.LEFT, padx=5)
        ttk.Label(verify_frame, text="Prueba:").pack(side=tk.LEFT)
        
        # Sección de resultados
        results_frame = ttk.LabelFrame(main_frame, text="4. Resultados", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview para mostrar resultados
        self.tree = ttk.Treeview(results_frame, 
                               columns=('estado', 'codigo', 'prueba', 'precio_csv', 'precio_bd', 'mensaje'), 
                               show='headings', height=20)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configurar columnas
        columns = {
            'estado': {'text': 'Estado', 'width': 80, 'anchor': tk.CENTER},
            'codigo': {'text': 'Código', 'width': 150, 'anchor': tk.CENTER},
            'prueba': {'text': 'Prueba', 'width': 250},
            'precio_csv': {'text': 'Precio CSV', 'width': 100, 'anchor': tk.CENTER},
            'precio_bd': {'text': 'Precio BD', 'width': 100, 'anchor': tk.CENTER},
            'mensaje': {'text': 'Mensaje', 'width': 400}
        }
        
        for col, config in columns.items():
            self.tree.heading(col, text=config['text'])
            self.tree.column(col, width=config['width'], anchor=config.get('anchor', tk.W))
        
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
        self.root.style.configure("green.TLabel", foreground='green')
        self.root.style.configure("blue.TLabel", foreground='blue')
        self.root.style.configure("red.TLabel", foreground='red')
        
        # Configurar colores para el Treeview
        self.tree.tag_configure('green', foreground='green')
        self.tree.tag_configure('blue', foreground='blue')
        self.tree.tag_configure('red', foreground='red')
        self.tree.tag_configure('gray', foreground='gray')
    
    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de tarifas",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
            initialdir=os.getcwd()
        )
        if archivo:
            self.archivo_csv.set(archivo)
            self.limpiar_resultados()
            logging.info(f"Archivo seleccionado: {archivo}")
    
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
            logging.error(f"Error validando archivo CSV: {str(e)}")
            raise ValueError(f"Error validando el archivo CSV: {str(e)}")
    
    def parse_precio(self, precio_str):
        """Convierte diferentes formatos de precios a float para Informix"""
        try:
            # Eliminar espacios y caracteres no numéricos excepto puntos y comas
            precio_str = re.sub(r'[^\d.,]', '', precio_str.strip())
            
            # Caso 1: Formato "1.400,02" (europeo)
            if '.' in precio_str and ',' in precio_str and precio_str.index('.') < precio_str.index(','):
                return float(precio_str.replace('.', '').replace(',', '.'))
            
            # Caso 2: Formato "1,400.02" (inglés)
            if ',' in precio_str and '.' in precio_str and precio_str.index(',') < precio_str.index('.'):
                return float(precio_str.replace(',', ''))
            
            # Caso 3: Formato "1400.02" o "1400,02"
            return float(precio_str.replace(',', '.'))
            
        except ValueError as e:
            logging.error(f"Error parseando precio {precio_str}: {str(e)}")
            raise ValueError(f"Formato de precio inválido: {precio_str}")

    def verificar_registro(self):
        codigo = self.codigo_verify.get().strip()
        prueba = self.prueba_verify.get().strip()
        
        if not codigo or not prueba:
            messagebox.showwarning("Advertencia", "Debe ingresar código y prueba para verificar")
            return
            
        try:
            conn = self.obtener_conexion()
            cursor = conn.cursor()
            
            # Consulta para obtener el registro y el tarifario asociado
            cursor.execute(
                """SELECT FIRST 1 t.codigo, t.prueba, t.precio, t.quien, t.cuando, 
                          (SELECT descripcion FROM TARIFARIOS tr WHERE t.codigo LIKE tr.codigo||'%' 
                           ORDER BY LENGTH(tr.codigo) DESC) as tarifario
                   FROM TARIFAS t
                   WHERE t.codigo = ? AND t.prueba = ?""",
                (codigo, prueba))
            
            resultado = cursor.fetchone()
            
            if resultado:
                message = (f"Registro encontrado en Informix:\n\n"
                          f"Código: {resultado.codigo}\n"
                          f"Prueba: {resultado.prueba}\n"
                          f"Precio: {float(resultado.precio):.2f}\n"
                          f"Tarifario: {resultado.tarifario or 'No identificado'}\n"
                          f"Usuario: {resultado.quien}\n"
                          f"Fecha: {resultado.cuando}")
                messagebox.showinfo("Resultado de verificación", message)
                logging.info(f"Verificación exitosa: {codigo} - {prueba}")
            else:
                # Intentar identificar el tarifario aunque no exista el registro
                cursor.execute(
                    """SELECT FIRST 1 descripcion 
                       FROM TARIFARIOS 
                       WHERE ? LIKE codigo||'%' 
                       ORDER BY LENGTH(codigo) DESC""",
                    (codigo,))
                tarifario = cursor.fetchone()
                
                messagebox.showinfo("Resultado de verificación", 
                                  f"No se encontró registro en Informix para:\n"
                                  f"Código: {codigo}\nPrueba: {prueba}\n"
                                  f"Tarifario probable: {tarifario[0] if tarifario else 'No identificado'}")
                logging.info(f"Registro no encontrado: {codigo} - {prueba}")
                
        except pyodbc.Error as e:
            error_msg = f"No se pudo verificar el registro:\n{str(e)}"
            messagebox.showerror("Error de base de datos", error_msg)
            logging.error(f"Error verificando registro {codigo} - {prueba}: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def obtener_conexion(self):
        """Obtiene una conexión a la base de datos Informix"""
        try:
            conn = pyodbc.connect(
                "DSN=BSD_py;UID=informix;PWD=unipadm",
                autocommit=False  # Desactivamos autocommit para manejar transacciones manualmente
            )
            logging.info("Conexión a Informix establecida correctamente")
            return conn
        except pyodbc.Error as e:
            logging.error(f"Error conectando a Informix: {str(e)}")
            raise

    def procesar_archivo(self):
        if not self.archivo_csv.get():
            messagebox.showerror("Error", "Por favor seleccione un archivo CSV")
            return
            
        try:
            self.limpiar_resultados()
            archivo = self.archivo_csv.get()
            logging.info(f"Iniciando procesamiento de archivo: {archivo}")
            
            # Validar el archivo primero
            self.validar_formato_csv(archivo)
            
            # Conexión a la base de datos Informix
            conn = self.obtener_conexion()
            cursor = conn.cursor()
            
            # Obtener todos los tarifarios disponibles
            cursor.execute("SELECT codigo, descripcion FROM TARIFARIOS ORDER BY LENGTH(codigo) DESC")
            tarifarios = cursor.fetchall()
            
            # Procesar archivo CSV
            with open(archivo, mode='r', encoding='utf-8') as csvfile:
                lector = csv.DictReader(csvfile)
                
                for fila in lector:
                    self.stats['total'].set(self.stats['total'].get() + 1)
                    
                    try:
                        # Limpieza de datos
                        codigo = fila['codigo'].strip()
                        prueba = fila['prueba'].strip()
                        precio = self.parse_precio(fila['precio'])
                        usuario = 'WQUISPE'
                        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Identificar el tarifario
                        tarifario = "No identificado"
                        for t in tarifarios:
                            if codigo.startswith(t.codigo):
                                tarifario = f"{t.descripcion} ({t.codigo})"
                                break
                        
                        # Verificar si el registro existe
                        cursor.execute(
                            """SELECT FIRST 1 precio FROM TARIFAS 
                               WHERE codigo = ? AND prueba = ?""", 
                            (codigo, prueba))
                        registro_existente = cursor.fetchone()
                        
                        if registro_existente:
                            # Comparación de precios con tolerancia decimal
                            precio_actual = float(registro_existente.precio)
                            if abs(precio - precio_actual) > 0.001:
                                # Actualizar registro existente
                                cursor.execute(
                                    """UPDATE TARIFAS 
                                       SET precio = ?, 
                                           quien = ?, 
                                           cuando = ? 
                                       WHERE codigo = ? AND prueba = ?""",
                                    (precio, usuario, fecha_actual, codigo, prueba))
                                conn.commit()  # Confirmar explícitamente
                                self.stats['updates'].set(self.stats['updates'].get() + 1)
                                estado = "UPDATE"
                                color = "blue"
                                mensaje = f"Actualizado: {precio_actual:.2f} → {precio:.2f} | {tarifario}"
                                bd_precio = f"{precio_actual:.2f}"
                                logging.info(f"UPDATE exitoso: {codigo} - {prueba} - Precio: {precio_actual:.2f} → {precio:.2f}")
                            else:
                                estado = "EXISTE"
                                color = "gray"
                                mensaje = f"Precio sin cambios | {tarifario}"
                                bd_precio = f"{precio_actual:.2f}"
                                logging.info(f"Precio sin cambios: {codigo} - {prueba} - Precio: {precio_actual:.2f}")
                        else:
                            # Inserción de nuevo registro
                            cursor.execute(
                                """INSERT INTO TARIFAS 
                                   (codigo, prueba, precio, codcli, descli, quien, cuando, modo, tipo) 
                                   VALUES (?, ?, ?, '', '', ?, ?, '-', '')""",
                                (codigo, prueba, precio, usuario, fecha_actual))
                            conn.commit()  # Confirmar explícitamente
                            self.stats['inserts'].set(self.stats['inserts'].get() + 1)
                            estado = "INSERT"
                            color = "green"
                            mensaje = f"Nuevo registro | {tarifario}"
                            bd_precio = "N/A"
                            logging.info(f"INSERT exitoso: {codigo} - {prueba} - Precio: {precio:.2f}")
                        
                        # Verificación post-operación para asegurar los cambios
                        cursor.execute(
                            """SELECT FIRST 1 precio FROM TARIFAS 
                               WHERE codigo = ? AND prueba = ?""",
                            (codigo, prueba))
                        registro_verificado = cursor.fetchone()
                        
                        if registro_verificado:
                            nuevo_precio = float(registro_verificado.precio)
                            bd_precio = f"{nuevo_precio:.2f}"
                            if estado == "INSERT":
                                mensaje = f"Confirmado: {bd_precio} | {tarifario}"
                            elif estado == "UPDATE":
                                # Verificar que el cambio realmente se aplicó
                                if abs(nuevo_precio - precio) > 0.001:
                                    estado = "ERROR"
                                    color = "red"
                                    mensaje = f"Error: Cambio no aplicado | {tarifario}"
                                    self.stats['errores'].set(self.stats['errores'].get() + 1)
                                    self.stats['updates'].set(self.stats['updates'].get() - 1)
                                    logging.error(f"Error en UPDATE: Cambio no aplicado para {codigo} - {prueba}")
                        
                        self.tree.insert('', tk.END, 
                                       values=(estado, codigo, prueba, f"{precio:.2f}", 
                                              bd_precio, mensaje), 
                                       tags=(color,))
                        
                    except pyodbc.Error as e:
                        conn.rollback()
                        self.stats['errores'].set(self.stats['errores'].get() + 1)
                        error_msg = str(e).split('\n')[0]
                        self.tree.insert('', tk.END, 
                                       values=("ERROR", codigo, prueba, fila.get('precio', ''), 
                                              "Error BD", f"{error_msg} | {tarifario}"), 
                                       tags=("red",))
                        logging.error(f"Error de BD procesando {codigo} - {prueba}: {error_msg}")
                    except Exception as e:
                        conn.rollback()
                        self.stats['errores'].set(self.stats['errores'].get() + 1)
                        error_msg = str(e).split('\n')[0]
                        self.tree.insert('', tk.END, 
                                       values=("ERROR", codigo, prueba, fila.get('precio', ''), 
                                              "Error", f"{error_msg} | {tarifario}"), 
                                       tags=("red",))
                        logging.error(f"Error procesando {codigo} - {prueba}: {error_msg}")
            
            messagebox.showinfo("Proceso completado", 
                              f"Archivo procesado con éxito!\n\n"
                              f"Total registros: {self.stats['total'].get()}\n"
                              f"INSERTs: {self.stats['inserts'].get()}\n"
                              f"UPDATEs: {self.stats['updates'].get()}\n"
                              f"Errores: {self.stats['errores'].get()}")
            logging.info(f"Proceso completado. Totales: {self.stats['total'].get()} registros, "
                       f"{self.stats['inserts'].get()} INSERTs, {self.stats['updates'].get()} UPDATEs, "
                       f"{self.stats['errores'].get()} errores")
            
        except pyodbc.Error as e:
            error_msg = f"No se pudo conectar a Informix:\n{str(e)}\nVerifique el DSN 'BSD_py' y credenciales"
            messagebox.showerror("Error de conexión", error_msg)
            logging.error(f"Error de conexión a Informix: {str(e)}")
        except Exception as e:
            error_msg = f"Ocurrió un error:\n{str(e)}"
            messagebox.showerror("Error", error_msg)
            logging.error(f"Error general: {str(e)}")
        finally:
            if 'conn' in locals():
                try:
                    conn.close()
                    logging.info("Conexión a Informix cerrada")
                except Exception as e:
                    logging.error(f"Error cerrando conexión: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TarifasApp(root)
    root.mainloop()