import pyodbc
import csv
import pandas as pd
from sqlalchemy import create_engine,types
import urllib
import time

conn = pyodbc.connect("Driver={ODBC Driver 13 for SQL Server};Server=tcp:mysqlserver09.database.windows.net,1433;Database=AKVDB;Uid=azureuser@mysqlserver09;Pwd=12345Ajuvad;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")

cur = conn.cursor()

with open('all_month.csv', newline='') as csv_file:
    reader = csv.reader(csv_file,delimiter = ' ', quotechar='"')
    next(reader, None)
    for row in reader:
        my_list = row[0].split(",")
        print(my_list)
        print(len(my_list))
        s = "','".join(my_list)
        s = "'"+s+"'"
        #print(s)
        #print(s[len(s)])
        query = "insert into earthquakeAssignment3 values("+s+")"
        print(query)
        break


params = urllib.parse.quote_plus("Driver={ODBC Driver 13 for SQL Server};Server=tcp:mysqlserver09.database.windows.net,1433;Database=AKVDB;Uid=azureuser@mysqlserver09;Pwd=12345Ajuvad;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

#print(engine.execute("SELECT * FROM earthquake").fetchall())
df = pd.read_csv("all_month.csv",sep=',',quotechar='"',encoding='utf8')
df.to_sql('earthquakeAssignment3',con=engine,index=False,if_exists='append')
print('Success')
#print(df)
#print(data.head())
#print(data)
#cur.execute(query)

#cur.execute("commit")

cur.close()