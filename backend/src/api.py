# from crypt import methods
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# CORS Headers


@app.after_request
def after_request(response):
    response.headers.add('Access-Control_Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control_Allow-Methods',
                         'GET,PATCH,POST,DELETE,OPTIONS')
    return response


db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_all_drinks():
    # get all the drinks
    all_drinks = Drink.query.all()
    # presenting data to short
    drinks = [drink.short() for drink in all_drinks]
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


@app.route('/drinks_detail', methods=['GET'])
@requires_auth('get:drinks_detail')
def get_all_drinks_details(payload):
    # get all drinks
    all_drinks = Drink.query.all()
    # presenting Drinks to long
    drinks = [drink.long() for drink in all_drinks]
    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks():
    # getting data
    data = request.get_json()
    drink_title = data['title']
    drink_recipe = data['recipe']
    # check the type of the data (drink recipe)
    if isinstance(drink_recipe, dict):
        drink_recipe = [drink_recipe]
    try:
        # initiating a drink
        drink = Drink()
        drink.title = drink_title
        # converting drink_recipe to string
        drink.recipe = json.dumps(drink_recipe)
        # insert new drink
        drink.insert()
    except:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    data = request.get_json()

    get_drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not get_drink:
        abort(404)
    try:
        drink_title = data['title']
        drink_recipe = data['recipe']
        if drink_title:
            get_drink.title = drink_title
        if drink_recipe:
            get_drink.recipe = json.dump(drink_recipe)
        # updating drink
        get_drink.update()
    except:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [get_drink.long()]
    }), 200


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):
    get_drink = Drink.query.get(id)
    if not get_drink:
        abort(404)
    try:
        get_drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        }), 200
    except:
        abort(404)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(AuthError)
def auth_error(error):
    print(error)
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


if __name__ == "__main__":
    app.debug = True
    app.run()
