import sqlite3
from dataBase.user import create_table
from cipher.cipher import xor_encrypt_decrypt

class DBAPI:
    def __init__(self, db_file : str):
        create_table(db_file)
        self.db_file = db_file
        self.conn = None  # Инициализация переменной для хранения соединения с базой данных


    def connect(self):
        self.conn = sqlite3.connect(self.db_file)  # Установка соединения с базой данных


    def disconnect(self):
        self.conn.close()  # Закрытие соединения с базой данных


    def add_password(self, user_id : int, service : str, login : str, password :str, key : str):
        self.connect()  # Установка соединения с базой данных

        password = xor_encrypt_decrypt(password, key)
        # Выполнение операции добавления пароля в базу данных
        self.conn.execute("INSERT INTO passwords (user_id, service, login, password, cipher) VALUES (?, ?, ?, ?, ?)",
             (user_id, service, login, password, (key != "")))

        self.conn.commit()  # Сохранение изменений в базе данных
        self.disconnect()  # Закрытие соединения с базой данных


    def get_password(self, user_id : int, service : str, login : str):
        self.connect()

        # Выполнение операции получения пароля из базы данных
        cursor = self.conn.cursor()
        cursor.execute("SELECT login, password, cipher FROM passwords WHERE user_id=? AND service=? AND login=?",
                    (user_id, service, login))
        result = cursor.fetchone()
        self.disconnect()
        return result
    
    def update_password(self, user_id : int, service : str, login : str, password : str, key : str):
        self.connect()

        self.delete_password(user_id, service, login)
        self.add_password(user_id, service, login, password, key)

        self.disconnect()


    def delete_password(self, user_id : int, service : str, login : str):
        self.connect()  # Установка соединения с базой данных
        # Выполнение операции удаления пароля из базы данных
        self.conn.execute("DELETE FROM passwords WHERE user_id=? AND service=? AND login=?",
                          (user_id, service, login))
        self.conn.commit()  # Сохранение изменений в базе данных
        self.disconnect()  # Закрытие соединения с базой данных