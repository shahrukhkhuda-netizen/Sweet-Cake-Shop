import sqlite3
from datetime import datetime, timedelta
import random

DATABASE_NAME = "cake_shop.db"

def get_connection():
    return sqlite3.connect(DATABASE_NAME)

def create_tables():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS cakes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cake_name TEXT NOT NULL,
        flavor TEXT,
        price REAL NOT NULL,
        quantity INTEGER DEFAULT 0
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        cake_id INTEGER,
        quantity INTEGER,
        total_price REAL,
        order_date TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (cake_id) REFERENCES cakes(id)
    )""")
    con.commit()
    con.close()

def add_initial_cakes():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM cakes")
    if cur.fetchone()[0] == 0:
        cakes = [
            ("Chocolate Cake","Chocolate",500,25),
            ("Vanilla Cake","Vanilla",450,25),
            ("Red Velvet Cake","Red Velvet",650,20),
            ("Black Forest Cake","Chocolate",550,25),
            ("Strawberry Cake","Strawberry",600,25),
            ("Butterscotch Cake","Butterscotch",550,20),
            ("Pineapple Cake","Pineapple",480,25),
            ("Fruit Cake","Mixed Fruit",700,20),
            ("Mango Cake","Mango",600,20),
            ("Coffee Cake","Coffee",550,20)
        ]
        cur.executemany(
            "INSERT INTO cakes (cake_name,flavor,price,quantity) VALUES (?,?,?,?)",
            cakes
        )
    con.commit()
    con.close()

def get_cakes():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT id,cake_name,flavor,price,quantity FROM cakes ORDER BY id")
    rows = cur.fetchall()
    con.close()
    return rows

def add_customer(name, phone):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO customers (name,phone) VALUES (?,?)",(name,phone))
    customer_id = cur.lastrowid
    con.commit()
    con.close()
    return customer_id

def add_order(customer_id,cake_id,quantity,total_price):
    con = get_connection()
    cur = con.cursor()
    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""INSERT INTO orders
        (customer_id,cake_id,quantity,total_price,order_date)
        VALUES (?,?,?,?,?)""",
        (customer_id,cake_id,quantity,total_price,order_date))
    cur.execute("UPDATE cakes SET quantity=MAX(0,quantity-?) WHERE id=?",
                (quantity,cake_id))
    con.commit()
    con.close()

def get_orders():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""SELECT orders.id,customers.name,cakes.cake_name,
        orders.quantity,orders.total_price,orders.order_date
        FROM orders
        JOIN customers ON orders.customer_id=customers.id
        JOIN cakes ON orders.cake_id=cakes.id
        ORDER BY orders.id DESC""")
    rows = cur.fetchall()
    con.close()
    return rows

def get_dashboard_data():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM cakes")
    total_cakes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM orders")
    total_orders = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM customers")
    total_customers = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(total_price),0) FROM orders")
    total_sales = cur.fetchone()[0]
    con.close()
    return total_cakes,total_orders,total_customers,total_sales

def add_cake(cake_name,flavor,price,quantity):
    con = get_connection()
    con.execute("INSERT INTO cakes (cake_name,flavor,price,quantity) VALUES (?,?,?,?)",
                (cake_name,flavor,price,quantity))
    con.commit()
    con.close()

def update_cake(cake_id,cake_name,flavor,price,quantity):
    con = get_connection()
    con.execute("""UPDATE cakes SET cake_name=?,flavor=?,price=?,quantity=?
                   WHERE id=?""",
                (cake_name,flavor,price,quantity,cake_id))
    con.commit()
    con.close()

def delete_cake(cake_id):
    con = get_connection()
    con.execute("DELETE FROM cakes WHERE id=?",(cake_id,))
    con.commit()
    con.close()

def generate_practice_orders(number_of_orders=50):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT id,cake_name,price FROM cakes")
    cakes = cur.fetchall()
    if not cakes:
        con.close()
        return 0

    names = ["Rahul Sharma","Aman Khan","Priya Singh","Neha Verma",
             "Arjun Patel","Sara Khan","Rohit Gupta","Pooja Sharma",
             "Vikas Jain","Anjali Mehta","Karan Singh","Simran Khan",
             "Aditya Verma","Nisha Patel","Mohit Sharma"]

    now = datetime.now()
    created = 0

    for _ in range(max(0,int(number_of_orders))):
        name = random.choice(names)
        phone = "98" + str(random.randint(10000000,99999999))
        cur.execute("INSERT INTO customers (name,phone) VALUES (?,?)",
                    (name,phone))
        customer_id = cur.lastrowid

        cake_id,cake_name,price = random.choice(cakes)
        quantity = random.randint(1,3)
        total_price = float(price) * quantity

        order_date = (now - timedelta(
            days=random.randint(0,180),
            hours=random.randint(0,23),
            minutes=random.randint(0,59)
        )).strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""INSERT INTO orders
            (customer_id,cake_id,quantity,total_price,order_date)
            VALUES (?,?,?,?,?)""",
            (customer_id,cake_id,quantity,total_price,order_date))
        created += 1

    con.commit()
    con.close()
    return created

create_tables()
add_initial_cakes()