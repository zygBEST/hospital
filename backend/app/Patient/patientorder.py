from flask import Blueprint, current_app, jsonify, redirect, request
from app.models import OrderDetail, OrderItem, Patient, Doctor, Order
from app import db


# 定义我的挂号蓝图对象
patientorder = Blueprint("patientorder", __name__)

# 查询订单信息，并连接患者、医生表获取姓名
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

        for item in order_items:
            result.append(
                {
                    **order.to_dict(),  # 使用 Order 模型的 to_dict 方法
                    "pName": p_name,  # 添加患者姓名
                    "dName": d_name,  # 添加医生姓名
                    "oRecord": (order_detail.o_record if order_detail else None),
                    "oTotalPrice": item.o_total_price,  # 直接展开订单项的字段
                    "oPriceState": item.o_price_state,
                    "oCheck": item.o_check,
                    "oDrug": item.o_drug,
                }
            )

    return jsonify({"status": 200, "msg": "查询成功", "data": result})


# 更新挂号状态
def update_order_state(o_id):
    order = Order.query.filter_by(o_id=o_id).first()
    if order:
        order.o_alipay = "PAID"
        db.session.commit()
        return True
    else:
        return False

# 更新前端页面显示的挂号结果
@patientorder.route("/order/o_state", methods=["GET"])
def update_order_o_state():
    o_id = request.args.get("oId")
    print(o_id)
    order = Order.query.filter_by(o_id=o_id).first()
    if order:
        message = order.o_alipay
        return jsonify({"status": 200, "message": message})
    else:
        return jsonify({"status": 400, "msg": "更新失败"})

# 更新订单支付状态
def update_order_item_state(trade_no):
    order_item = OrderItem.query.filter_by(o_id=trade_no).first()
    if order_item:
        order_item.o_price_state = 1
        order_item.o_total_price = 0
        order_item.o_alipay = "PAID"
        db.session.commit()
        return True
    else:
        return False


# 更新前端页面显示的订单状态
@patientorder.route("/order/status", methods=["GET"])
def update_order_status():
    o_id = request.args.get("oId")
    order_item = OrderItem.query.filter_by(o_id=o_id).first()
    if order_item:
        message = order_item.o_alipay
        return jsonify({"status": 200, "message": message})
    else:
        return jsonify({"status": 400, "msg": "更新失败"})
    

# 更新医生评分
@patientorder.route("/doctor/updateStar", methods=["GET"])
def update_star():
    d_id = request.args.get("dId")
    d_star = request.args.get("dStar", type=int)

    if not d_id or d_star is None:
        return jsonify({"status": 400, "msg": "参数缺失"})

    # 查询医生信息
    doctor = Doctor.query.filter_by(d_id=d_id).first()
    
    if not doctor:
        return jsonify({"status": 404, "msg": "医生不存在"})

    # 更新评分信息
    doctor.d_people += 1
    doctor.d_star += d_star
    doctor.d_avg_star = doctor.d_star / doctor.d_people

    # 提交数据库
    db.session.commit()

    return jsonify({"status": 200, "message": "谢谢您的评价!", "data": {"d_avg_star": doctor.d_avg_star}})