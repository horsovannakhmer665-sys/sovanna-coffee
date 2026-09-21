import sqlite3
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "shop.db")


def get_connection():
    return sqlite3.connect(DB_FILE)


def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    # ==============================
    # PRODUCTS
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT DEFAULT '',
            buy_price INTEGER DEFAULT 0,
            sell_price INTEGER DEFAULT 0,
            stock INTEGER DEFAULT 0,
            image TEXT DEFAULT '',
            barcode TEXT DEFAULT '',
            min_stock INTEGER DEFAULT 5
        )
    """)

    # ==============================
    # SALES
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT,
            product_id INTEGER,
            product_name TEXT,
            quantity INTEGER,
            sell_price INTEGER,
            total INTEGER,
            customer_name TEXT DEFAULT '',
            sale_date TEXT
        )
    """)

    # ==============================
    # STOCK HISTORY
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            product_name TEXT,
            stock_type TEXT,
            quantity INTEGER,
            note TEXT DEFAULT '',
            stock_date TEXT
        )
    """)

    # ==============================
    # CUSTOMERS
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT DEFAULT '',
            address TEXT DEFAULT '',
            note TEXT DEFAULT ''
        )
    """)

    # ==============================
    # SETTINGS
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_name TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            address TEXT DEFAULT ''
        )
    """)

    # ==============================
    # ADD MISSING COLUMNS
    # ==============================

    def add_column_if_missing(
        table_name,
        column_name,
        column_definition
    ):

        cursor.execute(
            f"PRAGMA table_info({table_name})"
        )

        columns = [
            row[1]
            for row in cursor.fetchall()
        ]

        if column_name not in columns:

            cursor.execute(
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN {column_name}
                {column_definition}
                """
            )

    add_column_if_missing(
        "products",
        "barcode",
        "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        "products",
        "min_stock",
        "INTEGER DEFAULT 5"
    )

    add_column_if_missing(
        "sales",
        "invoice_no",
        "TEXT"
    )

    add_column_if_missing(
        "sales",
        "customer_name",
        "TEXT DEFAULT ''"
    )

    # ==============================
    # DEFAULT SHOP SETTINGS
    # ==============================

    cursor.execute(
        "SELECT COUNT(*) FROM settings"
    )

    settings_count = cursor.fetchone()[0]

    if settings_count == 0:

        cursor.execute("""
            INSERT INTO settings
            (shop_name, phone, address)
            VALUES (?, ?, ?)
        """, (
            "ហាងសុវណ្ណាលក់គ្រឿងកាហ្វេ",
            "",
            ""
        ))

    # ==============================
    # DEFAULT COFFEE PRODUCT
    # ==============================

    cursor.execute(
        "SELECT id FROM products WHERE name = ?",
        ("កាហ្វេ",)
    )

    existing = cursor.fetchone()

    if existing is None:

        cursor.execute("""
            INSERT INTO products
            (
                name,
                category,
                buy_price,
                sell_price,
                stock,
                image,
                barcode,
                min_stock
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "កាហ្វេ",
            "គ្រឿងម្សៅ",
            20000,
            25000,
            50,
            "coffee.jpg",
            "",
            5
        ))

    conn.commit()
    conn.close()


if __name__ == "__main__":

    create_database()

    print("Database created successfully.")
    print(
        "Database:",
        DB_FILE
    )