import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sqlite3
import os
import shutil

# =========================
# កំណត់ទីតាំង
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "shop.db")
IMAGE_FOLDER = os.path.join(BASE_DIR, "images")

os.makedirs(IMAGE_FOLDER, exist_ok=True)


# =========================
# Database
# =========================
def get_products():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, category, buy_price,
               sell_price, stock, image
        FROM products
        ORDER BY id
    """)

    products = cursor.fetchall()

    conn.close()
    return products


# =========================
# បន្ថែមទំនិញ
# =========================
def add_product():

    window = tk.Toplevel(root)
    window.title("➕ បន្ថែមទំនិញ")
    window.geometry("500x650")

    selected_image = {"path": ""}

    tk.Label(
        window,
        text="➕ បន្ថែមទំនិញ",
        font=("Noto Sans Khmer", 20, "bold")
    ).pack(pady=15)

    # ឈ្មោះ
    tk.Label(
        window,
        text="ឈ្មោះទំនិញ",
        font=("Noto Sans Khmer", 12)
    ).pack()

    name_entry = tk.Entry(
        window,
        font=("Noto Sans Khmer", 12),
        width=30
    )
    name_entry.pack(pady=5)

    # ប្រភេទ
    tk.Label(
        window,
        text="ប្រភេទ",
        font=("Noto Sans Khmer", 12)
    ).pack()

    category_entry = tk.Entry(
        window,
        font=("Noto Sans Khmer", 12),
        width=30
    )
    category_entry.pack(pady=5)

    # តម្លៃទិញ
    tk.Label(
        window,
        text="តម្លៃទិញ (៛)",
        font=("Noto Sans Khmer", 12)
    ).pack()

    buy_entry = tk.Entry(
        window,
        font=("Noto Sans Khmer", 12),
        width=30
    )
    buy_entry.pack(pady=5)

    # តម្លៃលក់
    tk.Label(
        window,
        text="តម្លៃលក់ (៛)",
        font=("Noto Sans Khmer", 12)
    ).pack()

    sell_entry = tk.Entry(
        window,
        font=("Noto Sans Khmer", 12),
        width=30
    )
    sell_entry.pack(pady=5)

    # ស្តុក
    tk.Label(
        window,
        text="ចំនួនស្តុក",
        font=("Noto Sans Khmer", 12)
    ).pack()

    stock_entry = tk.Entry(
        window,
        font=("Noto Sans Khmer", 12),
        width=30
    )
    stock_entry.pack(pady=5)

    # រូបភាព
    image_label = tk.Label(
        window,
        text="មិនទាន់ជ្រើសរូបភាព",
        font=("Noto Sans Khmer", 11)
    )
    image_label.pack(pady=10)

    def choose_image():

        file_path = filedialog.askopenfilename(
            title="ជ្រើសរូបភាពទំនិញ",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            selected_image["path"] = file_path

            image_label.config(
                text="បានជ្រើសរូបភាព ✅"
            )

    tk.Button(
        window,
        text="🖼️ ជ្រើសរូបភាព",
        font=("Noto Sans Khmer", 12),
        command=choose_image
    ).pack(pady=5)

    # =========================
    # រក្សាទុក Database
    # =========================
    def save_product():

        name = name_entry.get().strip()
        category = category_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "ព្រមាន",
                "សូមបញ្ចូលឈ្មោះទំនិញ"
            )
            return

        try:
            buy = int(buy_entry.get())
            sell = int(sell_entry.get())
            stock = int(stock_entry.get())

        except ValueError:
            messagebox.showerror(
                "កំហុស",
                "តម្លៃទិញ តម្លៃលក់ និងស្តុក ត្រូវបញ្ចូលជាលេខ"
            )
            return

        image_name = ""

        # រក្សាទុករូបភាព
        if selected_image["path"]:

            original_name = os.path.basename(
                selected_image["path"]
            )

            image_name = original_name

            destination = os.path.join(
                IMAGE_FOLDER,
                image_name
            )

            shutil.copy2(
                selected_image["path"],
                destination
            )

        # បញ្ចូល Database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO products
            (name, category, buy_price, sell_price, stock, image)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            category,
            buy,
            sell,
            stock,
            image_name
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "ជោគជ័យ",
            f"បានបន្ថែម {name} រួចហើយ ✅"
        )

        window.destroy()

        refresh_products()

    tk.Button(
        window,
        text="💾 រក្សាទុក",
        font=("Noto Sans Khmer", 12, "bold"),
        command=save_product
    ).pack(pady=15)


# =========================
# បង្ហាញទំនិញ
# =========================
def refresh_products():

    for widget in products_frame.winfo_children():
        widget.destroy()

    products = get_products()

    for product in products:

        product_id = product[0]
        name = product[1]
        category = product[2]
        buy_price = product[3]
        sell_price = product[4]
        stock = product[5]
        image_name = product[6]

        card = tk.Frame(
            products_frame,
            bd=2,
            relief="groove",
            padx=15,
            pady=15
        )

        card.pack(
            side="left",
            padx=10,
            pady=10
        )

        # រូបភាព
        image_path = os.path.join(
            IMAGE_FOLDER,
            image_name
        )

        if image_name and os.path.exists(image_path):

            try:
                img = Image.open(image_path)
                img.thumbnail((160, 160))

                photo = ImageTk.PhotoImage(img)

                image_label = tk.Label(
                    card,
                    image=photo
                )

                image_label.image = photo
                image_label.pack()

            except:
                tk.Label(
                    card,
                    text="🖼️ រូបភាពមានបញ្ហា"
                ).pack()

        else:

            tk.Label(
                card,
                text="🖼️ មិនទាន់មានរូបភាព",
                font=("Noto Sans Khmer", 11)
            ).pack(pady=60)

        # ព័ត៌មាន
        tk.Label(
            card,
            text=name,
            font=("Noto Sans Khmer", 18, "bold")
        ).pack(pady=5)

        tk.Label(
            card,
            text=f"ប្រភេទ: {category}",
            font=("Noto Sans Khmer", 11)
        ).pack()

        tk.Label(
            card,
            text=f"តម្លៃទិញ: {buy_price:,} ៛",
            font=("Noto Sans Khmer", 11)
        ).pack()

        tk.Label(
            card,
            text=f"តម្លៃលក់: {sell_price:,} ៛",
            font=("Noto Sans Khmer", 11)
        ).pack()

        tk.Label(
            card,
            text=f"ស្តុក: {stock}",
            font=("Noto Sans Khmer", 11)
        ).pack()


# =========================
# Window
# =========================
root = tk.Tk()

root.title("ហាងសុវណ្ណាលក់គ្រឿងកាហ្វេ")
root.geometry("1000x700")

tk.Label(
    root,
    text="☕ ហាងសុវណ្ណាលក់គ្រឿងកាហ្វេ",
    font=("Noto Sans Khmer", 22, "bold")
).pack(pady=15)


# =========================
# ផ្ទាំងទំនិញ
# =========================
products_frame = tk.Frame(root)
products_frame.pack(
    fill="both",
    expand=True,
    padx=20
)

refresh_products()


# =========================
# ប៊ូតុង
# =========================
tk.Button(
    root,
    text="➕ បន្ថែមទំនិញ",
    font=("Noto Sans Khmer", 13),
    command=add_product
).pack(pady=8)

tk.Button(
    root,
    text="❌ បិទ",
    font=("Noto Sans Khmer", 12),
    command=root.destroy
).pack(pady=8)


root.mainloop()