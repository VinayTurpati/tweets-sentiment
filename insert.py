import mysql



from datetime import datetime
keyword ='vinay'

def insert(keyword):
	sql_uri = 'mysql://sql12324328:3cZf18ghZV@sql12.freemysqlhosting.net:3306/sql12324328'
	mydb = mysql.connector.connect(
		host="sql12.freemysqlhosting.net",
		user="sql12324328",
		passwd="3cZf18ghZV",
		database="sql12324328",
		port='3306')

	sub_date = datetime.now()
	val = [( keyword, sub_date)]
	mycursor = mydb.cursor()
	sql = "INSERT INTO tweets (keyword, sub_date) VALUES (%s, %s)"
	mycursor.executemany(sql, val)
	mydb.commit()
	mydb.close()
	
	print(mycursor.rowcount, "row was inserted.")

#insert(keyword)