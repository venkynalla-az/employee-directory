import pyodbc
import os
from flask import Flask, jsonify
from flask_cors import CORS
from collections import OrderedDict

# from azure.identity import ClientSecretCredential
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

app = Flask(__name__)
CORS(app)


def get_db_connection():
    # client_id = os.getenv("AZURE_CLIENT_ID")
    # tenant_id = os.getenv("AZURE_TENANT_ID")
    # client_secret = os.getenv("AZURE_CLIENT_SECRET")
    key_vault_uri = os.getenv("AZURE_KEY_VAULT_URI")
    # credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    credential = ManagedIdentityCredential()

    secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

    server = secret_client.get_secret("MSSQL-DB-SERVER")
    database = secret_client.get_secret("MSSQL-DB-NAME")
    username = secret_client.get_secret("MSSQL-DB-USER")
    password = secret_client.get_secret("MSSQL-DB-PASSWORD")

    connection_string = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server.value};'
        f'DATABASE={database.value};'
        f'UID={username.value};'
        f'PWD={password.value};'
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
