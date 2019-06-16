from flask import Flask, render_template, request, jsonify
import pypyodbc
import redis
from flask import request


# redis connection code
r = redis.StrictRedis(host='redisCacheAssignemnt3.redis.cache.windows.net',
        port=6380, password='CK6g5axYGYf4e0T08H9vBc6+obM7GtWJfZOPqrGgkBE=', ssl=True)



#print(cnxn)
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('client_homePage.html')

# method to connect to Db
def sqlConnect():
    cnxn = pypyodbc.connect(
        'Driver={ODBC Driver 13 for SQL Server};Server=tcp:mysqlserver09.database.windows.net,1433;Database=AKVDB;Uid=azureuser@mysqlserver09;Pwd=12345Ajuvad')
    return cnxn


@app.route("/client_homePage" , methods=['GET'])
def routerFunction():
    if request.args.get('form') == 'Submit':
        mag = request.args.get('eathquake_mag')
        oper = request.args.get('symbol_operator')
        print(oper)
        print(mag)
        # connect to db
        db = sqlConnect()
        cursor = db.cursor()
        # query = '''SELECT * FROM BVC79655.TBEARTHQUAKE WHERE "mag"'''+oper+mag
        query = '''SELECT * FROM earthquakeAssignment3 WHERE "mag"'''+oper+mag
        print(query)
        cursor.execute(query)
        row = cursor.fetchall()
        # ibm_db.bind_param(stmt, 1, name)
        return str(row)

