import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import shutil
from datetime import datetime
from PIL import Image, ImageTk


# =========================================================
# PATH
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "shop.db")
IMAGE_DIR = os.path.join(BASE_DIR, "images")
BACKUP_DIR = os.path.join(BASE_DIR, "backup")

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


# =========================================================
# DATABASE
# =========================================================

def db():
    if not os.path.exists(DB_FILE):
        import database
        database.create_database()

    return sqlite3.connect(DB_FILE)


# =========================================================
# HELPER
# =========================================================

def money(value):
    try:
        return f"{int(value):,} ៛"
    except:
        return "0 ៛"


def today():
    return datetime.now().strftime("%Y-%m-%d")


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def invoice_number():
    return "INV-" + datetime.now().strftime("%Y%m%d-%H%M%S")


def get_settings():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT shop_name, phone, address
        FROM settings
        WHERE id = 1
    """)

    row = cur.fetchone()
    conn.close()

    if row:
        return row

    return (
        "ហាងសុវណ្ណាលក់គ្រឿងកាហ្វេ",
        "",
        ""
    )


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()
root.title("ហាងសុវណ្ណាលក់គ្រឿងកាហ្វេ")
root.geometry("1450x850")
root.minsize(1100, 700)

FONT = ("Noto Sans Khmer", 11)
FONT_BOLD = ("Noto Sans Khmer", 12, "bold")
TITLE_FONT = ("Noto Sans Khmer", 18, "bold")

style = ttk.Style()

try:
    style.theme_use("clam")
except:
    pass

style.configure(
    "Treeview",
    font=("Arial", 11),
    rowheight=32
)

style.configure(
    "Treeview.Heading",
    font=("Arial", 11, "bold")
)

style.configure(
    "TButton",
    font=FONT,
    padding=7
)

style.configure(
    "TLabel",
    font=FONT
)

style.configure(
    "TEntry",
    font=("Arial", 11)
)

style.configure(
    "TCombobox",
    font=("Arial", 11)
)


# =========================================================
# CLEAR CONTENT
# =========================================================

def clear_content():
    for widget in content.winfo_children():
        widget.destroy()


# =========================================================
# HEADER
# =========================================================

header = tk.Frame(
    root,
    bg="#263238",
    height=70
)

header.pack(
    side="top",
    fill="x"
)

shop_name_var = tk.StringVar(
    value=get_settings()[0]
)

tk.Label(
    header,
    textvariable=shop_name_var,
    bg="#263238",
    fg="white",
    font=TITLE_FONT
).pack(
    side="left",
    padx=25,
    pady=15
)


# =========================================================
# MENU
# =========================================================

menu_frame = tk.Frame(
    root,
    bg="#37474F",
    width=190
)

menu_frame.pack(
    side="left",
    fill="y"
)

menu_frame.pack_propagate(False)


# =========================================================
# CONTENT
# =========================================================

content = tk.Frame(
    root,
    bg="#ECEFF1"
)

content.pack(
    side="right",
    fill="both",
    expand=True
)


# =========================================================
# MENU BUTTON
# =========================================================

def menu_button(text, command):
    btn = tk.Button(
        menu_frame,
        text=text,
        command=command,
        bg="#37474F",
        fg="white",
        activebackground="#546E7A",
        activeforeground="white",
        relief="flat",
        anchor="w",
        font=FONT_BOLD,
        padx=20,
        pady=12
    )

    btn.pack(
        fill="x",
        padx=5,
        pady=2
    )


# =========================================================
# DASHBOARD
# =========================================================

def dashboard_page():

    clear_content()

    tk.Label(
        content,
        text="🏠 ផ្ទាំងដើម",
        font=("Noto Sans Khmer", 20, "bold"),
        bg="#ECEFF1"
    ).pack(
        anchor="w",
        padx=25,
        pady=20
    )

    conn = db()
    cur = conn.cursor()

    # products
    cur.execute("SELECT COUNT(*) FROM products")
    product_count = cur.fetchone()[0]

    # stock
    cur.execute("""
        SELECT COALESCE(SUM(stock), 0)
        FROM products
    """)
    total_stock = cur.fetchone()[0]

    # today's invoices
    cur.execute("""
        SELECT COUNT(DISTINCT invoice_no)
        FROM sales
        WHERE date(sale_date) = ?
    """, (today(),))

    invoice_count = cur.fetchone()[0]

    # today's sales
    cur.execute("""
        SELECT COALESCE(SUM(total), 0)
        FROM sales
        WHERE date(sale_date) = ?
    """, (today(),))

    total_sales = cur.fetchone()[0]

    # today's profit
    cur.execute("""
        SELECT COALESCE(
            SUM(
                (s.sell_price - COALESCE(p.buy_price, 0))
                * s.quantity
            ),
            0
        )
        FROM sales s
        LEFT JOIN products p
        ON p.id = s.product_id
        WHERE date(s.sale_date) = ?
    """, (today(),))

    total_profit = cur.fetchone()[0]

    # low stock
    cur.execute("""
        SELECT COUNT(*)
        FROM products
        WHERE stock <= min_stock
    """)

    low_stock = cur.fetchone()[0]

    conn.close()

    cards = tk.Frame(
        content,
        bg="#ECEFF1"
    )

    cards.pack(
        fill="x",
        padx=20
    )

    card_data = [
        ("📦", "ចំនួនទំនិញ", product_count),
        ("📊", "ស្តុកសរុប", total_stock),
        ("🧾", "បុងថ្ងៃនេះ", invoice_count),
        ("💰", "លក់ថ្ងៃនេះ", money(total_sales)),
        ("💵", "ចំណេញថ្ងៃនេះ", money(total_profit)),
        ("⚠️", "ស្តុកជិតអស់", low_stock)
    ]

    for icon, title, value in card_data:

        frame = tk.Frame(
            cards,
            bg="white",
            relief="solid",
            borderwidth=1
        )

        frame.pack(
            side="left",
            expand=True,
            fill="both",
            padx=6,
            pady=10,
            ipady=20
        )

        tk.Label(
            frame,
            text=icon,
            font=("Arial", 25),
            bg="white"
        ).pack()

        tk.Label(
            frame,
            text=title,
            font=FONT,
            bg="white"
        ).pack()

        tk.Label(
            frame,
            text=str(value),
            font=("Arial", 18, "bold"),
            bg="white"
        ).pack(
            pady=5
        )

    # low stock list
    box = tk.LabelFrame(
        content,
        text=" ⚠️ ទំនិញស្តុកជិតអស់ ",
        font=FONT_BOLD,
        bg="white"
    )

    box.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=20
    )

    tree = ttk.Treeview(
        box,
        columns=("name", "stock", "min"),
        show="headings"
    )

    tree.heading("name", text="ទំនិញ")
    tree.heading("stock", text="ស្តុក")
    tree.heading("min", text="ស្តុកអប្បបរមា")

    tree.column("name", width=350)
    tree.column("stock", width=150)
    tree.column("min", width=180)

    tree.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, stock, min_stock
        FROM products
        WHERE stock <= min_stock
        ORDER BY stock ASC
    """)

    for row in cur.fetchall():
        tree.insert("", "end", values=row)

    conn.close()


