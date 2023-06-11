import sqlite3


def create_table(db_file : str):
    conn = sqlite3.connect(db_file)  # Установка соединения с базой данных
    conn.execute('''CREATE TABLE IF NOT EXISTS passwords
                    (user_id INT, service TEXT, login TEXT, password TEXT, cipher Boolean)''')  # Создание таблицы passwords
    conn.commit()  # Сохранение изменений в базе данных
    conn.close()  # Закрытие соединения с базой данных
