from functools import wraps
import jwt
from flask import request, abort
from flask import current_app

from api.utils.status_codes import Status
from api.models.user import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, Status.HTTP_401_UNAUTHORIZED
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user=User().get_by_id(data["user_id"])
            if current_user is None:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            if not current_user["is_active"]:
                abort(Status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, Status.HTTP_500_INTERNAL_SERVER_ERROR

        return f(current_user, *args, **kwargs)

    return decorated
