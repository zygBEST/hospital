from flask import Blueprint, jsonify, request
from ..models import Doctor
from app.Admin.doctor import find_doctor

# 定义个人信息蓝图对象
doctorinfo = Blueprint("doctorinfo", __name__)

@doctorinfo.route("/doctor/findDoctorById", methods=["POST"])
def find_doctor_byId():
    # 返回医生信息
    return find_doctor()
