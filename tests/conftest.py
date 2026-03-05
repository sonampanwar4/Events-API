import pytest
from flask import Flask
from models import db
from flask_jwt_extended import create_access_token, JWTManager
from routes.auth import auth_bp
from routes.events import events_bp
from routes.rsvps import rsvps_bp

@pytest.fixture
def app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"

    db.init_app(app)
    JWTManager(app)

    # Register API routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(rsvps_bp)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def session(app):
    return db.session

@pytest.fixture
def user():
    return {
        "id": 1,
        "email": "test@example.com"
    }

@pytest.fixture
def auth_headers(app, user):
    """
    Return valid JWT authorization headers
    for an authenticated test user.
    """

    with app.app_context():
        token = create_access_token(identity=str(user["id"]))

    return {
        "Authorization": f"Bearer {token}"
    }
