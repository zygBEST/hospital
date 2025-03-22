from app import db


# 与数据库表对应的患者类：
class Patient(db.Model):
    __tablename__ = "patient"

    p_id = db.Column(db.Integer, primary_key=True, nullable=False)
    p_password = db.Column(db.String(255), nullable=True)
    p_name = db.Column(db.String(255), nullable=True)
    p_gender = db.Column(db.String(255), nullable=True)
    p_phone = db.Column(db.String(255), nullable=True)
    p_card = db.Column(db.String(255), nullable=True)
    p_email = db.Column(db.String(255), nullable=True)
    p_state = db.Column(db.Integer, nullable=True)
    p_birthday = db.Column(db.String(255), nullable=True)
    p_age = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            "pId": self.p_id,
            "pName": self.p_name,
            "pGender": self.p_gender,
            "pAge": self.p_age,
            "pCard": self.p_card,
            "pPhone": self.p_phone,
            "pEmail": self.p_email,
            "pBirthday": self.p_birthday,
            "pState": self.p_state,
        }


# 与数据库表对应的管理员类：
class Admini(db.Model):
    __tablename__ = "admini"

    a_id = db.Column(db.Integer, primary_key=True, nullable=False)
    a_password = db.Column(db.String(255), nullable=True)
    a_name = db.Column(db.String(255), nullable=True)
    a_gender = db.Column(db.String(255), nullable=True)
    a_card = db.Column(db.String(255), nullable=True)
    a_phone = db.Column(db.String(255), nullable=True)
    a_email = db.Column(db.String(255), nullable=True)


# 与数据库表对应的医生账号类：
class Doctor(db.Model):
    __tablename__ = "doctor"

    d_id = db.Column(db.Integer, primary_key=True, nullable=False)
    d_password = db.Column(db.String(255), nullable=True)
    d_name = db.Column(db.String(255), nullable=True)
    d_state = db.Column(db.Integer, nullable=False)

    # 关联到 DoctorDetails
    details = db.relationship(
        "DoctorDetails", back_populates="doctor", uselist=False, cascade="all, delete"
    )

    def to_dict(self):
        return {
            "dId": self.d_id,
            "dName": self.d_name,
            "dState": self.d_state,
        }


# 与数据库表对应的医生详细信息类：
class DoctorDetails(db.Model):
    __tablename__ = "doctor_details"

    d_id = db.Column(
        db.Integer, db.ForeignKey("doctor.d_id"), primary_key=True, nullable=False
    )
    d_name = db.Column(db.String(255), nullable=True)
    d_gender = db.Column(db.String(255), nullable=True)
    d_phone = db.Column(db.String(255), nullable=True)
    d_card = db.Column(db.String(255), nullable=True)
    d_email = db.Column(db.String(255), nullable=True)
    d_post = db.Column(db.String(255), nullable=True)
    d_introduction = db.Column(db.String(255), nullable=True)
    d_section = db.Column(db.String(255), nullable=True)
    d_price = db.Column(db.Numeric(10, 2), nullable=True)
    d_people = db.Column(db.Integer, nullable=True)
    d_star = db.Column(db.Numeric(10, 2), nullable=True)
    d_avg_star = db.Column(db.Numeric(10, 2), nullable=True)

    # 关联到 Doctor
    doctor = db.relationship("Doctor", back_populates="details")

    def to_dict(self):
        return {
            "dId": self.d_id,
            "dName": self.d_name,
            "dGender": self.d_gender,
            "dPhone": self.d_phone,
            "dCard": self.d_card,
            "dEmail": self.d_email,
            "dPost": self.d_post,
            "dIntroduction": self.d_introduction,
            "dSection": self.d_section,
            "dPrice": self.d_price,
            "dAvgStar": self.d_avg_star,
        }


# 与数据库表对应的药品类：
class Drug(db.Model):
    __tablename__ = "drug"  # 数据库中的表名

    dr_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 药品ID，主键
    dr_name = db.Column(db.String(255), nullable=True)  # 药品名称
    dr_price = db.Column(db.Numeric(10, 2), nullable=True)  # 药品价格
    dr_number = db.Column(db.Integer, nullable=True)  # 药品数量
    dr_publisher = db.Column(db.String(255), nullable=True)  # 生产厂家
    dr_unit = db.Column(db.String(255), nullable=True)  # 计量单位

    def to_dict(self):
        return {
            "drId": self.dr_id,
            "drName": self.dr_name,
            "drPrice": round(float(self.dr_price), 2) if self.dr_price else None,
            "drNumber": self.dr_number,
            "drPublisher": self.dr_publisher,
            "drUnit": self.dr_unit,
        }


# 与数据库表对应的检查项目类：
class CheckItem(db.Model):
    __tablename__ = "checks"

    ch_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ch_name = db.Column(db.String(255), nullable=True)
    ch_price = db.Column(db.Numeric(10, 2), nullable=True)

    def to_dict(self):
        return {
            "chId": self.ch_id,
            "chName": self.ch_name,
            "chPrice": (
                round(float(self.ch_price), 2) if self.ch_price is not None else None
            ),
        }


