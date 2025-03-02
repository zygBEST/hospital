# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import secrets, redis

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
    from app.Admin.doctor import doctorInfo
    from app.Admin.patient import patientInfo
    from app.Doctor.doctorinfo import doctorinfo
    from app.Patient.patientinfo import patientinfo
    from app.Admin.drug import drugInfo
    from app.Admin.checks import checks
    from app.Admin.index import indexinfo
    from app.Admin.bed import bedinfo
    from app.Admin.arrange import arrangeinfo

    # 将所有蓝图存入列表
    blueprints = [
        Login,
        doctorInfo,
        patientInfo,
        doctorinfo,
        patientinfo,
        drugInfo,
        checks,
        indexinfo,
        bedinfo,
        arrangeinfo,
    ]

    # 统一注册蓝图
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app


# 连接redis服务器
redis_client = redis.Redis(
    host="127.0.0.1", port=6379, db=0, decode_responses=True
)  # 让返回结果自动解码成字符串
