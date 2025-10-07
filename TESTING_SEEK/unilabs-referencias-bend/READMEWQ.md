# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Deberías ver (venv) al inicio de tu prompt


# Buscar archivo de requisitos
# Generalmente será uno de estos:
pip install -r requirements.txt
# o
pip install -r requirements/local.txt
# o
pip install -r requirements/base.txt




Comandos correctos para PowerShell:
1. Ver archivos y carpetas en el directorio actual:
powershellGet-ChildItem
# O más corto:
ls
2. Ver solo nombres de archivos/carpetas:

powershellGet-ChildItem | Select-Object Name
# O:

ls | Select-Object Name

3. Ver estructura completa del proyecto:
powershellGet-ChildItem -Recurse | Select-Object FullName | Out-File estructura.txt
Get-Content estructura.txt
4. Ver solo archivos Python:
powershellGet-ChildItem -Recurse -Filter "*.py" | Select-Object FullName
5. Buscar archivos específicos:
powershell# Buscar settings.py
Get-ChildItem -Recurse -Name "settings.py"



# Buscar manage.py
Get-ChildItem -Recurse -Name "manage.py"

# Buscar .env
Get-ChildItem -Recurse -Name ".env*"




# 1. Ver qué hay en la carpeta actual
ls

# 2. Ver si hay manage.py (confirmar que es Django)
ls manage.py

# 3. Ver si hay carpeta de configuración
ls -Directory

# 4. Buscar archivos de configuración importantes
Get-ChildItem -Recurse -Name "*.env*"
Get-ChildItem -Recurse -Name "docker*"
Get-ChildItem -Recurse -Name "README*"

La estructura. Es un proyecto Django interesante. Vamos a explorarlo:

Estructura del proyecto identificada:
unilabs-referencias-bend/
├── manage.py              # ✅ Django project
├── db.sqlite3            # ✅ Base de datos SQLite (desarrollo)
├── README.md             # 📖 Documentación
├── requirements.txt      # 📦 Dependencias
├── modules/              # 🧩 Módulos/Apps principales
├── static/               # 🎨 Archivos estáticos (CSS, JS, imágenes)
├── templates/            # 🖼️ Plantillas HTML
├── utils/                # 🔧 Utilidades/Helpers
└── wapp/                 # ⚙️ Configuración principal (settings, urls)


Análisis Completo del Backend Unilabs Referencias
1. ESTRUCTURA DEL PROGRAMA
Arquitectura General


unilabs-referencias-bend/
├── wapp/                          # Proyecto Django principal
│   ├── settings.py               # Configuración (170+ líneas)
│   ├── urls.py                   # Enrutamiento central
│   └── wsgi.py                   # Servidor WSGI
│
├── modules/                       # Apps modulares (arquitectura correcta)
│   ├── users/                    # Gestión completa de usuarios
│   │   ├── models.py            # User, Reference, ReferenceAdmin, etc.
│   │   ├── admin.py             # 500+ líneas - muy complejo
│   │   ├── views/
│   │   │   ├── auth_view.py     # Autenticación JWT
│   │   │   ├── user_view.py     # CRUD usuarios
│   │   │   └── cron_view.py     # Sincronización
│   │   ├── serializers/         # Transformación datos
│   │   ├── helpers/             # Funciones auxiliares
│   │   └── tasks.py             # Tareas Celery
│   │
│   ├── luggage/                  # Muestras/equipajes de laboratorio
│   │   ├── models.py
│   │   ├── views/
│   │   │   ├── luggage_view.py
│   │   │   ├── patient_view.py
│   │   │   └── test_view.py
│   │   └── admin.py
│   │
│   ├── result/                   # Resultados de análisis
│   ├── report/                   # Generación de reportes (PDF/Excel)
│   │   ├── maker.py             # Usa pandas
│   │   └── tasks.py             # Limpieza automática
│   │
│   ├── analytical/               # Análisis y etapas del proceso
│   ├── information/              # Información general
│   ├── image/                    # Gestión de imágenes
│   ├── attention/                # Módulo de atención
│   └── setting/                  # Configuraciones del sistema
│
├── utils/                        # Utilidades compartidas
│   └── render.py                # Generación PDFs (xhtml2pdf)
│
├── templates/                    # Solo emails
│   └── emails/
│
├── static/                       # CSS/JS/Assets
│   ├── assets/
│   └── js/
│
├── media/                        # Archivos subidos
├── db.sqlite3                   # Base de datos (desarrollo)
├── manage.py
└── requirements.txt