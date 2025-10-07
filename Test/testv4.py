
from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import pytz
import math

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

DB_CONFIG = {

        'dbname': 'production_unilabs',
        'user': 'unilabs',
        'password': 'SEEK@2022#pe',
        'host': '172.16.1.34',
        'port': '5432'
}

PAGE_SIZE = 10

def get_web_sessions(start_date, end_date, search_term=None, estado_filter=None):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            query = """
            SELECT DISTINCT ON (u.username)
                s.id AS session_id,
                u.username,
                u.email,
                s.created AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima' AS fecha_conexion,
                ROUND((EXTRACT(EPOCH FROM (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima' - s.created AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')) / 60.0)::numeric, 2) AS tiempo_activo_minutos,
                s.reference_active_id,
                s.created
            FROM 
                users_usersession s
            JOIN 
                users_user u ON s.user_id = u.id
            WHERE 
                s.created::date >= %s AND s.created::date <= %s
            """
            params = [start_date, end_date]
            if search_term:
                query += " AND (LOWER(u.username) LIKE %s OR LOWER(u.email) LIKE %s)"
                params.extend([f"%{search_term.lower()}%", f"%{search_term.lower()}%"])
            query += " ORDER BY u.username, s.created DESC;"
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()

        df = pd.DataFrame(data, columns=columns)

        if not df.empty:
            df.sort_values(by=["username", "created"], ascending=[True, False], inplace=True)
            df = df.drop_duplicates(subset="username", keep="first")

            df["tiempo_activo_minutos"] = pd.to_numeric(df["tiempo_activo_minutos"], errors="coerce")

            def formatear_tiempo(minutos):
                if pd.isna(minutos):
                    return "N/A"
                horas = int(minutos // 60)
                mins = int(minutos % 60)
                if horas > 0 and mins > 0:
                    return f"{horas}h {mins}m"
                elif horas > 0:
                    return f"{horas}h"
                else:
                    return f"{mins}m"

            df["tiempo_activo"] = df["tiempo_activo_minutos"].apply(formatear_tiempo)
            df["uso_porcentaje"] = ((df["tiempo_activo_minutos"] / df["tiempo_activo_minutos"].max()) * 100).round(1)
            df["uso_detallado"] = df["uso_porcentaje"].apply(lambda x: f"{x}% del tiempo máximo activo")

            df["estado"] = df["tiempo_activo_minutos"].apply(lambda x: "Inactiva" if x > 30 else "Activa")

            if estado_filter:
                df = df[df["estado"].str.lower() == estado_filter.lower()]

            df["fecha_conexion"] = pd.to_datetime(df["fecha_conexion"])
            df["fecha_conexion"] = df["fecha_conexion"].dt.strftime("%Y-%m-%d %H:%M:%S")

        df.drop(columns=["reference_active_id", "created", "tiempo_activo_minutos"], inplace=True, errors="ignore")
        return df

    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})

def terminate_sessions(session_ids):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            ids = [int(sid) for sid in session_ids]
            cursor.execute("""
                DELETE FROM django_session 
                WHERE session_key IN (
                    SELECT reference_active_id::text FROM users_usersession WHERE id = ANY(%s)
                );
            """, (ids,))
            cursor.execute("DELETE FROM users_usersession WHERE id = ANY(%s);", (ids,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Error al eliminar sesiones:", e)
        return False

@app.route("/", methods=["GET"])
def index():
    today = datetime.now(pytz.timezone("America/Lima"))
    start_date = request.args.get("start_date") or session.get("start_date") or (today - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = request.args.get("end_date") or session.get("end_date") or today.strftime('%Y-%m-%d')
    search_term = request.args.get("search_term") or session.get("search_term") or ""
    estado_filter = request.args.get("estado") or session.get("estado") or ""
    page = int(request.args.get("page", 1))

    session["start_date"] = start_date
    session["end_date"] = end_date
    session["search_term"] = search_term
    session["estado"] = estado_filter

    df = get_web_sessions(start_date, end_date, search_term, estado_filter)
    if "error" in df:
        return f"<h3>Error al obtener sesiones: {df['error'][0]}</h3>"

    total_activas = (df['estado'] == 'Activa').sum() if 'estado' in df else 0
    total_inactivas = (df['estado'] == 'Inactiva').sum() if 'estado' in df else 0

    total_items = len(df)
    total_pages = math.ceil(total_items / PAGE_SIZE)
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    paginated_data = df.iloc[start_idx:end_idx].to_dict(orient="records")

    return render_template(
        "sesiones.html",
        data=paginated_data,
        columns=[col for col in df.columns if col != "session_key"],
        start_date=start_date,
        end_date=end_date,
        search_term=search_term,
        estado_filter=estado_filter,
        total_activas=total_activas,
        total_inactivas=total_inactivas,
        page=page,
        total_pages=total_pages
    )

@app.route("/terminate", methods=["POST"])
def terminate():
    session_ids = request.form.getlist("session_ids")
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')
    search_term = request.form.get('search_term', '')
    estado = request.form.get('estado', '')
    if terminate_sessions(session_ids):
        return redirect(url_for('index', start_date=start_date, end_date=end_date, search_term=search_term, estado=estado))
    else:
        return "<h3>Error al finalizar las sesiones seleccionadas</h3>"

@app.route("/consultas", methods=["GET"])
def consultas():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT pid, usename, client_addr, application_name, state, query
                FROM pg_stat_activity
                WHERE state = 'active'
                  AND query NOT ILIKE '%pg_stat_activity%'
                  AND usename != 'postgres'
                ORDER BY pid DESC;
            """)
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        return render_template("consultas_bd.html", data=data, columns=columns)
    except Exception as e:
        return f"<h3>Error al obtener consultas SQL activas: {str(e)}</h3>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)
