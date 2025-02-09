import requests
from bs4 import BeautifulSoup
from datetime import datetime
import mysql.connector

from dotenv import load_dotenv
import os

load_dotenv()

# Подключение к базе данных
connection = mysql.connector.connect(
    host=os.getenv('HOST_DB'),
    user=os.getenv('USER_DB'),
    password=os.getenv('PASSWORD_DB'),
    database=os.getenv('DATABASE_DB')
)
cursor = connection.cursor()

def is_registered(user_id):
    cursor.execute("SELECT id_user_tg FROM user WHERE id_user_tg = %s", (user_id,))
    return cursor.fetchone() is not None


def save_user_to_db(user_data):
    query = """
    INSERT INTO user (id_user_tg, name, surname, middlename, old, date, employed, count_children, Marital_status, disabled)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (
        user_data["user_id"],
        user_data["name"],
        user_data["surname"],
        user_data["middlename"],
        int(user_data["old"]),
        datetime.now(),
        user_data["employed"] == "да",
        int(user_data["count_children"]),
        user_data["Marital_status"],
        user_data["disabled"] == "да"
    )
    cursor.execute(query, data)
    connection.commit()


def get_payments():
    cursor.execute("SELECT id_payment, nomination FROM payment")
    return cursor.fetchall()


def get_user_has_payment_count(user_id, payment_id) -> tuple | None:
    # Проверка, существует ли уже запись
    cursor.execute(
        "SELECT user_has_payment_count FROM user_has_payment WHERE user_id_user_tg = %s AND payment_id_payment = %s",
        (user_id, payment_id)
    )
    result = cursor.fetchone()
    return result

def save_user_payment(user_id: int, payment_id: int):
    count = get_user_has_payment_count(user_id, payment_id)
    if count is None:
        # Если записи нет, добавить новую
        query = "INSERT INTO user_has_payment (user_id_user_tg, payment_id_payment, user_has_payment_count) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, payment_id, 1))
        connection.commit()
    else:
        query = "UPDATE user_has_payment SET user_has_payment_count = user_has_payment_count + 1 WHERE user_id_user_tg = %s AND payment_id_payment = %s"
        cursor.execute(query, (user_id, payment_id))
        connection.commit()
    return count

# получаем дополнительную информацию о выплате
def get_payment_details(payment_id: int):
    cursor.execute("SELECT link FROM payment WHERE id_payment = %s", (payment_id,))
    link = cursor.fetchone()[0]
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    soup = soup.select_one("div.article__info")

    # Проходим по заголовкам, вставляем текст и удаляем их
    for tag in soup.find_all("h3"):
        tag.insert_before(f"\n<u><b>{tag.text.strip()}</b></u>\n")  # Вставляем заголовок
        tag.decompose()  # Удаляем сам тег <h3> после вставки

    # Получаем итоговый текст без HTML-тегов
    plain_text = soup.get_text(separator="\n", strip=True)

    # Добавляем пустую строку после каждого заголовка
    formatted_text = plain_text.replace('<u>', '\n<u>')
    return formatted_text


def get_payment_id_for_nomination(payment_name):
    cursor.execute("SELECT id_payment FROM payment WHERE nomination = %s", (payment_name,))
    return cursor.fetchone()


def get_old():
    cursor.execute("SELECT old FROM user")
    return cursor.fetchall()


def get_old_count_children():
    cursor.execute("SELECT old, count_children FROM user")
    return cursor.fetchall()


def get_old_payment():
    cursor.execute("SELECT old, payment_id_payment FROM user, user_has_payment")
    ages_and_payments = cursor.fetchall()
    ages = [row[0] for row in ages_and_payments]
    count_payments = []
    for age in set(ages):
        count = ages.count(age)
        count_payments.append((age, count))
    return count_payments


def get_most_frequent_payment():
    cursor.callproc('GetPaymentStatistics')
    for result in cursor.stored_results():
        rows = result.fetchall()
    return rows



