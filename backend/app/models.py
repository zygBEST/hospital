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

    def to_dict(self):
        return {
            'd_id': self.d_id,
            'd_name': self.d_name,
            'd_gender': self.d_gender,
            'd_post': self.d_post,
            'd_section': self.d_section,
            'd_card': self.d_card,
            'd_phone': self.d_phone,
            'd_email': self.d_email,
            'd_avg_star':self.d_star,
            'd_price': self.d_price,
            'd_state': self.d_state,
        }

# 与数据库表对应的挂号类：
class Order(db.Model):
    __tablename__ = 'orders'

    o_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    p_id = db.Column(db.Integer, db.ForeignKey('patient.p_id'), nullable=True)
    d_id = db.Column(db.Integer, db.ForeignKey('doctor.d_id'), nullable=True)
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
