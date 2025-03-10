# 定义挂号完成蓝图列表
from datetime import datetime
from flask import Blueprint, jsonify, request

from app.models import Bed, Order, PBed
from app import db


orderfinish = Blueprint("orderfinish", __name__)

# 查询挂号完成列表
@orderfinish.route("/doctor/findOrderFinish", methods=["GET"])
def find_order_finish():
    d_id = request.args.get("dId", type=int)
    page_number = request.args.get("pageNumber", type=int, default=1)
    size = request.args.get("size", type=int, default=10)
    query = request.args.get("query", default="")

    if not d_id:
        return jsonify({"code": 400, "msg": "医生 ID 不能为空"})

    # 构建查询
    order_query = (
        db.session.query(Order)
        .filter(Order.d_id == d_id)
        .filter(Order.o_state == 1)  # 只查询已完成的订单
    )

    # 如果有查询关键字，增加模糊查询
    if query:
        order_query = order_query.filter(Order.p_id.like(f"%{query}%"))

    # 分页查询
    paginated_orders = order_query.paginate(page=page_number, per_page=size, error_out=False)

    # 结果封装
    orders = {
        "total": paginated_orders.total,
        "pages": paginated_orders.pages,
        "pageNumber": paginated_orders.page,
        "data": [order.to_dict() for order in paginated_orders.items],
    }

    return jsonify({"status": 200, "msg": "查询成功", "data": orders})

# 查询空床位
@orderfinish.route("/doctor/findNullBed", methods=["GET"])
def find_null_bed():
    beds = db.session.query(Bed).filter(Bed.b_state == 0).all()
    return jsonify({"status":200, "msg": "查询成功", "data": [bed.to_dict() for bed in beds]})

# 更新床位
@orderfinish.route("/doctor/updateBed", methods=["POST"])
def update_bed():
    data = request.get_json()
    b_id = data.get("bId")
    d_id = data.get("dId")
    p_id = data.get("pId")
    b_reason = data.get("bReason")
    b_start = datetime.now().strftime("%Y-%m-%d %H:%M")

    existing_bed = Bed.query.filter(Bed.b_id == b_id).first()
    if existing_bed:
        existing_bed.d_id = d_id
        existing_bed.p_id = p_id
        existing_bed.b_reason = b_reason
        existing_bed.b_start = b_start
        existing_bed.b_state = 1
        existing_bed.b_end = None
        db.session.commit()

    new_p_bed = PBed(b_id=b_id, d_id=d_id, p_id=p_id, b_reason=b_reason, b_start=b_start, b_end=None)
    db.session.add(new_p_bed)
    db.session.commit()

    return jsonify({"status": 200, "msg": "更新成功"})
