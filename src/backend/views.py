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
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    result = []
    for row in rows:
        d = {}
        for i, col in enumerate(cursor.description):
            d[col[0]] = row[i]
        result.append(d)
    return result

# http://127.0.0.1:5000/?maxprice=100minprice=0
@views.route('/', methods=['GET'])
def home():
    args = request.args
    maxprice = args.get('maxprice') if args.get('maxprice') else 1000000
    minprice = args.get('minprice') if args.get('minprice') else 0
    data = get_data('unit', DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
    return render_template("index.html", maxprice=maxprice, minprice=minprice, data=data)

@views.route('/test', methods=['GET'])
def query():
    data = get_data('unit', DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
    return render_template("test.html")



@views.route('/go-to-home', methods=['GET'])
def go_to_home():
    return redirect(url_for('views.home'))

if __name__ == '__main__':
    get_data('unit', DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)