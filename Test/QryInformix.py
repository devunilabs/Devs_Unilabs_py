import pyodbc
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def ejecutar_consulta():
    try:
        # Establecer conexión usando el DSN
        conn = pyodbc.connect("DSN=BSD_py;UID=informix;PWD=unipadm")
        cursor = conn.cursor()
        
        # Consulta SQL
        query = """
        SELECT 
            a.codigo as codigo_Tarifa,
            b.descripcion as Cliente_RAZ_COMERCIAL,
            b.cif as RUC,
            a.prueba,
            c.descripcion AS Descripcion_de_la_Prueba,
            a.precio,
            ROUND(a.precio*1.18, 2) AS PRECIO_CON_IGV,
            c.baja,
            c.alta,
            c.codexterno,
            c.quien 
        FROM 
            tarifas a 
        INNER JOIN 
            clientes b ON a.codigo = b.tarifa
        INNER JOIN 
            pruebas c ON a.prueba = c.codigo
        WHERE 
            b.codigo='REF_2034' 
            AND c.baja='3000-01-01 00:00:00'
        """
        
        cursor.execute(query)
        
        # Limpiar tabla existente
        for row in tabla.get_children():
            tabla.delete(row)
            
        # Insertar nuevos datos
        for row in cursor.fetchall():
            # Convertir todos los valores a string para mostrar correctamente
            valores = [str(item) if item is not None else "" for item in row]
            tabla.insert("", "end", values=valores)
            
        messagebox.showinfo("Éxito", "Consulta ejecutada correctamente")
        
    except pyodbc.Error as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado:\n{str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

# Crear ventana principal
root = tk.Tk()
root.title("Consulta de Tarifas")
root.geometry("1200x600")

# Frame para la tabla con scrollbars
frame_tabla = ttk.Frame(root)
frame_tabla.pack(expand=True, fill="both", padx=10, pady=10)

# Scrollbars
scroll_y = ttk.Scrollbar(frame_tabla)
scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal")

# Configurar tabla (Treeview)
columnas = [
    "codigo_Tarifa", 
    "Cliente_RAZ_COMERCIAL", 
    "RUC", 
    "prueba", 
    "Descripcion_de_la_Prueba",
    "precio", 
    "PRECIO_CON_IGV", 
    "baja", 
    "alta", 
    "codexterno", 
    "quien"
]

tabla = ttk.Treeview(
    frame_tabla,
    columns=columnas,
    show="headings",
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)

# Configurar scrollbars
scroll_y.config(command=tabla.yview)
scroll_x.config(command=tabla.xview)

# Configurar columnas
for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=100, anchor="center")

# Posicionar elementos
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
tabla.pack(expand=True, fill="both")

# Frame para botones
frame_botones = ttk.Frame(root)
frame_botones.pack(pady=10)

# Botón para ejecutar consulta
btn_ejecutar = ttk.Button(
    frame_botones,
    text="Ejecutar Consulta",
    command=ejecutar_consulta
)
btn_ejecutar.pack(side="left", padx=5)

# Botón para salir
btn_salir = ttk.Button(
    frame_botones,
    text="Salir",
    command=root.quit
)
btn_salir.pack(side="left", padx=5)

root.mainloop()