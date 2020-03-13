from app.model.user import Users
from app import response, db
from flask import request
import datetime
from flask_jwt_extended import *
from app import mail
from flask_mail import Message
from flask import render_template
from multiprocessing import Process


@jwt_required
def index():
    try:
        users = Users.query.all()
        data = transform(users)
        return response.ok(data, "")
    except Exception as e:
        print(e)


@jwt_required
def show(id):
    try:
        users = Users.query.filter_by(id=id).first()

        if not users:
            return response.badRequest([], 'data empty...!')

        data = singleTransform(users)
        return response.ok(data, "")
    except Exception as e:
        print(e)


def sendEmail(name, email):
    msg = Message("Hello, {} Welcome to Flask".format(name), sender="ceksongan@mail.com")
    msg.add_recipient(email)
    msg.html = render_template('mail.html', app_name="SMTP Gmail with Flask", app_contact="ceksongan@mail.com", name=name, email=email)
    mail.send(msg)


@jwt_required
def store():
    try:
        name = request.json['name']
        email = request.json['email']
        password = request.json['password']

        users = Users(name=name, email=email)
        users.setPassword(password)
        db.session.add(users)
        db.session.commit()

        p = Process(target=sendEmail, args=(name, email))
        p.start()

        return response.ok('', 'Succesfully create users!')
    except Exception as e:
        print(e)


@jwt_required
def update(id):
    try:
        name = request.json['name']
        email = request.json['email']
        password = request.json['password']

        users = Users.query.filter_by(id=id).first()
        users.name = name
        users.email = email
        users.setPassword(password)

        db.session.commit()

        return response.ok('', 'Succesfully update users!')
    except Exception as e:
        print(e)


@jwt_required
def delete(id):
    try:
        users = Users.query.filter_by(id=id).first()

        if not users:
            return response.badRequest([], 'data empty...!')

        db.session.delete(users)
        db.session.commit()

        return response.ok('', 'Succesfully delete users!')
    except Exception as e:
        print(e)


def login():
    try:
        email = request.json['email']
        password = request.json['password']

        users = Users.query.filter_by(email=email).first()

        if not users:
            return response.badRequest([], 'data empty...!')

        if not users.checkPassword(password):
            return response.badRequest([], 'credential is invalid!')

        data = singleTransform(users, withTodo=False)

        expires = datetime.timedelta(days=30)
        expires_refresh = datetime.timedelta(days=60)
        access_token = create_access_token(data, fresh=True, expires_delta=expires)
        refresh_token = create_refresh_token(data, expires_delta=expires_refresh)

        return response.ok({
            "data": data,
            "token_access": access_token,
            "token_refresh": refresh_token,
        }, "")
    except Exception as e:
        print(e)


@jwt_refresh_token_required
def refresh():
    try:
        user = get_jwt_identity()
        new_token = create_access_token(identity=user, fresh=False)

        return response.ok({
            "token_access": new_token
        }, "")

    except Exception as e:
        print(e)


def transform(users):
    array = []
    for i in users:
        array.append(singleTransform(i))
    return array


def singleTransform(users, withTodo=True):
    data = {
        'id': users.id,
        'name': users.name,
        'email': users.email,
    }

    if withTodo:
        todos = []
        for i in users.todos:
            todos.append({
                'id': i.id,
                'todo': i.todo,
                'description': i.description,
            })
        data['todos'] = todos

    return data
