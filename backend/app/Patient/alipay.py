# 定义支付宝支付蓝图对象

from flask import Blueprint, current_app, jsonify, request
from alipay import AliPay
from app.Patient.patientorder import update_order_item_state, update_order_state

alipay = Blueprint("alipay", __name__)


# 初始化支付宝 SDK
def create_alipay():
    ALIPAY_CONFIG = current_app.config["ALIPAY_CONFIG"]
    return AliPay(
        appid=ALIPAY_CONFIG["APP_ID"],
        app_notify_url=ALIPAY_CONFIG["NOTIFY_URL"],
        app_private_key_string=open(ALIPAY_CONFIG["APP_PRIVATE_KEY_PATH"]).read(),
        alipay_public_key_string=open(ALIPAY_CONFIG["ALIPAY_PUBLIC_KEY_PATH"]).read(),
        sign_type="RSA2",
        debug=True,
    )


# 调用支付接口
@alipay.route("/alipay/pay", methods=["POST"])
def alipay_pay():
    # 获取前端传来的 JSON 参数
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求体不能为空"})

    subject = data.get("subject")
    trade_no = data.get("tradeNo")
    total_amount = data.get("totalAmount")
    passback_params = data.get("passbackParams")  # 传递支付类型

    if not subject or not trade_no or not total_amount:
        return jsonify({"error": "缺少必要参数"})

    alipay = create_alipay()

    # 生成支付宝订单支付字符串
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=trade_no,
        total_amount=str(total_amount),
        subject=subject,
        passback_params=passback_params,
        return_url=current_app.config["ALIPAY_CONFIG"]["RETURN_URL"],
        notify_url=current_app.config["ALIPAY_CONFIG"]["NOTIFY_URL"],
    )

    # 拼接支付宝支付URL
    pay_url = f"https://openapi-sandbox.dl.alipaydev.com/gateway.do?{order_string}"
    # 返回支付URL
    return {"payUrl": pay_url, "tradeNo": trade_no}


# 获取支付宝支付成功回调的参数
@alipay.route("/pay_success")
def pay_success():
    out_trade_no = request.args.get("out_trade_no")
    total_amount = request.args.get("total_amount")

    # 返回 HTML 页面，执行 window.close() 关闭当前窗口
    return """
    <html>
    <head><title>支付成功</title></head>
    <body>
        <h2>支付成功！订单号: {}</h2>
        <h3>支付金额: {} 元</h3>
        <script>
            setTimeout(function() {{
                window.close();
            }}, 3000);  // 3秒后自动关闭窗口
        </script>
    </body>
    </html>
    """.format(
        out_trade_no, total_amount
    )


# 处理支付宝异步通知
@alipay.route("/alipay/notify", methods=["POST"])
def alipay_notify():
    data = request.form.to_dict()  # 获取支付宝返回的参数
    out_trade_no = data.get("out_trade_no")  # 获取 out_trade_no
    passback_params = data.get("passback_params")  # 获取支付类型

    if out_trade_no:
        if passback_params == "registration":
            print("挂号支付")
            out_trade_no = out_trade_no[2:]  # 去掉前两位
            update_order_state(out_trade_no)
        elif passback_params == "order":
            print("订单支付")
            update_order_item_state(out_trade_no)
        else:
            print("未知支付类型")
            return "failure"

        return "success"
    else:
        print("验证失败")
        return "failure"
