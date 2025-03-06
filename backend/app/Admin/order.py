# 导入挂号信息管理蓝图对象
from flask import Blueprint, jsonify, request

from app.models import Order
from app import db


orderinfo = Blueprint("orderinfo", __name__)


# 显示所有挂号信息
@orderinfo.route("/admin/findAllOrders", methods=["GET"])
def find_all_orders():
    page_number = request.args.get("pageNumber", type=int, default=1)
    size = request.args.get("size", type=int, default=10)
    query = request.args.get("query", default="")

    orders_query = Order.query.filter(Order.p_id.like(f"%{query}%")).order_by(
        Order.o_start.desc()
    )
    orders_paginated = orders_query.paginate(
        page=page_number, per_page=size, error_out=False
    )

    result = {
        "total": orders_paginated.total,
        "pages": orders_paginated.pages,
        "pageNumber": orders_paginated.page,
        "orders": [order.to_dict() for order in orders_paginated.items],
    }

    return jsonify({"code": 200, "msg": "查询成功", "data": result})


# 删除挂号信息
@orderinfo.route("/admin/deleteOrder", methods=["GET"])
def delete_order():
    o_id = request.args.get("oId")
    order = Order.query.filter_by(o_id=o_id).first()
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({"status": 200, "msg": "删除成功"})
    else:
        return jsonify({"status": 400, "msg": "删除失败"})
