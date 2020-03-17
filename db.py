import pymysql.cursors

print('init pymysql')
def getMysqlConnect():
   return pymysql.Connect(
      # host="db4free.net",
      # port=3306,
      # user="douyu_user",
      # passwd="11111111",
      # db="douyu_download",
      # charset='utf8'
       host="localhost",
       port=3306,
       user="root",
       passwd="mysqlmima123",
       db="douyu_download",
       charset='utf8'
   )

