# 导入挂号信息管理蓝图对象
from flask import Blueprint, jsonify, request

from app.models import Order, OrderDetail, OrderItem, Patient
from app import db


orderinfo = Blueprint("orderinfo", __name__)


# 显示所有挂号信息
@orderinfo.route("/admin/findAllOrders", methods=["GET"])
def find_all_orders():
    page_number = request.args.get("pageNumber", type=int, default=1)
    size = request.args.get("size", type=int, default=10)
    query = request.args.get("query", default="")

    # 关联查询 Order、OrderDetail、OrderItem
    orders_query = (
        db.session.query(Order, OrderDetail, OrderItem)
        .join(OrderDetail, Order.o_id == OrderDetail.o_id)  # 关联订单详情表
        .join(OrderItem, Order.o_id == OrderItem.o_id)  # 关联订单项目表
        .filter(Order.p_id.like(f"%{query}%"))  # 可选的搜索条件
        .order_by(Order.o_end.desc())
    )

    # 分页
    orders_paginated = orders_query.paginate(
        page=page_number, per_page=size, error_out=False
    )

    # 处理查询结果，将 Order、OrderDetail、OrderItem 合并到同一层级
    orders_list = []
    for order, order_detail, order_item in orders_paginated.items:
        orders_list.append(
            {
                "oId": order.o_id,
                "pId": order.p_id,
                "dId": order.d_id,
                "oStart": order.o_start,
                "oEnd": order.o_end,
                "oRecord": order_detail.o_record,
                "oDrug": order_item.o_drug,
                "oCheck": order_item.o_check,
                "oTotalPrice": order_item.o_total_price,
                "oPriceState": order_item.o_price_state,
                "oState": order.o_state,
            }
        )

    # 返回数据
    result = {
        "total": orders_paginated.total,
        "pages": orders_paginated.pages,
        "pageNumber": orders_paginated.page,
        "orders": orders_list,
    }

    return jsonify({"status": 200, "msg": "查询成功", "data": result})


# 删除挂号信息
@orderinfo.route("/admin/deleteOrder", methods=["GET"])
def delete_order():
    o_id = request.args.get("oId")
    print(o_id)
    order_detail = OrderDetail.query.filter_by(o_id=o_id).first()
    order_item = OrderItem.query.filter_by(o_id=o_id).first()
    order = Order.query.filter_by(o_id=o_id).first()
    db.session.delete(order_detail)
    db.session.delete(order_item)
    db.session.delete(order)
    db.session.commit()

    return jsonify({"status": 200, "msg": "删除成功"})
