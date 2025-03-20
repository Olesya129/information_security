import json
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog
)

PASSWORD_FILE = "password.json"


# Читает данные из файла, если файл не существует, создает его, заполняя поля для ADMIN
def load_user():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        users = {
            "ADMIN": {"password": "", "blocked": False, "restricted": False}
        }
        save_user(users)
        return users


# Сохраняет пользователя в файл
def save_user(users):
    with open(PASSWORD_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


# ОКНО АВТОРИЗАЦИИ
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.users = load_user()
        self.attempts_left = 3  # Счетчик попыток ввода
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.username_label = QLabel("Имя пользователя:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)  # замена символа на *
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.authenticate)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addSpacing(10)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addSpacing(20)
        layout.addWidget(self.login_button)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(layout)

    # проверка логина и пароля
    def authenticate(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        users = self.users

        # Проверка, введено ли имя пользователя
        if not username:
            QMessageBox.warning(self, "Ошибка", "Введите имя пользователя.")
            return

        # Проверка наличия пользователя в списке
        if username not in users:
            reply = QMessageBox.question(self, "Ошибка", "Пользователь не найден. Хотите повторить ввод?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.No:
                QApplication.quit()  # Завершение работы программы
            else:
                self.username_input.clear()  # Очистка поля ввода имени
                self.password_input.clear()  # Очистка поля ввода пароля
            return

        # Проверка пароля
        if users[username]["password"] == password:
            if users[username].get("blocked"):
                QMessageBox.warning(self, "Ошибка", "Ваш аккаунт заблокирован.")
            else:
                # Если пароль пустой, запрашиваем установку нового пароля
                if not password and username != "ADMIN":
                    self.set_initial_password(username)
                    return
                self.open_menu(username, users)
        else:
            self.attempts_left -= 1  # Уменьшаем количество оставшихся попыток
            if self.attempts_left > 0:
                QMessageBox.warning(self, "Ошибка",
                                   f"Неверное имя пользователя или пароль. Осталось попыток: {self.attempts_left}")
                self.password_input.clear()  # Очистка поля ввода пароля
            else:
                QMessageBox.critical(self, "Ошибка", "Превышено количество попыток. Программа завершена.")
                QApplication.quit()  # Завершение работы программы

    # Установка начального пароля для нового пользователя
    def set_initial_password(self, username):
        while True:
            new_password, ok = QInputDialog.getText(self, "Установка пароля", "Введите новый пароль:", QLineEdit.Password)
            if not ok:
                return
            confirm_password, ok = QInputDialog.getText(self, "Подтверждение пароля", "Повторите новый пароль:",
                                                       QLineEdit.Password)
            if new_password != confirm_password:
                QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
                continue

            # Проверка ограничений (если они включены)
            if self.users[username].get("restricted", False):
                restrictions = self.users[username].get("password_restrictions", {})
                is_valid, message = self.check_password_restrictions(new_password, restrictions)
                if not is_valid:
                    QMessageBox.warning(self, "Ошибка", message)
                    continue

            # Сохраняем новый пароль
            self.users[username]["password"] = new_password
            save_user(self.users)
            QMessageBox.information(self, " ", "Пароль успешно установлен.")
            self.open_menu(username, self.users)
            break

    # проверка соответствует ли пароль ограничениям
    def check_password_restrictions(self, password, restrictions):
        if restrictions.get("min_length") and len(password) < restrictions["min_length"]:
            return False, f"Пароль должен быть не короче {restrictions['min_length']} символов."
        if restrictions.get("uppercase") and not any(c.isupper() for c in password):
            return False, "Пароль должен содержать хотя бы одну заглавную букву."
        if restrictions.get("special_chars") and not any(c in "!@#$%^&*()_+-=[]{};':\",./<>?`~" for c in password):
            return False, "Пароль должен содержать хотя бы один специальный символ."
        return True, "Пароль соответствует ограничениям."

    # открывает либо меню админа, либо меню пользователя
    def open_menu(self, username, users):
        if username == "ADMIN":
            self.admin_window = AdminWindow(users)
            self.admin_window.show()
            self.close()
        else:
            self.user_window = UserWindow(username, users)
            self.user_window.show()
            self.close()


# ОКНО АДМИНА
class AdminWindow(QWidget):
    def __init__(self, users):
        super().__init__()
        self.users = users
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Меню администратора")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        self.change_password_button = QPushButton("Сменить пароль")
        self.change_password_button.clicked.connect(lambda: self.change_password("ADMIN"))
        self.view_users_button = QPushButton("Список пользователей")
        self.view_users_button.clicked.connect(self.view_users)
        self.add_user_button = QPushButton("Добавить пользователя")
        self.add_user_button.clicked.connect(self.add_user)
        self.block_user_button = QPushButton("Заблокировать пользователя")
        self.block_user_button.clicked.connect(self.block_user)
        self.set_restrictions_button = QPushButton("Изменить ограничения пароля")
        self.set_restrictions_button.clicked.connect(self.set_password_restrictions)
        self.logout_button = QPushButton("Завершение работы")
        self.logout_button.clicked.connect(self.logout)

        layout.addWidget(self.change_password_button)
        layout.addWidget(self.view_users_button)
        layout.addWidget(self.add_user_button)
        layout.addWidget(self.block_user_button)
        layout.addWidget(self.set_restrictions_button)
        layout.addWidget(self.logout_button)

        self.setLayout(layout)

    # смена пароля админа
    def change_password(self, username):
        old_password, ok = QInputDialog.getText(self, "Смена пароля", "Введите старый пароль:", QLineEdit.Password)
        if ok and self.users[username]["password"] == old_password:
            new_password, ok = QInputDialog.getText(self, "Смена пароля", "Введите новый пароль:", QLineEdit.Password)
            if ok:
                confirm_password, ok = QInputDialog.getText(self, "Подтверждение пароля", "Повторите новый пароль:", QLineEdit.Password)
                if ok and new_password == confirm_password:
                    self.users[username]["password"] = new_password
                    save_user(self.users)
                    QMessageBox.information(self, " ", "Пароль успешно изменён.")
                else:
                    QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный пароль.")

    # список пользователей
    def view_users(self):
        user_list = []
        for user, data in self.users.items():
            status = "Заблокирован" if data["blocked"] else "Активен"
            # ограничения на пароль
            restrictions = data.get("password_restrictions", {})
            restriction_text = []
            if restrictions.get("min_length"):
                restriction_text.append(f"\nМинимальная длина пароля:  {restrictions['min_length']}")
            if restrictions.get("uppercase"):
                restriction_text.append("Заглавные буквы")
            if restrictions.get("special_chars"):
                restriction_text.append("Спец. символы")
            restriction_str = ", ".join(restriction_text) if restriction_text else "Нет ограничений"
            user_list.append(f"{user} | Пароль: {data['password']} | {status} | Ограничения: {restriction_str}")

        QMessageBox.information(self, "Список пользователей", "\n".join(user_list))

    # добавление пользователя
    def add_user(self):
        new_username, ok = QInputDialog.getText(self, "Добавление пользователя", "Введите имя нового пользователя:")
        if ok and new_username and new_username not in self.users:
            self.users[new_username] = {
                "password": "",  # пустой пароль
                "blocked": False,
                "restricted": False
            }
            save_user(self.users)

            QMessageBox.information(self, " ", f"Пользователь {new_username} добавлен.")
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь уже существует.")

    # блокировка пользователя
    def block_user(self):
        username, ok = QInputDialog.getText(self, "Блокировка пользователя", "Введите имя пользователя:")
        if ok and username in self.users:
            self.users[username]["blocked"] = True
            save_user(self.users)
            QMessageBox.information(self, " ", f"Пользователь {username} заблокирован.")
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден.")

    # включение или отключение ограничений
    def set_password_restrictions(self):
        username, ok = QInputDialog.getText(self, "Настройки пароля", "Введите имя пользователя:")
        if not ok or username not in self.users:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден.")
            return

        # получаем текущие ограничения
        restrictions = self.users[username].get("password_restrictions", {})
        restriction_text = []
        if restrictions.get("min_length"):
            restriction_text.append(f"Минимальная длина: {restrictions['min_length']}")
        if restrictions.get("uppercase"):
            restriction_text.append("Заглавные буквы")
        if restrictions.get("special_chars"):
            restriction_text.append("Специальные символы")
        restrictions_str = "\n".join(restriction_text) if restriction_text else "Нет ограничений"

        # создаем диалоговое окно с выбором действия
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Управление ограничениями")
        dialog.setText(f"Текущие ограничения для {username}:\n{restrictions_str}\n\nВыберите действие:")

        enable_button = dialog.addButton("Включить", QMessageBox.ActionRole)
        disable_button = dialog.addButton("Отключить", QMessageBox.ActionRole)
        dialog.addButton("Выход", QMessageBox.RejectRole)
        dialog.exec()

        if dialog.clickedButton() == enable_button:  # если выбрано "Включить"
            min_length, ok = QInputDialog.getText(self, "Длина пароля", "Минимальная длина пароля:")
            if not ok:
                return
            min_length = int(min_length)

            uppercase = QMessageBox.question(self, "Ограничение", "Требовать заглавные буквы?") == QMessageBox.Yes
            special_chars = QMessageBox.question(self, "Ограничение",
                                                 "Требовать специальные символы?") == QMessageBox.Yes
            # сохраняем ограничения
            self.users[username]["password_restrictions"] = {
                "min_length": min_length,
                "uppercase": uppercase,
                "special_chars": special_chars
            }
            self.users[username]["restricted"] = True  # сохраняем флаг ограничений
            # сохраняем изменения
            save_user(self.users)
            QMessageBox.information(self, " ", f"Ограничения для {username} включены.")

        elif dialog.clickedButton() == disable_button:  # если выбрано "Отключить"
            if "password_restrictions" in self.users[username]:
                del self.users[username]["password_restrictions"]
            self.users[username]["restricted"] = False  # сохраняем флаг ограничений
            # сохраняем изменения
            save_user(self.users)
            QMessageBox.information(self, "Успех", f"Ограничения для {username} отключены.")

    # выход
    def logout(self):
        self.auth_window = LoginWindow()
        self.auth_window.show()
        self.close()


# ОКНО ПОЛЬЗОВАТЕЛЯ
class UserWindow(QWidget):
    def __init__(self, username, users):
        super().__init__()
        self.username = username
        self.users = users
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Меню пользователя")
        self.setFixedSize(300, 100)
        layout = QVBoxLayout()

        self.change_password_button = QPushButton("Сменить пароль")
        self.change_password_button.clicked.connect(self.change_password)
        self.logout_button = QPushButton("Выйти из аккаунта")
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.change_password_button)
        layout.addWidget(self.logout_button)

        self.setLayout(layout)

    # проверка соответствует ли пароль ограничениям
    def check_password_restrictions(self, password, restrictions):
        if restrictions.get("min_length") and len(password) < restrictions["min_length"]:
            return False, f"Пароль должен быть не короче {restrictions['min_length']} символов."
        if restrictions.get("uppercase") and not any(c.isupper() for c in password):
            return False, "Пароль должен содержать хотя бы одну заглавную букву."
        if restrictions.get("special_chars") and not any(c in "!@#$%^&*()_+-=[]{};':\",./<>?`~" for c in password):
            return False, "Пароль должен содержать хотя бы один специальный символ."
        return True, "Пароль соответствует ограничениям."

    # смена пароля
    def change_password(self):
        old_password, ok = QInputDialog.getText(self, "Смена пароля", "Введите старый пароль:", QLineEdit.Password)
        if ok and self.users[self.username]["password"] == old_password:
            while True:
                new_password, ok = QInputDialog.getText(self, "Смена пароля", "Введите новый пароль:", QLineEdit.Password)
                confirm_password, ok = QInputDialog.getText(self, "Подтверждение пароля", "Повторите новый пароль:", QLineEdit.Password)
                if new_password != confirm_password:
                    QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
                    continue
                # Проверка ограничений (если они включены)
                if self.users[self.username].get("restricted", False):
                    restrictions = self.users[self.username].get("password_restrictions", {})
                    is_valid, message = self.check_password_restrictions(new_password, restrictions)
                    if not is_valid:
                        QMessageBox.warning(self, "Ошибка", message)
                        continue

                # Сохраняем новый пароль
                self.users[self.username]["password"] = new_password
                save_user(self.users)
                QMessageBox.information(self, " ", "Пароль успешно изменён.")
                break
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный пароль.")
    # выход
    def logout(self):
        self.auth_window = LoginWindow()
        self.auth_window.show()
        self.close()


def main():
    app = QApplication([])
    auth_window = LoginWindow()
    auth_window.show()
    app.exec()


if __name__ == "__main__":
    main()
