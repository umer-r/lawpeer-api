"""
    Util file; Contains functions for OTP (One-Time Password) generation, saving, verification, and deletion from the database.

    External Libraries:
        - random: A module in Python that provides functions for generating random numbers.
        - string: A module in Python that provides functions for manipulating strings.
        - datetime: A module in Python that supplies classes for manipulating dates and times.

    Function Names:
        - generate_otp
        - save_otp
        - verify_otp
        - delete_all_otps
"""

# Lib Imports:
import random
import string
from datetime import datetime, timedelta

# Module Imports:
from api.database import db
from api.models.otp import OTP

# ----------------------------------------------- #

def generate_otp():
    """
    Function to generate OTP.

    Returns:
        - otp (str): The generated OTP.
    """
    
    otp = ''.join(random.choices(string.digits, k=6))  # 6-digit OTP
    return otp

def save_otp(email, otp, otp_for):
    """
    Function to save OTP with expiry time in the database.

    Parameters:
        - email (str): The email associated with the OTP.
        - otp (str): The OTP to be saved.
        - otp_for (str): The purpose for which OTP is generated.

    Returns:
        - None
    """
    expiry_time = datetime.now() + timedelta(minutes=5)  # OTP expiry time set to 5 minutes
    otp_record = OTP(email=email, otp=otp, otp_for=otp_for, expiry_time=expiry_time)
    db.session.add(otp_record)
    db.session.commit()

def verify_otp(email, otp):
    """
    Function to verify OTP.

    Parameters:
        - email (str): The email associated with the OTP.
        - otp (str): The OTP to be verified.

    Returns:
        - bool: True if the OTP is valid and not expired, False otherwise.
    """
    
    otp_record = OTP.query.filter_by(email=email).order_by(OTP.created_at.desc()).first()
    if otp_record and otp_record.otp == otp and datetime.now() <= otp_record.expiry_time:
        return True
    return False

def delete_all_otps(email):
    """
    Function to delete all OTPs associated with an email from the database.

    Parameters:
        - email (str): The email associated with the OTPs to be deleted.

    Returns:
        - None
    """
    
    otp_records = OTP.query.filter_by(email=email).all()
    for otp_record in otp_records:
        db.session.delete(otp_record)
    db.session.commit()
