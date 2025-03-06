from flask import Blueprint, jsonify, request
from app.models import Patient, Doctor, Order
from app import db


# 定义我的挂号蓝图对象
patientorder = Blueprint("patientorder", __name__)


@patientorder.route("/patient/findOrderByPid", methods=["GET"])
def findOrderByPid():
    p_id = request.args.get("pId")
    orders = (
        db.session.query(Order, Patient.p_name, Doctor.d_name)
        .join(Patient, Order.p_id == Patient.p_id)  # 连接 Patient 表，获取 p_name
        .join(Doctor, Order.d_id == Doctor.d_id)  # 连接 Doctor 表，获取 d_name
        .filter(Order.p_id == p_id)  # 根据 p_id 过滤
        .order_by(Order.o_start.desc())  # 按 o_start 降序
        .all()
    )
    # 格式化返回的数据
    result = []
    for order, p_name, d_name in orders:
        result.append(
            {
                "oId": order.o_id,
                "pId": order.p_id,
                "pName": p_name,
                "dId": order.d_id,
                "dName": d_name,
                "oStart": order.o_start,
            }
        )
    return jsonify({"status": 200, "msg": "查询成功", "data": result})
