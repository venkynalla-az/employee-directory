import pyodbc
import os
from flask import Flask, jsonify
from collections import OrderedDict

app = Flask(__name__)


def get_db_connection():
    server = os.getenv("MSSQL_DB_SERVER")
    database = os.getenv("MSSQL_DB_NAME")
    username = os.getenv("MSSQL_DB_USER")
    password = os.getenv("MSSQL_DB_PASSWORD")

    connection_string = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
    )

    return pyodbc.connect(connection_string)


@app.route("/employees", methods=["GET"])
def fetch_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 10 id, first_name, last_name, email FROM employee")

        rows = cursor.fetchall()
        data = [OrderedDict([
            ("id", row[0]),
            ("firstName", row[1]),
            ("lastName", row[2]),
            ("email", row[3])
        ]) for row in rows]

        cursor.close()
        conn.close()

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
