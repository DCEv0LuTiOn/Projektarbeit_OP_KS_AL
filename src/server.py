from datetime import datetime
from pathlib import Path
from flask import Flask, render_template

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=BASE_DIR / "templates",
    static_folder=BASE_DIR / "static"
)

@app.route("/")
def index():
    return render_template("index.html")


def _jetzt() -> str:
    """Aktueller Zeitpunkt als ISO-Text (SQLite speichert Datum/Zeit als Text)."""
    return  datetime.now().isoformat(timespec="seconds")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)