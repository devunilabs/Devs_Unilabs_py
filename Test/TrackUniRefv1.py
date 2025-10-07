
##########################################

from flask import Flask, render_template_string, request, redirect, url_for
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import os
import psutil

app = Flask(__name__)

DB_CONFIG = {
        'dbname': 'production_unilabs',
        'user': 'unilabs',
        'password': 'SEEK@2022#pe',
        'host': '172.16.1.34',
        'port': '5432'
}

TEMPLATE = """
<!DOCTYPE html>
<html lang=\"es\">
<head>
    <meta charset=\"UTF-8\">
    <title>Monitor de Sesiones Django</title>
    <link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css\">
</head>
<body class=\"bg-light\">
    <div class=\"container py-4\">
        <h2 class=\"mb-4\">📊 Monitor de Sesiones UNIREF</h2>
        <form class=\"row g-3 mb-4\" method=\"get\">
            <div class=\"col-md-4\">
                <label for=\"start_date\" class=\"form-label\">Desde:</label>
                <input type=\"date\" id=\"start_date\" name=\"start_date\" class=\"form-control\" value=\"{{ start_date }}\">
            </div>
            <div class=\"col-md-4\">
                <label for=\"end_date\" class=\"form-label\">Hasta:</label>
                <input type=\"date\" id=\"end_date\" name=\"end_date\" class=\"form-control\" value=\"{{ end_date }}\">
            </div>
            <div class=\"col-md-4 align-self-end\">
                <button type=\"submit\" class=\"btn btn-primary w-100\">🔄 Actualizar</button>
            </div>
        </form>
        {% if data %}
        <form method=\"post\" action=\"/terminate\">
            <input type=\"hidden\" name=\"session_id\" value=\"{{ data[0]['session_id'] }}\">
            <input type=\"hidden\" name=\"start_date\" value=\"{{ start_date }}\">
            <input type=\"hidden\" name=\"end_date\" value=\"{{ end_date }}\">
            <button type=\"submit\" class=\"btn btn-danger mb-3\">🛑 Finalizar sesión con mayor consumo</button>
        </form>
        <div class=\"table-responsive\">
            <table class=\"table table-bordered table-striped\">
                <thead class=\"table-dark\">
                    <tr>
                        {% for col in columns %}
                        <th>{{ col.replace('_', ' ').title() }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in data %}
                    <tr>
                        {% for col in columns %}
                        <td>
                            {% if col == 'tiempo_activo_minutos' %}{{ row[col]|float|round(1) }} min
                            {% elif col == 'uso_porcentaje' %}{{ row[col] }} %
                            {% elif col == 'cpu_percent' or col == 'memory_percent' %}{{ row[col] }} %
                            {% else %}{{ row[col] }}{% endif %}
                        </td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div class=\"alert alert-warning\">No hay sesiones encontradas para el rango seleccionado.</div>
        {% endif %}
    </div>
</body>
</html>
"""

def get_web_sessions(start_date, end_date):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        query = """
        SELECT 
            s.id AS session_id,
            u.username,
            u.email,
            s.created AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima' AS fecha_conexion,
            EXTRACT(EPOCH FROM (NOW() - s.created))/60.0 AS tiempo_activo_minutos
        FROM 
            users_usersession s
        JOIN 
            users_user u ON s.user_id = u.id
        WHERE 
            s.created::date >= %s AND s.created::date <= %s
        ORDER BY tiempo_activo_minutos DESC;
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (start_date, end_date))
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
        conn.close()
        df = pd.DataFrame(data, columns=columns)

        if not df.empty:
            df["tiempo_activo_minutos"] = pd.to_numeric(df["tiempo_activo_minutos"], errors="coerce")
            df["uso_porcentaje"] = ((df["tiempo_activo_minutos"] / df["tiempo_activo_minutos"].max()) * 100).round(1)

            # Simulación de uso de CPU y memoria
          
            procesos = list(psutil.process_iter(attrs=["cpu_percent", "memory_percent"]))[:len(df)]
            df = df.iloc[:len(procesos)]
            df["cpu_percent"] = [p.info.get("cpu_percent", 0.0) for p in procesos]
            df["memory_percent"] = [round(p.memory_percent(), 2) for p in procesos]

        return df
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})

def terminate_session(session_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        query = "DELETE FROM users_usersession WHERE id = %s;"
        with conn.cursor() as cursor:
            cursor.execute(query, (session_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Error al terminar sesión:", e)
        return False

@app.route("/", methods=["GET"])
def index():
    today = datetime.today()
    start_date = request.args.get("start_date", (today - timedelta(days=7)).strftime('%Y-%m-%d'))
    end_date = request.args.get("end_date", today.strftime('%Y-%m-%d'))

    df = get_web_sessions(start_date, end_date)
    if "error" in df:
        return f"<h3>Error al obtener sesiones: {df['error'][0]}</h3>"
    return render_template_string(TEMPLATE, data=df.to_dict(orient="records"), columns=df.columns, start_date=start_date, end_date=end_date)

@app.route("/terminate", methods=["POST"])
def terminate():
    session_id = request.form.get("session_id")
    if terminate_session(session_id):
        return redirect(url_for('index', start_date=request.form['start_date'], end_date=request.form['end_date']))
    else:
        return "<h3>Error al finalizar la sesión con mayor consumo</h3>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)





