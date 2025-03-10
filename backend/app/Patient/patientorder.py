from flask import Blueprint, current_app, jsonify, redirect, request
from app.models import OrderDetail, OrderItem, Patient, Doctor, Order
from app import db
from alipay import AliPay


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


# 初始化支付宝 SDK
def create_alipay():
    ALIPAY_CONFIG = current_app.config["ALIPAY_CONFIG"]
    return AliPay(
        appid=ALIPAY_CONFIG["APP_ID"],
        app_notify_url=ALIPAY_CONFIG["NOTIFY_URL"],
        app_private_key_string=open(ALIPAY_CONFIG["APP_PRIVATE_KEY_PATH"]).read(),
        alipay_public_key_string=open(ALIPAY_CONFIG["ALIPAY_PUBLIC_KEY_PATH"]).read(),
        sign_type="RSA2",
        debug=True,
    )


@patientorder.route("/alipay/pay", methods=["GET"])
def alipay_pay():
    # 获取前端传来的参数
    subject = request.args.get("subject")
    trade_no = request.args.get("tradeNo")
    total_amount = request.args.get("totalAmount")

    if not subject or not trade_no or not total_amount:
        return jsonify({"error": "缺少必要参数"})

    alipay = create_alipay()

    # 生成支付宝订单支付字符串
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=trade_no,
        total_amount=str(total_amount),
        subject=subject,
        return_url=current_app.config["ALIPAY_CONFIG"]["RETURN_URL"],
        notify_url=current_app.config["ALIPAY_CONFIG"]["NOTIFY_URL"],
    )

    # 拼接支付宝支付URL
    pay_url = f"https://openapi-sandbox.dl.alipaydev.com/gateway.do?{order_string}"
    # 重定向到支付宝支付页面
    return redirect(pay_url)

# 获取支付宝支付成功回调的参数
@patientorder.route("/pay_success")
def pay_success():
    out_trade_no = request.args.get("out_trade_no")
    total_amount = request.args.get("total_amount")
    # 如果验证通过，进行相应的操作，比如更新订单状态
    update_order_state(out_trade_no)
    return "支付成功，订单号: " + out_trade_no + ", 支付金额: " + total_amount + "元"

# 更新订单支付状态
def update_order_state(trade_no):
    order_item = OrderItem.query.filter_by(o_id=trade_no).first()
    print(order_item)
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
