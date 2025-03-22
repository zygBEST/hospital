from flask import Blueprint, jsonify, request

from app.Login.routes import hash_password
from ..models import Arrange, Doctor, DoctorDetails
from app import db

# 定义医生信息管理蓝图对象
doctorInfo = Blueprint("doctorInfo", __name__)


# 显示全部医生信息
@doctorInfo.route("/admin/findAllDoctors", methods=["GET"])
def find_all_doctors():
    page_number = request.args.get("pageNumber", type=int, default=1)
    size = request.args.get("size", type=int, default=10)
    query = request.args.get("query", default="")

    # 查询医生基本信息，并按状态排序
    doctors_query = Doctor.query.filter(Doctor.d_name.like(f"%{query}%")).order_by(
        Doctor.d_state.desc()
    )

    # 分页查询
    doctors_paginated = doctors_query.paginate(
        page=page_number, per_page=size, error_out=False
    )

    # 组合医生基本信息和详细信息
    result = {
        "total": doctors_paginated.total,
        "pages": doctors_paginated.pages,
        "pageNumber": doctors_paginated.page,
        "doctors": [
            {
                **doctor.to_dict(),
                "details": doctor.details.to_dict() if doctor.details else None,
            }
            for doctor in doctors_paginated.items
        ],
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

    # 创建医生账号
    new_doctor = Doctor(d_id=dId, d_password=hashed_password, d_name=dName, d_state=1)

    # 创建新的医生对象
    new_doctor_details = DoctorDetails(
        d_id=dId,
        d_name=dName,
        d_gender=dGender,
        d_phone=dPhone,
        d_card=dCard,
        d_email=dEmail,
        d_post=dPost,
        d_introduction=dIntroduction,
        d_section=dSection,
        d_price=dPrice,
        d_people=0,  # 初始评价人数
        d_star=0.0,  # 初始星级
        d_avg_star=0.0,  # 初始平均星级
    )

    # 将新医生保存到数据库
    db.session.add(new_doctor)
    db.session.add(new_doctor_details)
    db.session.commit()

    # 返回成功信息
    return jsonify({"status": 200, "message": "增加医生成功！"})


# 查询单个医生信息，用于管理员修改医生对话框
# 以及医生查询个人信息
@doctorInfo.route("/admin/findDoctor", methods=["POST"])
def find_doctor():
    d_id = request.json.get("dId")

    # 在数据库中查找医生
    doctor = Doctor.query.filter_by(d_id=d_id).first()
    doctor_details = DoctorDetails.query.filter_by(d_id=d_id).first()
    if not doctor:
        return jsonify({"status": 404, "message": "医生信息未找到"})

    # 合并数据
    doctor_info = doctor.to_dict()
    if doctor_details:
        doctor_info.update(doctor_details.to_dict())

    return jsonify({"status": 200, "message": "查询成功", "data": doctor_info})


# 修改医生信息
@doctorInfo.route("/admin/modifyDoctor", methods=["POST"])
def modify_doctor():
    # 获取 JSON 数据
    data = request.json
    d_id = data.get("dId")

    # 查找医生
    doctor = Doctor.query.filter_by(d_id=d_id).first()
    doctor_details = DoctorDetails.query.filter_by(d_id=d_id).first()

    if not doctor or not doctor_details:
        return jsonify({"status": 404, "message": "医生信息未找到"})

    # 映射 JSON 字段到数据库字段
    field_mapping = {
        "dGender": "d_gender",
        "dPost": "d_post",
        "dSection": "d_section",
        "dPhone": "d_phone",
        "dEmail": "d_email",
        "dCard": "d_card",
        "dPrice": "d_price",
        "dIntroduction": "d_introduction",
        "dState": "d_state",
        "dName": "d_name",
    }

    # 更新医生基础信息
    doctor.d_name = data.get("dName")
    doctor.d_state = data.get("dState")

    # 确保医生详细信息存在
    if not doctor.details:
        doctor.details = DoctorDetails(d_id=d_id)

    # 更新医生详细信息
    for json_key, db_field in field_mapping.items():
        if json_key in data and hasattr(doctor.details, db_field):
            setattr(doctor.details, db_field, data[json_key])

    db.session.commit()

    return jsonify({"status": 200, "message": "修改医生信息成功！"})


# 删除医生
@doctorInfo.route("/admin/deleteDoctor", methods=["POST"])
def delete_doctor():
    d_id = request.json.get("dId")

    # 检查是否有未完成的预约
    existing_appointments = Arrange.query.filter_by(d_id=d_id).first()
    if existing_appointments:
        return jsonify({"status": 403, "message": "该医生仍有关联数据，无法删除!"})

    # 查找医生
    doctor = Doctor.query.filter_by(d_id=d_id).first()
    doctor_details = DoctorDetails.query.filter_by(d_id=d_id).first()

    if not doctor:
        return jsonify({"status": 404, "message": "医生信息未找到"})

    # 删除医生和医生详情
    db.session.delete(doctor_details)
    db.session.delete(doctor)

    db.session.commit()

    return jsonify({"status": 200, "message": "删除医生成功！"})
