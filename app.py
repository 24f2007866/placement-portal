from flask import Flask
from flask_login import LoginManager
from models import db, User
from auth_routes import auth
from main_routes import main

def create_app():
    app = Flask(__name__)

    # ── Configuration ────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = 'change-this-secret-key-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Extensions ───────────────────────────────────────────────────────────
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'          # redirect here if not logged in
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'error'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Blueprints ───────────────────────────────────────────────────────────
    app.register_blueprint(auth)
    app.register_blueprint(main)

    # ── Create tables ────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    print("Starting Placement Portal...")
    print("Visit: http://127.0.0.1:5000")
    app.run(debug=True)
