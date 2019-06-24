from flask import Flask, render_template, request, jsonify
import pyodbc
import redis
from flask import request
import time
import os
from datetime import datetime
import json
from datetime import timedelta
import random


#port = int(os.getenv("VCAP_APP_PORT"))
port = int(os.getenv('PORT', 5000))

# redis connection code
r = redis.StrictRedis(host='redisCacheAssignemnt3.redis.cache.windows.net',
                      port=6380, password='CK6g5axYGYf4e0T08H9vBc6+obM7GtWJfZOPqrGgkBE=', ssl=True)



#print(cnxn)
app = Flask(__name__)

@app.route('/')
def hello_world():
    # a = [{'a':'abc'}, {'b':'pqr'}, {'c':'xyz'}]
    #a = [{"a":'abc'}, {"b":'pqr'}, {"c":'xyz'}]
    #return render_template('test.html', data=json.dumps(a))
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
    return data, isCacheOnboolean, isCacheOn


#read from DB
def readfromDb(cache, isCacheOnboolean, cursor, queryString):
    dataList = []
    print(queryString)
    cursor.execute(queryString)
    data = cursor.fetchall()
    # print(data)
    print("Only from DB")
    isCacheOn = 'From Db Only'
    return data, isCacheOnboolean, isCacheOn

#read from cache :- Make sure that data is in cache otherwise throw error

