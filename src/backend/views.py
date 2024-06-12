from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import json
import db_functions

DB_USER = "root"
DB_PASSWORD = "admpw"
DB_HOST = "localhost"
DB_NAME = "apartment_db"

views = Blueprint('views', __name__)

# http://127.0.0.1:5000/?maxprice=100minprice=0
@views.route('/', methods=['GET'])
def home():
    args = request.args
    maxprice = args.get('maxprice') if args.get('maxprice') else 1000000
    minprice = args.get('minprice') if args.get('minprice') else 0
    data = db_functions.get_data('unit', DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
    return render_template("index.html", maxprice=maxprice, minprice=minprice, data=data)

@views.route('/test', methods=['GET'])
def query():
    data = db_functions.get_data('unit', DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
    return render_template("test.html")

if __name__ == '__main__':
    db_functions.get_data('unit', DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)