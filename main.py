

import flask

import functions_framework

from app import get_index_context, init_connection_pool, migrate_db, save_vote


db_pool = None  # Global variable for connection pool

@functions_framework.http
def votes(request: flask.Request) -> flask.Response:
    global db_pool
    # Initialize connection pool if it doesn't exist
    if not db_pool:
        db_pool = init_connection_pool()

    # Fetch a connection from the pool
    conn = db_pool.getconn()
    try:
        # Perform operations using the connection
        if request.method == "GET":
            context = get_index_context(conn)  # Pass connection instead of pool
            return flask.render_template("index.html", **context)

        if request.method == "POST":
            team = request.form["team"]
            return save_vote(conn, team)

        return flask.Response(
            response="Invalid HTTP request. Method not allowed, must be 'GET' or 'POST'",
            status=400,
        )
    finally:
        # Return the connection to the pool
        db_pool.putconn(conn)
