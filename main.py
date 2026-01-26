import customtkinter as ctk
from supabase import create_client, Client
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from deep_translator import GoogleTranslator
import json


# Конфигурация supabase
SUPABASE_URL = "https://pewgzzuazrxxbacllqnb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBld2d6enVhenJ4eGJhY2xscW5iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkzMjU0ODksImV4cCI6MjA4NDkwMTQ4OX0.64Pz3tS0VSTk7y7__mO1h69gRYWXThopFD2udZs022Y"

# Настройки интерфейса
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class CredentialsManager:
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
        if text:
            return self.cipher.encrypt(text.encode()).decode()
        else:
            return ""

    def decrypt(self, text):
        if not text:
            return ""
        try:
            return self.cipher.decrypt(text.encode()).decode()
        except Exception:
            return ""

    def fetch_credentials(self):
        """Скачивает все учетные данные пользователя из облака"""
        if not self.user:
            return []

        # Supabase сам фильтрует данные по user_id благодаря RLS
        response = self.supabase.table("credentials").select("*").execute()
        return response.data

    def save_entry(self, title, login, password, email="",
                   phone_number="", url="", secret_question="", extra_data=None):
        """Шифрует учетные данные и отправляет их в бд"""
        if not self.user:
            return

        if extra_data is None:
            extra_data = []

        extra_json = json.dumps(extra_data, ensure_ascii=False)

        data = {
            "user_id": self.user.id,  # Привязываем к юзеру
            "service_name": title,
            "login_enc": self.encrypt(login),
            "password_enc": self.encrypt(password),
            "email_enc": self.encrypt(email),
            "phone_number_enc": self.encrypt(phone_number),
            "url": url,
            "secret_question_enc": self.encrypt(secret_question),
            "extra_data_enc": self.encrypt(extra_json)
        }
        self.supabase.table("credentials").insert(data).execute()


class Main(ctk.CTk):
    """Корневое окно - Screen Manager"""

    def __init__(self):
        super().__init__()
        self.title("Password Manager")
        self.geometry("800x600")

        self.manager = CredentialsManager()

        # Контейнер для смены экранов
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # Текущий экран (AuthScreen или MainScreen)
        self.current_screen = None

        # При старте всегда показываем экран авторизации
        self.show_auth_screen()

    def clear_screen(self):
        """
        Полностью очищает контейнер.
        Нужно, чтобы старый экран не оставался в памяти.
        """
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None

    def show_auth_screen(self):
        """
        Показывает экран входа / регистрации
        """
        self.clear_screen()

        self.current_screen = AuthScreen(
            master=self.container,
            manager=self.manager,
            on_success=self.show_main_screen  # callback
        )
        self.current_screen.pack(fill="both", expand=True)

    def show_main_screen(self):
        """
        Показывает основной экран приложения
        """
        self.clear_screen()

        self.current_screen = MainScreen(
            master=self.container,
            manager=self.manager
        )
        self.current_screen.pack(fill="both", expand=True)


class AuthScreen(ctk.CTkFrame):
    """Экран авторизации и регистрации"""

    def __init__(self, master, manager, on_success):
        super().__init__(master)
        self.manager = manager
        self.on_success = on_success

        # Центрируем содержимое
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.center_frame, text="Вход", font=("Roboto", 25)).pack(pady=20)

        # Поля для входа/регистрации в CredentialsManager

        self.entry_email = ctk.CTkEntry(self.center_frame, width=250, placeholder_text="Email")
        self.entry_email.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(self.center_frame, width=250, show="*", placeholder_text="Master Password")
        self.entry_pass.pack(pady=10)

        btn_login = ctk.CTkButton(self.center_frame, text="Вход", command=self.do_login)
        btn_login.pack(pady=10)

        btn_reg = ctk.CTkButton(self.center_frame, text="Регистрация", fg_color="transparent", border_width=1,
                                command=self.do_register)
        btn_reg.pack(pady=5)

        self.lbl_status = ctk.CTkLabel(self.center_frame, text="", text_color="yellow")
        self.lbl_status.pack(pady=10)

    def do_login(self):
        email = self.entry_email.get()
        pwd = self.entry_pass.get()
        success, msg = self.manager.login_user(email, pwd)
        if success:
            self.on_success()  # Переключаем экран через callback
        else:
            self.lbl_status.configure(text=f"Ошибка: {msg}")

    def do_register(self):
        email = self.entry_email.get()
        pwd = self.entry_pass.get()
        success, msg = self.manager.register_user(email, pwd)
        self.lbl_status.configure(text=msg)


