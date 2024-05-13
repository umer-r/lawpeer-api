"""
    Blueprint (urls) File; Manages routes related to ChatRoom & Messages.
    
    External Libraries:
        - flask
        - flask_jwt_extended
        - flask_socketio

    Function Names:
        - create_new_chat_room: (JWT)     Create a new chat room.
        - get_all: (JWT)                  Retrieve all chat rooms.
        - room_by_id: (JWT)               Retrieve a chat room by its ID.
        - room_by_name: (JWT)             Retrieve a chat room by its name.
        - user_rooms: (JWT)               Retrieve chat rooms of a user.
        - my_rooms: (JWT)                 Retrieve chat rooms of the logged-in user.
        - handle_join_room: (JWT)         Handle joining a chat room through WebSocket.
        - handle_send_message: (JWT)      Handle sending a message in a chat room through WebSocket.
        - handle_leave_room:              Handle leaving a chat room through WebSocket.
        - add_user: (JWT)                 Add a user to a chat room.
        - room_messages: (JWT)            Retrieve messages of a chat room.
        - save_doc: (JWT)                 Save a document.
        
    TODO:
            1 - Merge create_new_chat_room() and add_user().                    - [DONE]
            2 - Complete send_message                                           - [DONE] -- Test it now somehow.
            3 - Add check before letting a user join a room                     - [DONE]
            4 - Split check_room_exists and check_user_in_room (or modify)      - []
            5 - Implement adding user to chat room after creation               - []
            6 - Implement Access control.                                       - [DONE]
            7 - Implement ONLY Admin can create chat rooms for other people.
                User can not create chat rooms for other people.
            8 - Globalize the save document route for profile and other stuff.
            9 - Add Routes for:
            
                * ChatRoom:
                - Create Chat room.                                             - [DONE]
                - Get all rooms.                                                - [DONE]
                - Get user chat rooms.                                          - [DONE]
                - Get room by id.                                               - [DONE]
                - Get room by name.                                             - [DONE]
                - Delete chat room by name or id.                               - []
                
                * Message:
                - Messages for particular chat room.                            - [DONE]
                - Messages for particular chat room by ChatRoom name.           - []
                - Save document message                                         - []
"""

# Lib Imports:
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import join_room, leave_room, emit

# Module Imports:
from api.extentions.socketio import socketio
from api.utils.status_codes import Status

# Controller Imports:
from .room_controllers import create_chat_room, add_users_to_chat_room, check_room, get_all_rooms, get_user_rooms, get_room_by_name, get_room_by_id, delete_room_by_name_or_id
from .message_controllers import save_message, get_room_messages_by_id, save_document

# Decorators import:
from api.decorators.access_control_decorators import admin_required, user_or_admin_required
from api.decorators.mandatory_keys import check_mandatory

# ----------------------------------------------- #

chat_routes = Blueprint('chat', __name__) 

## --  ChatRoom Routes  --  ##

@chat_routes.route('/chat-rooms', methods=['POST'])
@jwt_required()
@check_mandatory(['name', 'user_ids'])
def create_new_chat_room():
    data = request.get_json()
    name = data.get('name')
    user_ids = data.get('user_ids')
    creator_id = get_jwt_identity().get('id')
    chat_room = create_chat_room(name=name, creator_id=creator_id, user_ids=user_ids)
    if chat_room is not None:
        return jsonify(chat_room.to_dict()), Status.HTTP_201_CREATED
    else:
        return jsonify({'error': 'Chat room with the same name already exists'}), Status.HTTP_409_CONFLICT
    
@chat_routes.route('/chat-rooms', methods=['GET'])
@jwt_required()
@admin_required
def get_all():
    rooms = get_all_rooms()
    if rooms:
        return jsonify([room.to_dict() for room in rooms]), Status.HTTP_200_OK
    
    return jsonify({'error': 'No Chat rooms found'}), Status.HTTP_404_NOT_FOUND

@chat_routes.route('/chat-rooms/<int:room_id>', methods=['GET'])
@jwt_required()
def room_by_id(room_id):
    room = get_room_by_id(room_id)
    if room:
        return jsonify(room.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'error': f'No Chat room: {room_id} found'}), Status.HTTP_404_NOT_FOUND

