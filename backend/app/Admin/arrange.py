from flask import Blueprint, jsonify, request
from sqlalchemy import and_
from app import db, redis_client
from app.models import Arrange, Doctor, DoctorDetails


# 创建排班信息管理蓝图对象
arrangeinfo = Blueprint("arrangeinfo", __name__)


# 分科室查询医生排班信息
@arrangeinfo.route("/admin/findDoctorBySectionPage", methods=["GET"])
def find_doctor_by_section_page():
    try:
        # 获取前端参数
        page_number = int(request.args.get("pageNumber", 1))  # 页码
        page_size = int(request.args.get("size", 10))  # 每页数量
        query = request.args.get("query", "").strip()  # 搜索关键词
        d_section = request.args.get("dSection", "").strip()  # 科室
        arrange_date = request.args.get("arrangeDate", "").strip()  # 排班日期

        # 构建查询条件
        filters = []
        if d_section:
            filters.append(DoctorDetails.d_section == d_section)
        if query:
            filters.append(Doctor.d_name.like(f"%{query}%"))  # 关联 Doctor 进行模糊查询

        # 查询符合条件的医生，使用 `join` 连接 `Doctor`
        doctors_query = (
            db.session.query(Doctor, DoctorDetails)
            .join(DoctorDetails, Doctor.d_id == DoctorDetails.d_id)
            .filter(*filters)
            .order_by(Doctor.d_state.desc())  # 使用 `Doctor.d_state` 排序
        )

        # 分页
        paginated_doctors = doctors_query.paginate(
            page=page_number, per_page=page_size, error_out=False
        )

        # 获取医生列表
        doctor_list = []
        for doctor, details in paginated_doctors.items:
            # 查询医生是否已排班
            arrange = Arrange.query.filter_by(
                ar_time=arrange_date, d_id=doctor.d_id
            ).first()
            arrange_id = arrange.ar_id if arrange else None  # 获取排班 ID

            doctor_list.append(
                {
                    "dId": doctor.d_id,
                    "dName": doctor.d_name,
                    "dGender": details.d_gender,
                    "dPost": details.d_post,
                    "dSection": details.d_section,
                    "arrangeId": arrange_id,  # 如果有排班，返回排班 ID
                }
            )

        # 组装返回数据
        return jsonify(
            {
                "status": 200,
                "message": "查询成功",
                "data": {
                    "total": paginated_doctors.total,  # 总条数
                    "pages": paginated_doctors.pages,  # 总页数
                    "pageNumber": paginated_doctors.page,  # 当前页
                    "doctors": doctor_list,  # 医生数据
                },
            }
        )

    except Exception as e:
        return jsonify({"status": 500, "message": "服务器错误", "error": str(e)})



# 添加医生排班
@arrangeinfo.route("/admin/addArrange", methods=["POST"])
def add_arrange():
    try:
        data = request.json
        ar_id = data.get("arId")  # 排班ID
        ar_time = data.get("arTime")  # 排班时间
        d_id = data.get("dId")  # 医生ID

        # 检查数据库中是否已有该排班
        existing_arrange = Arrange.query.get(ar_id)

        if existing_arrange:
            return jsonify({"status": 400, "message": "该排班信息已存在"})

        # 创建新的 Arrange 对象
        new_arrange = Arrange(ar_id=ar_id, ar_time=ar_time, d_id=d_id)

        # 将排班信息存入 Redis
        redis_data = {
            "eTOn": "40",
            "nTOt": "40",
            "tTOe": "40",
            "fTOf": "40",
            "fTOs": "40",
            "sTOs": "40",
        }
        redis_client.hmset(ar_id, redis_data)  # 存入 Redis
        redis_client.expire(ar_id, 604800)  # 设置 7 天（604800 秒）过期

        # 存入数据库
        db.session.add(new_arrange)
        db.session.commit()

        return jsonify({"status": 200, "message": "排班信息添加成功"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "message": "服务器错误", "error": str(e)})

@arrangeinfo.route("/admin/deleteArrange", methods=["POST"])
# 删除医生排班
def delete_arrange():
    try:
        # 获取 JSON 数据
        ar_id = request.get_json()["arId"]

        # 查找数据库中的排班信息
        arrange = Arrange.query.get(ar_id)
        if not arrange:
            return jsonify({"status": 404, "message": "排班信息未找到"})

        # 先删除 Redis 中的排班信息
        redis_client.delete(ar_id)

        # 删除 MySQL 中的排班信息
        db.session.delete(arrange)
        db.session.commit()

        return jsonify({"status": 200, "message": "排班信息删除成功！"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "message": "服务器错误", "error": str(e)}), 500
