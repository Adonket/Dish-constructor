import tkinter as tk
from tkinter import messagebox


class AdaptiveMobileLoginApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Авторизация")
        self.root.configure(bg='#E3F2FD')

        # Получаем размер экрана
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.window_width = max(300, min(int(self.screen_width * 0.8), 500))
        self.window_height = max(500, min(int(self.screen_height * 0.8), 800))

        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.minsize(300, 500)

        self.center_window()

        self.password_visible = False

        # Коэффициенты масштабирования
        self.setup_scaling_factors()

        self.create_widgets()

    def setup_scaling_factors(self):
        "Устанавливает коэффициенты масштабирования на основе размера экрана"
        self.base_width = 360
        self.base_height = 640

        self.width_scale = self.window_width / self.base_width
        self.height_scale = self.window_height / self.base_height
        self.overall_scale = min(self.width_scale, self.height_scale)

    def get_scaled_size(self, base_size):
        "Возвращает масштабированный размер"
        return int(base_size * self.overall_scale)

    def get_scaled_font(self, base_font_size, bold=False):
        "Возвращает масштабированный размер шрифта"
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

        # Прямоугольник-контейнер для формы с эффектом тени
        form_container = tk.Frame(main_frame, bg='white',
                                  relief='flat',
                                  bd=0)
        form_container.pack(fill='both', expand=True)

        shadow_frame = tk.Frame(form_container, bg='#BDBDBD', height=2)
        shadow_frame.pack(fill='x', side='bottom')
        shadow_frame2 = tk.Frame(form_container, bg='#E0E0E0', height=1)
        shadow_frame2.pack(fill='x', side='bottom')

        form_padding = self.get_scaled_size(25)
        form_content = tk.Frame(form_container, bg='white', padx=form_padding, pady=form_padding)
        form_content.pack(expand=True, fill='both')

        title_label = tk.Label(form_content, text="АВТОРИЗАЦИЯ",
                               font=self.get_scaled_font(18, bold=True),
                               bg='white', fg='black')
        title_label.pack(pady=(0, self.get_scaled_size(30)))

        # Поле логина
        login_frame = tk.Frame(form_content, bg='white')
        login_frame.pack(fill='x', pady=self.get_scaled_size(15))

        tk.Label(login_frame, text="Логин:", bg='white', fg='black',
                 font=self.get_scaled_font(14), anchor='w').pack(fill='x')


        login_input_frame = tk.Frame(login_frame, bg='#F5F5F5', relief='solid', bd=1)
        login_input_frame.pack(fill='x', pady=(self.get_scaled_size(5), 0))


        login_emoji_label = tk.Label(login_input_frame, text="👤",
                                     bg='#F5F5F5', fg='#666666',
                                     font=self.get_scaled_font(14))
        login_emoji_label.pack(side='left', padx=(self.get_scaled_size(10), self.get_scaled_size(5)))

        self.login_entry = tk.Entry(login_input_frame,
                                    font=self.get_scaled_font(14),
                                    bg='#F5F5F5', relief='flat', bd=0)
        self.login_entry.pack(side='left', fill='x', expand=True,
                              ipady=self.get_scaled_size(8))

        # Поле пароля с кнопкой показа/скрытия
        password_frame = tk.Frame(form_content, bg='white')
        password_frame.pack(fill='x', pady=self.get_scaled_size(15))

        tk.Label(password_frame, text="Пароль:", bg='white', fg='black',
                 font=self.get_scaled_font(14), anchor='w').pack(fill='x')

        password_input_frame = tk.Frame(password_frame, bg='#F5F5F5', relief='solid', bd=1)
        password_input_frame.pack(fill='x', pady=(self.get_scaled_size(5), 0))


        password_emoji_label = tk.Label(password_input_frame, text="🔒",
                                        bg='#F5F5F5', fg='#666666',
                                        font=self.get_scaled_font(14))
        password_emoji_label.pack(side='left', padx=(self.get_scaled_size(10), self.get_scaled_size(5)))

        self.password_entry = tk.Entry(password_input_frame,
                                       font=self.get_scaled_font(14),
                                       bg='#F5F5F5', relief='flat', bd=0, show='*')
        self.password_entry.pack(side='left', fill='x', expand=True,
                                 ipady=self.get_scaled_size(8))

        # Кнопка показа/скрытия пароля
        self.eye_btn = tk.Button(password_input_frame, text=" ⌣ ",
                                 font=self.get_scaled_font(12),
                                 bg='#F5F5F5', fg='#666666',
                                 relief='flat', bd=0, command=self.toggle_password)
        self.eye_btn.pack(side='right', padx=(self.get_scaled_size(5), self.get_scaled_size(10)))

        # Кнопка Вход
        self.login_btn = tk.Button(form_content, text="Вход",
                                   font=self.get_scaled_font(14, bold=True),
                                   bg='#3F51B5',  # Индиго цвет
                                   fg='white',
                                   relief='flat',
                                   bd=0,
                                   height=1,
                                   command=self.login,
                                   cursor='hand2')

        self.login_btn.pack(fill='x', pady=(self.get_scaled_size(30), 0))

        # Кнопка Регистрация
        self.register_btn = tk.Button(form_content, text="Нет аккаунта? Зарегистрируйтесь!",
                                      font=self.get_scaled_font(12),
                                      bg='white', fg='black',  # Также индиго для consistency
                                      relief='flat', bd=0, command=self.register)
        self.register_btn.pack(fill='x', pady=(self.get_scaled_size(15), 0))

    def toggle_password(self):
        "Переключение видимости пароля"
        if self.password_visible:
            # Скрыть пароль
            self.password_entry.config(show='*')
            self.eye_btn.config(text=" ⌣ ")
            self.password_visible = False
        else:
            # Показать пароль
            self.password_entry.config(show="")
            self.eye_btn.config(text="👁")
            self.password_visible = True

    def login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()

        if not login or not password:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
        else:
            print(f"Логин: {login}")
            print(f"Пароль: {password}")
            messagebox.showinfo("Успех", "Вход выполнен!")

            self.login_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            # Возвращаем пароль в скрытый режим после входа
            if self.password_visible:
                self.toggle_password()

    def register(self):
        messagebox.showinfo("Регистрация", "Переход к регистрации")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AdaptiveMobileLoginApp()
    app.run()