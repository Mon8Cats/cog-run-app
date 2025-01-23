from __future__ import annotations

import os
import datetime
import logging
from flask import Flask, render_template, request, Response
from psycopg2 import pool
import psycopg2

app = Flask(__name__)

logger = logging.getLogger()

# Database configuration
DB_USER = os.getenv("DB_USER", "db-userx")  # Now retrieved from environment variables
DB_PASSWORD = os.getenv("DB_PASSWORD", "db-passwordx")
DB_NAME = os.getenv("DB_NAME", "spn-dbx")
DB_HOST = os.getenv("DB_HOST","/cloudsql/spn-run:us-central1:spn-sqlx")
DB_PORT = os.getenv("DB_PORT", "5432x")

# Global connection pool
db_pool = None



def init_connection_pool():
    """Initializes the psycopg2 connection pool."""
    return pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,  # Adjust max connections based on your app's needs
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def migrate_db():
    """Creates the 'votes' table in the database if it does not exist."""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS votes (
                    id SERIAL PRIMARY KEY,
                    candidate VARCHAR(255) NOT NULL,
                    time_cast TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """)
            conn.commit()
    finally:
        db_pool.putconn(conn)


@app.before_first_request
def setup_db():
    """Sets up the connection pool and migrates the database schema."""
    global db_pool
    if db_pool is None:
        db_pool = init_connection_pool()
        migrate_db()


@app.route("/", methods=["GET"])
def render_index() -> str:
    """Serves the index page of the app."""
    conn = db_pool.getconn()
    try:
        context = get_index_context(conn)
        return render_template("index.html", **context)
    finally:
        db_pool.putconn(conn)


@app.route("/votes", methods=["POST"])
def cast_vote() -> Response:
    """Processes a single vote from the user."""
    team = request.form["team"]
    conn = db_pool.getconn()
    try:
        return save_vote(conn, team)
    finally:
        db_pool.putconn(conn)


def get_index_context(conn) -> dict:
    """Retrieves data from the database about the votes."""
    votes = []
    try:
        with conn.cursor() as cursor:
            # Fetch recent votes
            cursor.execute(
                "SELECT candidate, time_cast FROM votes ORDER BY time_cast DESC LIMIT 5"
            )
            rows = cursor.fetchall()
            votes = [{"candidate": row[0], "time_cast": row[1]} for row in rows]

            # Fetch vote counts
            cursor.execute("SELECT COUNT(*) FROM votes WHERE candidate = %s", ("TABS",))
            tab_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM votes WHERE candidate = %s", ("SPACES",))
            space_count = cursor.fetchone()[0]

        return {
            "space_count": space_count,
            "recent_votes": votes,
            "tab_count": tab_count,
        }
    except Exception as e:
        logger.exception("Error fetching index context: %s", e)
        raise


def save_vote(conn, team: str) -> Response:
    """Saves a single vote into the database."""
    time_cast = datetime.datetime.now(tz=datetime.timezone.utc)

    if team not in ["TABS", "SPACES"]:
        logger.warning(f"Received invalid 'team' property: '{team}'")
        return Response(
            response="Invalid team specified. Should be one of 'TABS' or 'SPACES'",
            status=400,
        )

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO votes (time_cast, candidate) VALUES (%s, %s)",
                (time_cast, team),
            )
            conn.commit()
        return Response(
            status=200,
            response=f"Vote successfully cast for '{team}' at time {time_cast}!",
        )
    except Exception as e:
        logger.exception("Error saving vote: %s", e)
        return Response(
            status=500,
            response="Unable to successfully cast vote! Please check the application logs for more details.",
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
