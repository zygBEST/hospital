from flask import jsonify, request, current_app, Blueprint
from ..models import Patient, Admini, Doctor
from app import db
from datetime import datetime, timedelta, timezone
import jwt, bcrypt

# 定义登录注册蓝图对象
Login = Blueprint("Login", __name__)


# 密码加密函数
def hash_password(password):
    # 生成加盐的哈希密码
    salt = bcrypt.gensalt()
    print(f"盐：{salt}")
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")  # 返回字符串形式


def check_password(password, hashed_password):
    # 验证密码
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


# 患者注册
@Login.route("/patient/addPatient", methods=["POST"])
def add_patient():
    # 获取 JSON 数据
    data = request.json
    pId = data.get("pId")
    pName = data.get("pName")
    pPassword = data.get("pPassword")
    pGender = data.get("pGender")
    pEmail = data.get("pEmail")
    pPhone = data.get("pPhone")
    pCard = data.get("pCard")
    pBirthday = data.get("pBirthday")

    # 检查 email 或 p_id 是否已被注册
    existing_patient = Patient.query.filter(
        (Patient.p_email == pEmail) | (Patient.p_id == pId)
    ).first()
    print(f"检查邮箱和患者id: {pEmail} or id: {pId}")
    if existing_patient:
        return jsonify({"status": 402, "message": "账号或邮箱已被占用！"})

    # 计算年龄
    print(pBirthday)
    year_of_birth = int(pBirthday[:4])
    current_year = datetime.now().year  # 动态获取当前年份
    age = current_year - year_of_birth  # 计算年龄

    # 加密密码
    p_password = hash_password(pPassword)
    # 创建新患者对象
    new_patient = Patient(
        p_id=pId,
        p_name=pName,
        p_password=p_password,
        p_gender=pGender,
        p_email=pEmail,
        p_phone=pPhone,
        p_card=pCard,
        p_birthday=pBirthday,
        p_age=age,  # 设置年龄
        p_state=1,  # 设置状态为 1，表示注册状态
    )

    # 保存到数据库
    db.session.add(new_patient)
    db.session.commit()

    return jsonify({"status": 200, "message": "注册成功！"})


# token函数
def generate_token(user_id, user_role):
    # Token 过期时间设定
    expiration = datetime.now(timezone.utc) + timedelta(days=1)  # 1天后过期
    # Token 负载数据
    payload = {"user_id": user_id, "user_role": user_role, "exp": expiration}
    # 使用应用密钥加密生成 Token
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token


# 管理员登录
@Login.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.form
    a_id = data.get("aId")
    a_password = data.get("aPassword")
    user_role = data.get("user_role")
    print(f"用户角色: {user_role}")

    # 查找管理员
    admin = Admini.query.filter_by(a_id=a_id).first()
    if admin is None or admin.a_password != a_password:
        return jsonify({"status": 400, "message": "用户名或密码错误"})
    # 生成 token
    token = generate_token(admin.a_id, user_role)
    return jsonify({"status": 200, "message": "登录成功", "data": {"token": token}})


# 医生登录
@Login.route("/doctor/login", methods=["POST"])
def doctor_login():
    data = request.form
    d_id = data.get("dId")
    d_password = data.get("dPassword")
    user_role = data.get("user_role")
    print(f"用户角色: {user_role}")

    # 查找医生
    doctor = Doctor.query.filter_by(d_id=d_id).first()
    if doctor is None or not check_password(d_password, doctor.d_password):
        return jsonify({"status": 400, "message": "用户名或密码错误"})

    # 如果登录成功，生成 Token
    token = generate_token(doctor.d_id, user_role)

    # 返回成功的响应
    return jsonify({"status": 200, "message": "登录成功", "data": {"token": token}})


# 患者登录
@Login.route("/patient/login", methods=["POST"])
def patient_login():
    data = request.form
    p_id = data.get("pId")
    p_password = data.get("pPassword")
    user_role = data.get("user_role")
    print(f"用户角色: {user_role}")

    # 查找患者
    patient = Patient.query.filter_by(p_id=p_id).first()
    if patient is None or not check_password(p_password, patient.p_password):
        return jsonify({"status": 400, "message": "用户名或密码错误"})

    # 生成 token
    token = generate_token(patient.p_id, user_role)
    return jsonify({"status": 200, "message": "登录成功", "data": {"token": token}})


# 解析 Token 并获取用户信息
@Login.route("/getUserInfo", methods=["GET"])
def get_user_info():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"code": 401, "message": "未提供 Token"}), 401

    # 解析 token，获取 user_id和user_role
    try:
        token = token.split(" ")[1]
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        user_id = payload["user_id"]
        user_role = payload["user_role"]
        print(f"用户角色: {user_role}, 用户id: {user_id}")
    except jwt.ExpiredSignatureError:
        return jsonify({"code": 401, "message": "Token 已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"code": 401, "message": "无效的 Token"}), 401

    # 在数据库中查找用户
    user_name = None
    if user_role == "管理员":
        admin = Admini.query.filter_by(a_id=user_id).first()
        user_name = admin.a_name
        print(f"管理员: {user_name}")

    elif user_role == "医生":
        doctor = Doctor.query.filter_by(d_id=user_id).first()
        user_name = doctor.d_name

    elif user_role == "患者":
        patient = Patient.query.filter_by(p_id=user_id).first()
        user_name = patient.p_name

    return jsonify(
        {
            "status": 200,
            "data": {
                "userName": user_name,
                "role": user_role
            },
        }
    )


if __name__ == "__main__":
    Login.run(debug=True)