class MainScreen(ctk.CTkFrame):
    """Основной экран с записями"""

    def __init__(self, master, manager):
        super().__init__(master)
        self.manager = manager
        self.new_write_window = None

        # Левая панель (Список)
        self.sidebar = ctk.CTkScrollableFrame(self, width=200, label_text="Мои сервисы")
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        # Правая панель (Контент)
        self.content = ctk.CTkFrame(self)
        self.content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Кнопка добавления
        add_btn = ctk.CTkButton(self.content, text="+ Добавить", command=self.open_new_write_window)
        add_btn.pack(pady=10, padx=10, fill="x")

        # Инфо-фрейм (здесь создаем виджеты ОДИН раз)
        self.info_frame = ctk.CTkFrame(self.content)
        self.info_frame.pack(fill="both", expand=True, pady=10, padx=10)

        # Инициализация виджетов отображения

        # Заголовок записи
        self.lbl_title = ctk.CTkLabel(self.info_frame, text="Выберите запись", font=("Arial", 20, "bold"))
        self.lbl_title.pack(pady=(20, 10))

        # URL
        self.lbl_url = ctk.CTkButton(self.info_frame, text="", fg_color="transparent", text_color=("blue", "cyan"),
                                     hover=False, cursor="hand2")
        # Не пакуем сразу, сделаем это в render_entry при наличии

        # Основные данные
        self.lbl_login = ctk.CTkLabel(self.info_frame, text="", font=("Arial", 14))
        self.lbl_login.pack(pady=5)

        self.lbl_pass = ctk.CTkLabel(self.info_frame, text="", font=("Arial", 14))
        self.lbl_pass.pack(pady=5)

        # Доп данные (будем скрывать/показывать)
        self.lbl_email = ctk.CTkLabel(self.info_frame, text="")
        self.lbl_phone = ctk.CTkLabel(self.info_frame, text="")
        self.lbl_secret = ctk.CTkLabel(self.info_frame, text="")

        # Блок для произвольных полей
        self.lbl_extra_content = ctk.CTkLabel(self.info_frame, text="", justify="left")

        # Загружаем список при старте
        self.refresh_list()

    def refresh_list(self):
        """Обновление кнопок в сайдбаре"""
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        data_list = self.manager.fetch_credentials()

        for entry in data_list:
            btn = ctk.CTkButton(self.sidebar,
                                text=entry['service_name'],
                                fg_color="transparent",
                                border_width=1,
                                anchor="w",
                                command=lambda e=entry: self.render_entry(e))
            btn.pack(pady=2, fill="x")

    def render_entry(self, entry):
        """Отображение данных без пересоздания виджетов"""

        # 1. Дешифровка
        dec_login = self.manager.decrypt(entry['login_enc'])
        dec_pass = self.manager.decrypt(entry['password_enc'])
        dec_email = self.manager.decrypt(entry['email_enc'])
        dec_phone = self.manager.decrypt(entry['phone_number_enc'])
        dec_secret = self.manager.decrypt(entry['secret_question_enc'])

        # Обработка JSON Extra
        try:
            dec_extra_data = json.loads(self.manager.decrypt(entry['extra_data_enc']))
            if not isinstance(dec_extra_data, list): dec_extra_data = []
        except:
            dec_extra_data = []

        # 2. Обновление UI
        self.lbl_title.configure(text=entry['service_name'])
        self.lbl_login.configure(text=f"Логин:  {dec_login}")
        self.lbl_pass.configure(text=f"Пароль: {dec_pass}")

        # Сначала скрываем всё
        self.lbl_email.pack_forget()
        self.lbl_phone.pack_forget()
        self.lbl_secret.pack_forget()
        self.lbl_extra_content.pack_forget()
        self.lbl_url.pack_forget()

        # URL
        if entry['url']:
            self.lbl_url.configure(text=entry['url'])
            self.lbl_url.pack(pady=2)

        # Email
        if dec_email:
            self.lbl_email.configure(text=f"Email: {dec_email}")
            self.lbl_email.pack(pady=2)

        # Phone
        if dec_phone:
            self.lbl_phone.configure(text=f"Телефон: {dec_phone}")
            self.lbl_phone.pack(pady=2)

        # Secret Question
        if dec_secret:
            self.lbl_secret.configure(text=f"Секретный вопрос: {dec_secret}")
            self.lbl_secret.pack(pady=2)

        # Extra
        if dec_extra_data:
            extra_text = "\n".join([f"{k}: {v}" for k, v in dec_extra_data if v])
            self.lbl_extra_content.configure(text=extra_text)
            self.lbl_extra_content.pack(pady=2)

    def open_new_write_window(self):
        if self.new_write_window is None or not self.new_write_window.winfo_exists():
            self.new_write_window = NewWrite(manager=self.manager, parent_screen=self)
        else:
            self.new_write_window.focus()


