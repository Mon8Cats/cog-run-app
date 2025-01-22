import os
import psycopg2
from flask import Flask

app = Flask(__name__)

# Configure the PostgreSQL connection
DB_USER = os.getenv("DB_USER", "db-user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "db-password")
DB_NAME = os.getenv("DB_NAME", "spn-db")
CLOUD_SQL_CONNECTION_NAME = os.getenv("spn-run:us-central1:spn-sql")  # Format: project:region:instance

# Unix socket path
DB_HOST = f"/cloudsql/{CLOUD_SQL_CONNECTION_NAME}"

def get_connection():
    """Creates a connection to the Cloud SQL database."""
    return psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
    )

@app.route("/")
def index():
    """Sample route to test database connectivity."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 'Connection successful!'")
            result = cursor.fetchone()
        connection.close()
        return result[0]
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))