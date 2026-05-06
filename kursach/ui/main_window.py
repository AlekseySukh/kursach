import tkinter as tk
from tkinter import ttk, messagebox
from core import db_manager
from ui.theme import BLUE_DARK, BLUE_MID, BG, TEXT_DARK, TEXT_LIGHT, WHITE


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Классификация древесин")
        self.geometry("900x650")
        self.resizable(True, True)
        self.configure(bg=BG)

        self._build_header()
        self._build_nav()
        self._build_content()
        self._show_home()

    def _build_header(self):
        hdr = tk.Frame(self, bg=BLUE_MID, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(
            hdr,
            text="Система классификации древесин",
            font=("Segoe UI", 16, "bold"),
            bg=BLUE_MID, fg=WHITE
        ).pack(side="left", padx=20, pady=10)

    def _build_nav(self):
        self.nav = tk.Frame(self, bg=BLUE_DARK, width=200)
        self.nav.pack(side="left", fill="y")
        self.nav.pack_propagate(False)

        self._nav_buttons = {}

        nav_items = [
            ("Главная", "home"),
            ("Определить вид", "classify"),
            ("Редактор знаний", "editor"),
        ]

        tk.Label(
            self.nav, text="МЕНЮ",
            font=("Segoe UI", 9), bg=BLUE_DARK, fg=TEXT_LIGHT
        ).pack(pady=(20, 5), padx=16, anchor="w")

        for label, key in nav_items:
            btn = tk.Button(
                self.nav,
                text=label,
                font=("Segoe UI", 11),
                bg=BLUE_DARK, fg=WHITE,
                activebackground=BLUE_MID, activeforeground=WHITE,
                relief="flat", anchor="w", padx=16, pady=10,
                cursor="hand2",
                command=lambda k=key: self._navigate(k),
            )
            btn.pack(fill="x")
            self._nav_buttons[key] = btn

        tk.Label(
            self.nav, text="БАЗА ДАННЫХ",
            font=("Segoe UI", 9), bg=BLUE_DARK, fg=TEXT_LIGHT
        ).pack(pady=(24, 5), padx=16, anchor="w")

        tk.Button(
            self.nav, text="Сбросить к начальным",
            font=("Segoe UI", 10),
            bg=BLUE_DARK, fg=TEXT_LIGHT,
            activebackground=BLUE_MID, activeforeground=WHITE,
            relief="flat", anchor="w", padx=16, pady=8,
            cursor="hand2",
            command=self._reset_db,
        ).pack(fill="x")

        tk.Button(
            self.nav, text="Очистить БД",
            font=("Segoe UI", 10),
            bg=BLUE_DARK, fg=TEXT_LIGHT,
            activebackground=BLUE_MID, activeforeground=WHITE,
            relief="flat", anchor="w", padx=16, pady=8,
            cursor="hand2",
            command=self._clear_db,
        ).pack(fill="x")

    def _navigate(self, key: str):
        for k, btn in self._nav_buttons.items():
            btn.configure(bg=BLUE_DARK if k != key else BLUE_MID)
        {
            "home": self._show_home,
            "classify": self._show_classify,
            "editor": self._show_editor,
        }[key]()

    def _build_content(self):
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_home(self):
        self._clear_content()
        self._nav_buttons["home"].configure(bg=BLUE_MID)

        frame = tk.Frame(self.content, bg=BG)
        frame.place(relx=0.5, rely=0.45, anchor="center")

        tk.Label(
            frame, text="Добро пожаловать",
            font=("Segoe UI", 20, "bold"), bg=BG, fg=TEXT_DARK
        ).pack(pady=(8, 4))
        tk.Label(
            frame,
            text="Система определяет вид древесины\nпо её физическим характеристикам",
            font=("Segoe UI", 12), bg=BG, fg=TEXT_DARK, justify="center"
        ).pack(pady=(0, 24))

        tk.Button(
            frame, text="Определить вид",
            font=("Segoe UI", 12, "bold"),
            bg=BLUE_MID, fg=WHITE,
            activebackground=BLUE_DARK, activeforeground=WHITE,
            relief="flat", padx=24, pady=10, cursor="hand2",
            command=lambda: self._navigate("classify")
        ).pack()

    def _show_classify(self):
        self._clear_content()
        from ui.input_form import InputForm
        InputForm(self.content).pack(fill="both", expand=True)

    def _show_editor(self):
        self._clear_content()
        from ui.knowledge_editor import KnowledgeEditor
        KnowledgeEditor(self.content).pack(fill="both", expand=True)

    def _reset_db(self):
        if messagebox.askyesno("Сброс БД", "Сбросить базу знаний к начальным данным?\nВсе изменения будут потеряны."):
            db_manager.reset_to_defaults()
            messagebox.showinfo("Готово", "База знаний восстановлена.")

    def _clear_db(self):
        if messagebox.askyesno("Очистка БД", "Очистить всю базу знаний?\nЭто удалит все данные без возможности восстановления."):
            db_manager.clear_db()
            messagebox.showinfo("Готово", "База знаний очищена.")
