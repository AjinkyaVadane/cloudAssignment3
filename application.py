from flask import Flask, render_template, request, jsonify
import pyodbc
import redis
from flask import request
import time
import os
from datetime import datetime
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
def readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString):
    if r.get(cache) == None:
        #startTime = time.time()
        print(queryString)
        cursor.execute(queryString)
        data = cursor.fetchall()
        #endTime = time.time()
        #execTime = endTime - startTime
        data_string = data
        #r.rpush(cache, data)
        r.set(cache, str(data_string))  # redis requires data to be in Convert to a byte, string or number first.
        finalList = data
        print("No Cache")
        #print("No cache Time : ", execTime)
        isCacheOn = 'No cache'

    else:
        #startTime = time.time()
        data1 = r.get(cache)
        #endTime = time.time()
        #execTime = endTime - startTime
        #print("Cache Time is", execTime)
        data1 = str(data1)
        data = data1
        print("Cache")
        #print("Cache Time is", execTime)
        isCacheOn = 'In cache'
        isCacheOnboolean = True
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


    if request.args.get('form') == 'Submit':
        isCacheOnboolean = False
        # db = sqlConnect()
        # cursor = db.cursor()
        mag = request.args.get('eathquake_mag')
        oper = request.args.get('symbol_operator')
        count = int(request.args.get('count_from_user'))
        cache = "mycache1"+oper+mag
        print('This is cache name for your input', cache)
        print(oper)
        print(mag)
        # connect to db
        db = sqlConnect()
        cursor = db.cursor()
        #For (count)
        startTime = time.time()
        for i in range(count):
            queryString = '''SELECT * FROM earthquakeAssignment3 WHERE "mag"'''+oper+mag
            data, isCacheOnboolean, isCacheOn = readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString)
            print('.......this is i............',i)
        endTime = time.time()
        execTime = endTime - startTime
        db.close()
        if (isCacheOnboolean):
            return render_template("cachetable.html", data=data, timetaken=str(execTime), isCacheOn=isCacheOn)
        else:
            return render_template("table.html", data=data, timetaken=str(execTime), isCacheOn=isCacheOn)

    if request.args.get('redis_cache_load') == 'redis_cache_load':
        isCacheOnboolean = False
        cache = "mycache"
        magnitudeVal = request.args.get('mag')
        finalList = []
        # connect to db
        db = sqlConnect()
        cursor = db.cursor()
        queryString = "select * from earthquakeAssignment3"
        data, isCacheOnboolean, execTime, isCacheOn = readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString)
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
        db = sqlConnect()
        cursor = db.cursor()

        # generate query string
        queryString = "SELECT id, latitude, longitude, depth, mag, magType "
        queryString = queryString + "FROM earthquakeAssignment3 where "
        queryString = queryString + "( 6371  * acos( cos( radians(" + lat + ") )"
        queryString = queryString + "* cos( radians( latitude ) )"
        queryString = queryString + "* cos( radians(longitude) - radians(" + lon + ")) + sin(radians(" + lat + ")) "
        queryString = queryString + "* sin( radians(latitude)))) <= " + rad
        # return queryString
        #queryString = "select * from earthquakeAssignment3 where mag > 7"
        #queryString = 'SELECT * FROM (select *,(((acos(sin((' + lat + '*3.14/180)) * sin(("latitude"*3.14/180))+cos((' + lat + '*3.14/180))*cos(("latitude"*3.14/180))*cos(((' + lon + ' - "longitude")*3.14/180))))*180/3.14)*60*1.1515*1.609344) as distance from earthquakeAssignment3 ) where distance <= ' + rad + ''
        #queryString = '''SELECT * FROM (SELECT *,(((ACOS(SIN((''' + lat + ''' * 0.0174533)) *  SIN(("latitude" * 0.0174533)) + COS((''' + lat + ''' * 0.0174533)) * COS(("latitude" * 0.0174533)) * COS(((''' + lon + ''' - "longitude") * 0.0174533)))) * 180/3.14) * 60 * 1.1515 * 1.609344) as DISTANCE FROM earthquakeAssignment3 ) WHERE DISTANCE <= ''' + rad + ''' AND "mag" > ''' + mag+''';'''
        print(queryString)
        data, isCacheOnboolean, execTime, isCacheOn = readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString)
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
        db = sqlConnect()
        cursor = db.cursor()
        # generate query string
        #'''SELECT * FROM BVC79655.TBEARTHQUAKE WHERE "mag" > ''' + mag1
        queryString = '''SELECT * FROM earthquakeAssignment3 WHERE "locationSource" = \'''' + location +'''\''''
        print(queryString)
        data, isCacheOnboolean, execTime, isCacheOn = readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString)
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
        f = "%Y-%m-%dT%H:%M"
        qot = "\'"
        print(date_time1)
        print(date_time2)
        db = sqlConnect()
        cursor = db.cursor()
        queryString = '''SELECT * FROM earthquakeAssignment3 WHERE "time" BETWEEN ''' + "\'" + str(
            datetime.strptime(date_time1, f)) + "\'" ''' AND ''' + "\'" + str(datetime.strptime(date_time2, f)) + "\'"
        data, isCacheOnboolean, execTime, isCacheOn = readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString)
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