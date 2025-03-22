# 创建管理员首页蓝图对象
from datetime import datetime
from flask import Blueprint, jsonify
from sqlalchemy import or_

from app.models import Bed, Order
from app import db


indexinfo = Blueprint("index", __name__)


# 统计今天挂号人数
@indexinfo.route("/admin/orderPeople", methods=["GET"])
def order_people():
    today = datetime.now().strftime("%Y-%m-%d")  # 获取今天的日期
    print(today)
    count = Order.query.filter(Order.o_start.like(f"{today}%")).count()
    return jsonify({"status": 200, "message": "统计今天挂号人数成功", "data": count})

# 统计今天住院人数
@indexinfo.route("/admin/bedPeople", methods=["GET"])
def bed_people():
    today = datetime.now().strftime("%Y-%m-%d %H:%M")  # 获取今天的日期

    # 统计符合条件的住院人数
    count = (
        db.session.query(Bed).filter(Bed.b_state == 1).count()
    )

    return jsonify({"status": 200, "message": "统计今天住院人数成功", "data": count})
