from flask import Blueprint, jsonify, request
from ..models import Doctor

# 定义个人信息蓝图对象
doctorinfo = Blueprint("doctorinfo", __name__)


@doctorinfo.route("/doctor/findDoctorById")
def find_doctor():
    d_id = request.args.get("dId")  # 获取前端传递的 pId
    doctor = Doctor.query.filter_by(d_id=d_id).first()

    # 返回医生信息
    return jsonify(
        {
            "status": 200,
            "data": doctor.to_dict(),
            "message": "查询成功"
        }
    )
