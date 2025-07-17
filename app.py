from flask import Flask, render_template

from config import Config
from extensions import db, login_manager
from models import User
from auth import auth_bp

def create_app():
    app = Flask(__name__)

    # Klucz do sesji i flask-login
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    app.register_blueprint(auth_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route("/")
    def home():
        return render_template('home.html')

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
