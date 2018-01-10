import sqlite3
import database as db
import tkinter as tk
from tkinter import simpledialog

DB = db.DataBase()
DB.SelectData()
i = 0
scores = DB.GetData()
for item in scores:
  print( item )
  i = i+1


application_window = tk.Tk()

answer = simpledialog.askstring("Input", "What is your first name?",
                                parent=application_window)