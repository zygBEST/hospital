# 创建管理员首页蓝图对象
from flask import Blueprint


indexinfo = Blueprint("index", __name__)


@indexinfo.route("/admin/index", methods=["GET"])
def index():
    return "管理员首页"
