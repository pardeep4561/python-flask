from flask import Blueprint, jsonify, request
import re
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from json import dumps
from .decorators import token_required
from flask import current_app
from jwt import encode
from . import db

api = Blueprint('api', __name__)


def checkEmail(email):
    return re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)


def validation(fields):
    errors = []

    for field in fields:
        if request.form.get(field) == None or len(request.form.get(field)) == 0:
            errors.append({field: "field is required."})
    if request.form.get('email') != None and not checkEmail(request.form.get('email')):
        errors.append({'email': "not a valid email."})

    return errors


def genrateToken(user):
    return encode({"user": user.to_dict()},
                  current_app.config['JWT_SECRET_KEY'], algorithm="HS256")


@api.route('/login', methods=['POST'])
def login():
    # validation
    if (len(validation(['email', 'password'])) > 0):
        return jsonify({'success': False, 'errors': validation(['email', 'password'])})

    user = User.query.filter_by(email=request.form.get('email')).first()

    if (user == None):
        return jsonify({'success': False, 'errors': {'email': 'This email is not registered with us.'}})

    if not check_password_hash(user.password, request.form.get('password')):
        return jsonify({'success': False, 'errors': {'password': 'Incorrect password.'}})

    return jsonify({'user': user.to_dict(), 'token': genrateToken(user), 'success': True})


@api.route('/sign-up', methods=['POST'])
def register():
    fieldsList = ['email', 'password', 'first_name', 'confirm_password']
    user = User.query.filter_by(email=request.form.get('email')).first()
   # validation
    if (len(validation(fieldsList)) > 0):
        return jsonify({'success': False, 'errors': validation(fieldsList)})

    if (user):
        return jsonify({'success': False, 'errors': {'email': 'Email already exists.'}})
    elif len(request.form.get('first_name')) < 2:
        return jsonify({'success': False, 'errors': {'first_name': 'First name must be greater than 1 character.'}})
    elif request.form.get('password') != request.form.get('confirm_password'):
        return jsonify({'success': False, 'errors': {'confirm_password': 'Passwords don\'t match.'}})
    elif len(request.form.get('password')) < 7:
        return jsonify({'success': False, 'errors': {'password': 'Password must be at least 7 characters.'}})

    # creating user
    insert = User(email=request.form.get('email'), first_name=request.form.get('first_name'), password=generate_password_hash(
        request.form.get('password'), method='sha256'))
    db.session.add(insert)
    db.session.commit()
    return jsonify({'user': insert.to_dict(), 'token': genrateToken(insert), 'success': True})


@api.route('/upload', methods=['POST'])
@token_required
def upload(current_user):
    print(request.files['video'])
    return jsonify({"hello": "world"})