# 与数据库表对应的床号类：
class Bed(db.Model):
    __tablename__ = "bed"

    b_id = db.Column(db.Integer, primary_key=True)
    p_id = db.Column(db.Integer, db.ForeignKey("patient.p_id"), nullable=True)
    b_state = db.Column(db.Integer, nullable=True)
    b_start = db.Column(db.String(255), nullable=True)
    d_id = db.Column(db.Integer, db.ForeignKey("doctor.d_id"), nullable=True)
    b_reason = db.Column(db.String(255), nullable=True)
    b_end = db.Column(db.String(255), nullable=True)

    # 关联 patient 和 doctor
    patient = db.relationship("Patient", backref="beds", foreign_keys=[p_id])
    doctor = db.relationship("Doctor", backref="beds", foreign_keys=[d_id])

    def to_dict(self):
        return {
            "bId": self.b_id,
            "pId": self.p_id,
            "bState": self.b_state,
            "bStart": self.b_start,
            "dId": self.d_id,
            "bReason": self.b_reason,
            "bEnd": self.b_end,
        }


# 与数据库表对应的患者床号类：
class PBed(db.Model):
    __tablename__ = "p_bed"

    pb_id = db.Column(db.Integer, primary_key=True)  # 主键
    b_id = db.Column(db.Integer, nullable=True)  # 床位ID
    p_id = db.Column(db.Integer, nullable=True)  # 患者ID
    d_id = db.Column(db.Integer, nullable=True)  # 医生ID
    b_reason = db.Column(db.String(255), nullable=True)
    b_start = db.Column(db.String(255), nullable=True)  # 入住时间
    b_end = db.Column(db.String(255), nullable=True)  # 出院时间

    def to_dict(self):
        return {
            "pbId": self.pb_id,
            "bId": self.b_id,
            "pId": self.p_id,
            "dId": self.d_id,
            "bReason": self.b_reason,
            "bStart": self.b_start,
            "bEnd": self.b_end,
        }


# 与数据库表对应的挂号类：
# 挂号时生成该表
class Order(db.Model):
    __tablename__ = "orders"

    o_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    p_id = db.Column(
        db.Integer, db.ForeignKey("patient.p_id"), nullable=False
    )  # 关联患者
    d_id = db.Column(
        db.Integer, db.ForeignKey("doctor.d_id"), nullable=False
    )  # 关联医生
    o_start = db.Column(db.String(255), nullable=False)  # 预约时间段
    o_end = db.Column(db.String(255), nullable=False)  # 就诊结束时间
    o_state = db.Column(db.Integer, nullable=False)  # 挂号状态

    # 关联 order_details 和 order_items 和 alipay
    details = db.relationship("OrderDetail", backref="order", lazy=True)
    items = db.relationship("OrderItem", backref="order", lazy=True)
    alipay = db.relationship("Alipay", backref="order", lazy=True,uselist=False)

    def to_dict(self):
        return {
            "oId": self.o_id,
            "pId": self.p_id,
            "dId": self.d_id,
            "oStart": self.o_start,
            "oEnd": self.o_end,
            "oState": self.o_state,
        }


# 订单详情表
# 存储医生手写的记录以及手写的追诊记录
class OrderDetail(db.Model):
    __tablename__ = "order_details"
    o_id = db.Column(
        db.Integer, db.ForeignKey("orders.o_id"), primary_key=True, nullable=False
    )  # 关联 orders
    o_record = db.Column(db.String(255), nullable=True)  # 病历记录
    o_advice = db.Column(db.String(255), nullable=True)  # 医嘱

    def to_dict(self):
        return {
            "oId": self.o_id,
            "oRecord": self.o_record,
            "oAdvice": self.o_advice,
        }


# 订单项（检查、药品等）
# 存储非手写的记录
class OrderItem(db.Model):
    __tablename__ = "order_items"

    o_id = db.Column(
        db.Integer, db.ForeignKey("orders.o_id"), primary_key=True, nullable=False
    )  # 关联 orders
    o_drug = db.Column(db.String(255), nullable=True)  # 药品信息
    o_check = db.Column(db.String(255), nullable=True)  # 检查项目
    o_total_price = db.Column(db.Numeric(10, 2), nullable=True)  # 订单总价

    def to_dict(self):
        return {
            "oId": self.o_id,
            "oDrug": self.o_drug,
            "oCheck": self.o_check,
            "oTotalPrice": self.o_total_price,
        }


# 与数据库对应的支付记录
# 用于检查支付状态
class Alipay(db.Model):
    __tablename__ = "alipay"
    o_id = db.Column(db.Integer, db.ForeignKey("orders.o_id"), primary_key=True)
    o_price_state = db.Column(db.String(255), nullable=True)
    o_total_price = db.Column(db.Numeric(10, 2), nullable=True)
    o_gh_alipay = db.Column(db.String(255), nullable=True)
    o_alipay = db.Column(db.String(255), nullable=True)
    o_end = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "oId": self.o_id,
            "oPriceState": self.o_price_state,
            "oTotalPrice": self.o_total_price,
            "oGhAlipay": self.o_gh_alipay,
            "oAlipay": self.o_alipay,
            "oEnd": self.o_end,
        }


# 与数据库表对应的排班类：
class Arrange(db.Model):
    __tablename__ = "arrange"

    ar_id = db.Column(db.String(255), primary_key=True)
    ar_time = db.Column(db.String(255), nullable=True)
    d_id = db.Column(
        db.Integer,
        db.ForeignKey("doctor.d_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )

    # 关联医生信息
    doctor = db.relationship(
        "Doctor", backref=db.backref("arranges", cascade="all, delete-orphan")
    )

    def to_dict(self):
        return {"arId": self.ar_id, "arTime": self.ar_time, "dId": self.d_id}
