# __init__.py
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import secrets, redis
from alipay import AliPay

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
        "RETURN_URL": "http://localhost:5000/alipay/pay_success",  # 支付成功后跳转
        "NOTIFY_URL": "http://agtzbv.natappfree.cc/alipay/notify",  # 支付宝异步通知URL
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
    from app.Doctor.orderfinish import orderfinish
    from app.Patient.bedinfo import pbedinfo
    from app.Admin.dataExpore import dataExpore
    from app.Patient.alipay import alipay
    from app.Patient.AIchat import AIchat
    from app.Patient.pdf import pdf

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
        orderfinish,
        pbedinfo,
        dataExpore,
        alipay,
        AIchat,
        pdf,
    ]

    # 统一注册蓝图
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app


# 初始化支付宝 SDK
def create_alipay():
    ALIPAY_CONFIG = current_app.config["ALIPAY_CONFIG"]
    return AliPay(
        appid=ALIPAY_CONFIG["APP_ID"],
        app_notify_url=ALIPAY_CONFIG["NOTIFY_URL"],
        app_private_key_string=open(ALIPAY_CONFIG["APP_PRIVATE_KEY_PATH"]).read(),
        alipay_public_key_string=open(ALIPAY_CONFIG["ALIPAY_PUBLIC_KEY_PATH"]).read(),
        sign_type="RSA2",
        debug=True,
    )


# 连接redis服务器
redis_client = redis.Redis(
    host="127.0.0.1", port=6379, db=0, decode_responses=True
)  # 让返回结果自动解码成字符串
