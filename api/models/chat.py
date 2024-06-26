# Lib Imports:
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY


# Module Imports:
from api.database import db
from api.utils.helper import to_dict

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sender_name = db.Column(db.Text)
    sender_profile_image = db.Column(db.Text)
    
    content = db.Column(db.Text)
    created = db.Column(db.DateTime(timezone=True), default=datetime.now)
    
    # Establish the relationship with the ChatRoom table
    chat_room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'))
    # chat_room = db.relationship('ChatRoom', backref='messages_recieved')  # Define the relationship
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender_name': self.sender_name,
            'sender_profile_image': self.sender_profile_image,
            'content': self.content,
            'created': self.created.isoformat()  # Convert datetime to ISO 8601 formatted string
            # Add other attributes as needed
        }

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer, nullable=False)
    user_ids = db.Column(ARRAY(db.Integer), nullable=False, default=[])  # Initialize as an empty list
    user_names = db.Column(ARRAY(db.String(80)), nullable=False, default=[])

    last_message = db.Column(db.Text)
    last_message_sender_name = db.Column(db.Text)
    messages = db.relationship('Message', backref='chat_room', lazy=True)
    
    def to_dict(self):
        return to_dict(self)
        