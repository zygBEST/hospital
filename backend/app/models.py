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
