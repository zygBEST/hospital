# 查看当天挂号列表
from datetime import datetime
from flask import Blueprint, jsonify, request
from app import db
from app.models import Doctor, Order, Patient


ordertoday = Blueprint("ordertoday", __name__)
@ordertoday.route("/doctor/findOrderByToday", methods=["GET"])
def findOrderByToday():
    d_id = request.args.get("dId")  # 获取医生ID

    today = datetime.now().strftime("%Y-%m-%d")
    print(d_id, today)

    # 查询当天的订单
    orders = (
        db.session.query(Order, Patient.p_name, Doctor.d_name)
        .join(Patient, Order.p_id == Patient.p_id)  # 连接 Patient 表，获取 p_name
        .join(Doctor, Order.d_id == Doctor.d_id)  # 连接 Doctor 表，获取 d_name
        .filter(Order.d_id == d_id)  # 根据 d_id 过滤
        .filter(Order.o_start.like(f"{today}%"))  # 根据 o_start 过滤，确保是当天的订单
        .all()  # 执行查询
    )
    print(orders)

    # 简化返回数据，直接合并订单信息、患者姓名、医生姓名
    result = [
        {**order.to_dict(), "pName": p_name, "dName": d_name}
        for order, p_name, d_name in orders
    ]

    return jsonify({"status": 200, "msg": "查询成功", "data": result})