# =========================================================
# PRODUCTS
# =========================================================

def products_page():

    clear_content()

    tk.Label(
        content,
        text="📦 គ្រប់គ្រងទំនិញ",
        font=("Noto Sans Khmer", 20, "bold"),
        bg="#ECEFF1"
    ).pack(
        anchor="w",
        padx=25,
        pady=15
    )

    top = tk.Frame(
        content,
        bg="#ECEFF1"
    )

    top.pack(
        fill="x",
        padx=20
    )

    search_var = tk.StringVar()

    tk.Label(
        top,
        text="ស្វែងរក:",
        bg="#ECEFF1",
        font=FONT
    ).pack(
        side="left"
    )

    search_entry = tk.Entry(
        top,
        textvariable=search_var,
        font=("Arial", 12),
        width=30
    )

    search_entry.pack(
        side="left",
        padx=10
    )

    table_frame = tk.Frame(
        content,
        bg="white"
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    columns = (
        "id",
        "name",
        "category",
        "buy",
        "sell",
        "stock",
        "barcode",
        "min"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    headings = {
        "id": "លេខ",
        "name": "ឈ្មោះទំនិញ",
        "category": "ប្រភេទ",
        "buy": "តម្លៃទិញ",
        "sell": "តម្លៃលក់",
        "stock": "ស្តុក",
        "barcode": "Barcode",
        "min": "ស្តុកអប្បបរមា"
    }

    widths = {
        "id": 60,
        "name": 250,
        "category": 150,
        "buy": 130,
        "sell": 130,
        "stock": 100,
        "barcode": 150,
        "min": 130
    }

    for col in columns:

        tree.heading(
            col,
            text=headings[col]
        )

        tree.column(
            col,
            width=widths[col],
            anchor="center"
        )

    tree.pack(
        fill="both",
        expand=True
    )

    def load_products():

        for item in tree.get_children():
            tree.delete(item)

        conn = db()
        cur = conn.cursor()

        keyword = search_var.get().strip()

        if keyword:

            cur.execute("""
                SELECT
                    id,
                    name,
                    category,
                    buy_price,
                    sell_price,
                    stock,
                    barcode,
                    min_stock
                FROM products
                WHERE name LIKE ?
                   OR category LIKE ?
                   OR barcode LIKE ?
                ORDER BY id DESC
            """, (
                "%" + keyword + "%",
                "%" + keyword + "%",
                "%" + keyword + "%"
            ))

        else:

            cur.execute("""
                SELECT
                    id,
                    name,
                    category,
                    buy_price,
                    sell_price,
                    stock,
                    barcode,
                    min_stock
                FROM products
                ORDER BY id DESC
            """)

        for row in cur.fetchall():

            row = list(row)

            row[3] = money(row[3])
            row[4] = money(row[4])

            tree.insert(
                "",
                "end",
                values=row
            )

        conn.close()

    search_var.trace_add(
        "write",
        lambda *args: load_products()
    )

    def product_form(product_id=None):

        form = tk.Toplevel(root)

        form.title(
            "បន្ថែមទំនិញ"
            if product_id is None
            else "កែទំនិញ"
        )

        form.geometry("550x650")
        form.transient(root)
        form.grab_set()

        fields = {}

        labels = [
            ("ឈ្មោះទំនិញ", "name"),
            ("ប្រភេទ", "category"),
            ("តម្លៃទិញ", "buy"),
            ("តម្លៃលក់", "sell"),
            ("ស្តុក", "stock"),
            ("Barcode", "barcode"),
            ("ស្តុកអប្បបរមា", "min")
        ]

        for label, key in labels:

            row = tk.Frame(form)
            row.pack(
                fill="x",
                padx=20,
                pady=7
            )

            tk.Label(
                row,
                text=label,
                width=18,
                anchor="w",
                font=FONT
            ).pack(
                side="left"
            )

            entry = tk.Entry(
                row,
                font=("Arial", 12)
            )

            entry.pack(
                side="left",
                fill="x",
                expand=True
            )

            fields[key] = entry

        image_var = tk.StringVar()

        image_frame = tk.Frame(form)
        image_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        tk.Label(
            image_frame,
            text="រូបភាព",
            width=18,
            anchor="w",
            font=FONT
        ).pack(
            side="left"
        )

        image_entry = tk.Entry(
            image_frame,
            textvariable=image_var,
            font=("Arial", 10)
        )

        image_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        def choose_image():

            file = filedialog.askopenfilename(
                title="ជ្រើសរូបភាព",
                filetypes=[
                    (
                        "Image",
                        "*.jpg *.jpeg *.png *.webp"
                    )
                ]
            )

            if not file:
                return

            filename = os.path.basename(file)
            destination = os.path.join(
                IMAGE_DIR,
                filename
            )

            try:
                shutil.copy2(
                    file,
                    destination
                )

                image_var.set(filename)

            except Exception as e:

                messagebox.showerror(
                    "កំហុស",
                    str(e)
                )

        tk.Button(
            image_frame,
            text="📷 ជ្រើសរូប",
            command=choose_image,
            font=FONT
        ).pack(
            side="left",
            padx=5
        )

        if product_id is not None:

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    name,
                    category,
                    buy_price,
                    sell_price,
                    stock,
                    barcode,
                    min_stock,
                    image
                FROM products
                WHERE id = ?
            """, (product_id,))

            row = cur.fetchone()
            conn.close()

            if row:

                fields["name"].insert(0, row[0])
                fields["category"].insert(0, row[1])
                fields["buy"].insert(0, row[2])
                fields["sell"].insert(0, row[3])
                fields["stock"].insert(0, row[4])
                fields["barcode"].insert(0, row[5])
                fields["min"].insert(0, row[6])
                image_var.set(row[7] or "")

        def save():

            name = fields["name"].get().strip()

            if not name:

                messagebox.showwarning(
                    "ព្រមាន",
                    "សូមបញ្ចូលឈ្មោះទំនិញ"
                )

                return

            try:

                buy = int(
                    fields["buy"].get() or 0
                )

                sell = int(
                    fields["sell"].get() or 0
                )

                stock = int(
                    fields["stock"].get() or 0
                )

                min_stock = int(
                    fields["min"].get() or 5
                )

            except:

                messagebox.showerror(
                    "កំហុស",
                    "តម្លៃទិញ លក់ ស្តុក ត្រូវតែជាលេខ"
                )

                return

            category = fields["category"].get().strip()
            barcode = fields["barcode"].get().strip()
            image = image_var.get().strip()

            conn = db()
            cur = conn.cursor()

            if product_id is None:

                cur.execute("""
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
                    name,
                    category,
                    buy,
                    sell,
                    stock,
                    image,
                    barcode,
                    min_stock
                ))

            else:

                cur.execute("""
                    UPDATE products
                    SET
                        name = ?,
                        category = ?,
                        buy_price = ?,
                        sell_price = ?,
                        stock = ?,
                        image = ?,
                        barcode = ?,
                        min_stock = ?
                    WHERE id = ?
                """, (
                    name,
                    category,
                    buy,
                    sell,
                    stock,
                    image,
                    barcode,
                    min_stock,
                    product_id
                ))

            conn.commit()
            conn.close()

            form.destroy()
            load_products()

        tk.Button(
            form,
            text="💾 រក្សាទុក",
            command=save,
            bg="#2E7D32",
            fg="white",
            font=FONT_BOLD,
            padx=20,
            pady=8
        ).pack(
            pady=20
        )

    def selected_id():

        selected = tree.selection()

        if not selected:
            return None

        values = tree.item(
            selected[0],
            "values"
        )

        return int(values[0])

    buttons = tk.Frame(
        content,
        bg="#ECEFF1"
    )

    buttons.pack(
        fill="x",
        padx=20,
        pady=10
    )

    tk.Button(
        buttons,
        text="➕ បន្ថែមទំនិញ",
        command=lambda: product_form(),
        font=FONT_BOLD
    ).pack(
        side="left",
        padx=5
    )

    def edit():

        pid = selected_id()

        if pid is None:

            messagebox.showwarning(
                "ព្រមាន",
                "សូមជ្រើសទំនិញជាមុន"
            )

            return

        product_form(pid)

    def delete():

        pid = selected_id()

        if pid is None:

            messagebox.showwarning(
                "ព្រមាន",
                "សូមជ្រើសទំនិញជាមុន"
            )

            return

        if not messagebox.askyesno(
            "បញ្ជាក់",
            "តើចង់លុបទំនិញនេះមែនទេ?"
        ):
            return

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM products WHERE id = ?",
            (pid,)
        )

        conn.commit()
        conn.close()

        load_products()

    tk.Button(
        buttons,
        text="✏️ កែ",
        command=edit,
        font=FONT_BOLD
    ).pack(
        side="left",
        padx=5
    )

    tk.Button(
        buttons,
        text="🗑️ លុប",
        command=delete,
        font=FONT_BOLD
    ).pack(
        side="left",
        padx=5
    )

    tk.Button(
        buttons,
        text="🔄 Refresh",
        command=load_products,
        font=FONT_BOLD
    ).pack(
        side="left",
        padx=5
    )

    load_products()


