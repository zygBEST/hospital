# 创建管理员首页蓝图对象
from datetime import datetime
from flask import Blueprint, jsonify, request

from app.models import Order


indexinfo = Blueprint("index", __name__)


# 统计今天挂号人数
@indexinfo.route("/admin/orderPeople", methods=["GET"])
def order_people():
    today = datetime.now().strftime("%Y-%m-%d")  # 获取今天的日期
    print(today)
    count = Order.query.filter(Order.o_start.like(f"{today}%")).count()
    return jsonify({"status": 200, "message": "统计今天挂号人数成功", "data": count})