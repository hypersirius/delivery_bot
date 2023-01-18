import sqlite3

from telebot import TeleBot
from telebot.types import Message, CallbackQuery, LabeledPrice

from configs import *
from keyboards import *

bot = TeleBot(TOKEN, parse_mode='HTML')

user_data = {}


# ------------------------------------------------------------------------------------------------
# Регистрация юзера
@bot.message_handler(commands=['start'])
def start(message: Message):
    global user_data
    chat_id = message.chat.id
    user_data['chat_id'] = chat_id
    database = sqlite3.connect('fast_food.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT telegram_id FROM users;
    ''')
    telegram_id = cursor.fetchall()
    users_id = []
    for u_id in telegram_id:
        users_id.append(u_id[0])
    if chat_id in users_id:
        welcome(message)
    else:
        bot.send_message(chat_id,
                         f'Здраствуйте. Чтобы воспользоваться услугами нашего бота доставки еды вам надо пройти регистрацию.')
        bot.send_message(chat_id,
                         f"Если вы хотите начать регистрацию, то нажмите на кнопку 'Пройти регистрацию'.",
                         reply_markup=generate_registrate())


@bot.message_handler(func=lambda message: 'Пройти регистрацию' == message.text)
def ask_full_name(message: Message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, f'Напишите своё имя и фамилию: ')
    bot.register_next_step_handler(msg, ask_phone_number)


def ask_phone_number(message: Message):
    global user_data
    chat_id = message.chat.id
    full_name = message.text
    user_data['full_name'] = full_name
    msg = bot.send_message(chat_id, f'Отправьте ваш контакт: ', reply_markup=generate_contact())
    bot.register_next_step_handler(msg, ask_email)


def ask_email(message: Message):
    global user_data
    chat_id = message.chat.id
    phone_number = message.contact.phone_number
    user_data['phone_number'] = phone_number
    msg = bot.send_message(chat_id, f'Отправьте ваш адрес почты: ')
    bot.register_next_step_handler(msg, submit_registration)


def submit_registration(message: Message):
    global user_data
    chat_id = message.chat.id
    email = message.text
    user_data['email'] = email
    bot.send_message(chat_id, f'''
<b>Имя и фамилия:</b> {user_data['full_name']}
<b>Номер телефона:</b> {user_data['phone_number']}
<b>Адрес почты:</b> {user_data['email']}
''', reply_markup=generate_yes_no())


@bot.message_handler(func=lambda message: 'Подтвердить ✅' == message.text)
def submit(message: Message):
    global user_data
    chat_id = message.chat.id
    database = sqlite3.connect('fast_food.db')
    cursor = database.cursor()

    cursor.execute('''
INSERT INTO users(telegram_id, full_name, phone_number, email)
VALUES (?,?,?,?)
''', (user_data['chat_id'], user_data['full_name'], user_data['phone_number'], user_data['email']))

    database.commit()
    database.close()
    bot.send_message(chat_id, f'Регистрация прошла успешно !')
    welcome(message)


@bot.message_handler(func=lambda message: 'Отменить ❌' == message.text)
def unsubmit(message: Message):
    global user_data
    user_data.clear()
    start(message)


def welcome(message: Message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     'Добро пожаловать в бот доставки еды FASTFOOD. Выберите что делать ?',
                     reply_markup=generate_main_menu())


# ---------------------------------------------------------------------------------------------
# Меню
@bot.message_handler(func=lambda message: message.text == 'Меню 🍽')
def reply_category_menu(message: Message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Выберите категорию: ', reply_markup=generate_categories_menu())
    bot.register_next_step_handler(msg, show_products)


def show_products(message: Message):
    if 'Назад' in message.text:
        start(message)
    else:
        chat_id = message.chat.id
        category_name = message.text
        database = sqlite3.connect('fast_food.db')
        cursor = database.cursor()

        cursor.execute('''
    SELECT category_image FROM categories
    WHERE category_name = ?
        ''', (category_name,))

        category_img = cursor.fetchone()[0]

        with open(category_img, mode='rb') as img:
            msg = bot.send_photo(chat_id,
                                 photo=img,
                                 caption=f'''Вы вибрали категорию {category_name}.''',
                                 reply_markup=generate_products_menu(category_name))
            bot.register_next_step_handler(msg, show_product)


def show_product(message: Message):
    if 'Назад' in message.text:
        reply_category_menu(message)
    else:
        chat_id = message.chat.id
        product_name = message.text
        database = sqlite3.connect('fast_food.db')
        cursor = database.cursor()
        cursor.execute('''
        SELECT description, price, image, product_id FROM products
        WHERE product_name = ?
        ''', (product_name,))
        product_data = cursor.fetchone()
        bot.send_message(chat_id, 'Выберите одно из следующих: ', reply_markup=generate_cart_back())
        with open(product_data[2], mode='rb') as img:
            bot.send_photo(chat_id,
                           photo=img,
                           caption=f'''{product_data[0]}
    <b>Цена: </b>{product_data[1]} сум.''',
                           reply_markup=generate_pagination(product_data[3]))


@bot.callback_query_handler(func=lambda call: 'change' in call.data)
def change_quantity(call: CallbackQuery):
    chat_id = call.message.chat.id
    # change_1_2
    _, product_id, quantity = call.data.split('_')
    product_id, quantity = int(product_id), int(quantity)
    message_id = call.message.message_id
    if quantity > 0:
        bot.edit_message_reply_markup(chat_id,
                                      message_id,
                                      reply_markup=generate_pagination(product_id, quantity))


@bot.callback_query_handler(lambda call: 'cart' in call.data)
def add_to_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    # cart_3_5
    _, product_id, quantity = call.data.split('_')
    product_id, quantity = int(product_id), int(quantity)

    database = sqlite3.connect('fast_food.db')
    cursor = database.cursor()

    try:
        cursor.execute('''SELECT cart_id FROM carts WHERE user_id = 
        (SELECT user_id FROM users WHERE telegram_id = ?)''', (chat_id,))
        cart_id = cursor.fetchone()[0]
    except:
        cursor.execute('''INSERT INTO carts(user_id) VALUES(
        (SELECT user_id FROM users WHERE telegram_id = ?))''', (chat_id,))
        cursor.execute('''SELECT cart_id FROM carts WHERE user_id = 
        (SELECT user_id FROM users WHERE telegram_id = ?)''', (chat_id,))
        cart_id = cursor.fetchone()[0]

    cursor.execute('''
    SELECT price, product_name
    FROM products WHERE product_id = ?
    ''', (product_id,))

    price, product_name = cursor.fetchone()
    final_price = price * quantity

    try:
        cursor.execute('''INSERT INTO cart_products(cart_id, product_name, quantity, final_price)
        VALUES (?,?,?,?)''', (cart_id, product_name, quantity, final_price))
        bot.answer_callback_query(call.id, 'Продукт успешно добавлен в корзину !')
        database.commit()
        database.close()
    except:
        cursor.execute('''SELECT quantity, final_price FROM cart_products WHERE cart_id = ? AND product_name = ?''',
                       (cart_id, product_name))
        old_quantity, old_price = cursor.fetchone()
        old_quantity += quantity
        old_price += final_price

        cursor.execute('''UPDATE cart_products
        SET quantity = ?,
        final_price = ?
        WHERE cart_id = ? AND product_name = ?''',
                       (old_quantity, old_price, cart_id, product_name))
        database.commit()
        database.close()
        bot.answer_callback_query(call.id, f'Добавлено {quantity} продуктов в корзину !')




@bot.message_handler(func=lambda message: '🛒 Корзина' == message.text)
def show_cart(message: Message, edit_message: bool = False):
    chat_id = message.chat.id

    database = sqlite3.connect('fast_food.db')
    cursor = database.cursor()

    cursor.execute('''
    SELECT user_id FROM users
    WHERE telegram_id = ?
    ''', (chat_id, ))
    user_id = cursor.fetchone()[0]

    cursor.execute('''
    SELECT cart_id FROM carts
    WHERE user_id = ?
    ''', (user_id, ))
    cart_id = cursor.fetchone()[0]

    cursor.execute('''
    SELECT quantity, final_price FROM cart_products
    WHERE cart_id = ?
    ''', (cart_id, ))
    data = cursor.fetchall()
    total_quantity = 0
    total_price = 0
    for product in data:
        total_quantity += product[0]
        total_price += product[1]
    # print(total_quantity)
    # print(total_price)
    cursor.execute('''
    UPDATE carts SET
    total_products = ?,
    total_price = ?
    WHERE cart_id = ?
    ''', (total_quantity, total_price, cart_id))

    bot.send_message(chat_id, 'Выберите категорию: ')

    cursor.execute('''
    SELECT product_name, quantity FROM cart_products
    WHERE cart_id = ?
    ''', (cart_id,))

    products = cursor.fetchall()
    text = '''В корзине: \n'''

    for product in products:
        text += f'''{product[1]} ❌️{product[0]}\n'''

    text += f'''Товары: {total_price} сум\nДоставка: 10000 сум\nИтого: {total_price + 10000} сум'''
    if edit_message:
        bot.edit_message_text(text, chat_id, message.message_id,
                              reply_markup=generate_cart_inline(cart_id))
    else:
        bot.send_message(chat_id, text, reply_markup=generate_cart_inline(cart_id))


@bot.callback_query_handler(lambda call: 'order' in call.data)
def create_order(call: CallbackQuery):
    chat_id = call.message.chat.id

    _, cart_id = call.data.split('_')
    cart_id = int(cart_id)

    database = sqlite3.connect('fast_food.db')
    cursor = database.cursor()

    cursor.execute('''
        SELECT product_name, quantity, final_price
        FROM cart_products
        WHERE cart_id = ?
    ''', (cart_id, ))

    cart_products = cursor.fetchall()


    cursor.execute('''
    SELECT total_products, total_price FROM carts
    WHERE user_id = 
    (
        SELECT user_id FROM users WHERE telegram_id = ?
    )
    
    ''', (chat_id, ))

    total_products, total_price = cursor.fetchone()

    text = 'Ваш чек: \n\n'
    i = 0

    for product_name, quantity, final_price in cart_products:
        i += 1
        text += f"""{i}. {product_name}\n\n
Количество: {quantity}\n
Цена: {final_price}\n\n"""

    text += f"""Цена корзины: {total_price}"""

    bot.send_invoice(
        chat_id=chat_id,
        title=f'Чек №{cart_id}',
        description=text,
        invoice_payload='bot-defined invoice payload',
        provider_token='398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065',
        currency='UZS',
        prices=[
            LabeledPrice(label='Итого', amount=int(str(total_price) + '00')),
            LabeledPrice(label='Доставка', amount=1000000)
        ]
    )

    bot.send_message(chat_id, 'Оплачено !')


@bot.callback_query_handler(lambda call: 'clear' in call.data)
def clear_cart(call: CallbackQuery):
    chat_id = call.message.chat.id

    database = sqlite3.connect('fast_food.db')
    cursor = database.cursor()

    cursor.execute('''
    SELECT user_id FROM users
    WHERE telegram_id = ?
    ''', (chat_id, ))

    user_id = cursor.fetchone()[0]

    cursor.execute('''
    SELECT cart_id FROM carts
    WHERE user_id = ?
    ''', (user_id, ))

    cart_id = cursor.fetchone()[0]

    cursor.execute('''
    DELETE FROM cart_products WHERE cart_id = ?
    ''', (cart_id, ))

    cursor.execute('''
    DELETE FROM carts WHERE cart_id = ?
    ''', (cart_id, ))
    database.commit()
    database.close()

    bot.send_message(chat_id, 'Ваша корзина очищена !')
    reply_category_menu(call.message)


@bot.callback_query_handler(lambda call: 'delete' in call.data)
def delete_product_cart(call: CallbackQuery):

    message = call.message

    _, cart_product_id = call.data.split('_')
    cart_product_id = int(cart_product_id)

    database = sqlite3.connect('fast_food.db')
    cursor = database.cursor()

    cursor.execute('''
    DELETE FROM cart_products
    WHERE cart_product_id = ?
    ''', (cart_product_id, ))

    database.commit()
    database.close()

    bot.answer_callback_query(call.id, 'Продукт успешно удален !')

    show_cart(message, edit_message=True)



# ---------------------------------------------------------------------------------------------
# Мои заказы

# ----------------------------------------------------------------------------------------------
# Оставить отзыв

@bot.message_handler(func=lambda message: 'Оставить отзыв ✍🏻' == message.text)
def take_feedback(message: Message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Отправьте ваш отзыв: ')
    bot.register_next_step_handler(msg, send_feedback)


def send_feedback(message: Message):
    chat_id = message.chat.id
    feedback = message.text
    database = sqlite3.connect('fast_food.db')
    cursor = database.cursor()
    cursor.execute('''
SELECT * FROM users
WHERE telegram_id = ?
    ''', (chat_id,))
    user_data = cursor.fetchone()

    cursor.execute('''
INSERT INTO feedbacks(user_id, feedback)
VALUES (?,?)
    ''', (user_data[0], feedback))
    database.commit()

    bot.send_message(CHANNEL_ID, f'''
<b>Имя и фамилия: </b>{user_data[2]}
<b>Номер телефона: </b>{user_data[3]}
<b>Отзыв: </b> {feedback}
''')
    bot.send_message(chat_id, 'Спасибо за ваш отзыв !')
    welcome(message)


bot.polling(none_stop=True)


# TODO: Обработать 2 шт кнопок назад
# TODO: Заполнить список продуктов
# TODO: Истории заказов
