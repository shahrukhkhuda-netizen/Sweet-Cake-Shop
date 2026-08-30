import sqlite3
from datetime import datetime, timedelta
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_NAME = str(BASE_DIR / "cake_shop.db")


def get_connection():
    con = sqlite3.connect(DATABASE_NAME)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def create_tables():
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cake_name TEXT NOT NULL,
            flavor TEXT,
            price REAL NOT NULL CHECK(price >= 0),
            quantity INTEGER DEFAULT 0 CHECK(quantity >= 0)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            cake_id INTEGER,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            total_price REAL NOT NULL CHECK(total_price >= 0),
            order_date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (cake_id) REFERENCES cakes(id)
        )
    """)

    con.commit()
    con.close()


def add_initial_cakes():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM cakes")
    count = cur.fetchone()[0]

    if count == 0:
        cakes = [
            ("Chocolate Cake", "Chocolate", 500, 25),
            ("Vanilla Cake", "Vanilla", 450, 25),
            ("Red Velvet Cake", "Red Velvet", 650, 20),
            ("Black Forest Cake", "Chocolate", 550, 25),
            ("Strawberry Cake", "Strawberry", 600, 25),
            ("Butterscotch Cake", "Butterscotch", 550, 20),
            ("Pineapple Cake", "Pineapple", 480, 25),
            ("Fruit Cake", "Mixed Fruit", 700, 20),
            ("Mango Cake", "Mango", 600, 20),
            ("Coffee Cake", "Coffee", 550, 20),
        ]
        cur.executemany(
            "INSERT INTO cakes (cake_name, flavor, price, quantity) VALUES (?, ?, ?, ?)",
            cakes
        )

    con.commit()
    con.close()


def get_cakes():
    con = get_connection()
    rows = con.execute("""
        SELECT id, cake_name, flavor, price, quantity
        FROM cakes
        ORDER BY id
    """).fetchall()
    con.close()
    return rows


def add_cake(cake_name, flavor, price, quantity):
    con = get_connection()
    con.execute(
        "INSERT INTO cakes (cake_name, flavor, price, quantity) VALUES (?, ?, ?, ?)",
        (cake_name.strip(), flavor.strip(), float(price), int(quantity))
    )
    con.commit()
    con.close()


def update_cake(cake_id, cake_name, flavor, price, quantity):
    con = get_connection()
    con.execute("""
        UPDATE cakes
        SET cake_name = ?, flavor = ?, price = ?, quantity = ?
        WHERE id = ?
    """, (cake_name.strip(), flavor.strip(), float(price), int(quantity), int(cake_id)))
    con.commit()
    con.close()


def delete_cake(cake_id):
    con = get_connection()
    # Do not allow deletion if the cake is already used in an order.
    used = con.execute(
        "SELECT COUNT(*) FROM orders WHERE cake_id = ?", (int(cake_id),)
    ).fetchone()[0]

    if used > 0:
        con.close()
        return False

    con.execute("DELETE FROM cakes WHERE id = ?", (int(cake_id),))
    con.commit()
    con.close()
    return True


def add_customer(name, phone):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO customers (name, phone) VALUES (?, ?)",
        (name.strip(), phone.strip())
    )
    customer_id = cur.lastrowid
    con.commit()
    con.close()
    return customer_id


def add_order(customer_id, cake_id, quantity, total_price):
    con = get_connection()
    cur = con.cursor()

    stock = cur.execute(
        "SELECT quantity FROM cakes WHERE id = ?", (int(cake_id),)
    ).fetchone()

    if stock is None:
        con.close()
        raise ValueError("Cake not found.")

    if int(stock[0]) < int(quantity):
        con.close()
        raise ValueError(f"Only {stock[0]} cake(s) are available.")

    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO orders
        (customer_id, cake_id, quantity, total_price, order_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        int(customer_id),
        int(cake_id),
        int(quantity),
        float(total_price),
        order_date
    ))

    cur.execute(
        "UPDATE cakes SET quantity = quantity - ? WHERE id = ?",
        (int(quantity), int(cake_id))
    )

    con.commit()
    con.close()


def get_orders():
    con = get_connection()
    rows = con.execute("""
        SELECT
            orders.id,
            customers.name,
            customers.phone,
            cakes.cake_name,
            cakes.flavor,
            orders.quantity,
            orders.total_price,
            orders.order_date
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        JOIN cakes ON orders.cake_id = cakes.id
        ORDER BY orders.id DESC
    """).fetchall()
    con.close()
    return rows


def get_dashboard_data():
    con = get_connection()

    total_cakes = con.execute(
        "SELECT COUNT(*) FROM cakes"
    ).fetchone()[0]

    total_orders = con.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    total_customers = con.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    total_sales = con.execute(
        "SELECT COALESCE(SUM(total_price), 0) FROM orders"
    ).fetchone()[0]

    total_cakes_sold = con.execute(
        "SELECT COALESCE(SUM(quantity), 0) FROM orders"
    ).fetchone()[0]

    low_stock = con.execute(
        "SELECT COUNT(*) FROM cakes WHERE quantity <= 5"
    ).fetchone()[0]

    con.close()

    return (
        total_cakes,
        total_orders,
        total_customers,
        float(total_sales),
        int(total_cakes_sold),
        int(low_stock),
    )


def get_sales_by_cake():
    con = get_connection()
    rows = con.execute("""
        SELECT
            cakes.cake_name,
            COALESCE(SUM(orders.quantity), 0) AS units_sold,
            COALESCE(SUM(orders.total_price), 0) AS sales
        FROM cakes
        LEFT JOIN orders ON cakes.id = orders.cake_id
        GROUP BY cakes.id, cakes.cake_name
        ORDER BY sales DESC
    """).fetchall()
    con.close()
    return rows


def get_sales_by_day():
    con = get_connection()
    rows = con.execute("""
        SELECT
            substr(order_date, 1, 10) AS sale_date,
            SUM(total_price) AS sales
        FROM orders
        GROUP BY substr(order_date, 1, 10)
        ORDER BY sale_date
    """).fetchall()
    con.close()
    return rows


def get_recent_orders(limit=10):
    con = get_connection()
    rows = con.execute("""
        SELECT
            orders.id,
            customers.name,
            cakes.cake_name,
            orders.quantity,
            orders.total_price,
            orders.order_date
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        JOIN cakes ON orders.cake_id = cakes.id
        ORDER BY orders.id DESC
        LIMIT ?
    """, (int(limit),)).fetchall()
    con.close()
    return rows


def generate_practice_orders(number_of_orders=50):
    """Generate demo/practice orders. This is for portfolio/demo data only."""
    number_of_orders = max(0, int(number_of_orders))

    con = get_connection()
    cur = con.cursor()

    cakes = cur.execute(
        "SELECT id, cake_name, price FROM cakes"
    ).fetchall()

    if not cakes:
        con.close()
        return 0

    names = [
        "Rahul Sharma", "Aman Khan", "Priya Singh", "Neha Verma",
        "Arjun Patel", "Sara Khan", "Rohit Gupta", "Pooja Sharma",
        "Vikas Jain", "Anjali Mehta", "Karan Singh", "Simran Khan",
        "Aditya Verma", "Nisha Patel", "Mohit Sharma", "Riya Jain",
        "Sahil Khan", "Kavita Sharma", "Rakesh Patel", "Meena Verma"
    ]

    now = datetime.now()
    created = 0

    for _ in range(number_of_orders):
        name = random.choice(names)
        phone = "98" + str(random.randint(10000000, 99999999))

        cur.execute(
            "INSERT INTO customers (name, phone) VALUES (?, ?)",
            (name, phone)
        )
        customer_id = cur.lastrowid

        cake_id, cake_name, price = random.choice(cakes)
        quantity = random.randint(1, 3)
        total_price = float(price) * quantity

        order_date = (
            now
            - timedelta(
                days=random.randint(0, 180),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
        ).strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            INSERT INTO orders
            (customer_id, cake_id, quantity, total_price, order_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            customer_id,
            cake_id,
            quantity,
            total_price,
            order_date
        ))
        created += 1

    con.commit()
    con.close()
    return created


create_tables()
add_initial_cakes()
