import mysql.connector

# Подключение
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vika2806",
    database="insurance"
)

cursor = connection.cursor()

# Создание таблицы user
create_user_table = """
CREATE TABLE IF NOT EXISTS user (
    id_user_tg INT PRIMARY KEY,
    name VARCHAR(45) NOT NULL,
    surname VARCHAR(45) NOT NULL,
    middlename VARCHAR(45),
    old INT,
    date DATE,
    employed BOOLEAN,
    count_children INT,
    marital_status VARCHAR(45),
    disabled BOOLEAN
);
"""
cursor.execute(create_user_table)

# Создание таблицы payment
create_payment_table = """
CREATE TABLE IF NOT EXISTS payment (
    id_payment INT PRIMARY KEY AUTO_INCREMENT,
    nomination VARCHAR(200) NOT NULL,
    link VARCHAR(100) NOT NULL,
    social_group ENUM('family', 'pensioners', 'other') NOT NULL
);
"""
cursor.execute(create_payment_table)

# Создание таблицы user_has_payment
create_user_has_payment_table = """
CREATE TABLE IF NOT EXISTS user_has_payment (
    user_id_user_tg INT,
    payment_id_payment INT,
    PRIMARY KEY (user_id_user_tg, payment_id_payment),
    FOREIGN KEY (user_id_user_tg) REFERENCES user(id_user_tg),
    FOREIGN KEY (payment_id_payment) REFERENCES payment(id_payment)
);
"""
cursor.execute(create_user_has_payment_table)

# Подтверждаем изменения
connection.commit()

# Закрываем соединение
cursor.close()
connection.close()