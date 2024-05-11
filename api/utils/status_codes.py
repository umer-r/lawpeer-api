"""
    Util file; Contains class that defines common HTTP status codes as class attributes.

    Class Names:
        - Status
"""

# ----------------------------------------------- #

class Status:
    """ 
    Defines common HTTP status codes
    """
    
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_409_CONFLICT = 409                 # Conflict - For Duplicate Content
    HTTP_422_UNPROCESSABLE_ENTITY = 422     # For Missing keys/fields
    HTTP_429_TOO_MANY_REQUESTS = 429
    HTTP_500_INTERNAL_SERVER_ERROR = 500
