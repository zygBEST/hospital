# 定义医生首页蓝图对象
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models import Order

index_info = Blueprint("index_info", __name__)


@index_info.route("/doctor/orderPeopleByDid", methods=["GET"])
def order_people():
    d_id = request.args.get("dId")
    today = datetime.now().strftime("%Y-%m-%d")  # 获取今天的日期

    # 查询属于今天并且属于当前 d_id 的订单数量
    print(d_id, today)
    count = Order.query.filter(
        Order.o_start.like(f"{today}%"),  # 过滤出今天的订单
        Order.d_id == d_id,  # 过滤出指定 d_id 的订单
    ).count()
    return jsonify({"status": 200, "msg": "查询成功", "data": count})
