import requests
from bs4 import BeautifulSoup
import mysql.connector

# Подключение к базе данных MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vika2806",
    database="insurance"
)
cursor = connection.cursor()

# Функция для записи данных в таблицу payment
def insert_payment(nomination, link, social_group):
    insert_query = """
    INSERT INTO payment (nomination, link, social_group)
    VALUES (%s, %s, %s)
    """
    cursor.execute(insert_query, (nomination, link, social_group))

# URL сайта
base_url = "https://www.xn--59-dlc3dya.xn--p1ai"
url = base_url + "/"

# Получение HTML страницы
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Извлечение данных из элементов payout__item
items = soup.select("div.payout__item")

for item in items:
    # Извлечение данных
    nomination = item.select_one(".payout__item-title span").text.strip()
    relative_link = item.select_one(".payout__item-text a")['href']
    link = base_url + relative_link  # Преобразуем относительную ссылку в абсолютную
    data_item = item.get("data-item")

    # Определение категории social_group
    if data_item == "OTHER":
        social_group = "other"
    elif data_item == "OLDER":
        social_group = "pensioners"
    elif data_item == "FAMILY":
        social_group = "family"
    else:
        social_group = "unknown"

    # Запись данных в базу
    insert_payment(nomination, link, social_group)

# Подтверждаем изменения и закрываем соединение
connection.commit()

cursor.close()
connection.close()
