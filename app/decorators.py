from functools import wraps
from flask import request, jsonify
from jwt import decode
from .models import User


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
            data = decode(token, "6fXDDDfMtWPPNUBDJDYnwH8Xouh66mi0OLBZTbus8cA")
            print(data, 'hello')
            # current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return f({'hhd'}, *args, **kwargs)

    return decorated
