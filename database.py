import os
import psycopg2
from psycopg2 import sql

#database credentials to use before deployment and heroku changes credentials frequently so must update before connect


#when deployed use, DATABASE_URL
class Database(object):
	def __init__(self):
		
		self.host = os.getenv("HOSTNAME")
		self.user = os.getenv("USERNAME")
		self.password = os.getenv("PASSWORD")
		self.database = os.getenv("DATABASE")
		
		self.con = None
		
	def connect(self):
		'''connect to database'''
		try:
			self.con = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
			self.cur = self.con.cursor()
		except Exception as error:
			print("connection error: ", error)
	def disconnect(self):
		'''disconnect from database'''
		try:
			if self.con:
				self.cur.close()
				self.con.close()
		except Exception as error:
			print("disconnection error: ", error)
	
	def __createTable(self, sqlStatement):
		#sqlStatement format: "create table 'table_name' (colume_name type, );"
		'''sqlStatement = sql.SQL("create table {table} (").format(table=sql.Identifier(tableName))
		vars = []
		for idx in range(len(kargs.items())):
			sqlStatement += "%s %s"
			if col != len(kargs.items())-1:
				sqlStatement += ","
			vars.append(kargs.items()[idx][0])
			vars.append(kargs.items()[idx][1])
		sqlStatement += ");"
		'''
		
		try:
			self.connect()
			self.cur.execute(sqlStatement)
			self.con.commit()
		except Exception as error:
			print("create table failed due to: ", error)
		finally:
			self.disconnect()
			
			
class CovidDatabase(Database):
	'''child of database with specific add func for the table'''
	def __init__(self):
		super(CovidDatabase, self).__init__()
		
		self.tableName = "covidtable"
	
	def getAllFromTable(self):
		'''get all data from table'''
		res = None
		try:
			self.connect()
			self.cur.execute(sql.SQL("SELECT * FROM {table}").format(table=sql.Identifier(self.tableName)))
			res = self.cur.fetchall()
			
		except:
			print("error getting data from table")
		finally:
			self.disconnect()
			if res:
				return res
	def addToTable(self, date, cases, recovered, deaths):
		'''add data to covidTable'''
		try:
			self.connect()
			self.cur.execute(sql.SQL("INSERT INTO {table} (date, cases, recovered, deaths) VALUES (%s, %s, %s, %s);").format(table=sql.Identifier(self.tableName)),(date, cases, recovered, deaths))
			self.con.commit()
		except Exception as error:
			print("error adding to table: ", error)
		finally:
			self.disconnect()
	def getRowByDate(self, date):
		'''get a row from database based on date'''
		try:
			self.connect()
			self.cur.execute(sql.SQL("SELECT * FROM {table} WHERE date = %s;").format(table=sql.Identifier(self.tableName)),(date,))
			res = self.cur.fetchone()
			data = {"cases": res[1], "recovered": res[2], "deaths": res[3]}
			
			return data #cases, recovered, deaths
		except Exception as error:
			print("error fetching row: ", error)
		finally:
			self.disconnect()
			
