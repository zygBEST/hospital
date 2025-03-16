from flask import Blueprint, jsonify, request

from app.Login.routes import hash_password
from ..models import Arrange, Doctor
from app import db

# 定义医生信息管理蓝图对象
doctorInfo = Blueprint("doctorInfo", __name__)


# 显示全部医生信息
@doctorInfo.route("/admin/findAllDoctors", methods=["GET"])
def find_all_doctors():
    page_number = request.args.get("pageNumber", type=int, default=1)
    size = request.args.get("size", type=int, default=10)
    query = request.args.get("query", default="")

    doctors_query = Doctor.query.filter(Doctor.d_name.like(f"%{query}%")).order_by(
        Doctor.d_state.desc()
    )
    doctors_paginated = doctors_query.paginate(
        page=page_number, per_page=size, error_out=False
    )

    result = {
        "total": doctors_paginated.total,
        "pages": doctors_paginated.pages,
        "pageNumber": doctors_paginated.page,
        "doctors": [doctor.to_dict() for doctor in doctors_paginated.items],
    }

    return jsonify({"code": 200, "msg": "查询成功", "data": result})


# 添加医生
@doctorInfo.route("/admin/addDoctor", methods=["POST"])
def add_doctor():
    # 获取 JSON 数据
    data = request.json
    dId = data.get("dId")
    dGender = data.get("dGender")
    dPassword = str(data.get("dPassword"))
    dName = data.get("dName")
    dPost = data.get("dPost")
    dSection = data.get("dSection")
    dPhone = data.get("dPhone")
    dEmail = data.get("dEmail")
    dCard = data.get("dCard")
    dPrice = data.get("dPrice")
    dIntroduction = data.get("dIntroduction")

    # 检查是否已经存在相同的医生ID
    existing_doctor = Doctor.query.filter(Doctor.d_id == dId).first()
    if existing_doctor:
        return jsonify({"status": 402, "message": "账号或邮箱已被占用！"})

    # 加密密码
    hashed_password = hash_password(dPassword)

    # 创建新的医生对象
    new_doctor = Doctor(
        d_id=dId,
        d_gender=dGender,
        d_password=hashed_password,
        d_name=dName,
        d_post=dPost,
        d_section=dSection,
        d_phone=dPhone,
        d_email=dEmail,
        d_card=dCard,
        d_price=dPrice,
        d_introduction=dIntroduction,
        d_state=1,  # 默认状态
        d_star=0.00,  # 默认星级
        d_people=0,  # 默认评价人数
    )

    # 将新医生保存到数据库
    db.session.add(new_doctor)
    db.session.commit()

    # 返回成功信息
    return jsonify({"status": 200, "message": "增加医生成功！"})


# 查询单个医生信息，用于管理员修改医生对话框
@doctorInfo.route("/admin/findDoctor", methods=["POST"])
def find_doctor():
    d_id = request.json.get("dId")

    # 在数据库中查找医生
    doctor = Doctor.query.filter_by(d_id=d_id).first()
    if not doctor:
        return jsonify({"status": 404, "message": "医生信息未找到"})

    # 返回医生信息
    return jsonify({"status": 200, "message": "查询成功", "data": doctor.to_dict()})


# 修改医生信息
@doctorInfo.route("/admin/modifyDoctor", methods=["POST"])
def modify_doctor():
    # 获取 JSON 数据
    data = request.json
    d_id = data.get("dId")
    d_gender = data.get("dGender")
    d_name = data.get("dName")
    d_post = data.get("dPost")
    d_section = data.get("dSection")
    d_phone = data.get("dPhone")
    d_email = data.get("dEmail")
    d_card = data.get("dCard")
    d_price = data.get("dPrice")
    d_introduction = data.get("dIntroduction")
    d_state = data.get("dState")
    # 查找医生
    doctor = Doctor.query.filter_by(d_id=d_id).first()

    if not doctor:
        return jsonify({"status": 404, "message": "医生信息未找到"})

    # 更新医生信息
    doctor.d_gender = d_gender
    doctor.d_name = d_name
    doctor.d_post = d_post
    doctor.d_section = d_section
    doctor.d_phone = d_phone
    doctor.d_email = d_email
    doctor.d_card = d_card
    doctor.d_price = d_price
    doctor.d_introduction = d_introduction
    doctor.d_state = d_state

    # 提交到数据库
    db.session.commit()

    return jsonify({"status": 200, "message": "修改医生信息成功！"})


# 删除医生
@doctorInfo.route("/admin/deleteDoctor", methods=["POST"])
def delete_doctor():
    d_id = request.json.get("dId")
    # 检查该医生是否有关联数据（例如：检查是否有未完成的预约）
    existing_appointments = Arrange.query.filter_by(d_id=d_id).first()
    if existing_appointments:
        return jsonify({"status": 403, "message": "该医生仍有关联数据，无法删除!"})

    # 查找医生
    doctor = Doctor.query.filter_by(d_id=d_id).first()

    if not doctor:
        return jsonify({"status": 404, "message": "医生信息未找到"})
    # 从数据库中删除医生
    db.session.delete(doctor)
    db.session.commit()

    return jsonify({"status": 200, "message": "删除医生成功！"})


