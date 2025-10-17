from flask import Flask
from flask_bootstrap import Bootstrap
from werkzeug.debug import DebuggedApplication
import os

def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    app.config['SECRET_KEY'] = "mysecret"
    app.config['UPLOAD_FOLDER'] =  os.path.join(os.path.dirname(__file__), '../static/images')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB


    bootstrap = Bootstrap(app)

    app.wsgi_app = DebuggedApplication(
        app.wsgi_app,
        evalex=True,
        console_path="/debug"
    )

    # Database Setup
    from .database import create_tables

    create_tables()

    # Add Routes
    from .routes import (
        index_bp,
        login_bp,
        register_bp,
        admin_bp,
        logout_bp,
        profile_bp,
        course_bp,
        endpoint_bp,
        forgot_pass_bp,
    )

    app.register_blueprint(index_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(endpoint_bp)
    app.register_blueprint(forgot_pass_bp)

    return app
