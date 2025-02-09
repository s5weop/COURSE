import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonPollType, Message

from variables import questions_registration, User, instructions
from connector import save_user_to_db, get_payments, save_user_payment, get_payment_details, get_payment_id_for_nomination

from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN_BOT")

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

def generate_ReplyKeyboard(text_buttons, row_width = 1):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = list()
    for text_button in text_buttons:
        buttons.append(KeyboardButton(text_button))
    markup.add(*buttons, row_width=row_width)
    return markup

def send_long_message(user_id, text):
    # Разбить текст на части по 4000 символов
    max_length = 4000
    for i in range(0, len(text), max_length):
        bot.send_message(user_id, text[i:i + max_length])

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    new_user = User(user_id)
    if new_user.is_registered:
        bot.send_message(user_id, "Добро пожаловать обратно! Выберите социальную выплату, чтобы узнать подробности:")
        show_payments(message, new_user)
    else:
        # Инициализация данных пользователя
        bot.send_message(user_id, "Пройдите регистрацию для продолжения.")
        bot.send_message(user_id, questions_registration[new_user.current_question][1])
        bot.register_next_step_handler(message, registration_procedure, new_user)


# Функция проходит по списку questions_registration. Выводит вопросы и сохраняет ответы.
# Заполняет словарь user_data по ключам из списка.
# После всех итерации сохраняет user_data в БД.
def registration_procedure(message, new_user):
    parameter_question = questions_registration[new_user.current_question][0]
    new_user.user_data[parameter_question] = message.text
    new_user.current_question += 1
    if new_user.current_question < len(questions_registration):
        bot.send_message(new_user.user_id, questions_registration[new_user.current_question][1])
        bot.register_next_step_handler(message, registration_procedure, new_user)
    else:
        new_user.is_registered = True
        new_user.user_data['user_id']= message.from_user.id
        save_user_to_db(new_user.user_data)
        print('Регистрация окончена:', new_user.user_data)
        bot.send_message(new_user.user_id, 'Регистрация окончена!')
        show_payments(message, new_user)

# достаем выплаты из бд, выводим их в чат
# создаем клавиатуру из id выплат
def show_payments(message, user_old):
    user_id = user_old.user_id
    payments = get_payments()
    text_list_payments = ''
    max_sumbol_in_row = 100
    for payment_id, nomination in payments:
        text_list_payments += f'{payment_id}. {nomination}\n{"-"*max_sumbol_in_row}\n'
    bot.send_message(user_id, f"Доступные социальные выплаты:\n{text_list_payments}")
    markup = generate_ReplyKeyboard([i for i in range(1, len(payments)+1)], 4)
    bot.send_message(user_id, 'Выберете номер выплаты, чтобы узнать дополнительную информацию:', reply_markup=markup)

    #Ожидаем выбор пользователя id выплаты
    bot.register_next_step_handler(message, handler_choice_payment, user_old, payments)

# функция обработчик выбора выплаты
# после пересылаем на подтверждение
def handler_choice_payment(message, user_old, payments):
    user_id = user_old.user_id
    try:
        # проверяем, что пользователь выбрал категории из представленных
        if message.text in [str(i) for i in range(1, len(payments)+1)]:
            id_payment = int(message.text)
            info_payment = get_payment_details(id_payment)
            send_long_message(user_id, info_payment)
            available_events = ["Информация о том, как получить выплату", "Вернуться к выбору доступных выплат"]
            markup = generate_ReplyKeyboard(available_events)
            bot.send_message(user_id, "Выберете следующее действие: ", reply_markup=markup)
            bot.register_next_step_handler(message, send_info_get_payment, user_old, id_payment, available_events)
        else:
            markup = generate_ReplyKeyboard([i for i in range(1, len(payments) + 1)], 4)
            bot.send_message(user_id, 'Выберете категорию из представленных!', reply_markup=markup)
            bot.register_next_step_handler(message, handler_choice_payment, user_old, payments)
    except Exception as E:
        print(E)

# Вывод информации, как получить выплату. Запрос на подтверждение получения
def send_info_get_payment(message, user_old, id_payment, available_events):
    user_id = user_old.user_id
    if message.text in available_events:
        if message.text == available_events[0]:
            available_events = ["Да, я получил выплату", "Вернуться к выбору доступных выплат"]
            bot.send_message(user_id, instructions)
            markup = generate_ReplyKeyboard(available_events)
            bot.send_message(user_id, "Подтвердите, пожалуйста, если вы получили выплату!", reply_markup=markup)
            bot.register_next_step_handler(message, confirmation_payment, user_old, id_payment, available_events)
        else:
            show_payments(message, user_old)
    else:
        markup = generate_ReplyKeyboard(available_events)
        bot.send_message(message, "Выберете категорию из представленных!", reply_markup=markup)
        bot.register_next_step_handler(message, send_info_get_payment, user_old, id_payment, available_events)

# Функция проверяет подтвержденную выплату и сохраняеет в бд
def confirmation_payment(message, user_old, id_payment, available_events):
    user_id = user_old.user_id
    if message.text in available_events:
        if message.text == available_events[0]:
            save_user_payment(user_id, id_payment)
            available_events = ["Продолжить➡️"]
            markup = generate_ReplyKeyboard(available_events)
            bot.send_message(user_id, 'Спасибо за предоставленную информацию 😁🙏\nНажмите, "Продолжить➡️", чтобы вернуться к выбору доступных выплат', reply_markup=markup)
            bot.register_next_step_handler(message, return_selection, user_old)
        else:
            show_payments(message, user_old)
    else:
        markup = generate_ReplyKeyboard(available_events)
        bot.send_message(message, "Выберете категорию из представленных!", reply_markup=markup)
        bot.register_next_step_handler(message, send_info_get_payment, user_old, id_payment, available_events)

# Функция возвращает к выбору выплат, после нажатия кнопки
def return_selection(message, user_old):
    show_payments(message, user_old)

@bot.message_handler(func=lambda message: True)
def handle_payment_selection(message):
    pass

bot.polling(none_stop=True)