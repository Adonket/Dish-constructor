import tkinter as tk
from tkinter import messagebox
import os

# Файл для хранения данных пользователей
USERS_FILE = "users.txt"

class AdaptiveMobileRegistrationApp:
    def __init__(self, master):
        self.master = master
        self.root = tk.Toplevel(master)
        self.root.title("Регистрация")
        self.root.configure(bg='#E3F2FD')

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.window_width = max(300, min(int(self.screen_width * 0.8), 500))
        self.window_height = max(500, min(int(self.screen_height * 0.8), 800))

        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.minsize(300, 500)

        self.center_window()
        self.password_visible = False
        self.setup_scaling_factors()
        self.create_widgets()
        self.root.grab_set()

    def setup_scaling_factors(self):
        self.base_width = 360
        self.base_height = 640

        self.width_scale = self.window_width / self.base_width
        self.height_scale = self.window_height / self.base_height
        self.overall_scale = min(self.width_scale, self.height_scale)

    def get_scaled_size(self, base_size):
        return int(base_size * self.overall_scale)

    def get_scaled_font(self, base_font_size, bold=False):
        font_size = int(base_font_size * self.overall_scale)
        if bold:
            return ('Arial', font_size, 'bold')
        else:
            return ('Arial', font_size)

    def center_window(self):
        "Центрирование окна на экране"
        x = (self.screen_width - self.window_width) // 2
        y = (self.screen_height - self.window_height) // 2
        self.root.geometry(f'+{x}+{y}')

    def create_widgets(self):
        # Основной контейнер
        main_frame = tk.Frame(self.root, bg='#E3F2FD')
        main_frame.pack(expand=True, fill='both', padx=self.get_scaled_size(20), pady=self.get_scaled_size(50))


        form_container = tk.Frame(main_frame, bg='white', relief='flat', bd=0)
        form_container.pack(fill='both', expand=True)

        shadow_frame = tk.Frame(form_container, bg='#BDBDBD', height=2)
        shadow_frame.pack(fill='x', side='bottom')
        shadow_frame2 = tk.Frame(form_container, bg='#E0E0E0', height=1)
        shadow_frame2.pack(fill='x', side='bottom')

        form_padding = self.get_scaled_size(25)
        form_content = tk.Frame(form_container, bg='white', padx=form_padding, pady=form_padding)
        form_content.pack(expand=True, fill='both')

        title_label = tk.Label(form_content, text="РЕГИСТРАЦИЯ",
                               font=self.get_scaled_font(18, bold=True),
                               bg='white', fg='black')
        title_label.pack(pady=(0, self.get_scaled_size(30)))

        self.create_input_field(form_content, "Логин:", "👤", self.get_scaled_font(14), self.get_scaled_size, 'login')
        self.create_input_field(form_content, "Пароль:", "🔒", self.get_scaled_font(14), self.get_scaled_size, 'password', show='*')
        self.create_input_field(form_content, "Подтверждение пароля:", "🔒", self.get_scaled_font(14), self.get_scaled_size, 'confirm_password', show='*')

        self.register_btn = tk.Button(form_content, text="Зарегистрироваться",
                                   font=self.get_scaled_font(14, bold=True),
                                   bg='#3F51B5',
                                   fg='white',
                                   relief='flat',
                                   bd=0,
                                   height=1,
                                   command=self.register_user,
                                   cursor='hand2')

        self.register_btn.pack(fill='x', pady=(self.get_scaled_size(30), 0))

        self.back_btn = tk.Button(form_content, text="Уже есть аккаунт? Войти!",
                                      font=self.get_scaled_font(12),
                                      bg='white', fg='black',
                                      relief='flat', bd=0, command=self.return_login)
        self.back_btn.pack(fill='x', pady=(self.get_scaled_size(15), 0))

    def create_input_field(self, parent, label_text, emoji, font, size_func, attr_name, show=None):
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=size_func(15))

        tk.Label(frame, text=label_text, bg='white', fg='black',
                 font=font, anchor='w').pack(fill='x')

        input_frame = tk.Frame(frame, bg='#F5F5F5', relief='solid', bd=1)
        input_frame.pack(fill='x', pady=(size_func(5), 0))

        emoji_label = tk.Label(input_frame, text=emoji,
                                     bg='#F5F5F5', fg='#666666',
                                     font=font)
        emoji_label.pack(side='left', padx=(size_func(10), size_func(5)))

        entry = tk.Entry(input_frame,
                         font=font,
                         bg='#F5F5F5', relief='flat', bd=0, show=show)
        entry.pack(side='left', fill='x', expand=True, ipady=size_func(8))

        setattr(self, f'{attr_name}_entry', entry)

        if 'password' in attr_name:
            self.eye_btn = tk.Button(input_frame, text=" ⌣ ",
                                     font=self.get_scaled_font(12),
                                     bg='#F5F5F5', fg='#666666',
                                     relief='flat', bd=0,
                                     command=lambda: self.toggle_password(entry, self.eye_btn))
            self.eye_btn.pack(side='right', padx=(size_func(5), size_func(10)))

    def toggle_password(self, entry, button):
        current_show = entry.cget('show')
        if current_show == '*':
            entry.config(show="")
            button.config(text="👁")
        else:
            entry.config(show='*')
            button.config(text=" ⌣ ")


    def is_login_taken(self, login):
        if not os.path.exists(USERS_FILE):
            return False
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                stored_login = line.strip().split(':')[0]
                if stored_login == login:
                    return True
        return False

    def register_user(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not login or not password or not confirm_password:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        if password != confirm_password:
            messagebox.showerror("Ошибка", "Пароли не совпадают!")
            return

        if len(password) < 4:
            messagebox.showerror("Ошибка", "Пароль должен содержать не менее 4 символов.")
            return

        if self.is_login_taken(login):
            messagebox.showerror("Ошибка", f"Логин '{login}' уже занят!")
            return

        # Сохранение данных в файл
        try:
            with open(USERS_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{login}:{password}\n")

            messagebox.showinfo("Успех", f"Пользователь '{login}' успешно зарегистрирован!")
            self.return_login()

            try:
                self.master.login_entry.delete(0, tk.END)
                self.master.login_entry.insert(0, login)
            except AttributeError:
                pass

        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")

    def return_login(self):
        self.root.destroy()
        self.master.deiconify()