def readFromCache(cache, isCacheOnboolean, cursor, queryString):
    if r.get(cache) == None:
        isCacheOn = 'key is not in cache'
        data = []
    else:
        data = (r.get(cache))
        # print(data)
        print("Cache")
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


    if request.args.get('form') == 'Submit' or request.args.get('load_db_form') == 'load_db_form' or request.args.get('load_cache_form') == 'load_cache_form':
        isCacheOnboolean = False
        isLoadFromDb = False
        isLoadFromCache = False
        if request.args.get('load_db_form') == 'load_db_form':
            print('i am in isLoadFromDb')
            isLoadFromDb = True
        if request.args.get('load_cache_form') == 'load_cache_form':
            isLoadFromCache = True
        # db = sqlConnect()
        # cursor = db.cursor()
        # mag = request.args.get('eathquake_mag')
        # oper = request.args.get('symbol_operator')
        # count = int(request.args.get('count_from_user'))
        # cache = "mycache1"+oper+mag

        depth1 = float(request.args.get('depth1'))
        depth2 = float(request.args.get('depth2'))
        count = int(request.args.get('count_from_user'))
        cache = "mycache1"
        #randomdepth1 = random.uniform(depth1,depth2)
        #randomdepth2 = random.uniform(depth1, depth2)

        print('This is cache name for your input', cache)
        time_list =[]
        randomdepth_list1 = []
        randomdepth_list2 = []
        count_list = []
        # connect to db
        db = sqlConnect()
        cursor = db.cursor()
        #For (count)
        startTimecumulative = time.time()
        for i in range(count):
            startTime = time.time()
            randomdepth1 = str(random.uniform(depth1, depth2))
            randomdepth2 = str(random.uniform(depth1, depth2))
            randomdepth_list1.append(randomdepth1)
            randomdepth_list2.append(randomdepth2)
            print(i)
            queryString = "SELECT COUNT(*) FROM quakequiz3updated2 WHERE  depthError >="+randomdepth1+ " AND depthError <="+randomdepth2
            if(isLoadFromDb):
                data, isCacheOnboolean, isCacheOn = readfromDb(cache, isCacheOnboolean, cursor, queryString)
            #db function
            elif(isLoadFromCache):
                #readFromCache
                data, isCacheOnboolean, isCacheOn = readFromCache(cache, isCacheOnboolean, cursor, queryString)
            else:
                data, isCacheOnboolean, isCacheOn = readOrLoadfromCache(cache, isCacheOnboolean, cursor, queryString)
                #print('.......this is i............',i)
            endTime = time.time()
            execTime = endTime - startTime
            time_list.append(execTime)
            print('data..........',data)
            count_list.append(data)
        endTimecumulative = time.time()
        execTimecumulative = endTimecumulative - startTimecumulative
        db.close()
        if (isCacheOnboolean):
            return render_template("table.html", data=count_list, timetaken=str(execTimecumulative),
                                   isCacheOn=isCacheOn, randomdepthlist1=randomdepth_list1,
                                   randomdepthlist2=randomdepth_list2, timetaken1=time_list)
            # return render_template("cachetable.html", data=json.loads(count_list), timetaken=str(execTime), isCacheOn=isCacheOn, randomdepthlist1 = randomdepth_list1, randomdepthlist2 = randomdepth_list2, timetaken1 = time_list)
        else:
            return render_template("table.html", data=count_list, timetaken=str(execTimecumulative), isCacheOn=isCacheOn, randomdepthlist1 = randomdepth_list1, randomdepthlist2 = randomdepth_list2, timetaken1 = time_list)

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
#Assignment 4

    if request.args.get('Assignment_4') == "Assignment_4":
        #depth1 = float(request.args.get('depth1'))
        #depth2 = float(request.args.get('depth2'))
        mag = int(request.args.get('mag'))
        count = int(request.args.get('count_from_user'))
        lstDictionaryDataDisplay = []
        magStart = 0
        magEnd = magStart+mag
        while magEnd<=count:
            startTime = time.time()
            # randomdepth1 = str(random.uniform(depth1, depth2))
            # randomdepth2 = str(random.uniform(depth1, depth2))
            queryString = "SELECT COUNT(*) AS counts FROM quakequiz3updated2 WHERE mag BETWEEN " + str(magStart) + " AND " + str(magEnd)
            #queryString = "SELECT  COUNT(*) AS counts FROM quakequiz3updated2 WHERE  depthError >=" + randomdepth1 + " AND depthError <=" + randomdepth2
            db = sqlConnect()
            cursor = db.cursor()
            cursor.execute(queryString)
            quakeCount = cursor.fetchone()
            print('.........', quakeCount)
            #print('.............',depthCount)
            print(str(mag))
            #lstDictionaryDataDisplay.append({"depthError": depthCount[0]})
            lstDictionaryDataDisplay.append({"# People": quakeCount[0], "Age Range": str(magStart) + " to " + str(magEnd)})
            print(lstDictionaryDataDisplay)
            magStart = magEnd
            magEnd = magEnd + mag
        db.close()
        #return "Hello"
        return render_template('assignment4.html', tableDatal=lstDictionaryDataDisplay)
        #return render_template('barchartforloop.html', result=json.dumps(lstDictionaryDataDisplay))

    if request.args.get('Assignment_4') == "Assignment_4_bar":
        mag = request.args.get('mag')
        lstDictionaryDataDisplay = []

        # randomdepth1 = str(random.uniform(depth1, depth2))
        # randomdepth2 = str(random.uniform(depth1, depth2))
        queryString = "SELECT COUNT(*) AS counts, mag  FROM quakequiz3updated2 GROUP BY mag"
        #queryString = "SELECT  COUNT(*) AS counts FROM quakequiz3updated2 WHERE  depthError >=" + randomdepth1 + " AND depthError <=" + randomdepth2
        db = sqlConnect()
        cursor = db.cursor()
        cursor.execute(queryString)
        quakeCount = cursor.fetchall()
        print('.......',quakeCount)
        #print('.........', quakeCount)
        #print('.............',depthCount)
        #print(str(mag))
        #lstDictionaryDataDisplay.append({"depthError": depthCount[0]})
        #lstDictionaryDataDisplay.append({"# People": quakeCount[0], "Age Range": str(magStart) + " to " + str(magEnd)})
        #print(lstDictionaryDataDisplay)
        db.close()
        return render_template('barchart.html', result=quakeCount)


    if request.args.get('Assignment_4') == "Assignment_4_pie":
        mag = request.args.get('mag')
        lstDictionaryDataDisplay = []

        # randomdepth1 = str(random.uniform(depth1, depth2))
        # randomdepth2 = str(random.uniform(depth1, depth2))
        queryString = "SELECT COUNT(*) AS counts, mag FROM quakequiz3updated2 GROUP BY mag"
        #queryString = "SELECT  COUNT(*) AS counts FROM quakequiz3updated2 WHERE  depthError >=" + randomdepth1 + " AND depthError <=" + randomdepth2
        db = sqlConnect()
        cursor = db.cursor()
        cursor.execute(queryString)
        quakeCount = cursor.fetchall()
        print('.......', quakeCount)
        #print('.........', quakeCount)
        #print('.............',depthCount)
        #print(str(mag))
        #lstDictionaryDataDisplay.append({"depthError": depthCount[0]})
        #lstDictionaryDataDisplay.append({"# People": quakeCount[0], "Age Range": str(magStart) + " to " + str(magEnd)})
        #print(lstDictionaryDataDisplay)
        db.close()
        return render_template('piechart.html', result=quakeCount)


    if request.args.get('Assignment_4') == "Assignment_4_pie_depth":
        depth1 = float(request.args.get('depth1'))
        depth2 = float(request.args.get('depth2'))
        count = int(request.args.get('count'))

        final_result = []
        for i in range(count):
            randomdepth1 = str(random.uniform(depth1, depth2))
            randomdepth2 = str(random.uniform(depth1, depth2))
            queryString = "SELECT"+randomdepth1+"-"+randomdepth2+" COUNT(*) AS counts  FROM quakequiz3updated2 WHERE depth BETWEEN "+randomdepth1 +" AND "+randomdepth2
            db = sqlConnect()
            cursor = db.cursor()
            cursor.execute(queryString)
            result = cursor.fetchall()
            final_result.append(result)
        print('.......', final_result)
        result = final_result
        db.close()
        return  render_template('piechartdepth.html', result = result)


    if request.args.get('Assignment_4') == "Asssignment_4_bar_graph-1":
        queryString = "select t.range as magnitudes, count(*) as occurences from ( select case when mag >= 0 and mag < 1 then 0 when mag >= 1 and mag < 2 then 1 when mag >= 2 and mag < 3 then 2 when mag >= 3 and mag < 4 then 3 when mag >= 4 and mag < 5 then 4 when mag >= 5 and mag < 6 then 5 when mag >= 6 and mag < 7 then 6 when mag >= 7 and mag < 8 then 7 when mag >= 8 and mag < 9 then 8 when mag >= 9 and mag < 10 then 9 else -1 end as range from quakequiz3updated2) t group by t.range order by magnitudes;"
        db = sqlConnect()
        cursor = db.cursor()
        cursor.execute(queryString)
        result = cursor.fetchall()
        print('..........',result)
        db.close()
        return render_template('barchart.html', result = result)

    if request.args.get('Assignment_4') == "Asssignment_4_pie_graph-1":
        queryString = "select t.range as magnitudes, count(*) as occurences from ( select case when mag >= 0 and mag < 1 then 0 when mag >= 1 and mag < 2 then 1 when mag >= 2 and mag < 3 then 2 when mag >= 3 and mag < 4 then 3 when mag >= 4 and mag < 5 then 4 when mag >= 5 and mag < 6 then 5 when mag >= 6 and mag < 7 then 6 when mag >= 7 and mag < 8 then 7 when mag >= 8 and mag < 9 then 8 when mag >= 9 and mag < 10 then 9 else -1 end as range from quakequiz3updated2) t group by t.range order by magnitudes;"
        db = sqlConnect()
        cursor = db.cursor()
        cursor.execute(queryString)
        result = cursor.fetchall()
        print('..........',result)
        db.close()
        return render_template('piechart.html', result = result)


    if request.args.get('Quiz4_Q1') == "Quiz4_Q1":
        pop1 = request.args.get('pop1')
        pop2 = request.args.get('pop2')
        queryString = '''SELECT StateName FROM TBquizupdated4 WHERE TotalPop BETWEEN ''' + pop1 + ''' and ''' + pop2
        db = sqlConnect()
        cursor = db.cursor()
        cursor.execute(queryString)
        result = cursor.fetchall()
        print('result', result)
        db.close()
        return render_template('custom_table.html', data = result)


    if request.args.get('Quiz4_Q2') == "Quiz4_Q2":
        row=[]
        step = int(request.args.get('pop_range'))
        rows = []
        start = 0
        while (start <= 100):

            step_new = start + step
            print('step_new......', step_new)
            queryString ="select count(*) from TBquizupdated4 where TotalPop  between "+str(start)+" and "+ str(step_new);
            #queryString = "select count(*) from TBquizupdated4 where TotalPop  between" + i + " and " + step_new
            db = sqlConnect()
            cursor = db.cursor()
            cursor.execute(queryString)
            result = cursor.fetchone()
            print(result)
            start = step_new;
            # while row:
            #     rows.append([start + step, row[0]])
            #     row = cursor.fetchone()
            #     print(row)
            #i = start + step
        return render_template('quest7.html', result=result)

    if request.args.get('Quiz4_Q8') == "Quiz4_Q8":
        num = request.args.get('num')
        return render_template('quest8.html', result=num)
         





