# =========================================================
# SALES
# =========================================================

def sales_page():

    clear_content()

    tk.Label(
        content,
        text="🛒 លក់ទំនិញ",
        font=("Noto Sans Khmer", 20, "bold"),
        bg="#ECEFF1"
    ).pack(
        anchor="w",
        padx=25,
        pady=15
    )

    main = tk.Frame(
        content,
        bg="#ECEFF1"
    )

    main.pack(
        fill="both",
        expand=True,
        padx=15
    )

    # LEFT
    left = tk.Frame(
        main,
        bg="white"
    )

    left.pack(
        side="left",
        fill="both",
        expand=True,
        padx=5
    )

    tk.Label(
        left,
        text="ជ្រើសទំនិញ",
        font=FONT_BOLD,
        bg="white"
    ).pack(
        anchor="w",
        padx=10,
        pady=10
    )

    search_var = tk.StringVar()

    search = tk.Entry(
        left,
        textvariable=search_var,
        font=("Arial", 12)
    )

    search.pack(
        fill="x",
        padx=10,
        pady=5
    )

    product_tree = ttk.Treeview(
        left,
        columns=(
            "id",
            "name",
            "sell",
            "stock"
        ),
        show="headings"
    )

    product_tree.heading(
        "id",
        text="លេខ"
    )

    product_tree.heading(
        "name",
        text="ទំនិញ"
    )

    product_tree.heading(
        "sell",
        text="តម្លៃលក់"
    )

    product_tree.heading(
        "stock",
        text="ស្តុក"
    )

    product_tree.column(
        "id",
        width=60
    )

    product_tree.column(
        "name",
        width=250
    )

    product_tree.column(
        "sell",
        width=130
    )

    product_tree.column(
        "stock",
        width=90
    )

    product_tree.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5
    )

    def load_sale_products():

        for item in product_tree.get_children():
            product_tree.delete(item)

        conn = db()
        cur = conn.cursor()

        keyword = search_var.get().strip()

        cur.execute("""
            SELECT
                id,
                name,
                sell_price,
                stock
            FROM products
            WHERE name LIKE ?
               OR barcode LIKE ?
            ORDER BY name
        """, (
            "%" + keyword + "%",
            "%" + keyword + "%"
        ))

        for row in cur.fetchall():

            product_tree.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    money(row[2]),
                    row[3]
                )
            )

        conn.close()

    search_var.trace_add(
        "write",
        lambda *args: load_sale_products()
    )

    # RIGHT
    right = tk.Frame(
        main,
        bg="white",
        width=600
    )

    right.pack(
        side="right",
        fill="both",
        expand=True,
        padx=5
    )

    tk.Label(
        right,
        text="🛒 កន្ត្រកលក់",
        font=FONT_BOLD,
        bg="white"
    ).pack(
        anchor="w",
        padx=10,
        pady=10
    )

    cart_tree = ttk.Treeview(
        right,
        columns=(
            "id",
            "name",
            "qty",
            "price",
            "total"
        ),
        show="headings"
    )

    for col, text in [
        ("id", "លេខ"),
        ("name", "ទំនិញ"),
        ("qty", "ចំនួន"),
        ("price", "តម្លៃ"),
        ("total", "សរុប")
    ]:

        cart_tree.heading(
            col,
            text=text
        )

    cart_tree.column(
        "id",
        width=50
    )

    cart_tree.column(
        "name",
        width=200
    )

    cart_tree.column(
        "qty",
        width=70
    )

    cart_tree.column(
        "price",
        width=110
    )

    cart_tree.column(
        "total",
        width=130
    )

    cart_tree.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5
    )

    # quantity
    qty_frame = tk.Frame(
        right,
        bg="white"
    )

    qty_frame.pack(
        fill="x",
        padx=10,
        pady=5
    )

    tk.Label(
        qty_frame,
        text="ចំនួន:",
        font=FONT,
        bg="white"
    ).pack(
        side="left"
    )

    qty_var = tk.IntVar(
        value=1
    )

    qty_spin = tk.Spinbox(
        qty_frame,
        from_=1,
        to=9999,
        textvariable=qty_var,
        width=8,
        font=("Arial", 12)
    )

    qty_spin.pack(
        side="left",
        padx=10
    )

    cart = []

    def add_to_cart():

        selected = product_tree.selection()

        if not selected:

            messagebox.showwarning(
                "ព្រមាន",
                "សូមជ្រើសទំនិញ"
            )

            return

        values = product_tree.item(
            selected[0],
            "values"
        )

        pid = int(values[0])
        name = values[1]

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT sell_price, stock
            FROM products
            WHERE id = ?
        """, (pid,))

        row = cur.fetchone()
        conn.close()

        if not row:
            return

        price = row[0]
        stock = row[1]

        try:
            qty = int(qty_var.get())
        except:
            qty = 1

        if qty <= 0:
            return

        existing_qty = 0

        for item in cart:

            if item["id"] == pid:

                existing_qty = item["qty"]

        if existing_qty + qty > stock:

            messagebox.showwarning(
                "ស្តុកមិនគ្រប់",
                f"{name}\nស្តុកនៅសល់ {stock}"
            )

            return

        found = False

        for item in cart:

            if item["id"] == pid:

                item["qty"] += qty
                found = True

        if not found:

            cart.append({
                "id": pid,
                "name": name,
                "qty": qty,
                "price": price
            })

        refresh_cart()

    def refresh_cart():

        for item in cart_tree.get_children():
            cart_tree.delete(item)

        total = 0

        for item in cart:

            line_total = (
                item["qty"]
                * item["price"]
            )

            total += line_total

            cart_tree.insert(
                "",
                "end",
                values=(
                    item["id"],
                    item["name"],
                    item["qty"],
                    money(item["price"]),
                    money(line_total)
                )
            )

        total_var.set(
            money(total)
        )

    tk.Button(
        qty_frame,
        text="➕ ដាក់ចូលកន្ត្រក",
        command=add_to_cart,
        font=FONT_BOLD
    ).pack(
        side="left",
        padx=10
    )

    def remove_cart():

        selected = cart_tree.selection()

        if not selected:
            return

        values = cart_tree.item(
            selected[0],
            "values"
        )

        pid = int(values[0])

        cart[:] = [
            item
            for item in cart
            if item["id"] != pid
        ]

        refresh_cart()

    tk.Button(
        qty_frame,
        text="🗑️ ដកចេញ",
        command=remove_cart,
        font=FONT_BOLD
    ).pack(
        side="left"
    )

    # customer
    customer_frame = tk.Frame(
        right,
        bg="white"
    )

    customer_frame.pack(
        fill="x",
        padx=10,
        pady=5
    )

    tk.Label(
        customer_frame,
        text="អតិថិជន:",
        font=FONT,
        bg="white"
    ).pack(
        side="left"
    )

    customer_var = tk.StringVar()

    tk.Entry(
        customer_frame,
        textvariable=customer_var,
        font=("Arial", 12)
    ).pack(
        side="left",
        fill="x",
        expand=True,
        padx=10
    )

    # total
    total_var = tk.StringVar(
        value="0 ៛"
    )

    total_frame = tk.Frame(
        right,
        bg="white"
    )

    total_frame.pack(
        fill="x",
        padx=10,
        pady=5
    )

    tk.Label(
        total_frame,
        text="សរុប:",
        font=("Noto Sans Khmer", 15, "bold"),
        bg="white"
    ).pack(
        side="left"
    )

    tk.Label(
        total_frame,
        textvariable=total_var,
        font=("Arial", 18, "bold"),
        bg="white"
    ).pack(
        side="right"
    )

    # cash
    cash_var = tk.StringVar()

    cash_frame = tk.Frame(
        right,
        bg="white"
    )

    cash_frame.pack(
        fill="x",
        padx=10,
        pady=5
    )

    tk.Label(
        cash_frame,
        text="ប្រាក់ទទួល:",
        font=FONT,
        bg="white"
    ).pack(
        side="left"
    )

    cash_entry = tk.Entry(
        cash_frame,
        textvariable=cash_var,
        font=("Arial", 13)
    )

    cash_entry.pack(
        side="left",
        fill="x",
        expand=True,
        padx=10
    )

    change_var = tk.StringVar(
        value="0 ៛"
    )

    tk.Label(
        cash_frame,
        text="អាប់:",
        font=FONT_BOLD,
        bg="white"
    ).pack(
        side="left"
    )

    tk.Label(
        cash_frame,
        textvariable=change_var,
        font=("Arial", 14, "bold"),
        bg="white"
    ).pack(
        side="left",
        padx=10
    )

    def calculate_change(*args):

        try:
            cash = int(
                cash_var.get() or 0
            )
        except:
            cash = 0

        total = 0

        for item in cart:

            total += (
                item["qty"]
                * item["price"]
            )

        change = cash - total

        change_var.set(
            money(change if change >= 0 else 0)
        )

    cash_var.trace_add(
        "write",
        calculate_change
    )

    def finish_sale():

        if not cart:

            messagebox.showwarning(
                "ព្រមាន",
                "កន្ត្រកនៅទទេ"
            )

            return

        total = sum(
            item["qty"] * item["price"]
            for item in cart
        )

        try:
            cash = int(
                cash_var.get() or 0
            )
        except:

            messagebox.showerror(
                "កំហុស",
                "សូមបញ្ចូលប្រាក់ជាលេខ"
            )

            return

        if cash < total:

            messagebox.showwarning(
                "ប្រាក់មិនគ្រប់",
                f"តម្លៃសរុប {money(total)}"
            )

            return

        invoice = invoice_number()
        customer = customer_var.get().strip()
        sale_time = now_text()

        conn = db()
        cur = conn.cursor()

        try:

            for item in cart:

                cur.execute("""
                    SELECT stock
                    FROM products
                    WHERE id = ?
                """, (item["id"],))

                row = cur.fetchone()

                if not row or row[0] < item["qty"]:

                    raise Exception(
                        f"ស្តុក {item['name']} មិនគ្រប់"
                    )

            for item in cart:

                line_total = (
                    item["qty"]
                    * item["price"]
                )

                cur.execute("""
                    INSERT INTO sales
                    (
                        invoice_no,
                        product_id,
                        product_name,
                        quantity,
                        sell_price,
                        total,
                        customer_name,
                        sale_date
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    invoice,
                    item["id"],
                    item["name"],
                    item["qty"],
                    item["price"],
                    line_total,
                    customer,
                    sale_time
                ))

                cur.execute("""
                    UPDATE products
                    SET stock = stock - ?
                    WHERE id = ?
                """, (
                    item["qty"],
                    item["id"]
                ))

                cur.execute("""
                    INSERT INTO stock_history
                    (
                        product_id,
                        product_name,
                        stock_type,
                        quantity,
                        note,
                        stock_date
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item["id"],
                    item["name"],
                    "លក់",
                    -item["qty"],
                    invoice,
                    sale_time
                ))

            conn.commit()

        except Exception as e:

            conn.rollback()
            conn.close()

            messagebox.showerror(
                "កំហុស",
                str(e)
            )

            return

        conn.close()

        change = cash - total

        receipt = create_receipt_text(
            invoice,
            cart,
            total,
            cash,
            change,
            customer,
            sale_time
        )

        show_receipt(
            receipt,
            invoice
        )

        cart.clear()
        customer_var.set("")
        cash_var.set("")
        change_var.set("0 ៛")

        refresh_cart()
        load_sale_products()

    tk.Button(
        right,
        text="💰 បញ្ចប់ការលក់ / ចេញបុង",
        command=finish_sale,
        bg="#2E7D32",
        fg="white",
        font=("Noto Sans Khmer", 14, "bold"),
        pady=12
    ).pack(
        fill="x",
        padx=10,
        pady=12
    )

    load_sale_products()


# =========================================================
# RECEIPT TEXT
# =========================================================

def create_receipt_text(
    invoice,
    cart,
    total,
    cash,
    change,
    customer,
    sale_time
):

    shop, phone, address = get_settings()

    lines = []

    lines.append(
        "=" * 45
    )

    lines.append(
        shop
    )

    if phone:
        lines.append(
            "ទូរស័ព្ទ: " + phone
        )

    if address:
        lines.append(
            "អាសយដ្ឋាន: " + address
        )

    lines.append(
        "=" * 45
    )

    lines.append(
        "លេខបុង: " + invoice
    )

    lines.append(
        "ថ្ងៃ: " + sale_time
    )

    if customer:
        lines.append(
            "អតិថិជន: " + customer
        )

    lines.append(
        "-" * 45
    )

    for item in cart:

        line_total = (
            item["qty"]
            * item["price"]
        )

        lines.append(
            f"{item['name']}"
        )

        lines.append(
            f"  {item['qty']} x "
            f"{money(item['price'])} = "
            f"{money(line_total)}"
        )

    lines.append(
        "-" * 45
    )

    lines.append(
        "សរុប: " + money(total)
    )

    lines.append(
        "ទទួល: " + money(cash)
    )

    lines.append(
        "អាប់: " + money(change)
    )

    lines.append(
        "=" * 45
    )

    lines.append(
        "សូមអរគុណ 🙏"
    )

    return "\n".join(lines)


# =========================================================
# SHOW RECEIPT
# =========================================================

def show_receipt(text, invoice):

    win = tk.Toplevel(root)

    win.title(
        "បុង " + invoice
    )

    win.geometry(
        "650x650"
    )

    text_box = tk.Text(
        win,
        font=("Arial", 12)
    )

    text_box.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    text_box.insert(
        "1.0",
        text
    )

    text_box.config(
        state="disabled"
    )

    buttons = tk.Frame(win)

    buttons.pack(
        fill="x",
        pady=10
    )

    def save():

        filename = filedialog.asksaveasfilename(
            title="រក្សាទុកបុង",
            defaultextension=".txt",
            initialfile=invoice + ".txt",
            filetypes=[
                ("Text file", "*.txt")
            ]
        )

        if not filename:
            return

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(text)

        messagebox.showinfo(
            "ជោគជ័យ",
            "រក្សាទុកបុងរួចហើយ"
        )

    tk.Button(
        buttons,
        text="💾 រក្សាទុកបុង",
        command=save,
        font=FONT_BOLD
    ).pack(
        side="left",
        padx=10
    )

    tk.Button(
        buttons,
        text="បិទ",
        command=win.destroy,
        font=FONT_BOLD
    ).pack(
        side="left"
    )


# =========================================================
# INVOICES
# =========================================================

def invoices_page():

    clear_content()

    tk.Label(
        content,
        text="🧾 ប្រវត្តិបុង / វិក្កយបត្រ",
        font=("Noto Sans Khmer", 20, "bold"),
        bg="#ECEFF1"
    ).pack(
        anchor="w",
        padx=25,
        pady=15
    )

    frame = tk.Frame(
        content,
        bg="white"
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    tree = ttk.Treeview(
        frame,
        columns=(
            "invoice",
            "date",
            "customer",
            "total"
        ),
        show="headings"
    )

    for col, text in [
        ("invoice", "លេខបុង"),
        ("date", "ថ្ងៃ"),
        ("customer", "អតិថិជន"),
        ("total", "សរុប")
    ]:

        tree.heading(
            col,
            text=text
        )

    tree.column(
        "invoice",
        width=220
    )

    tree.column(
        "date",
        width=180
    )

    tree.column(
        "customer",
        width=200
    )

    tree.column(
        "total",
        width=160
    )

    tree.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    def load():

        for item in tree.get_children():
            tree.delete(item)

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                invoice_no,
                MAX(sale_date),
                MAX(customer_name),
                SUM(total)
            FROM sales
            GROUP BY invoice_no
            ORDER BY MAX(sale_date) DESC
        """)

        for row in cur.fetchall():

            tree.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    row[2] or "",
                    money(row[3])
                )
            )

        conn.close()

    def preview():

        selected = tree.selection()

        if not selected:
            return

        values = tree.item(
            selected[0],
            "values"
        )

        invoice = values[0]

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                product_id,
                product_name,
                quantity,
                sell_price,
                total,
                customer_name,
                sale_date
            FROM sales
            WHERE invoice_no = ?
            ORDER BY id
        """, (invoice,))

        rows = cur.fetchall()
        conn.close()

        if not rows:
            return

        cart = []

        for row in rows:

            cart.append({
                "id": row[0],
                "name": row[1],
                "qty": row[2],
                "price": row[3]
            })

        total = sum(
            row[4]
            for row in rows
        )

        text = create_receipt_text(
            invoice,
            cart,
            total,
            total,
            0,
            rows[0][5] or "",
            rows[0][6]
        )

        show_receipt(
            text,
            invoice
        )

    buttons = tk.Frame(
        content,
        bg="#ECEFF1"
    )

    buttons.pack(
        fill="x",
        padx=20,
        pady=10
    )

    tk.Button(
        buttons,
        text="👁️ មើលបុង",
        command=preview,
        font=FONT_BOLD
    ).pack(
        side="left",
        padx=5
    )

    tk.Button(
        buttons,
        text="🔄 Refresh",
        command=load,
        font=FONT_BOLD
    ).pack(
        side="left",
        padx=5
    )

    load()


# =========================================================
# REPORTS
# =========================================================

def reports_page():

    clear_content()

    tk.Label(
        content,
        text="📊 របាយការណ៍ការលក់",
        font=("Noto Sans Khmer", 20, "bold"),
        bg="#ECEFF1"
    ).pack(
        anchor="w",
        padx=25,
        pady=15
    )

    filter_frame = tk.Frame(
        content,
        bg="#ECEFF1"
    )

    filter_frame.pack(
        fill="x",
        padx=20,
        pady=5
    )

    tk.Label(
        filter_frame,
        text="កាលបរិច្ឆេទ:",
        font=FONT,
        bg="#ECEFF1"
    ).pack(
        side="left"
    )

    date_var = tk.StringVar(
        value=today()
    )

    tk.Entry(
        filter_frame,
        textvariable=date_var,
        width=15,
        font=("Arial", 12)
    ).pack(
        side="left",
        padx=10
    )

    result_label = tk.Label(
        content,
        text="",
        font=("Noto Sans Khmer", 14, "bold"),
        bg="#ECEFF1"
    )

    result_label.pack(
        anchor="w",
        padx=25,
        pady=10
    )

    frame = tk.Frame(
        content,
        bg="white"
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=5
    )

    tree = ttk.Treeview(
        frame,
        columns=(
            "product",
            "qty",
            "sales"
        ),
        show="headings"
    )

    tree.heading(
        "product",
        text="ទំនិញ"
    )

    tree.heading(
        "qty",
        text="ចំនួនលក់"
    )

    tree.heading(
        "sales",
        text="ទឹកប្រាក់"
    )

    tree.column(
        "product",
        width=350
    )

    tree.column(
        "qty",
        width=150
    )

    tree.column(
        "sales",
        width=200
    )

    tree.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    def load_report():

        for item in tree.get_children():
            tree.delete(item)

        selected_date = date_var.get().strip()

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                COUNT(DISTINCT invoice_no),
                COALESCE(SUM(total), 0)
            FROM sales
            WHERE date(sale_date) = ?
        """, (selected_date,))

        invoice_count, sales_total = cur.fetchone()

        cur.execute("""
            SELECT
                product_name,
                SUM(quantity),
                SUM(total)
            FROM sales
            WHERE date(sale_date) = ?
            GROUP BY product_id, product_name
            ORDER BY SUM(total) DESC
        """, (selected_date,))

        rows = cur.fetchall()

        conn.close()

        result_label.config(
            text=
            f"បុង: {invoice_count}    |    "
            f"លក់សរុប: {money(sales_total)}"
        )

        for row in rows:

            tree.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    money(row[2])
                )
            )

    tk.Button(
        filter_frame,
        text="🔍 បង្ហាញ",
        command=load_report,
        font=FONT_BOLD
    ).pack(
        side="left"
    )

    load_report()


