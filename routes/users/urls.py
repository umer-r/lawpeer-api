# Lib imports
from flask import Blueprint, jsonify, request, send_file
import os

user_routes = Blueprint('users', __name__)

### Routes for Users below:
##
#
@user_routes.route('/', methods=['GET'])
def index():
    return jsonify(message='API Route for Users')