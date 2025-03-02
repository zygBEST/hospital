# 显示全部患者信息
from flask import Blueprint, jsonify, request
from app.models import Patient
from app import db


# 定义患者信息管理蓝图对象
patientInfo = Blueprint("patientInfo", __name__)


# 获取全部患者信息
@patientInfo.route("/admin/findAllPatients", methods=["GET"])
def find_all_patients():
    page_number = request.args.get("pageNumber", type=int, default=1)
    size = request.args.get("size", type=int, default=10)
    query = request.args.get("query", default="")

    patients_query = Patient.query.filter(Patient.p_name.like(f"%{query}%")).order_by(
        Patient.p_state.desc()
    )
    patients_paginated = patients_query.paginate(
        page=page_number, per_page=size, error_out=False
    )

    result = {
        "total": patients_paginated.total,
        "pages": patients_paginated.pages,
        "pageNumber": patients_paginated.page,
        "patients": [patient.to_dict() for patient in patients_paginated.items],
    }

    return jsonify({"code": 200, "message": "查询成功", "data": result})


# 删除患者
@patientInfo.route("/admin/deletePatient", methods=["POST"])
def delete_patient():
    p_id = request.json.get("pId")
    print(p_id)
    # 查找患者
    patient = Patient.query.filter_by(p_id=p_id).first()
    if patient:
        patient.p_state = 0
        db.session.commit()
        return jsonify({"code": 200, "message": "删除成功"})
    return jsonify({"code": 404, "message": "患者未找到"})
