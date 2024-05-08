import random
import string
from datetime import datetime, timedelta
from api.database import db
from api.models.otp import OTP

# Function to generate OTP
def generate_otp():
    otp = ''.join(random.choices(string.digits, k=6))  # 6-digit OTP
    return otp

# Function to save OTP with expiry time in the database
def save_otp(email, otp, otp_for):
    expiry_time = datetime.now() + timedelta(minutes=5)  # OTP expiry time set to 5 minutes
    otp_record = OTP(email=email, otp=otp, otp_for=otp_for, expiry_time=expiry_time)
    db.session.add(otp_record)
    db.session.commit()

# Function to verify OTP
def verify_otp(email, otp):
    otp_record = OTP.query.filter_by(email=email).order_by(OTP.created_at.desc()).first()
    if otp_record and otp_record.otp == otp and datetime.now() <= otp_record.expiry_time:
        return True
    return False

# Function to Delete all OTP's of an email
def delete_all_otps(email):
    otp_records = OTP.query.filter_by(email=email).all()
    for otp_record in otp_records:
        db.session.delete(otp_record)
    db.session.commit()
