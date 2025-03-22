# 创建历史挂号蓝图对象
from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from app.models import Alipay, Order, OrderDetail, OrderItem, Patient
from app import db
from app.Patient.appoint import random_oid


orderhistory = Blueprint("orderhistory", __name__)


# 查询历史挂号列表
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
    order_query = (
        db.session.query(
            Order,
            Patient,
            Alipay,
            OrderDetail,
            OrderItem,
        )
        .join(Patient, Order.p_id == Patient.p_id)
        .join(OrderDetail, Order.o_id == OrderDetail.o_id)
        .join(OrderItem, Order.o_id == OrderItem.o_id)
        .join(Alipay, Order.o_id == Alipay.o_id)
        .filter(Order.d_id == d_id)
        .filter(or_(Order.o_state == 1, Order.o_start < today))
        .order_by(Order.o_end.desc())
    )

    # 如果有查询关键字，增加模糊查询
    if query:
        order_query = order_query.filter(Order.p_id.like(f"%{query}%"))

    # 分页查询
    paginated_orders = order_query.paginate(
        page=page_number, per_page=size, error_out=False
    )

    # 结果转换
    result = [
        {
            **order.to_dict(),
            "pName": patient.p_name,
            "TotalPrice": alipay.o_total_price,
            **alipay.to_dict(),
            **order_detail.to_dict(),
            **order_item.to_dict(),
        }
        for order, patient, alipay, order_detail, order_item in paginated_orders.items
    ]

    return jsonify(
        {
            "status": 200,
            "msg": "查询成功",
            "data": result,
            "total": paginated_orders.total,  # 总条数
            "pages": paginated_orders.pages,  # 总页数
            "pageNumber": paginated_orders.page,  # 当前页
        }
    )


# 追诊
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

    # 查询相关表
    order_detail = OrderDetail.query.filter_by(o_id=o_id).first()
    order_item = OrderItem.query.filter_by(o_id=o_id).first()
    alipay = Alipay.query.filter_by(o_id=o_id).first()

    if not all([order_detail, order_item, alipay]):
        return jsonify({"status": 404, "message": "相关表数据不存在"})

    try:
        # 更新主订单状态
        order.o_state = 1
        order.o_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 更新订单详情 OrderDetail
        if o_advice:
            order_detail.o_advice = o_advice

        # 更新订单项 OrderItem
        if o_drug:
            order_item.o_drug = (order_item.o_drug or "") + o_drug
        if o_check:
            order_item.o_check = (order_item.o_check or "") + o_check
        if o_total_price is not None:
            order_item.o_total_price = o_total_price

        # 生成新 o_id 并更新（触发 CASCADE）
        new_o_id = random_oid(order.o_id)
        print(f"新 o_id: {new_o_id}")

        # 确保新 o_id 没有重复
        existing_order = Order.query.filter_by(o_id=new_o_id).first()
        if existing_order:
            return jsonify({"status": 500, "message": "生成的 new_o_id 已存在，可能导致更新失败"})

        # 先更新主订单 o_id
        order.o_id = new_o_id

        # 先提交 o_id 变更，让 CASCADE 生效
        db.session.commit()

        # 确保 Alipay 的 o_id 也被更新
        alipay_updated = Alipay.query.filter_by(o_id=new_o_id).first()
        if not alipay_updated:
            return jsonify({"status": 500, "message": "CASCADE 更新失败，Alipay 记录未找到"})

        # 继续更新 Alipay 记录
        if o_total_price is not None:
            alipay_updated.o_total_price = o_total_price
            alipay_updated.o_price_state = 0
            alipay_updated.o_alipay = "UNPAID"

        # 提交所有修改
        db.session.commit()

        return jsonify({"status": 200, "message": "订单更新成功"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "message": f"更新失败: {str(e)}"})




