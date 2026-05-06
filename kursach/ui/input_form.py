import tkinter as tk
from tkinter import ttk, messagebox
from core import database as db, solver
from core import ml_predictor
from ui.theme import BLUE_DARK, BLUE_MID, BLUE_LIGHT, BG, TEXT_DARK, TEXT_MID, WHITE


class InputForm(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._input_widgets = {}
        self._method = tk.StringVar(value="expert")
        self._build()

    def _build(self):
        tk.Label(
            self, text="Определение вида древесины",
            font=("Segoe UI", 15, "bold"), bg=BG, fg=TEXT_DARK
        ).pack(anchor="w", padx=24, pady=(20, 0))

        method_frame = tk.Frame(self, bg=BG)
        method_frame.pack(anchor="w", padx=24, pady=(8, 0))

        tk.Label(
            method_frame, text="Метод:",
            font=("Segoe UI", 10), bg=BG, fg=TEXT_MID
        ).pack(side="left", padx=(0, 8))

        self._expert_rb = tk.Radiobutton(
            method_frame, text="Экспертная система",
            variable=self._method, value="expert",
            font=("Segoe UI", 10), bg=BG, fg=TEXT_DARK,
            activebackground=BG, selectcolor=WHITE
        )
        self._expert_rb.pack(side="left", padx=(0, 16))

        ml_rb = tk.Radiobutton(
            method_frame, text="Random Forest",
            variable=self._method, value="ml",
            font=("Segoe UI", 10), bg=BG, fg=TEXT_DARK,
            activebackground=BG, selectcolor=WHITE
        )
        ml_rb.pack(side="left")

        if not ml_predictor.is_available():
            ml_rb.configure(state="disabled")
            tk.Label(
                method_frame, text="(модель не обучена)",
                font=("Segoe UI", 9), bg=BG, fg=TEXT_MID
            ).pack(side="left", padx=4)

        self._warning_frame = tk.Frame(self, bg="#FFF3E0",
                                        highlightbackground="#FFB300", highlightthickness=1)
        self._warning_label = tk.Label(
            self._warning_frame,
            text="",
            font=("Segoe UI", 9), bg="#FFF3E0", fg="#E65100",
            anchor="w", justify="left"
        )
        self._warning_label.pack(anchor="w", padx=10, pady=5)

        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=24, pady=12)

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self._scroll_frame = tk.Frame(canvas, bg=BG)

        self._scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._build_fields()

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(fill="x", padx=24, pady=(0, 16))

        self._classify_btn = tk.Button(
            btn_frame, text="Определить вид",
            font=("Segoe UI", 12, "bold"),
            bg=BLUE_MID, fg=WHITE,
            activebackground=BLUE_DARK, activeforeground=WHITE,
            relief="flat", padx=20, pady=8, cursor="hand2",
            command=self._classify
        )
        self._classify_btn.pack(side="left", padx=(0, 10))

        tk.Button(
            btn_frame, text="Сбросить",
            font=("Segoe UI", 11),
            bg=BLUE_LIGHT, fg=TEXT_DARK,
            activebackground=BLUE_MID, activeforeground=WHITE,
            relief="flat", padx=16, pady=8, cursor="hand2",
            command=self._reset
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btn_frame, text="Посмотреть базу знаний",
            font=("Segoe UI", 11),
            bg=BLUE_LIGHT, fg=TEXT_DARK,
            activebackground=BLUE_MID, activeforeground=WHITE,
            relief="flat", padx=16, pady=8, cursor="hand2",
            command=self._open_kb_viewer
        ).pack(side="left")

        self._check_completeness_and_update()

    def _check_completeness_and_update(self):
        """Проверяет полноту БЗ и блокирует/разблокирует экспертную систему."""
        errors = db.check_completeness()
        if errors:
            self._expert_rb.configure(state="disabled")
            if self._method.get() == "expert":
                if ml_predictor.is_available():
                    self._method.set("ml")
                    self._classify_btn.configure(
                        state="normal", bg=BLUE_MID, cursor="hand2",
                        activebackground=BLUE_DARK
                    )
                else:
                    self._classify_btn.configure(
                        state="disabled", bg="#B0BEC5", cursor="arrow",
                        activebackground="#B0BEC5"
                    )
            else:
                self._classify_btn.configure(
                    state="normal", bg=BLUE_MID, cursor="hand2",
                    activebackground=BLUE_DARK
                )

            text = f"База знаний неполна ({len(errors)} ошибок) - экспертная система недоступна\n"
            text += "Перейдите в Редактор знаний и исправьте ошибки"
            self._warning_label.configure(text=text)
            self._warning_frame.pack(fill="x", padx=24, pady=(0, 4))
        else:
            self._classify_btn.configure(
                state="normal", bg=BLUE_MID, cursor="hand2",
                activebackground=BLUE_DARK
            )
            self._expert_rb.configure(state="normal")
            self._warning_frame.pack_forget()

    def _build_fields(self):
        for w in self._scroll_frame.winfo_children():
            w.destroy()
        self._input_widgets.clear()

        properties = db.get_properties()
        if not properties:
            tk.Label(
                self._scroll_frame,
                text="База знаний пуста. Добавьте свойства в редакторе.",
                font=("Segoe UI", 11), bg=BG, fg=TEXT_MID
            ).pack(pady=20)
            return

        tk.Label(
            self._scroll_frame,
            text="Введите известные значения свойств образца:",
            font=("Segoe UI", 11), bg=BG, fg=TEXT_MID
        ).pack(anchor="w", pady=(8, 12))

        for prop in properties:
            self._build_property_field(prop)

    def _build_property_field(self, prop):
        row = tk.Frame(
            self._scroll_frame, bg=WHITE,
            highlightbackground=BLUE_LIGHT, highlightthickness=1
        )
        row.pack(fill="x", pady=4, ipady=6, ipadx=10)

        tk.Label(
            row, text=prop["name"],
            font=("Segoe UI", 11, "bold"), bg=WHITE, fg=TEXT_DARK,
            width=16, anchor="w"
        ).pack(side="left", padx=(10, 0))

        if prop["type"] == "numeric":
            nr = db.get_numeric_range(prop["id"])
            var = tk.StringVar()
            tk.Entry(
                row, textvariable=var,
                font=("Segoe UI", 11), width=14, relief="solid", bd=1
            ).pack(side="left", padx=8)
            if nr:
                tk.Label(
                    row, text=f"[{nr['min']} – {nr['max']}]",
                    font=("Segoe UI", 9), bg=WHITE, fg=TEXT_MID
                ).pack(side="left")
            self._input_widgets[prop["id"]] = (prop, var)
        else:
            values = db.get_categorical_values(prop["id"])
            var = tk.StringVar(value="не указано")
            cb = ttk.Combobox(
                row, textvariable=var,
                values=["не указано"] + values,
                font=("Segoe UI", 11), width=18, state="readonly"
            )
            cb.pack(side="left", padx=8)
            self._input_widgets[prop["id"]] = (prop, var)

    def _collect_input(self):
        result = {}
        for pid, (prop, var) in self._input_widgets.items():
            raw = var.get().strip()
            if not raw or raw == "не указано":
                continue
            if prop["type"] == "numeric":
                try:
                    result[prop["name"]] = float(raw.replace(",", "."))
                except ValueError:
                    messagebox.showerror(
                        "Ошибка ввода",
                        f'Свойство "{prop["name"]}": введите числовое значение.'
                    )
                    return None
            else:
                result[prop["name"]] = raw
        return result

    def _classify(self):
        self._check_completeness_and_update()

        input_values = self._collect_input()
        if input_values is None:
            return
        if not input_values:
            messagebox.showwarning("Нет данных", "Введите хотя бы одно значение свойства.")
            return

        if self._method.get() == "ml":
            try:
                ml_result = ml_predictor.predict(input_values)
                MLResultWindow(self, ml_result)
            except Exception as e:
                messagebox.showerror("Ошибка модели", str(e))
        else:
            ResultWindow(self, solver.classify(input_values))

    def _reset(self):
        for pid, (prop, var) in self._input_widgets.items():
            var.set("" if prop["type"] == "numeric" else "не указано")

    def _open_kb_viewer(self):
        KnowledgeBaseViewer(self)


