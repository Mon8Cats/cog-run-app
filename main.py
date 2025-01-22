

import flask

import functions_framework

from app import get_index_context, init_connection_pool, migrate_db, save_vote

db = None


@functions_framework.http
def votes(request: flask.Request) -> flask.Response:
    global db
    # initialize db within request context
    if not db:
        # initiate a connection pool to a Cloud SQL database
        db = init_connection_pool()
        # creates required 'votes' table in database (if it does not exist)
        migrate_db(db)
    if request.method == "GET":
        context = get_index_context(db)
        return flask.render_template("index.html", **context)

    if request.method == "POST":
        team = request.form["team"]
        return save_vote(db, team)

    return flask.Response(
        response="Invalid http request. Method not allowed, must be 'GET' or 'POST'",
        status=400,
    )
