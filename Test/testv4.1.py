
        
from flask import Flask, render_template, request, redirect, url_for
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

def get_web_sessions(start_date, end_date, search_term=None):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            # Obtener sesiones web
            query = """
            SELECT 
                s.id AS session_id,
                u.username,
                u.email,
                s.created AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima' AS fecha_conexion,
                ROUND((EXTRACT(EPOCH FROM (NOW() - s.created)) / 60.0)::numeric, 2) AS tiempo_activo_minutos,
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
            query += " ORDER BY tiempo_activo_minutos DESC;"
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
        
        df = pd.DataFrame(data, columns=columns)

        if not df.empty:
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

            # Asignar estado basado en duración
            df["estado"] = df["tiempo_activo_minutos"].apply(lambda x: "Activa" if x <= 60 else "Inactiva")

            # Obtener consultas SQL activas desde pg_stat_activity
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT usename, query
                        FROM pg_stat_activity
                        WHERE state = 'active' AND query NOT ILIKE '%pg_stat_activity%' AND usename != 'postgres'
                    """)
                    pg_data = cursor.fetchall()
                    df_pg = pd.DataFrame(pg_data, columns=["usename", "consulta_sql"])

            # Combinar usando el nombre de usuario
            df = df.merge(df_pg, how="left", left_on="username", right_on="usename")
            df.drop(columns=["usename"], inplace=True, errors="ignore")
            df["consulta_sql"].fillna("Sin consulta", inplace=True)

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
    today = datetime.today()
    start_date = request.args.get("start_date", (today - timedelta(days=7)).strftime('%Y-%m-%d'))
    end_date = request.args.get("end_date", today.strftime('%Y-%m-%d'))
    search_term = request.args.get("search_term", "")

    df = get_web_sessions(start_date, end_date, search_term)
    if "error" in df:
        return f"<h3>Error al obtener sesiones: {df['error'][0]}</h3>"

    total_activas = (df['estado'] == 'Activa').sum() if 'estado' in df else 0
    total_inactivas = (df['estado'] == 'Inactiva').sum() if 'estado' in df else 0

    return render_template(
        "sesiones.html",
        data=df.to_dict(orient="records"),
        columns=[col for col in df.columns if col != "session_key"],
        start_date=start_date,
        end_date=end_date,
        search_term=search_term,
        total_activas=total_activas,
        total_inactivas=total_inactivas
    )

@app.route("/terminate", methods=["POST"])
def terminate():
    session_ids = request.form.getlist("session_ids")
    if terminate_sessions(session_ids):
        return redirect(url_for('index', start_date=request.form['start_date'], end_date=request.form['end_date'], search_term=request.form.get('search_term', '')))
    else:
        return "<h3>Error al finalizar las sesiones seleccionadas</h3>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)

@app.route("/consultas", methods=["GET"])
def consultas_bd():
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT pid, usename, datname, application_name, client_addr, state, query_start, query
                    FROM pg_stat_activity
                    WHERE state = 'active'
                      AND query NOT ILIKE '%pg_stat_activity%'
                      AND usename != 'postgres'
                    ORDER BY query_start DESC;
                """)
                records = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(records, columns=columns)

        return render_template("consultas_bd.html", data=df.to_dict(orient="records"), columns=columns)

    except Exception as e:
        return f"<h3>Error al obtener consultas SQL: {str(e)}</h3>"
