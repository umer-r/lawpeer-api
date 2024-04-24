# Lib Imports:
from datetime import datetime

# Module Imports:
from api.database import db
from api.utils.helper import to_dict


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    created = db.Column(db.DateTime(timezone=True), default=datetime.now)
    
    # Establish the relationship with the ChatRoom table
    chat_room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'))
    # chat_room = db.relationship('ChatRoom', backref='messages_recieved')  # Define the relationship
    
    def to_dict(self):
        return to_dict(self)

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    messages = db.relationship('Message', backref='chat_room', lazy=True)
    
    def to_dict(self):
        return to_dict(self)
        
# Define the association table outside of any model class
user_chat_rooms = db.Table('user_chat_rooms',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('chat_room_id', db.Integer, db.ForeignKey('chat_rooms.id'), primary_key=True)
)
