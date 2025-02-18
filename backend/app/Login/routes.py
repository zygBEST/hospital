from flask import jsonify, request, current_app, Blueprint
from ..models import Patient, Admini, Doctor
from app import db
from datetime import datetime, timedelta, timezone
import jwt, bcrypt

# 定义登录蓝图对象
Login = Blueprint("Login", __name__)


# 密码加密函数
def hash_password(password):
    # 生成加盐的哈希密码
    salt = bcrypt.gensalt()
    print(f"盐：{salt}")
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')  # 返回字符串形式
def check_password(password, hashed_password):
    # 验证密码
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


# 路由测试
@Login.route("/hello")
def hello():
    return "hello1"


# 患者注册
@Login.route("/patient/addPatient", methods=["POST"])
def add_patient():
    # 获取 JSON 数据
    data = request.json
    p_id = data.get("pId")
    p_name = data.get("pName")
    p_password = data.get("pPassword")
    p_gender = data.get("pGender")
    p_email = data.get("pEmail")
    p_phone = data.get("pPhone")
    p_card = data.get("pCard")
    p_birthday = data.get("pBirthday")

    # 检查 email 或 p_id 是否已被注册
    existing_patient = Patient.query.filter(
        (Patient.p_email == p_email) | (Patient.p_id == p_id)
    ).first()
    print(f"检查邮箱和患者id: {p_email} or id: {p_id}")
    if existing_patient:
        # "message"用于控制台输出
        return jsonify({"status": 402, "message": "账号或邮箱已被占用！"})

    # 计算年龄
    print(p_birthday)
    year_of_birth = int(p_birthday[:4])
    current_year = datetime.now().year  # 动态获取当前年份
    age = current_year - year_of_birth  # 计算年龄

    # 加密密码
    p_password = hash_password(p_password)
    # 创建新患者对象
    new_patient = Patient(
        p_id=p_id,
        p_name=p_name,
        p_password=p_password,
        p_gender=p_gender,
        p_email=p_email,
        p_phone=p_phone,
        p_card=p_card,
        p_birthday=p_birthday,
        p_age=age,  # 设置年龄
        p_state=1,  # 设置状态为 1，表示注册状态
    )

    # 保存到数据库
    db.session.add(new_patient)
    db.session.commit()

    return jsonify({"status": 200, "message": "注册成功！"})


# token函数
def generate_token(user_id):
    # Token 过期时间设定
    expiration = datetime.now(timezone.utc) + timedelta(days=1)  # 1天后过期
    # Token 负载数据
    payload = {"user_id": user_id, "exp": expiration}
    # 使用应用密钥加密生成 Token
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token


# 管理员登录
@Login.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.form
    a_id = data.get("aId")
    a_password = data.get("aPassword")

    # 查找管理员
    admin = Admini.query.filter_by(a_id=a_id).first()
    if admin is None or admin.a_password != a_password:
        return jsonify({"status": 400, "message": "用户名或密码错误"})
    # 生成 token
    token = generate_token(admin.a_id)
    return jsonify({"status": 200, "message": "登录成功", "data": {"token": token}})


# 医生登录
@Login.route("/doctor/login", methods=["POST"])
def doctor_login():
    data = request.form
    d_id = data.get("dId")
    d_password = data.get("dPassword")

    # 查找医生
    doctor = Doctor.query.filter_by(d_id=d_id).first()
    if doctor is None or doctor.d_password != d_password:
        return jsonify({"status": 400, "message": "用户名或密码错误"})

    # 如果登录成功，生成 Token
    token = generate_token(doctor.d_id)

    # 返回成功的响应
    return jsonify({"status": 200, "message": "登录成功", "data": {"token": token}})


# 患者登录
@Login.route("/patient/login", methods=["POST"])
def patient_login():
    data = request.form
    p_id = data.get("pId")
    p_password = data.get("pPassword")

    # 查找患者
    patient = Patient.query.filter_by(p_id=p_id).first()
    if patient is None or not check_password(p_password, patient.p_password):
        return jsonify({"status": 400, "message": "用户名或密码错误"})

    # 生成 token
    token = generate_token(patient.p_id)
    return jsonify({"status": 200, "message": "登录成功", "data": {"token": token}})

# 解析 Token 并获取用户信息
@Login.route("/getUserInfo", methods=["GET"])
def get_user_info():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"status": 401, "message": "未提供 Token"}), 401
    
    try:
        token = token.split("Bearer ")[1]  # 提取 token
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        user_id = payload["user_id"]  # 解析 token 获取 user_id
    except jwt.ExpiredSignatureError:
        return jsonify({"status": 401, "message": "Token 已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"status": 401, "message": "Token 无效"}), 401
    # 在数据库中查找用户
    user = None
    user_role = ""
    user_name = ""

    # 依次查找管理员、医生、患者
    admin = Admini.query.filter_by(a_id=user_id).first()
    doctor = Doctor.query.filter_by(d_id=user_id).first()
    patient = Patient.query.filter_by(p_id=user_id).first()
    
    if admin:
        user = admin
        user_role = "管理员"
        user_name = user.a_name
    elif doctor:
        user = doctor
        user_role = "医生"
        user_name = user.d_name
    elif patient:
        user = patient
        user_role = "患者"
        user_name = user.p_name
        
    if not user:
        return jsonify({"status": 404, "message": "用户不存在"}), 404

    return jsonify({
        "status": 200,
        "data": {
            "userName": user_name
        }
    })

if __name__ == "__main__":
    Login.run(debug=True)
