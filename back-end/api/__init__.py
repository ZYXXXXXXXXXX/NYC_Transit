from flask import Blueprint
from .routes import register_routes


def create_routes(app):

    api_bp = Blueprint('api', __name__, url_prefix='/api')

    register_routes(api_bp)

    app.register_blueprint(api_bp)