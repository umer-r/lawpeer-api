from sqlalchemy import inspect
from datetime import datetime
from sqlalchemy.orm import validates

from api.database import db

# ----------------------------------------------- #

# SQL Datatype Objects => https://docs.sqlalchemy.org/en/14/core/types.html
class User(db.Model):
  __tablename__ = 'users'
  # Auto Generated Fields:
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  created = db.Column(db.DateTime(timezone=True), default=datetime.now)                           # The Date of the Instance Creation => Created one Time when Instantiation
  updated = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)    # The Date of the Instance Update => Changed with Every Update

  # Input by User Fields:
  email = db.Column(db.String(100), nullable=False, unique=True)
  username = db.Column(db.String(100), nullable=False)
  dob = db.Column(db.Date)
  country = db.Column(db.String(100))
  phone_number = db.Column(db.String(20))
  
  # Set an empty string to null for username field => https://stackoverflow.com/a/57294872
  @validates('username')
  def empty_string_to_null(self, key, value):
    if isinstance(value, str) and value == '': return None
    else: return value


# How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
  def toDict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

  def __repr__(self):
    return "<%r>" % self.email
