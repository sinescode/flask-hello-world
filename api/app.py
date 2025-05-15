from flask import Flask, send_from_directory, g
from api.config import Config
from api.extensions import db, Base
from flask_cors import CORS
from api.models.models import User, AvailableAccount, GeneratedAccount
from api.routes.accounts import accounts_bp
from api.routes.api import api_bp
from api.routes.auth import auth_bp


def create_app():
    # Create the Flask application instance
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(accounts_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Ensure database tables are created once per application start
    with app.app_context():
        db.create_all()
        Base.metadata.create_all(db.engine)

    # Serve Next.js static files
    @app.route('/<path:path>')
    def serve_nextjs(path):
        return send_from_directory('static/nextjs', path)

    @app.route('/')
    def serve_nextjs_index():
        return send_from_directory('static/nextjs', 'index.html')

    @app.route('/login', strict_slashes=False)
    def serve_login():
        return send_from_directory('static/nextjs/login', 'index.html')

    @app.route('/saved', strict_slashes=False)
    def serve_saved():
        return send_from_directory('static/nextjs/saved', 'index.html')

    @app.route('/generate_account', strict_slashes=False)
    def serve_generate_account():
        return send_from_directory('static/nextjs/generate_account', 'index.html')

    @app.route('/register', strict_slashes=False)
    def serve_register():
        return send_from_directory('static/nextjs/register', 'index.html')

    return app

app = create_app()
