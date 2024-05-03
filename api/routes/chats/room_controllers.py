"""
    TODO: 
            1 - create a function for: ChatRoom.query.filter_by(name=name).first()
"""

# Module Imports:
from api.models.chat import ChatRoom
from api.models.user import User
from api.database import db

def get_all_rooms():
    return ChatRoom.query.all()

def get_user_rooms(id):
    # Query rooms where the user_ids array contains the specified id
    return ChatRoom.query.filter(ChatRoom.user_ids.contains([id])).all()

def get_room_by_name(name):
    return ChatRoom.query.filter_by(name=name).first()

def get_room_by_id(id):
    return ChatRoom.query.get(id)

def delete_room_by_name_or_id(identifier):
    """
    Delete a chat room by either its name or its ID.

    Args:
        identifier (str or int): Name or ID of the chat room to delete.

    Returns:
        ChatRoom or None: Deleted chat room instance, or None if not found.
    """
    
    if isinstance(identifier, str):
        # Delete by name
        room = ChatRoom.query.filter_by(name=identifier).first()
    else:
        # Delete by ID
        room = ChatRoom.query.get(identifier)
    
    if room:
        db.session.delete(room)
        db.session.commit()
    
    return room

def create_chat_room(name, creator_id, user_ids):
    """
    Create a new chat room.

    Args:
        name (str): Name of the chat room.
        creator_id (int): ID of the user creating the chat room.
        user_ids (list): List of user IDs to add to the chat room.

    Returns:
        ChatRoom: Created chat room instance.
    """
    
    # Check if a chat room with the same name already exists
    existing_chat_room = ChatRoom.query.filter_by(name=name).first()
    if existing_chat_room:
        # Return None if a chat room with the same name already exists
        return None
    
    # Create a new chat room
    chat_room = ChatRoom(name=name, creator_id=creator_id)

    # Add user IDs to the chat room
    for user_id in user_ids:
        user = User.query.get(user_id)
        if user:
            existing_user_ids = chat_room.user_ids or []  # Handle case when user_ids is None (Initially)
            new_user_ids = [user_id for user_id in user_ids if user_id not in existing_user_ids]
            chat_room.user_ids = existing_user_ids + new_user_ids
    
    # Commit the chat room creation
    try:
        db.session.add(chat_room)
        db.session.commit()
    except Exception as e:
        # Rollback the session if an exception occurs
        db.session.rollback()
        raise e  # Re-raise the exception for handling at a higher level
    
    return chat_room

def check_room(room, user_id):
    """
    Check if a user is added to a (existing) chat room.

    Args:
        room_id (int): ID of the chat room.
        user_id (int): ID of the user.

    Returns:
        bool: True if the user is added to the chat room, False otherwise.
    """
    
    chat_room = ChatRoom.query.filter_by(name=room).first()
    if chat_room:
        return user_id in chat_room.user_ids
    return False

    
def add_users_to_chat_room(chat_room_id, user_ids):
    """
    Add users to a chat room.

    Args:
        chat_room_id (int): ID of the chat room.
        user_ids (list): List of user IDs to add.

    Returns:
        ChatRoom or str: Updated chat room instance with added users, or error message.
    """
    
    chat_room = ChatRoom.query.get(chat_room_id)
    if chat_room:
        # try:
            for user_id in user_ids:
                user = User.query.get(user_id)
                if not user:
                    print("no user")
                    return f"User with ID {user_id} not found"
                if user_id not in chat_room.user_ids:  # Avoid duplicates
                    print("this works?")
                    chat_room.user_ids.append(user_id)
            db.session.commit()
            return chat_room
        # except Exception as e:
        #     db.session.rollback()
        #     return str(e)  # Return the error message as a string
    return "Chat room not found"