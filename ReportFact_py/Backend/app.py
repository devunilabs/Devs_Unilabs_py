#
#  App  divida en Backend y Frontend  para mejor mantenimiento, manteniendo toda la funcionalidad:
#   ## FUNCIONANDO CORRECTAMENTE  USAR ##
#
#/proyecto_reportfact/
#│ 
#├── backend/
#│   ├── app.py                # Script principal Flask
#│   ├── file_processor.py     # Lógica de procesamiento
#│   └── requirements.txt      # Dependencias
#│
#└── frontend/
#    ├── static/
#    │   ├── css/
#    │   │   └── styles.css    # Estilos CSS
#    │   └── js/
#    │       └── script.js     # JavaScript
#    │
#    └── templates/
#        └── index.html        # Plantilla HTML
# ****** backend/app.py *******

# backend/app.py

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from file_processor import procesar_archivos

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = os.path.join(os.path.expanduser("~"), 'Downloads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar():
    if 'archivos' not in request.files:
        return jsonify({"error": "No se subieron archivos"}), 400
        
    archivos = request.files.getlist('archivos')
    resultados = procesar_archivos(archivos, app.config)
    
    if 'error' in resultados:
        return jsonify(resultados), 400
        
    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True)

