import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox

def ejecutar_consulta():
    codigo_cliente = entry_codigo.get().strip()
    
    if not codigo_cliente:
        messagebox.showwarning("Advertencia", "Por favor ingrese un código de cliente")
        return
    
    try:
        conn = pyodbc.connect("DSN=BSD_py;UID=informix;PWD=unipadm")
        cursor = conn.cursor()
        
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
            b.codigo = ?
            AND c.baja = '3000-01-01 00:00:00'
        """
        
        cursor.execute(query, codigo_cliente)
        
        # Limpiar tabla existente
        for row in tabla.get_children():
            tabla.delete(row)
            
        # Insertar nuevos datos
        resultados = cursor.fetchall()
        if not resultados:
            messagebox.showinfo("Información", "No se encontraron resultados para el código ingresado")
        else:
            for row in resultados:
                valores = [str(item) if item is not None else "" for item in row]
                tabla.insert("", "end", values=valores)
            
    except pyodbc.Error as e:
        messagebox.showerror("Error de conexión", f"Error al conectar a la base de datos:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado:\n{str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

# Crear ventana principal
root = tk.Tk()
root.title("Consulta de Tarifas por Cliente")
root.geometry("1300x650")

# Frame para controles de búsqueda
frame_busqueda = ttk.Frame(root, padding="10")
frame_busqueda.pack(fill="x")

# Etiqueta y campo para ingresar código
ttk.Label(frame_busqueda, text="Código de Cliente:").pack(side="left", padx=5)
entry_codigo = ttk.Entry(frame_busqueda, width=20)
entry_codigo.pack(side="left", padx=5)
entry_codigo.focus()

# Botón de búsqueda
btn_buscar = ttk.Button(
    frame_busqueda,
    text="Buscar",
    command=ejecutar_consulta
)
btn_buscar.pack(side="left", padx=10)

# Frame para la tabla
frame_tabla = ttk.Frame(root)
frame_tabla.pack(expand=True, fill="both", padx=10, pady=(0, 10))

# Scrollbars
scroll_y = ttk.Scrollbar(frame_tabla)
scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal")

# Configurar tabla
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
anchos = [120, 200, 100, 80, 200, 80, 100, 100, 100, 100, 100]
for col, ancho in zip(columnas, anchos):
    tabla.heading(col, text=col)
    tabla.column(col, width=ancho, anchor="center")

# Posicionar elementos
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
tabla.pack(expand=True, fill="both")

# Frame para botones adicionales
frame_botones = ttk.Frame(root, padding="10")
frame_botones.pack(fill="x")

# Botón para exportar a Excel
btn_exportar = ttk.Button(
    frame_botones,
    text="Exportar a Excel",
    command=lambda: exportar_a_excel(tabla)
)
btn_exportar.pack(side="left", padx=5)

# Botón para limpiar
btn_limpiar = ttk.Button(
    frame_botones,
    text="Limpiar",
    command=lambda: limpiar_tabla(tabla)
)
btn_limpiar.pack(side="left", padx=5)

# Botón para salir
btn_salir = ttk.Button(
    frame_botones,
    text="Salir",
    command=root.quit
)
btn_salir.pack(side="right", padx=5)

def limpiar_tabla(tabla):
    for row in tabla.get_children():
        tabla.delete(row)
    entry_codigo.delete(0, tk.END)
    entry_codigo.focus()

def exportar_a_excel(tabla):
    try:
        import pandas as pd
        from tkinter.filedialog import asksaveasfilename
        
        # Obtener datos de la tabla
        datos = []
        for item in tabla.get_children():
            valores = tabla.item(item)['values']
            datos.append(valores)
        
        if not datos:
            messagebox.showwarning("Advertencia", "No hay datos para exportar")
            return
            
        # Crear DataFrame
        df = pd.DataFrame(datos, columns=columnas)
        
        # Solicitar ubicación para guardar
        archivo = asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Guardar como"
        )
        
        if archivo:
            df.to_excel(archivo, index=False)
            messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{archivo}")
            
    except ImportError:
        messagebox.showerror("Error", "Para exportar a Excel necesita instalar pandas:\npip install pandas openpyxl")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar a Excel:\n{str(e)}")

# Permitir búsqueda con Enter
entry_codigo.bind("<Return>", lambda event: ejecutar_consulta())

root.mainloop()