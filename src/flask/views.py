from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import mysql.connector
import json

views = Blueprint('views', __name__)


DB_USER = "root"
DB_PASSWORD = "admpw"
DB_HOST = "localhost"
DB_NAME = "apartment_db"
def get_data(table, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME):
    conn = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM unit")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return json.dumps(data, default=str)

# http://127.0.0.1:5000/?maxprice=100minprice=0
@views.route('/', methods=['GET'])
def home():
    args = request.args
    maxprice = args.get('maxprice') if args.get('maxprice') else 1000000
    minprice = args.get('minprice') if args.get('minprice') else 0
    return render_template("index.html", maxprice=maxprice, minprice=minprice)

@views.route('/query', methods=['GET'])
def query():
    data = get_data('unit', DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
    return render_template("query_result.html", data=data)



@views.route('/go-to-home', methods=['GET'])
def go_to_home():
    return redirect(url_for('views.home'))