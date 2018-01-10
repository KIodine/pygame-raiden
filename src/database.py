import sqlite3

class DataBase():

    def __init__(self, name="score.db", column=""):
        self.name = name
        self.conn = sqlite3.connect( name )
        self.cursor = self.conn.cursor()
        self.scores = None
    
    def SelectData(self):
        
        order = "CREATE TABLE IF NOT EXISTS Rank( name TEXT, time FLOAT )"
        self.cursor.execute( order )
        self.conn.commit()
        self.scores = self.cursor.execute("SELECT * FROM Rank order by time")
        

        return

    def GetData(self):
        self.SelectData()
        #for item in self.scores:
            #print("?")
            #print( item )
        
        return self.scores

    def Reset(self):
        self.conn = sqlite3.connect( self.name )
        self.cursor = self.conn.cursor()
        self.scores = None
        return

    def InsertData(self, name, time):
        order = "CREATE TABLE IF NOT EXISTS Rank( name TEXT, time FLOAT )"
        self.cursor.execute( order )
        sql = "insert into Rank (name, time) values ('%s', '%s')" % (name, time)
        self.cursor.execute( sql )
        self.conn.commit()
        self.Close()
        self.Reset()
        return

    def Close(self):
        self.conn.close()
        return
