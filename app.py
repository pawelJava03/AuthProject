from flask import Flask, render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user

from config import Config
from extensions import db, login_manager
from models import User, Site
from auth import auth_bp
from sites import sites_bp
from dashboard import dashboard_bp
from blog import blog_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    app.register_blueprint(auth_bp)
    app.register_blueprint(sites_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(blog_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route("/")
    def home():
        return render_template('home.html')

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
