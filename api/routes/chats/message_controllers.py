# Module Imports:
from api.models.chat import ChatRoom, Message
from api.models.user import User
from api.database import db

def save_message(room_name, message_content, user_id):
    """
    Send a message to a chat room.

    Args:
        room_id (int): ID of the chat room.
        message_content (str): Content of the message.
        user_id (int): ID of the user sending the message.
    """
    
    room = ChatRoom.query.filter_by(name=room_name).first()
    if room:
        room_id = room.id
    else:
        room_id = 0
    
    message = Message(sender_id=user_id, content=message_content, chat_room_id=room_id)
    db.session.add(message)
    db.session.commit()
    
def get_room_messages_by_id(id):
    return Message.query.filter_by(chat_room_id=id).all()