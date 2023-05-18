from flask import *
import os

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})



import psycopg2
from datetime import datetime
import pytz



app = Flask(__name__)

switch1 = True
switch2 = True

sqlURL = 'postgres://mbidwufk:BQ8BSbGc0pl_AWOMv4oxgi1G44ogy0id@horton.db.elephantsql.com/mbidwufk'


connection = psycopg2.connect(sqlURL)
try:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE TABLE switch_data (switchno INT, switchstatus INT);")
            cursor.execute("CREATE TABLE farm_data (Time VARCHAR ( 50 ), Temperature VARCHAR ( 10 ), Humidity VARCHAR ( 10 ), moisture VARCHAR ( 10 ));")
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO switch_data VALUES (%s,%s);", (1, 1))
            cursor.execute("INSERT INTO switch_data VALUES (%s,%s);", (2, 1))
except psycopg2.errors.DuplicateTable:
    pass


@app.route('/send_data', methods=['GET'])
def AddData():
    temp = str(request.args['temperature'])
    humid = str(request.args['humidity'])
    moist = str(request.args['moisture'])

    # it will get the time zone
    # of the specified location
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    today = datetime.today()
    d1 = str(today.strftime("%d/%m/%Y"))
    current_time = d1+" "+str(now.strftime("%H:%M:%S"))
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO farm_data VALUES (%s,%s,%s,%s);", (current_time, temp, humid, moist))

    return jsonify("data updated succesfully")


@app.route('/retrieve_data', methods=['GET'])
def retrieveData():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT Time,Temperature,Humidity,moisture FROM farm_data ORDER BY Time DESC LIMIT 10;")
            result = cursor.fetchall()
    resp = make_response(jsonify(result))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/retrievestatus', methods=['GET'])
def switchStatus():
    # search = str(request.args['query'])
    dict = {}
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM switch_data order by switchno asc;")
            switch_data = cursor.fetchall()
    if switch_data[0][0] == 1 and switch_data[0][1] == 1:
        dict['switch1'] = True;
    if switch_data[0][0] == 1 and switch_data[0][1] == 0:
        dict['switch1'] = False;

    if switch_data[1][0] == 2 and switch_data[1][1] == 1:
        dict['switch2'] = True;
    if switch_data[1][0] == 2 and switch_data[1][1] == 0:
        dict['switch2'] = False;
    resp = make_response(dict)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/switch1', methods=['GET'])
def changeStatus1():
    search = str(request.args['query'])
    if search == 'on':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE switch_data SET switchstatus=%s WHERE switchno=%s;", (1, 1))
                # cursor.execute("INSERT INTO switch_data VALUES (%s,%s);", (1, 1))
        return jsonify('switch1 is on')
    if search == 'off':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE switch_data SET switchstatus=%s WHERE switchno=%s;", (0, 1))
        return jsonify('switch1 is off')


@app.route('/switch2', methods=['GET'])
def changeStatus2():
    search = str(request.args['query'])
    if search == 'on':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE switch_data SET switchstatus=%s WHERE switchno=%s;", (1, 2))
        return jsonify('switch2 is on')
    if search == 'off':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE switch_data SET switchstatus=%s WHERE switchno=%s;", (0, 2))
        return jsonify('switch2 is off')


if __name__ == '__main__':
  app.run(port=5000)
