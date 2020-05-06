import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# CORS header


# @app.after_request
# def after_request(response):
#     response.headers.add(
#         "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
#     )
#     response.headers.add("Access-Control-Allow-Methods",
#                          "GET,PUT,POST,DELETE,OPTIONS")
#     return response


"""
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
"""
db_drop_and_create_all()

# Seed dummy data

drink = Drink(
    title="esspresso",
    recipe='[{"name": "esspresso", "color": "brown", "parts": 1}]',
)
Drink.insert(drink)


# ROUTES


@app.route("/drinks")
def get_drinks():
    """Get drinks
       Response:
        success: A boolean indicating success
        drinks: A list of drinks
    """
    drinks = Drink.query.all()
    format_drinks = [drink.short() for drink in drinks]

    return jsonify({"success": True, "drinks": format_drinks}), 200


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks_detail(jwt):
    """Get drinks
       Response:
        success: A boolean indicating success
        drinks: A list of drinks
    """
    try:
        drinks = Drink.query.all()
        format_drinks = [drink.long() for drink in drinks]

        return jsonify({"success": True, "drinks": format_drinks}), 200
    except:
        abort(500)


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drink(jwt):
    try:
        get_input = request.get_json()

        title = get_input["title"]
        dict_recipe = get_input["recipe"]

        new_drink = Drink(title=title, recipe=json.dumps(dict_recipe))
        new_drink.insert()

        return jsonify({"success": True, "drinks": drink.long()}), 200
    except:
        abort(422)


@app.route("/drinks/<id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(jwt, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        else:
            title = request.get_json()["title"]
            if title == "":
                abort(400)
            else:
                drink.title = title
                drink.update()

                return jsonify({
                    "success": True,
                    "drinks": [drink.long()]
                    }), 200
    except:
        abort(422)


@app.route("/drinks/<id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(jwt, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        else:
            drink.delete()

            return jsonify({"success": True, "delete": id}), 200
    except:
        abort(422)


# Error Handling


@app.errorhandler(404)
def resource_not_found(error):
    return (
        jsonify({
            "success": False, "error": 404, "message": "resource not found"}),
        404,
    )


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, "error": 422, "message": "unprocessable"}), 422


@app.errorhandler(500)
def server_error(error):
    return (
        jsonify({
            "success": False, "error": 500, "message": "Server Error"}),
        500,
    )


@app.errorhandler(400)
def bad_request(error):
    return (
        jsonify(
            {
                "success": False,
                "error": 400,
                "message": "Bad Request, please check your inputs",
            }
        ),
        400,
    )


@app.errorhandler(401)
def unathorized(error):
    return jsonify({
        "success": False, "error": 401, "message": error.description, }), 401


@app.errorhandler(403)
def forbidden(error):
    return (
        jsonify(
            {
                "success": False,
                "error": 403,
                "message": "You are forbidden from accessing this resource",
            }
        ),
        403,
    )
