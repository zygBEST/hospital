from flask import Blueprint, jsonify, request
from ..models import Patient


# 定义个人信息蓝图对象
patientinfo = Blueprint("patientinfo", __name__)


@patientinfo.route("/patient/findPatientById", methods=["GET"])
def find_patient():
    p_id = request.args.get("pId")  # 获取前端传递的 pId
    patient = Patient.query.filter_by(p_id=p_id).first()

    # 返回患者信息
    return jsonify({"status": 200, "data": patient.to_dict(), "message": "查询成功"})
