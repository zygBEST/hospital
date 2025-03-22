# 定义医生首页蓝图对象
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import and_
from app.models import Arrange, Order

index_info = Blueprint("index_info", __name__)


# 统计今天挂号人数
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


# 查询自己的排班情况
@index_info.route("/doctor/arrangeByDid", methods=["GET"])
def schedule_people():
    d_id = request.args.get("dId")
    today = datetime.now().strftime("%Y-%m-%d")  # 获取今天的日期
    # 查询今天及以后的排班信息
    arranges = Arrange.query.filter(
        and_(Arrange.d_id == d_id, Arrange.ar_time >= today)
    ).all()

    # 将查询结果转换为 JSON 格式
    result = [
        {
            "d_id": s.d_id,
            "ar_time": s.ar_time,
        }
        for s in arranges
    ]

    return jsonify({"status": 200, "msg": "查询成功", "data": result})
