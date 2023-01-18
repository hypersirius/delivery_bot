import sqlite3

database = sqlite3.connect('fast_food.db')
cursor = database.cursor()


# ------------------------------------------------------------------------------------------------
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS users(
#     user_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     telegram_id INTEGER,
#     full_name VARCHAR(50),
#     phone_number VARCHAR(20),
#     email VARCHAR(50)
# )
# ''')
#
#
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS categories(
#         category_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         category_name VARCHAR(50) UNIQUE,
#         category_image TEXT
# )''')
# cursor.execute('''
# INSERT INTO categories(category_name, category_image)
# VALUES ('Сет 🍱', 'photos/categories/Set.jpg'),
# ('Лаваш 🌯', 'photos/categories/Lavash.jpg'),
# ('Шаурма 🥙', 'photos/categories/Shaurma.jpg'),
# ('Донар 🌮', 'photos/categories/Donar.jpg'),
# ('Бургер 🍔', 'photos/categories/Burger.jpg'),
# ('Хот-Дог 🌭', 'photos/categories/Hot-Dog.jpg'),
# ('Десерт 🍰', 'photos/categories/Desert.jpg'),
# ('Напитки 🥤', 'photos/categories/Napitki.jpg'),
# ('Гарнир 🍟', 'photos/categories/Garnir.jpg')
# ''')

# cursor.execute('''
# CREATE TABLE products(
#     product_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     category_id INTEGER NOT NULL,
#     product_name VARCHAR(50) NOT NULL UNIQUE,
#     price DECIMAL(15, 2) NOT NULL,
#     description VARCHAR(200),
#     image TEXT,
#     FOREIGN KEY(category_id) REFERENCES categories(category_id)
# )
# ''')

# cursor.execute('''
# INSERT INTO products(category_id, product_name, price, description, image)
# VALUES
# (1,
# 'COMBO +',
# 16000,
# 'Самое выгодное предложение! Горячий хрустящий картофель фри и стакан Pepsi',
# 'photos/products/Set1.jpg'
# ),
# (1,
# 'Kids COMBO',
# 16000,
# 'Выгодное предложение для маленьких гостей за 16 000 сум',
# 'photos/products/Set2.jpg'
# )
# ''')


# cursor.execute('''
# CREATE TABLE feedbacks(
#     feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id INTEGER,
#     feedback TEXT,
#     feedback_date DATE DEFAULT (datetime('now','localtime')),
#     FOREIGN KEY(user_id) REFERENCES users(user_id)
# )
# ''')

# cursor.execute('''
# DROP TABLE feedbacks;
# ''')

def create_cart_table():
    cursor.execute('''
CREATE TABLE IF NOT EXISTS carts(
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(user_id) UNIQUE,
    total_products INTEGER DEFAULT 0,
    total_price DECIMAL(10, 2) DEFAULT 0
)
    ''')
#
#
def create_cart_products_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart_products(
    cart_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER REFERENCES carts(cart_id),
    product_name VARCHAR(20) NOT NULL UNIQUE,
    quantity INTEGER NOT NULL,
    final_price DECIMAL(10, 2) NOT NULL
)
    ''')


create_cart_table()
create_cart_products_table()

# def create_orders_table():
#     cursor.execute('''
# CREATE TABLE IF NOT EXISTS orders(
#     order_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id INTEGER REFERENCES users(user_id) UNIQUE,
#     time_create DATE DEFAULT (datetime('now','localtime')),
#     status BOOLEAN DEFAULT FALSE,
#     location TEXT,
#     feedback TEXT
# )
#     ''')
#
#
# def create_order_products_table():
#     cursor.execute('''
# CREATE TABLE IF NOT EXISTS order_products(
#     order_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     order_id INTEGER REFERENCES orders(order_id) UNIQUE,
#     product_name VARCHAR(20) NOT NULL UNIQUE,
#     quantity INTEGER NOT NULL,
#     final_price_product DECIMAL(10, 2) NOT NULL
# )
#     ''')


# create_orders_table()
# create_order_products_table()

database.commit()
database.close()
