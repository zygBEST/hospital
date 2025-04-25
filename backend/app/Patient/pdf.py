# 定义pdf蓝图对象
from datetime import datetime
from io import BytesIO
import textwrap
from flask import Blueprint, make_response, request
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from app import db
from app.models import Order


pdf = Blueprint("pdf", __name__)


@pdf.route("/patient/pdf", methods=["GET"])
def get_report_pdf():
    o_id = request.args.get("oId")
    if not o_id:
        return {"status": 400, "msg": "缺少订单编号oId"}

    order = db.session.query(Order).filter_by(o_id=o_id).first()
    if not order:
        return {"status": 404, "msg": "未找到该订单"}

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.lib.colors import black, grey

    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

    y = height - 50

    def draw_center_text(text, size=14, offset=30, underline=False):
        nonlocal y
        pdf.setFont("STSong-Light", size)
        pdf.drawCentredString(width / 2, y, text)
        if underline:
            text_width = pdf.stringWidth(text, "STSong-Light", size)
            pdf.line((width - text_width) / 2, y - 3, (width + text_width) / 2, y - 3)
        y -= offset

    def draw_label_value(label, value, size=12, label_x=60, value_x=140):
        nonlocal y
        pdf.setFont("STSong-Light", size)
        pdf.drawString(label_x, y, f"{label}:")
        pdf.drawString(value_x, y, str(value))
        y -= 22

    def draw_section_title(title):
        nonlocal y
        y -= 10
        pdf.setStrokeColor(grey)
        pdf.line(50, y, width - 50, y)
        y -= 25
        pdf.setFont("STSong-Light", 13)
        pdf.setFillColor(black)
        pdf.drawString(60, y, title)
        y -= 15
        pdf.setStrokeColor(black)

    draw_center_text("病情报告单（电子病历）", size=20, underline=True)
    draw_center_text(
        f"打印时间：{datetime.today().strftime('%Y-%m-%d')}", size=10, offset=40
    )

    def draw_wrapped_text(text, max_width=80, font_size=11, line_height=18, start_x=70):
        nonlocal y
        pdf.setFont("STSong-Light", font_size)
        if not text:
            text = "（无）"  # 空内容处理，避免报错
        wrapper = textwrap.TextWrapper(width=max_width)
        lines = wrapper.wrap(text)
        for line in lines:
            pdf.drawString(start_x, y, line)
            y -= line_height

    # 基本信息
    draw_section_title("一、基本信息")
    draw_label_value("姓名", order.patient.p_name)
    draw_label_value("性别", order.patient.p_gender)
    draw_label_value("年龄", f"{order.patient.p_age} 岁")
    draw_label_value("联系电话", order.patient.p_phone)
    draw_label_value("订单编号", order.o_id)
    draw_label_value("诊疗日期", order.o_end)

    # 症状信息
    draw_section_title("二、症状信息")
    draw_wrapped_text(order.details.o_record)

    # 检查项目
    draw_section_title("三、检查项目及价格")
    draw_wrapped_text(order.items.o_check)

    # 药物信息
    draw_section_title("四、药物信息及价格")
    draw_wrapped_text(order.items.o_drug)

    # 医生意见
    draw_section_title("五、医生诊断与建议")
    draw_wrapped_text(order.details.o_advice)

    # 页脚
    pdf.setFont("STSong-Light", 11)
    pdf.setFillColor(grey)
    pdf.drawCentredString(width / 2, 50, "该报告单仅供参考")
    pdf.setFont("STSong-Light", 13)
    pdf.setFillColor(black)
    pdf.drawCentredString(width / 2, 30, "版权医院所有")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers["Content-Type"] = "application/pdf"
    return response
