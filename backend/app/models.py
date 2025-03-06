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
    p_state = db.Column(db.Integer, nullable=True)  # 新增字段
    p_birthday = db.Column(db.String(255), nullable=True)
    p_age = db.Column(db.Integer, nullable=True)  # 新增字段

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


# 与数据库表对应的医生类：
class Doctor(db.Model):
    __tablename__ = "doctor"

    d_id = db.Column(db.Integer, primary_key=True, nullable=False)
    d_password = db.Column(db.String(255), nullable=True)
    d_name = db.Column(db.String(255), nullable=True)
    d_gender = db.Column(db.String(255), nullable=True)
    d_phone = db.Column(db.String(255), nullable=True)
    d_card = db.Column(db.String(255), nullable=True)
    d_email = db.Column(db.String(255), nullable=True)
    d_post = db.Column(db.String(255), nullable=True)
    d_introduction = db.Column(db.String(255), nullable=True)
    d_section = db.Column(db.String(255), nullable=True)
    d_state = db.Column(db.Integer, nullable=False)
    d_price = db.Column(db.Numeric(10, 2), nullable=True)
    d_people = db.Column(db.Integer, nullable=True)
    d_star = db.Column(db.Numeric(10, 2), nullable=True)
    d_avg_star = db.Column(db.Numeric(10, 2), nullable=True)

    def to_dict(self):
        return {
            "dId": self.d_id,
            "dName": self.d_name,
            "dGender": self.d_gender,
            "dPost": self.d_post,
            "dSection": self.d_section,
            "dCard": self.d_card,
            "dPhone": self.d_phone,
            "dEmail": self.d_email,
            "dAvgStar": self.d_avg_star,
            "dPrice": self.d_price,
            "dIntroduction": self.d_introduction,
            "dState": self.d_state,
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
            "drPrice": float(self.dr_price) if self.dr_price else None,
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
            "chPrice": str(self.ch_price),
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
    version = db.Column(db.Integer, nullable=True)

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
            "version": self.version,
        }


# 与数据库表对应的挂号类：
class Order(db.Model):
    __tablename__ = "orders"

    o_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    p_id = db.Column(db.Integer, db.ForeignKey("patient.p_id"), nullable=True)
    d_id = db.Column(db.Integer, db.ForeignKey("doctor.d_id"), nullable=True)
    o_record = db.Column(db.String(255), nullable=True)
    o_start = db.Column(db.String(255), nullable=True)
    o_end = db.Column(db.String(255), nullable=True)
    o_state = db.Column(db.Integer, nullable=True)
    o_drug = db.Column(db.String(255), nullable=True)
    o_check = db.Column(db.String(255), nullable=True)
    o_total_price = db.Column(db.Numeric(10, 2), nullable=True)
    o_price_state = db.Column(db.Integer, nullable=True)
    o_advice = db.Column(db.String(255), nullable=True)
    o_alipay = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "oId": self.o_id,
            "pId": self.p_id,
            "dId": self.d_id,
            "oRecord": self.o_record,
            "oStart": self.o_start,
            "oEnd": self.o_end,
            "oState": self.o_state,
            "oDrug": self.o_drug,
            "oCheck": self.o_check,
            "oTotalPrice": self.o_total_price,
            "oPriceState": self.o_price_state,
            "oAdvice": self.o_advice,
            "oAlipay": self.o_alipay,
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
