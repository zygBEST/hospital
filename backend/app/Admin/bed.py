from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models import Bed, PBed
from app import db

# 创建病床信息管理蓝图对象
bedinfo = Blueprint("bedinfo", __name__)


# 获取所有病床信息
@bedinfo.route("/admin/findAllBeds", methods=["GET", "POST"])
def find_all_beds():
    page_number = request.args.get("pageNumber", type=int, default=1)
    size = request.args.get("size", type=int, default=10)
    query = request.args.get("query", default="")

    beds_query = Bed.query.filter(Bed.p_id.like(f"%{query}%")).order_by(Bed.b_id.asc())
    beds_paginated = beds_query.paginate(
        page=page_number, per_page=size, error_out=False
    )

    result = {
        "total": beds_paginated.total,
        "pages": beds_paginated.pages,
        "pageNumber": beds_paginated.page,
        "beds": [bed.to_dict() for bed in beds_paginated.items],
    }

    return jsonify({"code": 200, "msg": "查询成功", "data": result})


# 清空病床信息
@bedinfo.route("/admin/emptyBed", methods=["POST"])
def clear_beds():
    b_id = request.json.get("bId")
    bed = Bed.query.filter(Bed.b_id == b_id).first()

    if not bed:
        return jsonify({"status": 402, "message": "该病床不存在"})

    bed.p_id = -1
    bed.d_id = -1
    bed.b_start = None
    bed.b_reason = None
    bed.b_state = 0

    p_bed = PBed.query.filter(PBed.b_id == b_id).first()
    p_bed.b_end = datetime.now().strftime("%Y-%m-%d %H:%M")
    bed.b_end = datetime.now().strftime("%Y-%m-%d %H:%M")

    db.session.commit()
    return jsonify({"status": 200, "message": "清空成功"})


# 删除病床信息
@bedinfo.route("/admin/deleteBed", methods=["POST"])
def delete_bed():
    b_id = request.json.get("bId")
    bed = Bed.query.filter(Bed.b_id == b_id).first()
    if bed:
        db.session.delete(bed)
        db.session.commit()
        return jsonify({"status": 200, "message": "删除成功"})
    else:
        return jsonify({"status": 402, "message": "该病床不存在"})


# 增加病床信息
@bedinfo.route("/admin/addBed", methods=["POST"])
def add_bed():
    data = request.json
    b_id = data.get("bId")
    p_id = data.get("pId")
    d_id = data.get("dId")

    # 检查是否存在该病床
    existing_bed = Bed.query.filter(Bed.b_id == b_id).first()
    if existing_bed:
        return jsonify({"status": 402, "message": "该病床号已存在"})

    new_bed = Bed(b_id=b_id, p_id=p_id, d_id=d_id, b_state=0)
    db.session.add(new_bed)
    db.session.commit()
    return jsonify({"status": 200, "message": "添加成功"})
