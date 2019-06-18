from flask import Flask, render_template, request, jsonify
import pyodbc
import redis
from flask import request
import time
import os
from datetime import datetime
import json
from datetime import timedelta


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
    return cnxn


#function to check in cache
def readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString, count):
    st = time.time()
    for i in range(count):
        if r.get(cache) == None:
            dataList=[]
            #startTime = time.time()
            print(queryString)
            cursor.execute(queryString)
            data = cursor.fetchall()
            print(data)
            for row in data:
                dataList.append([x for x in row])
                print('.........',dataList)
            #endTime = time.time()
            #execTime = endTime - startTime
            #data_string = data
            #r.rpush(cache, data)
            #r.set(cache, str(data_string))  # redis requires data to be in Convert to a byte, string or number first.
            r.set(cache, json.dumps(dataList))
            #finalList = data
            print("No Cache")
            #print("No cache Time : ", execTime)
            isCacheOn = 'No cache'

        else:
            #startTime = time.time()
            #data = json.loads(r.get(cache))
            data = r.get(cache)
            print(data)
            #endTime = time.time()
            #execTime = endTime - startTime
            #print("Cache Time is", execTime)
            print("Cache")
            #print("Cache Time is", execTime)
            isCacheOn = 'In cache'
            isCacheOnboolean = True
        print(time.time() - st)
    return data, isCacheOnboolean, isCacheOn


#read from DB
def readfromDb(cursor, queryString):
        print(queryString)
        cursor.execute(queryString)
        data = cursor.fetchall()
        # print(data)
        print("Only from DB")
        isCacheOn = 'From Db Only'
        return data, isCacheOn

#read from cache :- Make sure that data is in cache otherwise throw error

def readFromCache(cache, isCacheOnboolean, cursor, queryString, count):
    st = time.time()
    if r.get(cache) == None:
        isCacheOn = 'key is not in cache'
        data = []
    else:
        data = (r.get(cache))
        # print(data)
        print("Cache")
        isCacheOn = 'In cache'
        isCacheOnboolean = True
    print(time.time()-st)
    return data, isCacheOnboolean, isCacheOn







#delete Cache
def deleteCache(delete_cache_string):
    r.delete(delete_cache_string)
    return delete_cache_string



