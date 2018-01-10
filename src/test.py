import sqlite3
import database as db

DB = db.DataBase()
DB.SelectData()
i = 0
scores = DB.GetData()
for item in scores:
  print( item )
  i = i+1
