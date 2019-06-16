from flask import Flask, render_template, request, jsonify
import pyodbc
import redis
from flask import request
import time
import os




#port = int(os.getenv("VCAP_APP_PORT"))
#port = int(os.getenv('PORT', 5000))

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
    server = 'mysqlserver09.database.windows.net,1433'
    database = 'AKVDB'
    username = 'azureuser@mysqlserver09'
    password = '12345Ajuvad'
    driver = '{ODBC Driver 17 for SQL Server}'
    cnxn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    #cursor = cnxn.cursor()
    # cnxn = pypyodbc.connect(
    #     'Driver={ODBC Driver 13 for SQL Server};Server=tcp:mysqlserver09.database.windows.net,1433;Database=AKVDB;Uid=azureuser@mysqlserver09;Pwd=12345Ajuvad')
    return cnxn


@app.route("/client_homePage" , methods=['GET'])
def routerFunction():
    if request.args.get('form') == 'Submit':
        # db = sqlConnect()
        # cursor = db.cursor()
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
        # return "Hello Ajinkya You are doing great"


    if request.args.get('redis_cache_load') == 'redis_cache_load':
        cache = "mycache"
        magnitudeVal = request.args.get('mag')
        finalList = []
        # connect to db
        db = sqlConnect()
        cursor = db.cursor()
        queryString = "select * from earthquakeAssignment3 where mag > 6"
        # r.delete(cache)
        # print("deleted cache")
        if r.get(cache) == None:
            startTime = time.time()
            cursor.execute(queryString)
            data = cursor.fetchall()
            endTime = time.time()
            execTime = endTime - startTime
            print('This is your data',data)
            data_string = data
            r.set(cache, str(data_string)) #redis requires data to be in Convert to a byte, string or number first.
            finalList = data
            print("No Cache")
            print("No cache Time : ", execTime)
            isCacheOn = 'No cache'
        else:
            startTime = time.time()
            data1 = r.get(cache)
            endTime = time.time()
            execTime = endTime - startTime
            print("Cache Time is",execTime)
            data = data1
            print(data)
            print("Cache")
            print("Cache Time is", execTime)
            isCacheOn = 'In cache'
        db.close()
        return render_template("table.html", data = data, timetaken = str(execTime) , isCacheOn = isCacheOn)
        #return str(data)


        # cache = "mycache"
        # start_t = time.time()
        # query = "select * from earthquakeAssignment3"
        # if pickle.get(cache):
        #     t = "with"
        #     print(t)
        #     isCache = 'with Cache'
        #
        #     rows = pickle.loads(pickle.get(cache))
        #     pickle.delete(cache)
        #
        # else:
        #     t = "without"
        #     print(t)
        #     db = sqlConnect()
        #     cursor = db.cursor()
        #     cursor.execute(query)
        #     rows = cursor.fetchall()
        #     pickle.set(cache, pickle.dump(rows))
        # end_t = time.time() - start_t
        # print(end_t)
        # return render_template("table.html", data=t, stime=end_t)

#
# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=port, debug=False)