class NewWrite(ctk.CTkToplevel):
    """Окно добавления записи"""

    def __init__(self, manager, parent_screen):
        super().__init__()
        self.manager = manager
        self.parent_screen = parent_screen  # Ссылка на MainScreen для обновления списка

        self.geometry("400x450")  # Чуть увеличим размер
        self.title("Добавить запись")
        self.attributes('-topmost', True)

        # Фрейм Меню (Верхняя часть)
        # Он создается один раз и не очищается
        self.menu_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.menu_frame.pack(side="top", fill="x", padx=5, pady=10)

        # Кнопки меню в один ряд (side="left")
        self.btn_login = ctk.CTkButton(
            self.menu_frame,
            text="Вход в систему",
            width=150,
            command=self.show_add_login
        )
        self.btn_login.pack(side="left", expand=True)

        self.btn_card = ctk.CTkButton(
            self.menu_frame,
            text="Банковская карта",
            width=150,
            command=self.show_add_card
        )
        self.btn_card.pack(side="left", expand=True)

        # Фрейм Контента
        # Сюда будем добавлять поля ввода. Его мы будем очищать.
        self.content_frame = ctk.CTkScrollableFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Список для хранения ссылок на динамически созданные поля ввода
        self.dynamic_entries = []

        # Сразу открываем первую вкладку по умолчанию
        self.show_add_login()

    def clear_content(self):
        """Очистка только области контента, меню остается нетронутым"""
        self.dynamic_entries = []
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_add_login(self):
        """Экран добавления входа в систему"""
        self.clear_content()  # Чистим только нижний фрейм

        # Меняем цвета кнопок для визуального эффекта (активная/неактивная)
        self.btn_login.configure(fg_color=("gray75", "gray30"))
        self.btn_card.configure(fg_color="transparent", border_width=1)

        # Все виджеты добавляем в self.content_frame
        ctk.CTkLabel(self.content_frame, text="Заголовок сервиса:", anchor="w").pack(fill="x", padx=20)
        e_title = ctk.CTkEntry(self.content_frame)
        e_title.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="Логин:", anchor="w").pack(fill="x", padx=20)
        e_login = ctk.CTkEntry(self.content_frame)
        e_login.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="Пароль:", anchor="w").pack(fill="x", padx=20)
        e_pass = ctk.CTkEntry(self.content_frame)
        e_pass.pack(fill="x", padx=20, pady=5)

        # Фрейм для строки добавления (Выпадающий список + Кнопка)
        add_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_frame.pack(pady=10)

        # Варианты полей
        field_options = ["Ссылка (URL)", "Заметки", "Телефон", "Email", "Дата рождения", "Секретный вопрос"]
        combo_fields = ctk.CTkComboBox(add_frame, values=field_options, width=200)
        combo_fields.pack(side="left", padx=5, pady=5, fill="x")

        def add_field():
            """Функция добавляет виджеты на экран"""
            field_type = combo_fields.get()

            lbl = ctk.CTkLabel(self.content_frame, text=f"{field_type}:", anchor="w")
            lbl.pack(fill="x", padx=10)

            entry = ctk.CTkEntry(self.content_frame)
            entry.pack(fill="x", padx=10, pady=2)

            # Сохраняем entry и название поля, чтобы потом забрать данные
            self.dynamic_entries.append({"type": field_type, "widget": entry})

        btn_add = ctk.CTkButton(add_frame, text="+ Добавить поле", width=40, command=add_field)
        btn_add.pack(side="left")

        ctk.CTkButton(self.content_frame,
                      text="Добавить свое поле",
                      fg_color="transparent", border_width=1,
                      command=self.show_add_entry).pack(pady=10, side="bottom", anchor="s")

        # Сохранение
        def save():
            if e_title.get() and e_pass.get():
                extra_data = []
                e_email, e_phone_number, e_url, e_secret_question = "", "", "", ""
                for item in self.dynamic_entries:
                    val = item["widget"].get()
                    match item["type"]:
                        case "Email": e_email = val.strip()
                        case "Телефон": e_phone_number = val.strip()
                        case "Ссылка (URL)": e_url = val.strip()
                        case "Секретный вопрос": e_secret_question = val.strip()
                        case _:  extra_data.append((item['type'], val))

                self.manager.save_entry(e_title.get().strip(), e_login.get().strip(), e_pass.get().strip(),
                                             e_email, e_phone_number, e_url, e_secret_question, extra_data)
                self.parent_screen.refresh_list()
                self.destroy()

        ctk.CTkButton(self.content_frame,
                      text="Сохранить",
                      command=save).pack(pady=20, side="bottom")

    def show_add_card(self):
        """Экран добавления банковской карты"""
        self.clear_content()  # Чистим только фрейм посередине
        self.btn_card.configure(fg_color=("gray75", "gray30"))
        self.btn_login.configure(fg_color="transparent", border_width=1)

        ctk.CTkLabel(self.content_frame, text="Название банка:").pack(pady=5)
        e_title = ctk.CTkEntry(self.content_frame)
        e_title.pack(pady=5)

        # выпадающий список
        ctk.CTkLabel(self.content_frame, text="Тип карты:").pack(pady=5)
        e_card_num = ctk.CTkEntry(self.content_frame)
        e_card_num.pack(pady=5)

        ctk.CTkLabel(self.content_frame, text="Номер карты:").pack(pady=5)
        e_card_num = ctk.CTkEntry(self.content_frame)
        e_card_num.pack(pady=5)

        ctk.CTkLabel(self.content_frame, text="CVC/CVV:").pack(pady=5)
        e_cvc = ctk.CTkEntry(self.content_frame, width=80)
        e_cvc.pack(pady=5)

        ctk.CTkLabel(self.content_frame, text="Пин-код:").pack(pady=5)
        e_pin = ctk.CTkEntry(self.content_frame, show="*")
        e_pin.pack(pady=5)

        def save_card():
            # Тут пока сохраняем как обычную запись, можно потом расширить структуру БД
            full_info = f"Карта: {e_card_num.get()} | CVC: {e_cvc.get()} | PIN: {e_pin.get()}"
            if e_title.get():
                self.manager.save_entry(e_title.get(), "BANK_CARD", full_info)
                self.parent_screen.refresh_list()
                self.destroy()

        ctk.CTkButton(self.content_frame,
                      text="Сохранить",
                      command=save_card).pack(pady=20, side="bottom")

    def show_add_entry(self):
        window = ctk.CTkToplevel(self)
        window.geometry("300x200")
        window.title("Добавить поле")
        window.attributes('-topmost', True)

        ctk.CTkLabel(window, text="Эта функция пока в разработке").pack(pady=40)

if __name__ == "__main__":
    app = Main()
    app.mainloop()
