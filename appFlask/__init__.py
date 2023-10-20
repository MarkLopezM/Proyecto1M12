from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_wtf.csrf import CSRFProtect

db_manager = SQLAlchemy()

csrf = CSRFProtect()
def create_app():
    # Construct the core app object

    app = Flask(__name__)
    
    csrf.init_app(app)

    basedir = os.path.abspath(os.path.dirname(__file__)) 

    app.config["SECRET_KEY"] = "definitivamente una buena key"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + basedir + "/database.db"

    app.config["SQLALCHEMY_ECHO"] = True

    # Inicialitza SQLAlchemy
    db_manager.init_app(app)

    with app.app_context():
        from . import routes_main
        app.register_blueprint(routes_main.main_bp)

    app.logger.info("Aplicación iniciada")

    return app