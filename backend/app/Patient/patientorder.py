from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import Alipay, DoctorDetails, OrderDetail, OrderItem, Patient, Doctor, Order
from app import db, create_alipay


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

        # 查询订单项（药品和检查项）
        order_items = (
            db.session.query(OrderItem).filter(OrderItem.o_id == order.o_id).all()
        )

        # 查询支付记录
        alipay = (
            db.session.query(Alipay).filter(Alipay.o_id == order.o_id).first()
        )

        for item in order_items:
            result.append(
                {
                    **order.to_dict(),  # 使用 Order 模型的 to_dict 方法
                    "pName": p_name,  # 添加患者姓名
                    "dName": d_name,  # 添加医生姓名
                    "oTotalPrice": alipay.o_total_price,
                    "oPriceState": alipay.o_price_state,
                }
            )

    return jsonify({"status": 200, "msg": "查询成功", "data": result})


# 更新挂号支付状态
def update_order_state(o_id):
    alipay = Alipay.query.filter_by(o_id=o_id).first()
    if alipay:
        alipay.o_gh_alipay = "PAID"
        alipay.o_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 支付结束时间
        db.session.commit()
        return True
    else:
        return False


# 返回挂号支付状态（前端轮询模块）
@patientorder.route("/order/o_state", methods=["GET"])
def update_order_o_state():
    o_id = request.args.get("oId")
    alipay = Alipay.query.filter_by(o_id=o_id).first()
    if alipay:
        # 如果数据库已经标记支付成功，直接返回
        if alipay.o_gh_alipay == "PAID":
            return jsonify({"status": 200, "message": "PAID"})
        # 否则，主动查询支付宝订单状态
        o_id = f"gh{o_id}"  # 拼接 "gh" 前缀
        print(o_id)
        alipay_query = create_alipay()
        result = alipay_query.api_alipay_trade_query(out_trade_no=str(o_id))
        # 如果支付宝返回支付成功，更新数据库
        if result.get("trade_status") == "TRADE_SUCCESS":
            update_order_state(o_id[2:])
            return jsonify({"status": 200, "message": "PAID"})
        else:
            return jsonify({"status": 200, "message": "PENDING"})  # 等待支付
    else:
        return jsonify({"status": 400, "msg": "更新失败"})


# 更新订单支付状态
def update_order_item_state(trade_no):
    alipay = Alipay.query.filter_by(o_id=trade_no).first()
    if alipay:
        alipay.o_price_state = 1
        alipay.o_total_price = 0
        alipay.o_alipay = "PAID"
        alipay.o_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 支付结束时间
        db.session.commit()
        return True
    else:
        return False


# 返回订单支付状态（前端轮询模块）
@patientorder.route("/order/status", methods=["GET"])
def update_order_status():
    o_id = request.args.get("oId")
    alipay = Alipay.query.filter_by(o_id=o_id).first()
    if alipay:
        # 如果数据库已经标记支付成功，直接返回
        if alipay.o_alipay == "PAID":
            return jsonify({"status": 200, "message": "PAID"})
        # 否则，主动查询支付宝订单状态
        alipay_query = create_alipay()
        result = alipay_query.api_alipay_trade_query(out_trade_no=o_id)
        if result.get("trade_status") == "TRADE_SUCCESS":
            update_order_item_state(o_id)
            return jsonify({"status": 200, "message": "PAID"})
        else:
            message = "PENDING"
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
    doctor = DoctorDetails.query.filter_by(d_id=d_id).first()

    if not doctor:
        return jsonify({"status": 404, "msg": "医生不存在"})

    # 更新评分信息
    doctor.d_people += 1
    doctor.d_star += d_star
    doctor.d_avg_star = doctor.d_star / doctor.d_people

    # 提交数据库
    db.session.commit()

    return jsonify(
        {
            "status": 200,
            "message": "谢谢您的评价!",
            "data": {"d_avg_star": doctor.d_avg_star},
        }
    )
