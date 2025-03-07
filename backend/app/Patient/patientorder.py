from flask import Blueprint, jsonify, request
from app.models import OrderDetail, OrderItem, Patient, Doctor, Order
from app import db


# 定义我的挂号蓝图对象
patientorder = Blueprint("patientorder", __name__)


@patientorder.route("/patient/findOrderByPid", methods=["GET"])
def findOrderByPid():
    p_id = request.args.get("pId")

    # 查询订单信息，并连接患者、医生表获取姓名
    orders = (
        db.session.query(Order, Patient.p_name, Doctor.d_name)
        .join(Patient, Order.p_id == Patient.p_id)  # 连接 Patient 表，获取 p_name
        .join(Doctor, Order.d_id == Doctor.d_id)  # 连接 Doctor 表，获取 d_name
        .filter(Order.p_id == p_id)  # 根据 p_id 过滤
        .order_by(Order.o_start.desc())  # 按 o_start 降序
        .all()
    )

    # 组织返回数据
    result = []
    for order, p_name, d_name in orders:
        # 查询订单详情（病历、医嘱等）
        order_detail = (
            db.session.query(OrderDetail).filter(OrderDetail.o_id == order.o_id).first()
        )

        # 查询订单项（药品和检查项）
        order_items = (
            db.session.query(OrderItem).filter(OrderItem.o_id == order.o_id).all()
        )

        # 使用 to_dict() 方法简化返回的数据
        result.append(
            {
                **order.to_dict(),  # 使用 Order 模型的 to_dict 方法
                "pName": p_name,     # 添加患者姓名
                "dName": d_name,     # 添加医生姓名
                "orderDetail": order_detail.to_dict() if order_detail else None,  # 使用 OrderDetail 模型的 to_dict 方法
                "orderItems": [item.to_dict() for item in order_items]  # 使用 OrderItem 模型的 to_dict 方法
            }
        )

    return jsonify({"status": 200, "msg": "查询成功", "data": result})