# =========================================================
# STOCK
# =========================================================

def stock_page():

    clear_content()

    tk.Label(
        content,
        text="📦 គ្រប់គ្រងស្តុក",
        font=("Noto Sans Khmer", 20, "bold"),
        bg="#ECEFF1"
    ).pack(
        anchor="w",
        padx=25,
        pady=15
    )

    frame = tk.Frame(
        content,
        bg="white"
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    tree = ttk.Treeview(
        frame,
        columns=(
            "id",
            "name",
            "type",
            "qty",
            "note",
            "date"
        ),
        show="headings"
    )

    headings = {
        "id": "លេខ",
        "name": "ទំនិញ",
        "type": "ប្រភេទ",
        "qty": "ចំនួន",
        "note": "កំណត់សម្គាល់",
        "date": "ថ្ងៃ"
    }

    for col in headings:

        tree.heading(
            col,
            text=headings[col]
        )

    tree.column(
        "id",
        width=60
    )

    tree.column(
        "name",
        width=250
    )

    tree.column(
        "type",
        width=120
    )

    tree.column(
        "qty",
        width=100
    )

    tree.column(
        "note",
        width=220
    )

    tree.column(
        "date",
        width=180
    )

    tree.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    def load():

        for item in tree.get_children():
            tree.delete(item)

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                product_name,
                stock_type,
                quantity,
                note,
                stock_date
            FROM stock_history
            ORDER BY id DESC
        """)

        for row in cur.fetchall():

            tree.insert(
                "",
                "end",
                values=row
            )

        conn.close()

    def add_stock():

        selected = product_tree.selection()

        if not selected:

            messagebox.showwarning(
                "ព្រមាន",
                "សូមជ្រើសទំនិញ"
            )

            return

        values = product_tree.item(
            selected[0],
            "values"
        )

        pid = int(values[0])
        name = values[1]

        win = tk.Toplevel(root)

        win.title(
            "បន្ថែមស្តុក"
        )

        win.geometry(
            "450x300"
        )

        tk.Label(
            win,
            text=f"ទំនិញ: {name}",
            font=FONT_BOLD
        ).pack(
            pady=15
        )

        tk.Label(
            win,
            text="ចំនួនបន្ថែម",
            font=FONT
        ).pack()

        qty_var = tk.StringVar()

        tk.Entry(
            win,
            textvariable=qty_var,
            font=("Arial", 14)
        ).pack(
            pady=10
        )

        tk.Label(
            win,
            text="កំណត់សម្គាល់",
            font=FONT
        ).pack()

        note_var = tk.StringVar()

        tk.Entry(
            win,
            textvariable=note_var,
            font=("Arial", 12)
        ).pack(
            pady=10
        )

        def save_stock():

            try:
                qty = int(
                    qty_var.get()
                )
            except:

                messagebox.showerror(
                    "កំហុស",
                    "សូមបញ្ចូលចំនួនជាលេខ"
                )

                return

            if qty <= 0:
                return

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                UPDATE products
                SET stock = stock + ?
                WHERE id = ?
            """, (
                qty,
                pid
            ))

            cur.execute("""
                INSERT INTO stock_history
                (
                    product_id,
                    product_name,
                    stock_type,
                    quantity,
                    note,
                    stock_date
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pid,
                name,
                "បន្ថែម",
                qty,
                note_var.get().strip(),
                now_text()
            ))

            conn.commit()
            conn.close()

            win.destroy()
            load()

        tk.Button(
            win,
            text="💾 បន្ថែមស្តុក",
            command=save_stock,
            bg="#2E7D32",
            fg="white",
            font=FONT_BOLD,
            pady=8
        ).pack(
            pady=10
        )

    # product selection for stock
    product_box = tk.LabelFrame(
        content,
        text="ជ្រើសទំនិញសម្រាប់បន្ថែមស្តុក",
        font=FONT_BOLD,
        bg="#ECEFF1"
    )

    product_box.pack(
        fill="x",
        padx=20,
        pady=5
    )

    product_tree = ttk.Treeview(
        product_box,
        columns=(
            "id",
            "name",
            "stock"
        ),
        show="headings",
        height=4
    )

    product_tree.heading(
        "id",
        text="លេខ"
    )

    product_tree.heading(
        "name",
        text="ទំនិញ"
    )

    product_tree.heading(
        "stock",
        text="ស្តុក"
    )

    product_tree.column(
        "id",
        width=60
    )

    product_tree.column(
        "name",
        width=350
    )

    product_tree.column(
        "stock",
        width=120
    )

    product_tree.pack(
        fill="x",
        padx=10,
        pady=5
    )

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, stock
        FROM products
        ORDER BY name
    """)

    for row in cur.fetchall():

        product_tree.insert(
            "",
            "end",
            values=row
        )

    conn.close()

    tk.Button(
        content,
        text="➕ បន្ថែមស្តុក",
        command=add_stock,
        font=FONT_BOLD
    ).pack(
        anchor="w",
        padx=20,
        pady=5
    )

    load()


