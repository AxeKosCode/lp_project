from flask import Flask, render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_migrate import Migrate
# from flask_uploads import UploadSet, configure_uploads, IMAGES

from webapp.db import db
from webapp.user.models import User
from webapp.admin.views import blueprint as admin_blueprint
from webapp.advert.views import blueprint as advert_blueprint
from webapp.user.views import blueprint as user_blueprint


# reff = '/'

#export FLASK_APP=webapp && export FLASK_ENV=development && flask run
#./run.sh
def create_app():
    app = Flask(__name__, static_url_path='', static_folder='static') #advert/images
    app.config.from_pyfile('config.py')
    db.init_app(app)
    migrate = Migrate(app, db)

    # photos = UploadSet('photos', IMAGES)
    # configure_uploads(app, photos)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'

    app.register_blueprint(admin_blueprint)
    app.register_blueprint(advert_blueprint)
    app.register_blueprint(user_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    # @app.route('/upload')

    return app
