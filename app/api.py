from flask import Blueprint, jsonify, request
import re
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from json import dumps
from .decorators import token_required
from jwt import encode
api = Blueprint('api', __name__)


def checkEmail(email):
    return re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)


def validation(fields):
    errors = []

    for field in fields:
        if request.form.get(field) == None:
            errors.append({field: "field is required."})
    if request.form.get('email') != None and not checkEmail(request.form.get('email')):
        errors.append({'email': "not a valid email."})

    return errors


@api.route('/login', methods=['POST'])
def login():
    #validation 
    if (len(validation(['email', 'password'])) > 0):
        return jsonify({"success": False, "errors": validation(['email', 'password'])})

    user = User.query.filter_by(email=request.form.get('email')).first()
    
    if(user == None):
     return jsonify({"success":False,"errors":{'email':"This email is not registered with us."}})
   
    if not check_password_hash(user.password, request.form.get('password')):
      return jsonify({"success":False,"errors":{'password':"Incorrect password."}})
    token = encode({"user": user.to_dict()}, "6fXDDDfMtWPPNUBDJDYnwH8Xouh66mi0OLBZTbus8cA", algorithm="HS256")
    print(token)
    return jsonify({'user':'hellowo'})


@api.route('/profile',methods=['GET'])
@token_required
def profile(current_user):
    return jsonify({"hello":"world"})