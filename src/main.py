"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db, Person

APP = Flask(__name__)
APP.url_map.strict_slashes = False
APP.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(APP, db)
db.init_app(APP)
CORS(APP)

@APP.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@APP.route('/')
def sitemap():

    def has_no_empty_params(rule):
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)

    links = []
    for rule in APP.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append(url)

    links_html = "".join(["<li>" + y + "</li>" for y in links])
    return """
        <div style="text-align: center;">
        <img src='https://assets.breatheco.de/apis/img/4geeks/rigo-baby.jpg' />
        <h1>Hello Rigo!!</h1>
        This is your api home, remember to specify a real endpoint path like: <ul style="text-align: left;">"""+links_html+"</ul></div>"



@APP.route('/person', methods=['POST', 'GET'])
def handle_person():

    # POST request
    if request.method == 'POST':
        body = request.get_json()

        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        if 'username' not in body:
            raise APIException('You need to specify the username', status_code=400)
        if 'email' not in body:
            raise APIException('You need to specify the email', status_code=400)

        user1 = Person(username=body['username'], email=body['email'])
        db.session.add(user1)
        db.session.commit()
        # all_people = Person.query.all()
        # all_people = list(map(lambda x: x.serialize(), all_people))
        # return jsonify(all_people), 200
        return "ok", 200

    # GET request
    if request.method == 'GET':
        return "<div>yellow</div>", 200
        # all_people = Person.query.all()
        # all_people = list(map(lambda x: x.serialize(), all_people))
        # return jsonify(all_people), 200

    return "Invalid Method", 404


@APP.route('/person/<int:person_id>', methods=['PUT', 'GET', 'DELETE'])
def get_single_person(person_id):
    """
    Single person
    """

    # PUT request
    if request.method == 'PUT':
        body = request.get_json()
        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)

        user1 = Person.query.get(person_id)
        if user1 is None:
            raise APIException('User not found', status_code=404)

        if "username" in body:
            user1.username = body["username"]
        if "email" in body:
            user1.email = body["email"]
        db.session.commit()

        return jsonify(user1.serialize()), 200

    # GET request
    if request.method == 'GET':
        user1 = Person.query.get(person_id)
        if user1 is None:
            raise APIException('User not found', status_code=404)
        return jsonify(user1.serialize()), 200

    # DELETE request
    if request.method == 'DELETE':
        user1 = Person.query.get(person_id)
        if user1 is None:
            raise APIException('User not found', status_code=404)
        db.session.delete(user1)
        db.session.commit()
        return "ok", 200

    return "Invalid Method", 404


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    APP.run(host='0.0.0.0', port=PORT)


# print(app)