# =========================================================
# CUSTOMERS
# =========================================================

def customers_page():

    clear_content()

    tk.Label(
        content,
        text="👤 អតិថិជន",
        font=("Noto Sans Khmer", 20, "bold"),
        bg="#ECEFF1"
    ).pack(
        anchor="w",
        padx=25,
        pady=15
    )

    frame = tk.Frame(
        content,
        bg="white"
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    tree = ttk.Treeview(
        frame,
        columns=(
            "id",
            "name",
            "phone",
            "address",
            "note"
        ),
        show="headings"
    )

    headings = {
        "id": "លេខ",
        "name": "ឈ្មោះ",
        "phone": "ទូរស័ព្ទ",
        "address": "អាសយដ្ឋាន",
        "note": "ចំណាំ"
    }

    for col in headings:

        tree.heading(
            col,
            text=headings[col]
        )

    tree.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    for col, width in [
        ("id", 60),
        ("name", 200),
        ("phone", 180),
        ("address", 250),
        ("note", 250)
    ]:

        tree.column(
            col,
            width=width
        )

    def load():

        for item in tree.get_children():
            tree.delete(item)

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                name,
                phone,
                address,
                note
            FROM customers
            ORDER BY id DESC
        """)

        for row in cur.fetchall():

            tree.insert(
                "",
                "end",
                values=row
            )

        conn.close()

    def add_customer():

        win = tk.Toplevel(root)

        win.title(
            "បន្ថែមអតិថិជន"
        )

        win.geometry(
            "500x400"
        )

        fields = {}

        for label, key in [
            ("ឈ្មោះ", "name"),
            ("ទូរស័ព្ទ", "phone"),
            ("អាសយដ្ឋាន", "address"),
            ("ចំណាំ", "note")
        ]:

            row = tk.Frame(win)
            row.pack(
                fill="x",
                padx=20,
                pady=8
            )

            tk.Label(
                row,
                text=label,
                width=15,
                anchor="w",
                font=FONT
            ).pack(
                side="left"
            )

            entry = tk.Entry(
                row,
                font=("Arial", 12)
            )

            entry.pack(
                side="left",
                fill="x",
                expand=True
            )

            fields[key] = entry

        def save():

            name = fields["name"].get().strip()

            if not name:

                messagebox.showwarning(
                    "ព្រមាន",
                    "សូមបញ្ចូលឈ្មោះ"
                )

                return

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO customers
                (
                    name,
                    phone,
                    address,
                    note
                )
                VALUES (?, ?, ?, ?)
            """, (
                name,
                fields["phone"].get().strip(),
                fields["address"].get().strip(),
                fields["note"].get().strip()
            ))

            conn.commit()
            conn.close()

            win.destroy()
            load()

        tk.Button(
            win,
            text="💾 រក្សាទុក",
            command=save,
            font=FONT_BOLD
        ).pack(
            pady=20
        )

    def delete_customer():

        selected = tree.selection()

        if not selected:
            return

        values = tree.item(
            selected[0],
            "values"
        )

        if not messagebox.askyesno(
            "បញ្ជាក់",
            "តើចង់លុបអតិថិជននេះមែនទេ?"
        ):
            return

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM customers WHERE id = ?",
            (values[0],)
        )

        conn.commit()
        conn.close()

        load()

    buttons = tk.Frame(
        content,
        bg="#ECEFF1"
    )

    buttons.pack(
        fill="x",
        padx=20,
        pady=5
    )

    tk.Button(
        buttons,
        text="➕ បន្ថែមអតិថិជន",
        command=add_customer,
        font=FONT_BOLD
    ).pack(
        side="left",
        padx=5
    )

    tk.Button(
        buttons,
        text="🗑️ លុប",
        command=delete_customer,
        font=FONT_BOLD
    ).pack(
        side="left",
        padx=5
    )

    load()


