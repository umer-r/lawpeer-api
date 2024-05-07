from api.database import db
from api.utils.helper import to_dict

# Define Skill Model
class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    def to_dict(self):
        return to_dict(self)

# Define Association Table
lawyer_skills = db.Table('lawyer_skills',
    db.Column('lawyer_id', db.Integer, db.ForeignKey('lawyers.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True)
)