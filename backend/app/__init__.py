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

    # 支付宝沙箱环境配置
    app.config["ALIPAY_CONFIG"] = {
        "APP_ID": "9021000141650869",
        "APP_PRIVATE_KEY_PATH": "alipay\私钥数据.txt",
        "ALIPAY_PUBLIC_KEY_PATH": "alipay\公钥数据.txt",
        "GATEWAY_URL": "https://openapi.alipaydev.com/gateway.do",  # 支付宝沙箱网关
        "RETURN_URL": "http://localhost:5000/pay_success",  # 支付成功后跳转
        "NOTIFY_URL": "http://localhost:5000/notify",  # 支付宝异步通知URL
    }

    # 注册蓝图
    from app.Login.routes import Login
    from app.Admin.doctor import doctorInfo
    from app.Admin.patient import patientInfo
    from app.Admin.drug import drugInfo
    from app.Admin.checks import checks
    from app.Admin.index import indexinfo
    from app.Admin.bed import bedinfo
    from app.Admin.arrange import arrangeinfo
    from app.Admin.order import orderinfo
    from app.Doctor.doctorinfo import doctorinfo
    from app.Patient.patientinfo import patientinfo
    from app.Patient.appoint import appoint
    from app.Patient.patientorder import patientorder
    from app.Doctor.index import index_info
    from app.Doctor.ordertoday import ordertoday
    from app.Doctor.orderhistory import orderhistory

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
        appoint,
        orderinfo,
        patientorder,
        index_info,
        ordertoday,
        orderhistory,
    ]

    # 统一注册蓝图
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app


# 连接redis服务器
redis_client = redis.Redis(
    host="127.0.0.1", port=6379, db=0, decode_responses=True
)  # 让返回结果自动解码成字符串
