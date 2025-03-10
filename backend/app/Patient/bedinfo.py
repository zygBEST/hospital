# 创建住院信息蓝图对象
from flask import Blueprint, request

from app.models import PBed


pbedinfo = Blueprint("pbedinfo", __name__)
# 查询历史住院信息
@pbedinfo.route("/patient/findBedByPid", methods=["GET"])
def find_bed_by_pid():
    p_id= request.args.get("pId")
    print(p_id)
    p_beds = PBed.query.filter_by(p_id=p_id).all()
    result = [p_bed.to_dict() for p_bed in p_beds]

    return {"status": 200, "msg": "查询成功", "data": result}