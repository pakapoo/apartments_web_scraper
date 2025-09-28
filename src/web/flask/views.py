from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import json
import db_functions as db

DB_USER = "admin"
DB_PASSWORD = "test1234"
DB_HOST = "apartments-rds.c5yi466cgccj.us-west-1.rds.amazonaws.com"
DB_PORT = "3306"
DB_NAME = "apartment_db"

views = Blueprint('views', __name__, template_folder="../templates", static_folder="../static")

@views.route('/', methods=['GET'])
def home():
    data = db.get_units(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
    top_management = db.get_top_management(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
    top_neighborhood = db.get_top_neighborhood(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

    return render_template(
        "index.html",
        data=data,
        top_management=top_management,
        top_neighborhood=top_neighborhood
    )

# http://127.0.0.1:5001/test?maxprice=100minprice=0
@views.route('/test', methods=['GET'])
def query():
    args = request.args
    maxprice = args.get('maxprice') if args.get('maxprice') else 1000000
    minprice = args.get('minprice') if args.get('minprice') else 0
    data = db.get_data('unit', DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
    return render_template("test.html", maxprice=maxprice, minprice=minprice)
