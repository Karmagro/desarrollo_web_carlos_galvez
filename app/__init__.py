from flask import Flask
from config import Config
from .extensions import db
import os
UPLOAD_FOLDER = os.path.join("app", "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db.init_app(app)    

    from .routes import main
    app.register_blueprint(main)

    return app
