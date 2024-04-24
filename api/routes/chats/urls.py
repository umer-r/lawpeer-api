# Lib Imports:
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import join_room, leave_room

# Module Imports:
from api.socketio import socketio
from api.utils.status_codes import Status

# Controller Imports:
from .controllers import create_chat_room, add_user_to_chat_room, send_message

chat_routes = Blueprint('chat', __name__)  # Define the chat routes Blueprint

@chat_routes.route('/chat-rooms', methods=['POST'])
@jwt_required()
def create_chat_room():
    data = request.get_json()
    name = data.get('name')
    chat_room = create_chat_room(name)
    if chat_room:
        return jsonify(chat_room.to_dict()), Status.HTTP_201_CREATED
    else:
        return jsonify({'message': 'Failed to create chat room'}), Status.HTTP_500_INTERNAL_SERVER_ERROR

@chat_routes.route('/chat-rooms/<int:chat_room_id>/users', methods=['POST'])
@jwt_required()
def add_user_to_chat_room(chat_room_id):
    data = request.get_json()
    user_id = data.get('user_id')
    chat_room = add_user_to_chat_room(chat_room_id, user_id)
    if chat_room:
        return jsonify(chat_room.to_dict()), Status.HTTP_200_OK
    else:
        return jsonify({'message': 'Failed to add user to chat room'}), Status.HTTP_500_INTERNAL_SERVER_ERROR

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data.get('room_id')
    join_room(room_id)

@socketio.on('leave_room')
def handle_leave_room(data):
    room_id = data.get('room_id')
    leave_room(room_id)

@socketio.on('send_message')
def handle_send_message(data):
    room_id = data.get('room_id')
    message_content = data.get('content')
    user_id = get_jwt_identity()
    send_message(room_id, message_content, user_id)
