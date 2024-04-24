# Lib Imports:
from flask_socketio import emit

# Module Imports:
from api.models.chat import ChatRoom, Message
from api.models.user import User
from api.database import db

def create_chat_room(name):
    """
    Create a new chat room.

    Args:
        name (str): Name of the chat room.

    Returns:
        ChatRoom: Created chat room instance.
    """
    chat_room = ChatRoom(name=name)
    db.session.add(chat_room)
    db.session.commit()
    return chat_room

def add_user_to_chat_room(chat_room_id, user_id):
    """
    Add a user to a chat room.

    Args:
        chat_room_id (int): ID of the chat room.
        user_id (int): ID of the user to add.

    Returns:
        ChatRoom: Updated chat room instance with added user.
    """
    chat_room = ChatRoom.query.get(chat_room_id)
    if chat_room:
        user = User.query.get(user_id)
        if user:
            chat_room.users.append(user)
            db.session.commit()
            return chat_room
    return None

def send_message(room_id, message_content, user_id):
    """
    Send a message to a chat room.

    Args:
        room_id (int): ID of the chat room.
        message_content (str): Content of the message.
        user_id (int): ID of the user sending the message.
    """
    message = Message(sender_id=user_id, content=message_content, chat_room_id=room_id)
    db.session.add(message)
    db.session.commit()
    emit('receive_message', message.to_dict(), room=room_id, broadcast=True)
