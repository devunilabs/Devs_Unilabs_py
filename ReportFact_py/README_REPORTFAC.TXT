1. Programa pendie de revision de formato  :Si no puede con UTF-8, prueba automáticamente con ISO-8859-1.
2. Programa pendiente de la version con la hora y fecha de procesamiento
3. Pendiente de automatizar de forma periodica todos los lunes con N8N o POWER AUTAMATE
4. Pendiente de conectat con Jira de forma periodica .



#
#  App  divida en Backend y Frontend  para mejor mantenimiento, manteniendo toda la funcionalidad:
#   ## FUNCIONANDO CORRECTAMENTE  USAR ##

#  Proyecto ReportFact V1

Sistema de procesamiento de archivos CSV a Excel con interfaz web profesional, barra de progreso, y arquitectura modular basada en Flask + HTML/CSS/JS.

---

## 📁 Estructura del Proyecto

proyecto_reportfact/
│
├── backend/
│ ├── app.py # 🚀 Servidor principal con FastAPI o Flask
│ ├── file_processor.py # 🧠 Lógica de procesamiento de archivos (limpieza, formateo, transformación a Excel)
│ └── requirements.txt # 📦 Lista de dependencias Python necesarias
│
└── frontend/
├── static/
│ ├── css/
│ │ └── styles.css # 🎨 Estilos personalizados (botones, logos, loader)
│ └── js/
│ └── script.js # ⚙️ Lógica JS para barra de progreso y manejo dinámico de interfaz
│
└── templates/
└── index.html # 🖥️ Plantilla principal HTML (interfaz de usuario)

