import sqlite3
from telebot.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton)


# ------------------------------------------------------------------------------------------------
def generate_registrate():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn = KeyboardButton(text='Пройти регистрацию')
    markup.add(btn)
    return markup


def generate_contact():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn = KeyboardButton(text='Отправить контакт', request_contact=True)
    markup.add(btn)
    return markup


def generate_yes_no():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_yes = KeyboardButton(text='Подтвердить ✅')
    btn_no = KeyboardButton(text='Отменить ❌')
    markup.add(btn_yes, btn_no)
    return markup


# -------------------------------------------------------------------------------------------------
def generate_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_menu = KeyboardButton(text='Меню 🍽')
    btn_myorders = KeyboardButton(text='Мои заказы 🛍')
    btn_feedback = KeyboardButton(text='Оставить отзыв ✍🏻')
    markup.add(btn_menu, btn_myorders, btn_feedback)
    return markup


def generate_categories_menu():
    database = sqlite3.connect('fast_food.db')
    cursor = database.cursor()

    cursor.execute('''
SELECT category_name FROM categories;
''')
    categories = cursor.fetchall()
    buttons = []
    for category in categories:
        btn = KeyboardButton(text=category[0])
        buttons.append(btn)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*buttons)
    btn_cart = KeyboardButton(text='Корзина 🛒')
    btn_back = KeyboardButton(text='Назад ⬅')
    markup.row(btn_cart, btn_back)
    return markup


def generate_products_menu(category_name):
    database = sqlite3.connect('fast_food.db')
    cursor = database.cursor()

    cursor.execute('''
SELECT product_name FROM categories
JOIN products USING (category_id)
WHERE category_name = ?
    ''', (category_name,))
    products = cursor.fetchall()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = []
    for product in products:
        btn = KeyboardButton(text=product[0])
        buttons.append(btn)

    markup.add(*buttons)
    btn_back = KeyboardButton(text='Назад ⬅')
    markup.row(btn_back)
    return markup


def generate_pagination(product_id,
                        quantity=1):
    markup = InlineKeyboardMarkup()
    btn_plus = InlineKeyboardButton(text='+',
                                    callback_data=f'change_{product_id}_{quantity+1}')
    btn_minus = InlineKeyboardButton(text='-',
                                     callback_data=f'change_{product_id}_{quantity-1}')
    btn_quantity = InlineKeyboardButton(text=str(quantity),
                                        callback_data='quantity')
    btn_add_to_cart = InlineKeyboardButton(text='🛒 Добавить в корзину',
                                           callback_data=f'cart_{product_id}_{quantity}')
    markup.row(btn_minus,
               btn_quantity,
               btn_plus)
    markup.row(btn_add_to_cart)
    return markup



def generate_cart_back():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn_cart = KeyboardButton(text='🛒 Корзина')
    btn_back = KeyboardButton(text='⬅ Назад')
    markup.row(btn_cart)
    markup.row(btn_back)
    return markup

def generate_cart_inline(cart_id: int):
    markup = InlineKeyboardMarkup()
    submit_order = InlineKeyboardButton(text='Оформить заказ 🚖', callback_data=f'order_{cart_id}')
    clear_cart = InlineKeyboardButton(text='Очистить корзону 🛒', callback_data='clear')
    markup.row(submit_order)
    markup.row(clear_cart)

    database = sqlite3.connect('fast_food.db')
    cursor = database.cursor()

    cursor.execute('''
    SELECT cart_product_id, product_name
    FROM cart_products
    WHERE cart_id = ?
    ''', (cart_id, ))

    cart_products = cursor.fetchall()
    database.close()

    for product_id, product_name in cart_products:
        markup.row(InlineKeyboardButton(text=f'❌️{product_name}', callback_data=f'delete_{product_id}'))

    return markup



