from app import app
import os


if __name__ == "__main__":
    app.run("0.0.0.0", port=os.getenv('FLASK_PORT', 6969))
