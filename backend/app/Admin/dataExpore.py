from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from sqlalchemy import distinct, func

from app.models import Doctor, Order, Patient
from app import db

# 定义数据统计分析蓝图对象
dataExpore = Blueprint("dataExpore", __name__)

"""统计不同年龄段患者人数"""
@dataExpore.route("/patient/patientAge", methods=["GET"])
def patient_age():
    # 定义年龄段
    age_ranges = [(0, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 60), (61, 100)]

    # 查询 orders 里 o_state = 1 的各年龄段患者人数
    age_list = [
        db.session.query(func.count(distinct(Patient.p_id)))
        .join(Order, Order.p_id == Patient.p_id)  # 关联 orders 表
        .filter(Patient.p_age.between(start, end))  # 按年龄筛选
        .filter(Order.o_state == 1)  # 只统计 o_state = 1 的订单
        .scalar()
        for start, end in age_ranges
    ]

    return jsonify({
        "status": 200,
        "msg": "统计年龄分布成功",
        "data": age_list
    })


"""统计不同年龄段患者人数"""
@dataExpore.route("/order/orderGender", methods=["GET"])
def order_gender():
    results = (
    db.session.query(
        Patient.p_gender, 
        func.count(distinct(Patient.p_id)).label("countGender")  # 统计唯一 p_id
    )
    .join(Order, Order.p_id == Patient.p_id)  # 关联 orders 表
    .group_by(Patient.p_gender)  # 按性别分组
    .all()
)

    # 构造返回的 JSON 数据
    data = [{"patient": {"pGender": gender}, "countGender": count} for gender, count in results]

    return jsonify({
        "status": 200,
        "msg": "查询成功",
        "data": data
    })

"""统计近20天各科室挂号人数"""
@dataExpore.route("/order/orderSection", methods=["GET"])
def order_section():
    start_time = (datetime.today() - timedelta(days=20)).strftime("%Y-%m-%d")
    end_time = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    print(start_time, end_time)

    results = (
        db.session.query(Doctor.d_section, func.count(Order.d_id).label("countSection"))
        .join(Order, Order.d_id == Doctor.d_id)
        .filter(Order.o_start.between(start_time, end_time))
        .group_by(Doctor.d_section)
        .all()
    )

    # 构造返回的 JSON 数据
    data = [{"doctor": {"dSection": d_section}, "countSection": count} for d_section, count in results]

    print(data)
    return jsonify({
        "status": 200,
        "msg": "统计过去 20 天科室挂号人数成功",
        "data": data
    })

"""统计近二十天挂号人数"""
@dataExpore.route("/order/orderTwenty", methods=["GET"])
def order_twenty():
    result = []
    
    for i in range(20, -1, -1):  # 过去 20 天
        o_start = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")

        count = (
            db.session.query(func.count(Order.p_id))
            .filter(Order.o_start.like(f"{o_start}%"))  # 使用 LIKE 进行日期匹配
            .scalar()
        )

        result.append(count)

    return jsonify({
        "status": 200,
        "msg": "获取过去 20 天的挂号人数成功",
        "data": result
    })
