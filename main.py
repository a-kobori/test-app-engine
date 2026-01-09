"""App Engine entrypoint."""
import sys
from pathlib import Path

# Add src to Python path for App Engine
sys.path.insert(0, str(Path(__file__).parent / "src"))

from todo_app.main import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)