class KnowledgeBaseViewer(tk.Toplevel):
    """Окно просмотра базы знаний — все виды и их свойства."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Просмотр базы знаний")
        self.geometry("700x520")
        self.resizable(True, True)
        self.configure(bg=BG)
        self.grab_set()
        self._woods = []
        self._props = []
        self._build()

    def _build(self):
        tk.Label(
            self, text="База знаний",
            font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXT_DARK
        ).pack(pady=(16, 4), padx=20, anchor="w")

        tk.Label(
            self, text="Выберите вид древесины для просмотра характеристик:",
            font=("Segoe UI", 10), bg=BG, fg=TEXT_MID
        ).pack(padx=20, anchor="w", pady=(0, 8))

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=20, pady=(0, 8))

        self._wood_var = tk.StringVar()
        self._woods = db.get_wood_types()
        self._props = db.get_properties()

        wood_names = [w["name"] for w in self._woods]
        self._wood_cb = ttk.Combobox(
            top, textvariable=self._wood_var,
            values=wood_names, state="readonly",
            font=("Segoe UI", 11), width=28
        )
        self._wood_cb.pack(side="left")
        self._wood_cb.bind("<<ComboboxSelected>>", lambda e: self._load_wood())

        if wood_names:
            self._wood_var.set(wood_names[0])

        self._detail_frame = tk.Frame(self, bg=BG)
        self._detail_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        tk.Button(
            self, text="Вернуться к вводу исходных данных",
            font=("Segoe UI", 11),
            bg=BLUE_MID, fg=WHITE,
            activebackground=BLUE_DARK,
            relief="flat", padx=20, pady=6, cursor="hand2",
            command=self.destroy
        ).pack(pady=(0, 16))

        if wood_names:
            self._load_wood()

    def _load_wood(self):
        for w in self._detail_frame.winfo_children():
            w.destroy()

        wood = next((w for w in self._woods if w["name"] == self._wood_var.get()), None)
        if not wood:
            return

        assigned_ids = set(db.get_wood_property_ids(wood["id"]))

        outer = tk.Frame(self._detail_frame, bg=BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        if not assigned_ids:
            tk.Label(
                inner,
                text="Для данного вида не задано ни одного свойства.",
                font=("Segoe UI", 10, "italic"), bg=BG, fg=TEXT_MID
            ).pack(anchor="w", pady=10)
            return

        for prop in self._props:
            card = tk.Frame(
                inner, bg=WHITE,
                highlightbackground=BLUE_LIGHT, highlightthickness=1
            )
            card.pack(fill="x", pady=4, ipady=6, ipadx=10)

            tk.Label(
                card, text=prop["name"],
                font=("Segoe UI", 11, "bold"), bg=WHITE, fg=TEXT_DARK,
                width=16, anchor="w"
            ).pack(side="left", padx=(10, 0))

            if prop["id"] not in assigned_ids:
                tk.Label(
                    card, text="свойство не задано для этого вида",
                    font=("Segoe UI", 10, "italic"), bg=WHITE, fg=TEXT_MID
                ).pack(side="left", padx=8)
                continue

            vals = db.get_property_values(wood["id"], prop["id"])

            if prop["type"] == "numeric":
                text = f"[{vals['min']}; {vals['max']}]" if vals else "значение не задано"
            else:
                colors = vals.get("values", []) if vals else []
                text = ", ".join(colors) if colors else "значение не задано"

            tk.Label(
                card, text=text,
                font=("Segoe UI", 11), bg=WHITE, fg=TEXT_DARK
            ).pack(side="left", padx=8)


class ResultWindow(tk.Toplevel):
    def __init__(self, parent, result):
        super().__init__(parent)
        self.title("Результат классификации")
        self.geometry("620x540")
        self.resizable(True, True)
        self.configure(bg=BG)
        self.grab_set()
        self._result = result
        self._build()

    def _build(self):
        tk.Label(
            self, text="Результат классификации",
            font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXT_DARK
        ).pack(pady=(18, 4), padx=20, anchor="w")

        tk.Label(
            self, text="Метод: экспертная система",
            font=("Segoe UI", 10), bg=BG, fg=TEXT_MID
        ).pack(padx=20, anchor="w", pady=(0, 8))

        suit_frame = tk.LabelFrame(
            self, text="  Подходящие виды  ",
            font=("Segoe UI", 10, "bold"),
            bg=BG, fg="#2E7D32", bd=1
        )
        suit_frame.pack(fill="x", padx=20, pady=(0, 8))

        suitable = self._result["found"]
        if suitable:
            for w in suitable:
                tk.Label(
                    suit_frame, text=w["name"],
                    font=("Segoe UI", 11), bg=BG, fg="#1B5E20"
                ).pack(anchor="w", padx=8, pady=2)
        else:
            tk.Label(
                suit_frame,
                text="Ни один вид не соответствует введённым данным.",
                font=("Segoe UI", 10, "italic"), bg=BG, fg="#B71C1C"
            ).pack(anchor="w", padx=8, pady=4)

        expl_frame = tk.LabelFrame(
            self, text="  Объяснение (исключённые виды)  ",
            font=("Segoe UI", 10, "bold"),
            bg=BG, fg=TEXT_MID, bd=1
        )
        expl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        canvas = tk.Canvas(expl_frame, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(expl_frame, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        for exc in self._result["skipped"]:
            tk.Label(inner, text=exc["name"], font=("Segoe UI", 10, "bold"), bg=BG, fg="#B71C1C").pack(anchor="w", padx=8, pady=(6, 0))
            tk.Label(inner, text=f"    {exc['reason']}", font=("Segoe UI", 9), bg=BG, fg=TEXT_MID).pack(anchor="w", padx=8)

        tk.Button(
            self, text="Закрыть",
            font=("Segoe UI", 11),
            bg=BLUE_MID, fg=WHITE,
            activebackground=BLUE_DARK,
            relief="flat", padx=20, pady=6, cursor="hand2",
            command=self.destroy
        ).pack(pady=(0, 16))


class MLResultWindow(tk.Toplevel):
    def __init__(self, parent, result):
        super().__init__(parent)
        self.title("Результат классификации")
        self.geometry("500x480")
        self.resizable(True, True)
        self.configure(bg=BG)
        self.grab_set()
        self._result = result
        self._build()

    def _build(self):
        tk.Label(
            self, text="Результат классификации",
            font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXT_DARK
        ).pack(pady=(18, 4), padx=20, anchor="w")

        tk.Label(
            self, text="Метод: Random Forest",
            font=("Segoe UI", 10), bg=BG, fg=TEXT_MID
        ).pack(padx=20, anchor="w", pady=(0, 8))

        res_frame = tk.LabelFrame(
            self, text="  Определённый вид  ",
            font=("Segoe UI", 10, "bold"),
            bg=BG, fg="#2E7D32", bd=1
        )
        res_frame.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(
            res_frame, text=self._result["result"],
            font=("Segoe UI", 13, "bold"), bg=BG, fg="#1B5E20"
        ).pack(anchor="w", padx=8, pady=6)

        prob_frame = tk.LabelFrame(
            self, text="  Вероятности (топ 5)  ",
            font=("Segoe UI", 10, "bold"),
            bg=BG, fg=TEXT_MID, bd=1
        )
        prob_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        for name, prob in self._result["probabilities"][:5]:
            row = tk.Frame(prob_frame, bg=BG)
            row.pack(fill="x", padx=8, pady=3)

            tk.Label(
                row, text=name,
                font=("Segoe UI", 10), bg=BG, fg=TEXT_DARK,
                width=22, anchor="w"
            ).pack(side="left")

            bar_bg = tk.Frame(row, bg="#E0E0E0", height=16, width=160)
            bar_bg.pack(side="left", padx=(4, 8))
            bar_bg.pack_propagate(False)

            bar = tk.Frame(bar_bg, bg=BLUE_MID, height=16, width=int(prob * 160))
            bar.place(x=0, y=0)

            tk.Label(
                row, text=f"{prob * 100:.1f}%",
                font=("Segoe UI", 10), bg=BG, fg=TEXT_MID
            ).pack(side="left")

        tk.Button(
            self, text="Закрыть",
            font=("Segoe UI", 11),
            bg=BLUE_MID, fg=WHITE,
            activebackground=BLUE_DARK,
            relief="flat", padx=20, pady=6, cursor="hand2",
            command=self.destroy
        ).pack(pady=(0, 16))