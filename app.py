import os
from flask import Flask, jsonify
from flask_cors import CORS
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from sqlalchemy import create_engine, text

app = Flask(__name__)
CORS(app)

# Get database credentials from Azure Key Vault
key_vault_uri = os.getenv("AZURE_KEY_VAULT_URI")
credential = ManagedIdentityCredential()
secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

server = secret_client.get_secret("MSSQL-DB-SERVER").value
database = secret_client.get_secret("MSSQL-DB-NAME").value
username = secret_client.get_secret("MSSQL-DB-USER").value
password = secret_client.get_secret("MSSQL-DB-PASSWORD").value

# SQLAlchemy connection string
DATABASE_URL = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

# Create SQLAlchemy engine with connection pooling
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=5)


@app.route("/employees", methods=["GET"])
def fetch_data():
    """Fetches employee data using a connection from the pool."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT TOP 10 id, first_name, last_name, email FROM employee"))
            data = [{"id": row[0], "firstName": row[1], "lastName": row[2], "email": row[3]} for row in result]

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
