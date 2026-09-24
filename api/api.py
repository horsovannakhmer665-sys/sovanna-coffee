from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import psycopg

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL")


def init_database():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT,
                    buy_price DOUBLE PRECISION DEFAULT 0,
                    sell_price DOUBLE PRECISION DEFAULT 0,
                    stock INTEGER DEFAULT 0,
                    image TEXT
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    address TEXT NOT NULL,
                    total DOUBLE PRECISION DEFAULT 0,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'ថ្មី'
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price DOUBLE PRECISION NOT NULL,
                    subtotal DOUBLE PRECISION NOT NULL
                )
            """)

        conn.commit()


init_database()


# GET - បង្ហាញទំនិញទាំងអស់
@app.route("/api/products", methods=["GET"])
def products():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, category, sell_price, stock, image
                FROM products
                ORDER BY id DESC
            """)

            rows = cur.fetchall()

    result = []

    for row in rows:
        result.append({
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "sell_price": row[3],
            "stock": row[4],
            "image": row[5]
        })

    return jsonify(result)


# POST - បញ្ចូលទំនិញថ្មី
@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.get_json()

    name = data.get("name")
    category = data.get("category")
    buy_price = data.get("buy_price", 0)
    sell_price = data.get("sell_price", 0)
    stock = data.get("stock", 0)
    image = data.get("image")

    if not name:
        return jsonify({
            "error": "ត្រូវបញ្ចូលឈ្មោះទំនិញ"
        }), 400

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO products
                (name, category, buy_price, sell_price, stock, image)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                name,
                category,
                buy_price,
                sell_price,
                stock,
                image
            ))

            product_id = cur.fetchone()[0]

        conn.commit()

    return jsonify({
        "message": "បានបញ្ចូលទំនិញ",
        "id": product_id
    }), 201
@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json()

    name = data.get("name")
    category = data.get("category")
    buy_price = data.get("buy_price", 0)
    sell_price = data.get("sell_price", 0)
    stock = data.get("stock", 0)
    image = data.get("image")

    if not name:
        return jsonify({
            "error": "ត្រូវបញ្ចូលឈ្មោះទំនិញ"
        }), 400

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:

            cur.execute("""
                UPDATE products
                SET
                    name = %s,
                    category = %s,
                    buy_price = %s,
                    sell_price = %s,
                    stock = %s,
                    image = %s
                WHERE id = %s
            """, (
                name,
                category,
                buy_price,
                sell_price,
                stock,
                image,
                product_id
            ))

            if cur.rowcount == 0:
                return jsonify({
                    "error": "រកមិនឃើញទំនិញ"
                }), 404

        conn.commit()

    return jsonify({
        "message": "បានកែទំនិញ",
        "id": product_id
    })

# POST - ទទួលកម្ម៉ង់ពី Website
@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    customer_name = data.get("customer_name")
    phone = data.get("phone")
    address = data.get("address")
    items = data.get("items", [])

    if not customer_name or not phone or not address:
        return jsonify({
            "error": "សូមបំពេញឈ្មោះ លេខទូរស័ព្ទ និងអាសយដ្ឋាន"
        }), 400

    if not items:
        return jsonify({
            "error": "មិនមានទំនិញក្នុងកម្ម៉ង់"
        }), 400

    total = 0

    for item in items:
        quantity = int(item.get("quantity", 0))
        price = float(item.get("sell_price", 0))
        total += quantity * price

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO orders
                (customer_name, phone, address, total)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (
                customer_name,
                phone,
                address,
                total
            ))

            order_id = cur.fetchone()[0]

            for item in items:
                product_id = int(item.get("id"))
                product_name = item.get("name")
                quantity = int(item.get("quantity"))
                price = float(item.get("sell_price"))
                subtotal = quantity * price

                cur.execute("""
                    INSERT INTO order_items
                    (order_id, product_id, product_name, quantity, price, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    order_id,
                    product_id,
                    product_name,
                    quantity,
                    price,
                    subtotal
                ))

        conn.commit()

    return jsonify({
        "message": "កម្ម៉ង់បានជោគជ័យ",
        "order_id": order_id,
        "total": total
    }), 201


@app.route("/")
def home():
    return "Sovanna Coffee API is running"


if __name__ == "__main__":
    app.run(debug=True)