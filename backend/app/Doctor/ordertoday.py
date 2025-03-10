# 查看当天挂号列表
from datetime import datetime
from flask import Blueprint, jsonify, request
from app import db
from app.Admin.checks import find_all_checks
from app.models import Doctor, Order, OrderDetail, OrderItem, Patient


ordertoday = Blueprint("ordertoday", __name__)
# 查询当天的挂号
@ordertoday.route("/doctor/findOrderByToday", methods=["GET"])
def findOrderByToday():
    d_id = request.args.get("dId")  # 获取医生ID
    today = datetime.now().strftime("%Y-%m-%d")

    # 查询当天的订单
    orders = (
        db.session.query(Order, Patient.p_name, Doctor.d_name)
        .join(Patient, Order.p_id == Patient.p_id)  # 连接 Patient 表，获取 p_name
        .join(Doctor, Order.d_id == Doctor.d_id)  # 连接 Doctor 表，获取 d_name
        .filter(Order.d_id == d_id)  # 根据 d_id 过滤
        .filter(Order.o_start.like(f"{today}%"))  # 根据 o_start 过滤，确保是当天的订单
        .all()  # 执行查询
    )

    # 简化返回数据，直接合并订单信息、患者姓名、医生姓名
    result = [
        {**order.to_dict(), "pName": p_name, "dName": d_name}
        for order, p_name, d_name in orders
    ]

    return jsonify({"status": 200, "msg": "查询成功", "data": result})

# 创建挂号订单
@ordertoday.route("/doctor/updateOrder", methods=["POST"])
def update_order():
    try:
        data = request.get_json()
        o_id = data.get("oId")
        o_record = data.get("oRecord")
        o_drug = data.get("oDrug")
        o_check = data.get("oCheck")
        o_total_price = data.get("oTotalPrice")

        # 查询主订单
        order = Order.query.filter_by(o_id=o_id).first()
        if not order:
            return jsonify({"status": 400, "msg": "订单不存在"})

        # 查询订单详情表 OrderDetail
        order_detail = OrderDetail.query.filter_by(o_id=o_id).first()
        if not order_detail:
            order_detail = OrderDetail(o_id=o_id)  # 如果没有，创建新的详情对象
            db.session.add(order_detail)

        # 查询订单项表 OrderItem
        order_item = OrderItem.query.filter_by(o_id=o_id).first()
        if not order_item:
            order_item = OrderItem(o_id=o_id)  # 如果没有，创建新的订单项对象
            db.session.add(order_item)

        # 更新主订单 Order
        order.o_state = 1  # 订单状态修改为已提交
        order.o_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 结束时间

        # 更新订单详情 OrderDetail
        order_detail.o_record = o_record

        # 更新订单项 OrderItem
        order_item.o_drug = o_drug
        order_item.o_check = o_check
        order_item.o_total_price = o_total_price

        # 提交数据库事务
        db.session.commit()

        return jsonify({"status": 200, "msg": "订单及关联信息更新成功"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "msg": "服务器错误", "error": str(e)})