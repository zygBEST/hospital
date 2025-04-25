from flask import Blueprint, jsonify, request
from app.models import Drug
from app import db


# 定义药物信息管理蓝图对象
drugInfo = Blueprint("drugInfo", __name__)


# 显示所有药品信息
@drugInfo.route("/admin/findAllDrugs", methods=["GET"])
def find_all_drugs():
    page_number = request.args.get("pageNumber", type=int, default=1)
    size = request.args.get("size", type=int, default=10)
    query = request.args.get("query", default="")

    drugs_query = Drug.query.filter(Drug.dr_name.like(f"%{query}%")).order_by(
        Drug.dr_id.asc()
    )
    drugs_paginated = drugs_query.paginate(
        page=page_number, per_page=size, error_out=False
    )

    result = {
        "total": drugs_paginated.total,
        "pages": drugs_paginated.pages,
        "pageNumber": drugs_paginated.page,
        "drugs": [drug.to_dict() for drug in drugs_paginated.items],
    }

    return jsonify({"status": 200, "msg": "查询成功", "data": result})


# 查找单个药品信息
@drugInfo.route("/admin/findDrug", methods=["POST"])
def find_drug():
    dr_id = request.json.get("drId")
    # 在数据库中查找药品
    drug = Drug.query.filter_by(dr_id=dr_id).first()
    if drug:
        return jsonify({"status": 200, "message": "查询成功", "data": drug.to_dict()})
    else:
        return jsonify({"status": 404, "message": "药品信息未找到"})


# 增加药物信息
@drugInfo.route("/admin/addDrug", methods=["POST"])
def add_drug():
    # 获取JSON数据
    data = request.json
    dr_id = data.get("drId")
    dr_price = data.get("drPrice")
    dr_name = data.get("drName")
    dr_number = data.get("drNumber")
    dr_publisher = data.get("drPublisher")
    dr_unit = data.get("drUnit")

    # 检查是否已经存在相同的药品ID
    existing_drug = Drug.query.filter(Drug.dr_id == dr_id).first()
    if existing_drug:
        return jsonify({"status": 402, "message": "药品编号已存在！"})

    # 创建新的药品对象
    new_drug = Drug(
        dr_id=dr_id,
        dr_price=dr_price,
        dr_name=dr_name,
        dr_number=dr_number,
        dr_publisher=dr_publisher,
        dr_unit=dr_unit,
    )

    # 将新的药品对象添加到数据库中
    db.session.add(new_drug)
    db.session.commit()

    return jsonify({"status": 200, "message": "增加药品成功！"})


# 编辑药物信息
@drugInfo.route("/admin/modifyDrug", methods=["POST"])
def modify_drug():
    # 获取 JSON 数据
    data = request.json
    dr_id = data.get("drId")
    dr_price = data.get("drPrice")
    dr_name = data.get("drName")
    dr_number = data.get("drNumber")
    dr_publisher = data.get("drPublisher")
    dr_unit = data.get("drUnit")
    # 查找要修改的药品对象
    drug = Drug.query.filter_by(dr_id=dr_id).first()

    if not drug:
        return jsonify({"status": 404, "message": "药品不存在！"})

    # 更新药品信息
    drug.dr_price = dr_price
    drug.dr_name = dr_name
    drug.dr_number = dr_number
    drug.dr_publisher = dr_publisher
    drug.dr_unit = dr_unit
    db.session.commit()
    return jsonify({"status": 200, "message": "修改药品信息成功！"})


# 删除药物信息
@drugInfo.route("/admin/deleteDrug", methods=["POST"])
def delete_drug():
    # 获取 JSON 数据
    dr_id = request.json.get("drId")

    # 查找要删除的药品对象
    drug = Drug.query.filter_by(dr_id=dr_id).first()

    if not drug:
        return jsonify({"status": 404, "message": "药品不存在！"})

    db.session.delete(drug)
    db.session.commit()
    return jsonify({"status": 200, "message": "删除药品信息成功！"})

# 更新药物库存
@drugInfo.route("/drug/reduceDrugNumber", methods=["POST"])
def reduce_drug_number():
    # 获取 JSON 数据
    dr_id = request.json.get("drId")
    dr_number = request.json.get("usedNumber")

    # 查找药品对象
    drug = Drug.query.filter_by(dr_id=dr_id).first()
    if drug.dr_number < dr_number:
        return jsonify({"status": 402, "message": "药品库存不足！"})

    if not drug:
        return jsonify({"status": 404, "message": "药品不存在！"})
    
    drug.dr_number -= dr_number
    db.session.commit()
    return jsonify({"status": 200, "message": "减少药品库存成功！"})