@chat_routes.route('/chat-rooms/<path:name>', methods=['GET'])
@jwt_required()
def room_by_name(name):
    room = get_room_by_name(name)
    if room:
        return jsonify(room.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'error': f'No Chat room: {name} found'}), Status.HTTP_404_NOT_FOUND

@chat_routes.route('/chat-rooms/user/<int:id>', methods=['GET'])
@jwt_required()
@user_or_admin_required
def user_rooms(id):
    rooms = get_user_rooms(id)
    if rooms:
        return jsonify([room.to_dict() for room in rooms]), Status.HTTP_200_OK
    
    return jsonify({'error': f'No Chat rooms found for user: {id}'}), Status.HTTP_404_NOT_FOUND

@chat_routes.route('/chat-rooms/my-rooms', methods=['GET'])
@jwt_required()
def my_rooms():
    id = get_jwt_identity().get('id')
    rooms = get_user_rooms(id)
    if rooms:
        return jsonify([room.to_dict() for room in rooms]), Status.HTTP_200_OK
    
    return jsonify({'error': f'No Chat rooms found for user: {id}'}), Status.HTTP_404_NOT_FOUND

## --  ChatRoom Routes  --  # END #

## --  SOCKET.io Events  --  ##

@socketio.on('join')
@jwt_required()
def handle_join_room(data):
    room = data.get('room_name')
    username = data.get('username')
    user_id = get_jwt_identity().get('id')
    
    if check_room(room, user_id):
        join_room(room)
        emit("join", 
             {  "sid": request.sid, 
                "success": True,
                "is_online": True, 
                "status": f"{username} is Online."}, 
            to=room)
    else:
        emit("join", {"error": "Chat room not accessible.", "success": False})

@socketio.on('send_message')
@jwt_required()
def handle_send_message(data):
    
    room = data.get('room_name')
    message_content = data.get('content')
    user_id = get_jwt_identity().get('id')
    if check_room(room, user_id):
        join_room(room)
        message = save_message(room_name=room, message_content=message_content, user_id=user_id)
        emit("send_message", message.to_dict(),
            #  {  "status": "message sent", 
            #     "success": True,
            #     "from": user_id, 
            #     "message": message_content, 
            #     "room": room }, 
        to=room)
    else:
        emit("send_message", {"error": "Chat room not accessible.", "success": False})

@socketio.on('leave_room')
def handle_leave_room(data):
    room_id = data.get('room_id')
    leave_room(room_id)
    
## --  SOCKET.io Events  --  # END #

# FIXME:
## - Complete the following
@chat_routes.route('/chat-rooms/<int:chat_room_id>/users', methods=['POST'])
@jwt_required()
def add_user(chat_room_id):
    data = request.get_json()
    user_id = data.get('user_id')
    chat_room = add_users_to_chat_room(chat_room_id, user_id)
    if chat_room:
        return jsonify(chat_room.to_dict()), Status.HTTP_200_OK
    else:
        return jsonify({'error': 'Failed to add user to chat room'}), Status.HTTP_500_INTERNAL_SERVER_ERROR
    
## --  Messages Routes  --  ##

@chat_routes.route('/room-messages/<int:room_id>', methods=['GET'])
@jwt_required()
def room_messages(room_id):
    msgs = get_room_messages_by_id(room_id)
    if msgs:
        return jsonify([msg.to_dict() for msg in msgs]), Status.HTTP_200_OK
    
    return jsonify({'error': 'No Chat rooms found'}), Status.HTTP_404_NOT_FOUND

@chat_routes.route('/save-document', methods=['POST'])
@jwt_required()
def save_doc():
    doc = request.files.get('document')
    document_saved = save_document(doc)
    if document_saved:
        return jsonify({'path': document_saved}), Status.HTTP_200_OK
    
    return jsonify({'error': 'Server error while saving document'}), Status.HTTP_500_INTERNAL_SERVER_ERROR

## --  Messages Routes  --  # END #
