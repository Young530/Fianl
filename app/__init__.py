# app/__init__.py
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import db, User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    login_manager.init_app(app)  # 初始化 Flask-Login
    migrate = Migrate(app, db)
    # 设置登录视图
    login_manager.login_view = 'main.login'

    # 定义 user_loader 回调函数
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # 从数据库中获取用户对象

    from . import routes
    app.register_blueprint(routes.bp)

    return app
