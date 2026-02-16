import sqlite3
import os
from datetime import datetime
import requests
import logging
import argparse
import schedule
import time
logging.basicConfig(filename='data.log' , level=logging.INFO, 
                    format='%(asctime)s| %(levelname)s | %(message)s')
def auto_run():
    logging.info('Automatic system is started')
    fetch_and_store_products()
    save_report_to_file()
    logging.info('Automatic mode is completed')
def main():
    parser = argparse.ArgumentParser(description='Ecomm analytical pulse system')
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--report' , action='store_true')
    parser.add_argument('--expensive' , type=float)
    parser.add_argument('--stats' , action='store_true')
    parser.add_argument('--schedule',action='store_true', help='Turns automatic mode')
    args  = parser.parse_args()
    if args.fetch:
        fetch_and_store_products()
    elif args.schedule:
        auto_run()
        schedule.every().day.at('09:00').do(auto_run)
        while True:
            schedule.run_pending()
            time.sleep(1)
    elif args.report:
        save_report_to_file()
    elif args.expensive:
        get_expensive_products(args.expensive)
    elif args.stats:
        get_category_stats()
folder = 'data'
if not os.path.exists(folder):
    os.mkdir(folder)
file_pathway = os.path.join(folder, 'inventory.db')
base = sqlite3.connect(file_pathway)
conn = base.cursor()
conn.execute('CREATE TABLE IF NOT EXISTS products '
'(id INTEGER PRIMARY KEY, ' \
'name TEXT UNIQUE, category TEXT,' \
'price REAL, timestamp TEXT)')
base.commit()
base.close()

def add_product(name, category, price):
    base = sqlite3.connect(file_pathway)
    conn = base.cursor()
    time = datetime.now().strftime('%H:%M:%S')
    sql_command='INSERT OR IGNORE INTO products (name,category,price, timestamp) VALUES (?,?,?,?) '
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
    base.close()
def fetch_and_store_products():
    url= 'https://fakestoreapi.com/products'
    try: 
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        for y in data:
            title = y['title']
            category = y['category']
            price = y['price']
            add_product(title, category, price)
    except requests.exceptions.RequestException as e:
        logging.error(f'Connection lost with API:{e}')
def get_expensive_products(limit_price):
    base= sqlite3.connect(file_pathway)
    conn = base.cursor()
    conn.execute('SELECT*FROM products WHERE price>? ORDER BY price DESC', (limit_price,))
    result = conn.fetchall()
    for x in result:
        print(f'Expensive product:{x[1]} - Price: {x[3]}')
def get_category_stats():
    base = sqlite3.connect(file_pathway)
    conn = base.cursor()
    query = "SELECT category, COUNT(*) FROM products GROUP BY category"
    conn.execute(query)
    stats = conn.fetchall()
    print("\n--- Kateqoriya Statistikası ---")
    for s in stats:
        print(f"Kateqoriya: {s[0]} | Məhsul sayı: {s[1]}")
    base.close()
def generate_weekly_summary():
    base = sqlite3.connect(file_pathway)
    conn = base.cursor()
    conn.execute('SELECT COUNT(*), AVG(price), MAX(price) FROM products')
    result = conn.fetchone()
    total = result[0]
    Average = result[1]
    Maximum = result[2]
    base.close()
    print(f'Report: Totally, there are {total} products. Average : {Average:.2f}, The most expensive:{Maximum}')
def save_report_to_file():
    base = sqlite3.connect(file_pathway)
    conn = base.cursor()
    conn.execute('SELECT COUNT(*), AVG(price), MAX(price) FROM products')
    result = conn.fetchone()
    total = result[0]
    average = round(result[1], 2)
    maximum = result[2]
    with open('weekly.report.txt', 'w' , encoding='utf-8') as file:
        file.write('==Weekly E-commerce report === \n')
        file.write(f"date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        file.write("-" * 35 + "\n")
        file.write(f"Total product number: {total}\n")
        file.write(f"Average: {average}\n")
        file.write(f"The most expensive: {maximum}\n")
        file.write("-" * 35 + "\n")
    base.close()
    
if __name__ == "__main__":
    main()
