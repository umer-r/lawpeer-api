from werkzeug.utils import secure_filename
import os
# Module Imports:
from api.models.chat import ChatRoom, Message
from api.models.user import User
from api.database import db
from api.utils.helper import allowed_documents, get_upload_folder, rename_document

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
    
        user = User.query.get(user_id)
        if user:
            sender_name = user.first_name + " " + user.last_name
            
            # Set room related fields:
            room.last_message = message_content
            room.last_message_sender_name = sender_name
            
            if user.profile_image:
                sender_profile_image = user.profile_image
            else:
                sender_profile_image = '/static/stock_user.jpg'
        else:
            return None
        
        message = Message(sender_id=user_id, sender_name=sender_name, sender_profile_image=sender_profile_image, content=message_content, chat_room_id=room_id)
        db.session.add(message)
        db.session.commit()
    
def get_room_messages_by_id(id):
    return Message.query.filter_by(chat_room_id=id).all()

def save_document(file):
    UPLOAD_FOLDER = get_upload_folder()
    if file:
        filename = secure_filename(rename_document(file))
        if allowed_documents(filename):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Refactor if gives a bug:
            url = os.path.join('/static', filename).replace('\\', '/')
            return url
    return None