@app.route("/client_homePage" , methods=['GET'])
def routerFunction():

    #delete cache
    if request.args.get('delete_cache') == 'delete_cache':
        delete_cache_string = request.args.get('symbol_operator')
        deleteCache(delete_cache_string)
        return "deleted cache  "+delete_cache_string


    if request.args.get('clear_cache') == 'clear_cache':
        r.flushdb()
        return "Flush Redis"


    if request.args.get('form') == 'Submit' or request.args.get('load_db_form') == 'load_db_form' or request.args.get('load_cache_form') == 'load_cache_form':

        depth1 = request.args.get('depth1')
        depth2 = request.args.get('depth2')
        longi = request.args.get('longitude')
        db = sqlConnect()
        cursor = db.cursor()
        queryString = "SELECT latitude, longitude, time, depthError FROM quakequiz3updated2 WHERE depthError BETWEEN "+depth1+" AND "+depth2+" AND longitude > "+longi
        data, isCacheOn = readfromDb (cursor, queryString)

        return render_template("table.html", data=data, isCacheOn=isCacheOn)

    if request.args.get('redis_cache_load') == 'redis_cache_load':
        isCacheOnboolean = False
        cache = "mycache"
        magnitudeVal = request.args.get('mag')
        count = int(request.args.get('count_from_user'))
        finalList = []
        # connect to db
        db = sqlConnect()
        cursor = db.cursor()
        startTime = time.time()
        for i in range(count):
            queryString = "select * from earthquakeAssignment3"
            data, isCacheOnboolean, isCacheOn = readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString)
        endTime = time.time()
        execTime = endTime - startTime
        db.close()
        if (isCacheOnboolean):
            return render_template("cachetable.html", data = data, timetaken = str(execTime) , isCacheOn = isCacheOn)
        else:
            return render_template("table.html", data=data, timetaken=str(execTime), isCacheOn=isCacheOn)

        #Within some range
        #input latitude , longitude, radius  and magintude

    if request.args.get('form_find_earthquake_in_range') == 'Submit':
        isCacheOnboolean = False
        cache = "mycache2"
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        rad = request.args.get('rad')
        count = int(request.args.get('count_from_user'))
        db = sqlConnect()
        cursor = db.cursor()
        startTime = time.time()
        # generate query string
        for i in range(count):
            queryString = "SELECT id, latitude, longitude, depth, mag, magType "
            queryString = queryString + "FROM earthquakeAssignment3 where "
            queryString = queryString + "( 6371  * acos( cos( radians(" + lat + ") )"
            queryString = queryString + "* cos( radians( latitude ) )"
            queryString = queryString + "* cos( radians(longitude) - radians(" + lon + ")) + sin(radians(" + lat + ")) "
            queryString = queryString + "* sin( radians(latitude)))) <= " + rad
            data, isCacheOnboolean, isCacheOn = readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString)
        endTime = time.time()
        execTime = endTime - startTime
        db.close()
        if (isCacheOnboolean):
            return render_template("cachetable.html", data=data, timetaken=str(execTime), isCacheOn=isCacheOn)
        else:
            return render_template("table.html", data=data, timetaken=str(execTime), isCacheOn=isCacheOn)

    #Search by location
    if request.args.get('form_find_earthquake_in_location') == 'Submit':
        isCacheOnboolean = False
        cache = "mycache3"
        location =request.args.get('location')
        count = int(request.args.get('count_from_user'))
        db = sqlConnect()
        cursor = db.cursor()
        # generate query string
        #'''SELECT * FROM BVC79655.TBEARTHQUAKE WHERE "mag" > ''' + mag1
        startTime = time.time()
        for i in range(count):
            queryString = '''SELECT * FROM earthquakeAssignment3 WHERE "locationSource" = \'''' + location +'''\''''
            data, isCacheOnboolean, isCacheOn = readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString)
        endTime = time.time()
        execTime = endTime - startTime
        db.close()
        if (isCacheOnboolean):
            return render_template("cachetable.html", data=data, timetaken=str(execTime), isCacheOn=isCacheOn)
        else:
            return render_template("table.html", data=data, timetaken=str(execTime), isCacheOn=isCacheOn)

    #search within time range
    if request.args.get('form_find_earthquake_in_timerange') == 'Submit':
        isCacheOnboolean = False
        cache = "mycache4"
        date_time1 = request.args.get('time1')
        date_time2 = request.args.get('time2')
        count = int(request.args.get('count_from_user'))
        f = "%Y-%m-%dT%H:%M"
        qot = "\'"
        print(date_time1)
        print(date_time2)
        db = sqlConnect()
        cursor = db.cursor()
        startTime = time.time()
        for i in range(count):
            queryString = '''SELECT * FROM earthquakeAssignment3 WHERE "time" BETWEEN ''' + "\'" + str(
                datetime.strptime(date_time1, f)) + "\'" ''' AND ''' + "\'" + str(datetime.strptime(date_time2, f)) + "\'"
            data, isCacheOnboolean, isCacheOn = readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString)
        endTime = time.time()
        execTime = endTime - startTime
        db.close()
        if (isCacheOnboolean):
            return render_template("cachetable.html", data=data, timetaken=str(execTime), isCacheOn=isCacheOn)
        else:
            return render_template("table.html", data=data, timetaken=str(execTime), isCacheOn=isCacheOn)


    if request.args.get('form_find_earthquake_in_magrange') == 'Submit':
        isCacheOnboolean = False
        cache = "mycache5"
        mag1 = request.args.get('mag1')
        mag2 = request.args.get('mag2')
        count = int(request.args.get('count_from_user'))
        db = sqlConnect()
        cursor = db.cursor()
        startTime =time.time()
        for i in range(count):
            queryString = '''SELECT * FROM earthquakeAssignment3 WHERE "mag" BETWEEN ''' + mag1 +''' and ''' +mag2
            data, isCacheOnboolean, isCacheOn = readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString)
        db.close()
        endTime = time.time()
        execTime = endTime - startTime
        if (isCacheOnboolean):
            return render_template("cachetable.html", data=data, timetaken=str(execTime), isCacheOn=isCacheOn)
        else:
            return render_template("table.html", data=data, timetaken=str(execTime), isCacheOn=isCacheOn)