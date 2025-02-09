import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from connector import is_registered, user_data, questions, save_user_to_db, get_payments, save_user_payment, get_payment_details, get_payment_id_for_nomination


bot = telebot.TeleBot("7071800191:AAGIs28xt9bsQonvemOezuxjG0K1M9U9nGI")


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_registered(user_id):
        bot.send_message(user_id, "Добро пожаловать обратно! Выберите социальную выплату, чтобы узнать подробности:")
        show_payments(message)
    else:
        # Инициализация данных пользователя
        user_data[user_id] = {"step": 0}
        bot.send_message(user_id, "Пройдите регистрацию для продолжения.")
        ask_next_question(message)

def ask_next_question(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"step": 0}  # Инициализация на случай отсутствия данных
    step = user_data[user_id]["step"]
    key, question = questions[step]
    bot.send_message(user_id, question)

@bot.message_handler(func=lambda message: message.from_user.id in user_data)
def handle_registration(message):
    user_id = message.from_user.id

    if user_id not in user_data or "step" not in user_data[user_id]:
        # Если данные пользователя отсутствуют, инициализируем
        user_data[user_id] = {"step": 0}

    step = user_data[user_id]["step"]
    key, question = questions[step]
    value = message.text.strip()

    if key in ["old", "count_children"] and not value.isdigit():
        bot.send_message(user_id, "Введите корректное число.")
        return ask_next_question(message)

    if key in ["employed", "disabled"] and value.lower() not in ["да", "нет"]:
        bot.send_message(user_id, "Введите 'да' или 'нет'.")
        return ask_next_question(message)

    user_data[user_id][key] = value
    user_data[user_id]["step"] += 1

    if user_data[user_id]["step"] < len(questions):
        ask_next_question(message)
    else:
        save_user_to_db(user_id)
        bot.send_message(user_id, "Регистрация завершена! Выберите социальную выплату, чтобы узнать подробности:")
        show_payments(message)

#достаем выплаты из бд и выгружаем их на кнопки
def show_payments(message):
    user_id = message.from_user.id
    payments = get_payments()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for payment_id, nomination in payments:
        markup.add(KeyboardButton(nomination))
    bot.send_message(user_id, "Доступные социальные выплаты:", reply_markup=markup)

#для отправки длинного сообщения
def send_long_message(user_id, text: str):
    # Разбить текст на части по 4000 символов
    max_length = 4000
    for i in range(0, len(text), max_length):
        bot.send_message(user_id, text[i:i + max_length])


@bot.message_handler(func=lambda message: True)
def handle_payment_selection(message):
    user_id = message.from_user.id
    payment_name = message.text.strip()
    result = get_payment_id_for_nomination(payment_name)
    if result:

        '''<Получение доп. информации о выплате>'''
        payment_id = result[0]
        save_user_payment(user_id, payment_id)
        details = get_payment_details(payment_id)

        send_long_message(user_id, f"Подробности о выплате:\n{details}")
        '''<Получение доп. информации о выплате/>'''

        # Предложить варианты действий
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("Как получить выплату"))
        markup.add(KeyboardButton("Посмотреть другую выплату"))
        bot.send_message(user_id, "Что вы хотите сделать дальше?", reply_markup=markup)

        # Сохранить состояние пользователя
        user_data[user_id] = {"selected_payment_id": payment_id}
    else:
        bot.send_message(user_id, "Выплата не найдена. Выберите из доступных.")
        show_payments(message)

@bot.message_handler(func=lambda message: message.from_user.id in user_data and "selected_payment_id" in user_data[message.from_user.id])
def handle_payment_action(message):
    user_id = message.from_user.id
    payment_id = user_data[user_id]["selected_payment_id"]
    action = message.text.strip()

    if action == "Как получить выплату":
        instructions = (
            "Как получить выплату:\n"
            "1. Вы подаете заявление и пакет документов, предусмотренный законодательством для назначения выплаты, "
            "в ближайший филиал многофункционального центра или на портале \"Госуслуги\".\n"
            "2. Территориальный отдел Центра социальных выплат и компенсаций Пермского края рассматривает направленный "
            "в их адрес пакет документов (в сроки, установленные административным регламентом для данного вида выплаты - "
            "от десяти до 30 рабочих дней).\n"
            "3. В случае принятия решения об отказе в назначении пособия (ввиду отсутствия правовых оснований) в Ваш адрес "
            "в течение пяти рабочих дней после принятия решения будет направлено уведомление с указанием причин отказа. "
            "В случае принятия положительного решения о назначении пособия денежные средства будут перечислены на Ваш счет "
            "в сроки, установленные графиком выплат Центра социальных выплат и компенсаций Пермского края, начиная с месяца, "
            "следующего за месяцем подачи заявления."
        )
        bot.send_message(user_id, instructions)
    elif action == "Посмотреть другую выплату":
        show_payments(message)
    else:
        bot.send_message(user_id, "Неверный выбор. Попробуйте снова.")

bot.polling(none_stop=True)
