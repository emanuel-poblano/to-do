import os
import sqlite3
from pathlib import Path

from flask import Flask, current_app, g, redirect, render_template, request, url_for


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "change-this-in-production"),
        DATABASE=os.environ.get(
            "DATABASE", str(Path(app.instance_path) / "todos.sqlite")
        ),
    )

    if test_config:
        app.config.update(test_config)

    # Keep the default database in Flask's instance directory.
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    init_db(app)

    @app.teardown_appcontext
    def close_db(error=None):
        # Close request-scoped connections after Flask finishes each request.
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.route("/", methods=("GET", "POST"))
    def index():
        # Adding tasks through POST keeps browser refreshes from submitting twice.
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            if title:
                db = get_db()
                db.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
                db.commit()
            return redirect(url_for("index"))

        tasks = get_db().execute(
            "SELECT id, title, completed FROM tasks ORDER BY id DESC"
        ).fetchall()
        return render_template("index.html", tasks=tasks)

    @app.post("/tasks/<int:task_id>/toggle")
    def toggle_task(task_id):
        # The update is conditional so unknown task IDs simply have no effect.
        db = get_db()
        db.execute(
            "UPDATE tasks SET completed = 1 - completed WHERE id = ?", (task_id,)
        )
        db.commit()
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/delete")
    def delete_task(task_id):
        # Parameterized SQL ensures submitted values are treated as data.
        db = get_db()
        db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        db.commit()
        return redirect(url_for("index"))

    return app


def get_db():
    """Return this request's SQLite connection, creating it when needed."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db(app):
    """Create the task table the first time the application starts."""
    with sqlite3.connect(app.config["DATABASE"]) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )


# Expose the application object for production servers such as Gunicorn.
app = create_app()