# =========================================================
# SETTINGS
# =========================================================

def settings_page():

    clear_content()

    tk.Label(
        content,
        text="⚙️ កំណត់ហាង",
        font=("Noto Sans Khmer", 20, "bold"),
        bg="#ECEFF1"
    ).pack(
        anchor="w",
        padx=25,
        pady=20
    )

    form = tk.Frame(
        content,
        bg="white"
    )

    form.pack(
        fill="x",
        padx=30,
        pady=10
    )

    shop, phone, address = get_settings()

    fields = {}

    for label, value, key in [
        ("ឈ្មោះហាង", shop, "shop"),
        ("ទូរស័ព្ទ", phone, "phone"),
        ("អាសយដ្ឋាន", address, "address")
    ]:

        row = tk.Frame(
            form,
            bg="white"
        )

        row.pack(
            fill="x",
            padx=20,
            pady=12
        )

        tk.Label(
            row,
            text=label,
            width=20,
            anchor="w",
            font=FONT,
            bg="white"
        ).pack(
            side="left"
        )

        entry = tk.Entry(
            row,
            font=("Arial", 13)
        )

        entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        entry.insert(
            0,
            value
        )

        fields[key] = entry

    def save():

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE settings
            SET
                shop_name = ?,
                phone = ?,
                address = ?
            WHERE id = 1
        """, (
            fields["shop"].get().strip(),
            fields["phone"].get().strip(),
            fields["address"].get().strip()
        ))

        conn.commit()
        conn.close()

        shop_name_var.set(
            fields["shop"].get().strip()
        )

        messagebox.showinfo(
            "ជោគជ័យ",
            "រក្សាទុកការកំណត់រួចហើយ"
        )

    tk.Button(
        content,
        text="💾 រក្សាទុក",
        command=save,
        bg="#2E7D32",
        fg="white",
        font=FONT_BOLD,
        padx=30,
        pady=10
    ).pack(
        anchor="w",
        padx=30,
        pady=15
    )


# =========================================================
# BACKUP
# =========================================================

def backup_database():

    if not os.path.exists(DB_FILE):

        messagebox.showerror(
            "កំហុស",
            "រកមិនឃើញ shop.db"
        )

        return

    filename = (
        "shop_backup_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".db"
    )

    destination = os.path.join(
        BACKUP_DIR,
        filename
    )

    try:

        shutil.copy2(
            DB_FILE,
            destination
        )

        messagebox.showinfo(
            "Backup ជោគជ័យ",
            "Backup រួចហើយ\n\n"
            + destination
        )

    except Exception as e:

        messagebox.showerror(
            "កំហុស",
            str(e)
        )


# =========================================================
# CLOSE
# =========================================================

def close_app():

    if messagebox.askyesno(
        "បិទកម្មវិធី",
        "តើចង់បិទកម្មវិធីមែនទេ?"
    ):

        root.destroy()


# =========================================================
# MENU
# =========================================================

menu_button(
    "🏠  ដើម",
    dashboard_page
)

menu_button(
    "🛒  លក់",
    sales_page
)

menu_button(
    "📦  ទំនិញ",
    products_page
)

menu_button(
    "🧾  បុង",
    invoices_page
)

menu_button(
    "📊  របាយការណ៍",
    reports_page
)

menu_button(
    "📦  ស្តុក",
    stock_page
)

menu_button(
    "👤  អតិថិជន",
    customers_page
)

menu_button(
    "⚙️  កំណត់",
    settings_page
)

menu_button(
    "💾  Backup",
    backup_database
)

menu_button(
    "❌  បិទ",
    close_app
)


# =========================================================
# START
# =========================================================

dashboard_page()

root.mainloop()