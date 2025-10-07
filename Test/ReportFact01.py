import os
import pandas as pd
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from io import StringIO

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

RESULT_FOLDER = os.path.join(os.path.expanduser("~"), 'Downloads')

# Mapeo de nombres de archivos a hojas
nombre_hojas = {
    "BASADRE": ["BASADRE", "BSD"],
    "CGH": ["CGH"],
    "CSI": ["CSI"],
    "HUACHO": ["HUACHO", "HUA"],
    "AVIVA MENDIOLA": ["AVI_MEND", "AVIMEND"],
    "AVIVA COLONIAL": ["AVI_COL", "AVIVACOL"]
}

# Columnas clave para tipo texto
columna_inicio = "DNI"
columna_fin = "descripciÃ³n prueba"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar():
    archivos = request.files.getlist("archivos")
    hojas_data = {}

    for archivo in archivos:
        nombre = secure_filename(archivo.filename)
        contenido_original = archivo.read().decode('utf-8', errors='ignore')

        # Limpieza: quitar \r\n y tabuladores
        contenido_limpio = contenido_original.replace('\r\n', ' ').replace('\t', '')

        # Detectar nombre de hoja destino
        hoja_destino = None
        for hoja, claves in nombre_hojas.items():
            if any(clave in nombre.upper() for clave in claves):
                hoja_destino = hoja
                break

        if not hoja_destino:
            continue  # saltar si no se reconoce

        # Leer desde memoria con separador |
        df = pd.read_csv(StringIO(contenido_limpio), sep='|', dtype=str, engine='python')
        df = df.fillna("")

        # Convertir columnas entre 'DNI' y 'descripción prueba' a texto
        columnas = list(df.columns)
        try:
            i_ini = columnas.index(columna_inicio)
            i_fin = columnas.index(columna_fin)
            cols_texto = columnas[i_ini:i_fin+1]
            for col in cols_texto:
                df[col] = df[col].astype(str)
        except:
            pass  # Si no encuentra alguna columna, omitir

        hojas_data[hoja_destino] = df

    # Crear archivo Excel consolidado
    wb = Workbook()
    wb.remove(wb.active)  # eliminar hoja por defecto

    orden_final = [
        "BASADRE", "CGH", "CSI", "HUACHO",
        "AVIVA MENDIOLA", "AVIVA COLONIAL"
    ]

    for nombre_hoja in orden_final:
        df = hojas_data.get(nombre_hoja, pd.DataFrame())
        ws = wb.create_sheet(title=nombre_hoja)
        for fila in dataframe_to_rows(df, index=False, header=True):
            ws.append(fila)

    ruta_final = os.path.join(RESULT_FOLDER, "Consolidado.xlsx")
    wb.save(ruta_final)

    return f"""
    <h2>✅ Procesamiento completo</h2>
    <p>Archivo guardado en <b>{ruta_final}</b></p>
    <a href="/">Volver</a>
    """

if __name__ == '__main__':
    app.run(debug=True)
