from functools import wraps
from flask import request, jsonify
from jwt import decode
from .models import User
from flask import current_app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = decode(token, current_app.config['JWT_SECRET_KEY'],algorithms=['HS256'])
            current_user = data['user']
        except:
            return jsonify({
                'message': 'Token is invalid or expired. !!'
            }), 401
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated
