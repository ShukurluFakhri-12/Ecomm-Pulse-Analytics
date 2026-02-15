import sqlite3
import os
from datetime import datetime
folder = 'data'
if not os.path.exists(folder):
    os.mkdir(folder)
file_pathway = os.path.join(folder, 'inventory.db')
base = sqlite3.connect(file_pathway)
conn = base.cursor()
conn.execute('CREATE TABLE IF NOT EXISTS products '
'(id INTEGER PRIMARY KEY, ' \
'name TEXT, category TEXT,' \
'price REAL, timestamp TEXT)')
base.commit()
base.close()

def add_product(name, category, price):
    base = sqlite3.connect(file_pathway)
    conn = base.cursor()
    time = datetime.now().strftime('%H:%M:%S')
    sql_command='INSERT INTO products (name,category,price, timestamp) VALUES (?,?,?,?) '
    information = (name,category,price,time) 
    conn.execute(sql_command,information)
    base.commit()
    base.close()
    print(f'{name} is added to base')
def get_all_products():
    base = sqlite3.connect(file_pathway)
    conn = base.cursor()
    conn.execute('SELECT*FROM products')
    all = conn.fetchall()
    for x in all:
        print(x)
