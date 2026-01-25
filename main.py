import customtkinter as ctk
from supabase import create_client, Client
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Конфигурация supabase
SUPABASE_URL = "https://pewgzzuazrxxbacllqnb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBld2d6enVhenJ4eGJhY2xscW5iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkzMjU0ODksImV4cCI6MjA4NDkwMTQ4OX0.64Pz3tS0VSTk7y7__mO1h69gRYWXThopFD2udZs022Y"

# Настройки интерфейса
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class PasswordManager:
    """Отвечает за общение с облаком и криптографию."""

    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.cipher = None
        self.user = None  # Здесь будем хранить данные залогиненного юзера

    def generate_key_from_password(self, password: str, email: str) -> bytes:
        """
        Генерирует криптографический ключ на основе пароля.
        Это позволяет не хранить файл ключа. Зная пароль и email,
        мы всегда получим один и тот же ключ шифрования на любом устройстве.
        """
        # Используем email как "соль", чтобы одинаковые пароли у разных людей давали разные ключи
        salt = email.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def login_user(self, email, password):
        """Авторизация через Supabase Auth"""
        try:
            # 1. Логинимся в облако (получаем токен доступа)
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            self.user = response.user

            # 2. Генерируем ключ шифрования из ТОГО ЖЕ пароля
            # (или можно попросить отдельный мастер-пароль, но для удобства берем этот)
            key = self.generate_key_from_password(password, email)
            self.cipher = Fernet(key)
            return True, "Успешно"
        except Exception as e:
            return False, str(e)

    def register_user(self, email, password):
        """Регистрация нового пользователя в облаке"""
        try:
            self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            return True, "Регистрация успешна! Проверьте почту (если включено подтверждение) или входите."
        except Exception as e:
            return False, str(e)

    def encrypt(self, text):
        return self.cipher.encrypt(text.encode()).decode()

    def decrypt(self, text):
        try:
            return self.cipher.decrypt(text.encode()).decode()
        except Exception:
            return "Error"

    def fetch_passwords(self):
        """Скачивает все пароли пользователя из облака"""
        if not self.user:
            return []

        # Supabase сам фильтрует данные по user_id благодаря RLS
        response = self.supabase.table("passwords").select("*").execute()
        return response.data

    def save_entry(self, title, login, password):
        """Шифрует и отправляет в облако"""
        if not self.user:
            return

        data = {
            "user_id": self.user.id,  # Привязываем к юзеру
            "service_name": title,
            "login_enc": self.encrypt(login),
            "password_enc": self.encrypt(password)
        }
        self.supabase.table("passwords").insert(data).execute()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.manager = PasswordManager()

        self.title("Password Manager")
        self.geometry("700x500")
        self.eval('tk::PlaceWindow . center')

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.show_auth_screen()

    def clear_frame(self):
        """Очистка контейнера"""
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_auth_screen(self):
        """Экран авторизации (вход / регистрация)"""
        self.clear_frame()
        frame = ctk.CTkFrame(self.container)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="Вход", font=("Arial", 20)).pack(pady=20, padx=40)

        self.entry_email = ctk.CTkEntry(frame, width=250, placeholder_text="Email")
        self.entry_email.pack(pady=10, padx=40)

        self.entry_pass = ctk.CTkEntry(frame, width=250, show="*", placeholder_text="Master Password")
        self.entry_pass.pack(pady=10, padx=40)

        btn_login = ctk.CTkButton(frame, text="Вход", command=self.do_login)
        btn_login.pack(pady=10)

        btn_reg = ctk.CTkButton(frame, text="Регистрация", fg_color="transparent", border_width=1,
                                command=self.do_register)
        btn_reg.pack(pady=5)

        self.lbl_status = ctk.CTkLabel(frame, text="", text_color="yellow")
        self.lbl_status.pack(pady=10)

    def do_login(self):
        """Логика входа"""
        email = self.entry_email.get()
        pwd = self.entry_pass.get()
        success, msg = self.manager.login_user(email, pwd)
        if success:
            self.show_main_screen()
        else:
            self.lbl_status.configure(text=f"Ошибка: {msg}")

    def do_register(self):
        """Логика регистрации"""
        email = self.entry_email.get()
        pwd = self.entry_pass.get()
        success, msg = self.manager.register_user(email, pwd)
        self.lbl_status.configure(text=msg)

    def show_main_screen(self):
        """Экран с паролями"""
        self.clear_frame()

        # Левая панель
        self.sidebar = ctk.CTkScrollableFrame(self.container, width=200, label_text="Мои сервисы")
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        # Правая панель
        self.content = ctk.CTkFrame(self.container)
        self.content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        add_btn = ctk.CTkButton(self.content, text="+ Добавить", command=self.show_add_form)
        add_btn.pack(pady=10, padx=10, fill="x")

        self.info_frame = ctk.CTkFrame(self.content)
        self.info_frame.pack(fill="both", expand=True, pady=10)

        self.label_title = ctk.CTkLabel(self.info_frame, text="Выберите запись", font=("Arial", 18))
        self.label_title.pack(pady=20)

        self.label_login = ctk.CTkLabel(self.info_frame, text="")
        self.label_login.pack(pady=5)

        self.label_pass = ctk.CTkLabel(self.info_frame, text="")
        self.label_pass.pack(pady=5)

        self.refresh_list()

    def refresh_list(self):
        """Обновление записей"""
        # Очистка старых кнопок из левой панели
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        # Загрузка из облака
        data_list = self.manager.fetch_passwords()

        for entry in data_list:
            service_name = entry['service_name']
            # Передаем весь объект entry, чтобы не искать его снова
            btn = ctk.CTkButton(self.sidebar, text=service_name, fg_color="transparent", border_width=1,
                                command=lambda e=entry: self.show_details(e))
            btn.pack(pady=2, fill="x")

    def show_details(self, entry):
        """Экран показа всей информации по выбранной записи"""
        # Дешифруем полученные данные
        dec_login = self.manager.decrypt(entry['login_enc'])
        dec_pass = self.manager.decrypt(entry['password_enc'])

        self.label_title.configure(text=entry['service_name'])
        self.label_login.configure(text=f"Логин: {dec_login}")
        self.label_pass.configure(text=f"Пароль: {dec_pass}")

    def show_add_form(self):
        """Экран добавления записи"""
        window = ctk.CTkToplevel(self)
        window.geometry("300x350")
        window.title("Добавить")
        window.attributes('-topmost', True)

        ctk.CTkLabel(window, text="Сервис:").pack(pady=5)
        e_title = ctk.CTkEntry(window)
        e_title.pack(pady=5)

        ctk.CTkLabel(window, text="Логин:").pack(pady=5)
        e_login = ctk.CTkEntry(window)
        e_login.pack(pady=5)

        ctk.CTkLabel(window, text="Пароль:").pack(pady=5)
        e_pass = ctk.CTkEntry(window)
        e_pass.pack(pady=5)

        def save():
            if e_title.get() and e_pass.get():
                self.manager.save_entry(e_title.get(), e_login.get(), e_pass.get())
                self.refresh_list()
                window.destroy()

        ctk.CTkButton(window, text="Сохранить", command=save).pack(pady=20)


if __name__ == "__main__":
    app = App()
    app.mainloop()