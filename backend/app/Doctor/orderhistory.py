# 创建历史挂号蓝图对象
from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from app.models import Order, OrderDetail, OrderItem, Patient
from app import db
from app.Patient.appoint import random_oid


orderhistory = Blueprint("orderhistory", __name__)


@orderhistory.route("/doctor/findOrderByDid", methods=["GET"])
def find_order_by_did():
    d_id = request.args.get("dId", type=int)
    page_number = request.args.get("pageNumber", type=int, default=1)
    size = request.args.get("size", type=int, default=10)
    query = request.args.get("query", default="")

    if not d_id:
        return jsonify({"status": 400, "msg": "缺少 dId 参数"})

    today = datetime.now().strftime("%Y-%m-%d")

    # 基础查询
    order_query = db.session.query(Order, Patient, OrderDetail, OrderItem) \
        .join(Patient, Order.p_id == Patient.p_id) \
        .join(OrderDetail, Order.o_id == OrderDetail.o_id) \
        .join(OrderItem, Order.o_id == OrderItem.o_id) \
        .filter(Order.d_id == d_id) \
        .filter(or_(Order.o_state == 1, Order.o_start < today)) \
        .order_by(Order.o_end.desc())

    # 如果有查询关键字，增加模糊查询
    if query:
        order_query = order_query.filter(Order.p_id.like(f"%{query}%"))

    # 分页查询
    paginated_orders = order_query.paginate(page=page_number, per_page=size, error_out=False)

    # 结果转换
    result = [
        {
            **order.to_dict(),
            "pName": patient.p_name,
            **order_detail.to_dict(),
            **order_item.to_dict(),
        }
        for order, patient, order_detail, order_item in paginated_orders.items
    ]

    return jsonify({
        "status": 200,
        "msg": "查询成功",
        "data": result,
        "total": paginated_orders.total,  # 总条数
        "pages": paginated_orders.pages,  # 总页数
        "pageNumber": paginated_orders.page, # 当前页
    })


@orderhistory.route("/doctor/updateOrderByAdd", methods=["POST"])
def update_order_by_add():
    data = request.json
    o_id = data.get("oId")
    o_advice = data.get("oAdvice")
    o_drug = data.get("oDrug")
    o_check = data.get("oCheck")
    o_total_price = data.get("oTotalPrice")

    if not o_id:
        return jsonify({"status": 400, "message": "订单 ID 不能为空"})
    
    # 查询主订单
    order = Order.query.filter_by(o_id=o_id).first()
    if not order:
        return jsonify({"status": 404, "message": "订单不存在"})
    
     # 查询订单详情表 OrderDetail
    order_detail = OrderDetail.query.filter_by(o_id=o_id).first()
    # 查询订单项表 OrderItem
    order_item = OrderItem.query.filter_by(o_id=o_id).first()

    # 更新主订单状态
    order.o_state = 1
    order.o_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 订单结束时间
    # 更新订单详情 OrderDetail
    order_detail.o_advice = o_advice

     # 更新订单项 OrderItem
    if order_item:  # 确保 order_item 不是 None
        order_item.o_drug = (order_item.o_drug or "") + (o_drug or "")
        order_item.o_check = (order_item.o_check or "") + (o_check or "")
        order_item.o_total_price = o_total_price
        order_item.o_price_state = 0
        order_item.o_alipay = "UNPAID"

    # 更新订单id以支持支付宝支付
    order.o_id = random_oid(order.o_id)
    order_item.o_id = order.o_id

    db.session.commit()

    return jsonify({"status": 200, "message": "订单更新成功"})
