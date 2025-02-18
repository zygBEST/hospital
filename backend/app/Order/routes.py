# 定义挂号蓝图对象
from flask import Blueprint, jsonify, request
from ..models import Doctor


Order = Blueprint("Order", __name__)
# 测试路由
@Order.route("/hello1")
def hello():
    return "hello world！"

# 医生信息管理
@Order.route("/admin/findAllDoctors", methods=['GET'])
def find_all_doctors():
    page_number = request.args.get('pageNumber', type=int, default=1)
    size = request.args.get('size', type=int, default=10)
    query = request.args.get('query', default='')

    doctors_query = Doctor.query.filter(Doctor.d_name.like(f"%{query}%")).order_by(Doctor.d_state.desc())
    doctors_paginated = doctors_query.paginate(page=page_number, per_page=size, error_out=False)

    result = {
        "total": doctors_paginated.total,
        "pages": doctors_paginated.pages,
        "pageNumber": doctors_paginated.page,
        "doctors": [doctor.to_dict() for doctor in doctors_paginated.items]
    }

    return jsonify({"code": 200, "msg": "查询成功", "data": result})