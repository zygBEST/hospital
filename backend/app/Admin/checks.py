from flask import Blueprint, jsonify, request
from ..models import CheckItem
from app import db

# 定义检查项目蓝图对象
checks = Blueprint("checks", __name__)


# 查询所有检查项目
@checks.route("/admin/findAllChecks", methods=["GET"])
def find_all_checks():
    page_number = request.args.get("pageNumber", type=int, default=1)
    size = request.args.get("size", type=int, default=10)
    query = request.args.get("query", default="")

    checks_query = CheckItem.query.filter(
        CheckItem.ch_name.like(f"%{query}%")
    ).order_by(CheckItem.ch_id.asc())
    checks_paginated = checks_query.paginate(
        page=page_number, per_page=size, error_out=False
    )

    result = {
        "total": checks_paginated.total,
        "pages": checks_paginated.pages,
        "pageNumber": checks_paginated.page,
        "checks": [check.to_dict() for check in checks_paginated.items],
    }

    return jsonify({"code": 200, "msg": "查询成功", "data": result})

# 查询单个检查项目
@checks.route("/admin/findCheck", methods=["POST"])
def find_check():
    ch_id = request.json.get("chId")
    check = CheckItem.query.filter(CheckItem.ch_id == ch_id).first()
    if check:
        return jsonify({"status": 200, "message": "查询成功", "data": check.to_dict()})
    else:
        return jsonify({"status": 404, "message": "检查项目不存在"})

# 添加检查项目
@checks.route("/admin/addCheck", methods=["POST"])
def add_check():
    data = request.json
    ch_id = data.get("chId")
    ch_name = data.get("chName")
    ch_price = data.get("chPrice")

    # 检查是否已经存在相同的ID
    existing_check = CheckItem.query.filter(CheckItem.ch_id == ch_id).first()
    if existing_check:
        return jsonify({"status": 402, "message": "药品编号已存在！"})

    # 创建新的检查项目
    new_check = CheckItem(ch_id=ch_id, ch_name=ch_name, ch_price=ch_price)

    db.session.add(new_check)
    db.session.commit()

    return jsonify({"status": 200, "message": "添加成功"})


# 编辑检查项目信息
@checks.route("/admin/modifyCheck", methods=["POST"])
def modify_check():
    data = request.json
    ch_id = data.get("chId")
    ch_name = data.get("chName")
    ch_price = data.get("chPrice")
    check = CheckItem.query.filter(CheckItem.ch_id == ch_id).first()
    if check:
        check.ch_id = ch_id
        check.ch_name = ch_name
        check.ch_price = ch_price
        db.session.commit()
        return jsonify({"status": 200, "message": "修改成功"})
    else:
        return jsonify({"status": 404, "message": "检查项目不存在"})

# 删除检查项目
@checks.route("/admin/deleteCheck", methods=["POST"])
def delete_check():
    ch_id = request.json.get("chId")
    check = CheckItem.query.filter(CheckItem.ch_id == ch_id).first()
    if check:
        db.session.delete(check)
        db.session.commit()
        return jsonify({"status": 200, "message": "删除成功"})