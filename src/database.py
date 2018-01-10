import sqlite3

class DataBase():

    def __init__(self, name="score.db", column=""):
        self.conn = sqlite3.connect( name )
        self.cursor = self.conn.cursor()
        self.scores = None
    
    def SelectData(self):
        order = "CREATE TABLE IF NOT EXISTS Score( name TEXT, time FLOAT)"
        self.cursor.execute( order )
        self.scores = self.cursor.execute("SELECT * FROM player order by time")
        self.conn.commit()

        return

    def PrintData(self):
        for item in self.scores:
            print( item )
        
        return

    def InsertData(self, name, time):
        sql = "insert into player (name, time) values ('%s', '%s')" % (name, time)
        self.cursor.execute( sql )
        self.conn.commit()
        return

    def Close(self):
        self.conn.close()
        return
