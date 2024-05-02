"""
    TODO:
            1 - Merge create_new_chat_room() and add_user().                    - [DONE]
            2 - Complete send_message                                           - [DONE] -- Test it now somehow.
            3 - Add check before letting a user join a room                     - [DONE]
            4 - Split check_room_exists and check_user_in_room (or modify)      - []
            5 - Implement adding user to chat room after creation               - []
            6 - Implement Access control.                                       - [DONE]
            7 - Add Routes for:
            
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
from api.socketio import socketio
from api.utils.status_codes import Status

# Controller Imports:
from .room_controllers import create_chat_room, add_users_to_chat_room, check_room, get_all_rooms, get_user_rooms, get_room_by_name, get_room_by_id, delete_room_by_name_or_id
from .message_controllers import save_message, get_room_messages_by_id

# Decorators import:
from api.decorators.access_control_decorators import admin_required, user_or_admin_required

chat_routes = Blueprint('chat', __name__)  # Define the chat routes Blueprint

## --  ChatRoom Routes  --  ##

@chat_routes.route('/chat-rooms', methods=['POST'])
@jwt_required()
def create_new_chat_room():
    data = request.get_json()
    name = data.get('name')
    user_ids = data.get('user_ids')
    creator_id = get_jwt_identity().get('id')
    chat_room = create_chat_room(name=name, creator_id=creator_id, user_ids=user_ids)
    if chat_room is not None:
        return jsonify(chat_room.to_dict()), Status.HTTP_201_CREATED
    else:
        return jsonify({'message': 'Chat room with the same name already exists'}), Status.HTTP_409_CONFLICT
    
@chat_routes.route('/chat-rooms', methods=['GET'])
@jwt_required()
@admin_required
def get_all():
    rooms = get_all_rooms()
    if rooms:
        return jsonify([room.to_dict() for room in rooms]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No Chat rooms found'}), Status.HTTP_404_NOT_FOUND

@chat_routes.route('/chat-rooms/<int:room_id>', methods=['GET'])
@jwt_required()
def room_by_id(room_id):
    room = get_room_by_id(room_id)
    if room:
        return jsonify(room.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'message': f'No Chat room: {room_id} found'}), Status.HTTP_404_NOT_FOUND

@chat_routes.route('/chat-rooms/<path:name>', methods=['GET'])
@jwt_required()
def room_by_name(name):
    room = get_room_by_name(name)
    if room:
        return jsonify(room.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'message': f'No Chat room: {name} found'}), Status.HTTP_404_NOT_FOUND

@chat_routes.route('/chat-rooms/user/<int:id>', methods=['GET'])
@jwt_required()
@user_or_admin_required
def user_rooms(id):
    rooms = get_user_rooms(id)
    if rooms:
        return jsonify([room.to_dict() for room in rooms]), Status.HTTP_200_OK
    
    return jsonify({'message': f'No Chat rooms found for user: {id}'}), Status.HTTP_404_NOT_FOUND

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
        emit("join", {"data": f"id: {request.sid}", "status": f"{username} is Online."}, to=room)
    else:
        emit("join", {"error": "Chat room not accessible."})

@socketio.on('send_message')
@jwt_required()
def handle_send_message(data):
    
    room = data.get('room_name')
    message_content = data.get('content')
    user_id = get_jwt_identity().get('id')
    if check_room(room, user_id):
        join_room(room)
        save_message(room_name=room, message_content=message_content, user_id=user_id)
        emit("send_message", {"data": f"from: {user_id}", "message": f"{message_content}"}, to=room)
    else:
        emit("send_message", {"error": "Chat room not accessible."})

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
        return jsonify({'message': 'Failed to add user to chat room'}), Status.HTTP_500_INTERNAL_SERVER_ERROR
    
## --  Messages Routes  --  ##

@chat_routes.route('/room-messages/<int:room_id>', methods=['GET'])
@jwt_required()
def room_messages(room_id):
    msgs = get_room_messages_by_id(room_id)
    if msgs:
        return jsonify([msg.to_dict() for msg in msgs]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No Chat rooms found'}), Status.HTTP_404_NOT_FOUND

## --  Messages Routes  --  # END #