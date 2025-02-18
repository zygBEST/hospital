# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import secrets

secret_key = secrets.token_hex(
    32
)  # 生成一个64个字符的十六进制字符串,如果没有会发出警告提示
# 创建 SQLAlchemy 实例
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # 数据库配置
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://root:123456@localhost/hospital"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = secret_key

    # 启用跨域
    CORS(app)

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    from app.Login.routes import Login
    from app.Order.routes import Order

    app.register_blueprint(Login)
    app.register_blueprint(Order)
    return app
