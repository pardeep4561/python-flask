from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_s3 import FlaskS3
from flask_migrate import Migrate

db = SQLAlchemy()
s3 = FlaskS3()


def create_app(DB_NAME, db):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    ACCESS_ID = 'QPHTN5KR6NLVV6JRNPMG'
    SECRET_KEY = '6fXDDDfMtWPPNUBDJDYnwH8Xouh66mi0OLBZTbus8cA'

    app.config['AWS_ACCESS_KEY_ID'] = ACCESS_ID
    app.config['AWS_SECRET_ACCESS_KEY'] = SECRET_KEY
    app.config['FLASKS3_BUCKET_DOMAIN'] = 'ams3.digitaloceanspaces.com'
    app.config['FLASKS3_BUCKET_NAME'] = 'pose-app'
    app.config['JWT_SECRET_KEY'] = "6fXDDDfMtWPPNUBDJDYnwH8Xouh66mi0OLBZTbus8cA"
    s3.init_app(app)

    from .views import views
    from .auth import auth
    from .api import api
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(api, url_prefix="/api")

    from .models import User

    # create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app, db):
    DB_NAME = "database.db"
    if not path.exists(DB_NAME):

        with app.app_context():
            # db.drop_all(app=app)
            # db.create_all(app=app)
            #  db.create_all(app=app)
            db.create_all()
            # print('Created Database!')


# app = create_app(DB_NAME)
# create_database(app)
