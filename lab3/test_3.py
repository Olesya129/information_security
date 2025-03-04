import sys
import json
import getpass
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLineEdit, QLabel, QFormLayout, QMessageBox)

USERS_FILE = "users.json"

def load_users():
    """Загрузка пользователей из файла."""
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"ADMIN": {"password": "", "blocked": False, "password_restriction": False}}

def save_users(users):
    """Сохранение пользователей в файл."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

class AuthWindow(QWidget):
    def __init__(self, users):
        super().__init__()
        self.users = users
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Аутентификация")

        self.username_label = QLabel("Имя пользователя:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.authenticate)

        layout = QFormLayout()
        layout.addRow(self.username_label, self.username_input)
        layout.addRow(self.password_label, self.password_input)
        layout.addRow(self.login_button)

        self.setLayout(layout)
        self.show()

    def authenticate(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if username not in self.users:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден.")
            return

        if self.users[username]["blocked"]:
            QMessageBox.warning(self, "Ошибка", "Учетная запись заблокирована.")
            return

        if self.users[username]["password"] == password:
            QMessageBox.information(self, "Успех", "Вход выполнен успешно.")
            if username == "ADMIN":
                self.admin_window = AdminWindow(self.users)
                self.admin_window.show()
                self.close()
            else:
                QMessageBox.information(self, "Информация", "Обычный пользователь. Доступны только смена пароля и выход.")
                self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный пароль.")

class AdminWindow(QWidget):
    def __init__(self, users):
        super().__init__()
        self.users = users
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Меню администратора")

        self.view_button = QPushButton("Просмотр списка пользователей")
        self.view_button.clicked.connect(self.view_users)

        self.add_button = QPushButton("Добавить пользователя")
        self.add_button.clicked.connect(self.add_user)

        self.change_password_button = QPushButton("Сменить пароль администратора")
        self.change_password_button.clicked.connect(self.change_password)

        layout = QVBoxLayout()
        layout.addWidget(self.view_button)
        layout.addWidget(self.add_button)
        layout.addWidget(self.change_password_button)

        self.setLayout(layout)

    def view_users(self):
        users_list = "\n".join(self.users.keys())
        QMessageBox.information(self, "Список пользователей", users_list)

    def add_user(self):
        # Здесь можно добавить окно для добавления пользователя
        pass

    def change_password(self):
        # Здесь можно добавить окно для смены пароля
        pass

def main():
    app = QApplication(sys.argv)
    users = load_users()
    auth_window = AuthWindow(users)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
