#create database for the first time only 
import mysql.connector 
# init db
mydb = mysql.connector.connect(
    auth_plugin='mysql_native_password',
    host='localhost',
    user = 'root',
    passwd = 'password123456789',
)
# connect to db
my_cursor = mydb.cursor()

# this code run for once 
# my_cursor.execute('CREATE DATABASE blogger')

my_cursor.execute('SHOW DATABASES')


for db in my_cursor:
    print(db)


