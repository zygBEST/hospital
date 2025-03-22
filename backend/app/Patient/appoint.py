import random
from flask import Blueprint, jsonify, request
import redis
from ..models import (
    Alipay,
    Arrange,
    Doctor,
    DoctorDetails,
    Order,
    OrderDetail,
    OrderItem,
)
from sqlalchemy.orm import joinedload
from app import redis_client, db


# 创建预约挂号蓝图对象
appoint = Blueprint("appoint", __name__)


# 请求科室获取医生信息
@appoint.route("/patient/findDoctorBySection", methods=["GET"])
def find_doctor_by_section():
    d_section = request.args.get("dSection").strip()
    doctors = DoctorDetails.query.filter(DoctorDetails.d_section == d_section).all()
    doctor_list = [doctor.to_dict() for doctor in doctors]

    return jsonify({"status": 200, "msg": "查询成功", "data": {"doctors": doctor_list}})


# 请求日期获取医生信息
@appoint.route("/patient/findByTime", methods=["GET"])
def find_doctor_by_time():
    ar_time = request.args.get("arTime").strip()
    d_section = request.args.get("dSection").strip()

    # 查询医生信息，确保其在 Arrange 表中有相应的排班
    doctors = (
        db.session.query(Doctor, DoctorDetails)
        .join(DoctorDetails, Doctor.d_id == DoctorDetails.d_id)
        .join(Arrange, Doctor.d_id == Arrange.d_id)
        .filter(DoctorDetails.d_section == d_section, Arrange.ar_time == ar_time)
        .all()
    )

    # 组装返回数据
    doctor_list = [
        {**doctor.to_dict(), **details.to_dict(), "arTime": ar_time}
        for doctor, details in doctors
    ]
    return jsonify({"status": 200, "message": "查询成功", "data": doctor_list})


# 获取挂号时间段已剩余票数
@appoint.route("/patient/findOrderTime", methods=["GET"])
def find_order_time():
    ar_id = request.args.get("arId").strip()
    # 从 Redis 获取哈希数据
    order_time = redis_client.hgetall(ar_id)
    # 如果 Redis 没有数据，则初始化默认值
    if not order_time:
        order_time = {
            "tTOe": "40",
            "nTOt": "40",
            "sTOs": "40",
            "eTOn": "40",
            "fTOf": "40",
            "fTOs": "40",
        }

    # 确保所有字段都存在
    default_values = {
        "tTOe": "40",
        "nTOt": "40",
        "sTOs": "40",
        "eTOn": "40",
        "fTOf": "40",
        "fTOs": "40",
    }

    for key, value in default_values.items():
        order_time.setdefault(key, value)

    # 将更新后的数据存回 Redis，并设置 7 天过期时间
    redis_client.hmset(ar_id, order_time)
    redis_client.expire(ar_id, 604800)
    return jsonify({"status": 200, "message": "查询成功", "data": order_time})


def random_oid(p_id):
    """生成唯一挂号ID"""
    return p_id + random.randint(10000, 99999)


# 添加挂号
@appoint.route("/patient/addOrder", methods=["POST"])
def add_order():
    data = request.json
    p_id = data.get("pId")
    d_id = data.get("dId")
    ar_id = data.get("arId")
    o_start = data.get("oStart")
    print(data)

    if not all([p_id, d_id, ar_id, o_start]):
        return {"status": 400, "message": "缺少必要参数"}

    time_slot = o_start[11:22]  # 获取时间段
    time_map = {
        "00:01-09:30": "eTOn",
        "09:30-10:30": "nTOt",
        "10:30-11:30": "tTOe",
        "14:30-15:30": "fTOf",
        "15:30-16:30": "fTOs",
        "16:30-23:59": "sTOs",
    }

    if time_slot in time_map:
        key = time_map[time_slot]
        with redis_client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(ar_id)
                    count = redis_client.hget(ar_id, key)

                    if count is None or int(count) == 0:
                        pipe.unwatch()
                        return {
                            "status": 400,
                            "message": "该时间段无剩余号源！请重新选择！",
                        }

                    pipe.multi()
                    pipe.hincrby(ar_id, key, -1)
                    pipe.execute()
                    break
                except redis.WatchError:
                    continue  # 重新尝试

    # 创建挂号单
    new_order = Order(
        o_id=random_oid(p_id),
        p_id=p_id,
        d_id=d_id,
        o_start=o_start[:22],  # 格式化时间，保留前22个字符
        o_end=None,  # 结束时间
        o_state=0,  # 默认订单状态
    )

    # 将新订单添加到数据库
    db.session.add(new_order)

    # 创建订单项，关联到订单
    new_order_item = OrderItem(
        o_id=new_order.o_id,  # 关联刚刚创建的订单
        o_drug=None,  # 药品信息
        o_check=None,  # 检查项目
        o_total_price=0.00,  # 总价
    )

    # 将新订单项添加到数据库
    db.session.add(new_order_item)

    # 创建订单详情，关联到刚刚创建的订单
    new_order_detail = OrderDetail(
        o_id=new_order.o_id,  # 关联刚刚创建的订单
        o_record=None,  # 病历记录，根据实际情况添加
        o_advice=None,  # 医嘱，根据实际情况添加
    )

    # 将新订单详情添加到数据库
    db.session.add(new_order_detail)

    # 创建支付记录，关联到刚刚创建的订单
    new_alipay = Alipay(
        o_id=new_order.o_id,  # 关联刚刚创建的订单
        o_price_state=0,  # 支付状态，根据实际情况添加
        o_total_price=0.00,  # 支付金额，根据实际情况添加
        o_gh_alipay=None,  # 支付宝交易号，根据实际情况添加
        o_alipay=None,  # 支付宝交易号，根据实际情况添加
    )
    # 将支付记录添加到数据库
    db.session.add(new_alipay)

    # 提交事务
    db.session.commit()

    return {"status": 200, "message": "挂号成功！", "oId": new_order.o_id}
