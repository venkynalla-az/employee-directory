import pyodbc
import os


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


def fetch_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 10 * FROM employee")

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        for row in rows:
            print(dict(zip(columns, row)))

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    fetch_data()
