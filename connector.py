import requests
from bs4 import BeautifulSoup
from datetime import datetime
import mysql.connector

# Подключение к базе данных
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vika2806",
    database="insurance"
)
cursor = connection.cursor()

def is_registered(user_id):
    cursor.execute("SELECT id_user_tg FROM user WHERE id_user_tg = %s", (user_id,))
    return cursor.fetchone() is not None


user_data = {}
questions = [
    ("name", "Введите ваше имя:"),
    ("surname", "Введите вашу фамилию:"),
    ("middlename", "Введите ваше отчество (если есть, иначе введите '-'):"),
    ("old", "Введите ваш возраст (число):"),
    ("employed", "Вы трудоустроены? (да/нет):"),
    ("count_children", "Введите количество детей (число):"),
    ("Marital_status", "Введите ваше семейное положение:"),
    ("disabled", "Есть ли у вас инвалидность? (да/нет):")
]

def save_user_to_db(user_id):
    query = """
    INSERT INTO user (id_user_tg, name, surname, middlename, old, date, employed, count_children, Marital_status, disabled)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (
        user_id,
        user_data[user_id]["name"],
        user_data[user_id]["surname"],
        user_data[user_id]["middlename"],
        int(user_data[user_id]["old"]),
        datetime.now(),
        user_data[user_id]["employed"] == "да",
        int(user_data[user_id]["count_children"]),
        user_data[user_id]["Marital_status"],
        user_data[user_id]["disabled"] == "да"
    )
    cursor.execute(query, data)
    connection.commit()


def get_payments():
    cursor.execute("SELECT id_payment, nomination FROM payment")
    return cursor.fetchall()


def save_user_payment(user_id, payment_id):
    # Проверка, существует ли уже запись
    cursor.execute(
        "SELECT * FROM user_has_payment WHERE user_id_user_tg = %s AND payment_id_payment = %s",
        (user_id, payment_id)
    )
    if cursor.fetchone() is None:
        # Если записи нет, добавить новую
        query = "INSERT INTO user_has_payment (user_id_user_tg, payment_id_payment) VALUES (%s, %s)"
        cursor.execute(query, (user_id, payment_id))
        connection.commit()


def get_payment_details(payment_id):
    cursor.execute("SELECT link FROM payment WHERE id_payment = %s", (payment_id,))
    link = cursor.fetchone()[0]
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    details = soup.select_one("div.article__info").text.strip()
    return details

def get_payment_id_for_nomination(payment_name):
    cursor.execute("SELECT id_payment FROM payment WHERE nomination = %s", (payment_name,))
    return cursor.fetchone()