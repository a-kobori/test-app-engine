"""Flask application factory."""
from flask import Flask, render_template


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    @app.route("/")
    def index():
        """Render the main page."""
        return render_template("index.html", title="TODO App")
    
    @app.route("/health")
    def health():
        """Health check endpoint."""
        return {"status": "ok"}, 200
    
    return app