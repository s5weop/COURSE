import os
import matplotlib.pyplot as plt
import numpy as np

# Импортируем функции из другого файла
from connector import get_old, get_old_count_children, get_old_payment, get_most_frequent_payment

# Папка для сохранения графиков
OUTPUT_DIR = 'static/src'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_old():
    """Построить круговую диаграмму распределения возраста пользователей."""
    data = get_old()
    ages = [row[0] for row in data]
    age_groups = ['0-18', '19-30', '31-45', '46-60', '61+']
    bins = [0, 18, 30, 45, 60, 100]
    age_distribution = [0] * (len(bins) - 1)

    for age in ages:
        for i in range(len(bins) - 1):
            if bins[i] < age <= bins[i + 1]:
                age_distribution[i] += 1
                break

    plt.pie(age_distribution, labels=age_groups, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title('Распределение пользователей по возрасту')
    plt.savefig(os.path.join(OUTPUT_DIR, '1.png'))
    plt.close()

def plot_old_vs_children():
    """Построить график зависимости количества детей от возраста."""
    data = get_old_count_children()
    ages = [row[0] for row in data]
    children = [row[1] for row in data]

    plt.scatter(ages, children, alpha=0.7, color='green')
    plt.title('Количество детей в зависимости от возраста')
    plt.xlabel('Возраст')
    plt.ylabel('Количество детей')
    plt.grid(linestyle='--', alpha=0.7)
    plt.yticks(ticks=[0, 1, 2, 3, 4, 5])
    plt.savefig(os.path.join(OUTPUT_DIR, '2.png'))
    plt.close()

def plot_old_vs_payment():
    """Построить столбчатую диаграмму получения выплат в зависимости от возраста."""
    data = get_old_payment()
    ages = [row[0] for row in data]
    count = [row[1] for row in data]

    plt.hist(count, bins=25, color='purple', alpha=0.7, edgecolor='black')
    plt.title('Получение выплат в зависимости от возраста')
    plt.xlabel('Возраст')
    plt.ylabel('Количество выплат')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(OUTPUT_DIR, '3.png'))
    plt.close()

#plot_old_vs_payment()

def plot_most_frequent_payments():
    """Построить столбчатую диаграмму популярности социальных выплат."""
    frequent_payments_data = get_most_frequent_payment()


    payment_names = [row[0] if len(row[0]) <= 15 else row[0][:25] + '...' for row in frequent_payments_data]
    payment_counts = [row[1] for row in frequent_payments_data]
    colors = np.random.rand(len(payment_counts), 3)  # Генерация случайных цветов

    # Построение столбчатой диаграммы
    bars = plt.bar(range(len(payment_counts)), payment_counts, color=colors, alpha=0.7)

    # Настройка графика
    plt.title('Популярность социальных выплат')
    plt.xlabel('Выплаты')
    plt.ylabel('Количество пользователей')
    plt.yticks(ticks=[a for a in range(max(payment_counts)+1)])
    plt.xticks([])
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Добавление легенды внизу
    plt.legend(bars, payment_names, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
    # Сохранение графика
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '4.png'), bbox_inches='tight')
    plt.close()


def creatiDiagram():
    """Вызов всех функций для построения графиков."""
    plot_old()
    plot_old_vs_children()
    plot_old_vs_payment()
    plot_most_frequent_payments()

    directory = "static/src/"
    files = os.listdir(directory)

    return files




