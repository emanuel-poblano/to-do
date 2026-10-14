# To-do list

A small, customizable to-do list built with Flask and SQLite. Tasks can be
added, marked complete, and deleted. The database is created automatically
when the app starts.

## Run locally

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug
```

Open <http://127.0.0.1:5000>. The database defaults to
`instance/todos.sqlite`; set the `DATABASE` environment variable to use a
different path or a persistent volume.

## Deploy

The included `Procfile` starts the application with Gunicorn:

```sh
gunicorn app:app
```

Install the packages from `requirements.txt` on the hosting platform. Make
sure the database location is writable and persisted between deployments.

## Customize

Edit `static/style.css` to change the colors and layout. The color variables
at the top of the file are an easy starting point. The page structure and
task labels can be changed in `templates/index.html`.

## Tests

```sh
python -m unittest discover -s tests
```
