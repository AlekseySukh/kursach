import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from core import database as db
from ui.theme import BLUE_DARK, BLUE_MID, BLUE_LIGHT, BG, TEXT_DARK, TEXT_MID, WHITE


class KnowledgeEditor(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        tk.Label(
            self, text="Редактор базы знаний",
            font=("Segoe UI", 15, "bold"), bg=BG, fg=TEXT_DARK
        ).pack(anchor="w", padx=24, pady=(16, 8))

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self._tab_woods = WoodTypesTab(nb)
        self._tab_props = PropertiesTab(nb)
        self._tab_vals = PossibleValuesTab(nb)
        self._tab_desc = WoodPropertiesTab(nb)
        self._tab_kvals = KnowledgeValuesTab(nb)
        self._tab_check = CompletenessTab(nb)

        nb.add(self._tab_woods, text="  Виды древесины  ")
        nb.add(self._tab_props, text="  Свойства  ")
        nb.add(self._tab_vals, text="  Возможные значения  ")
        nb.add(self._tab_desc, text="  Описание свойств вида  ")
        nb.add(self._tab_kvals, text="  Значение для вида  ")
        nb.add(self._tab_check, text="  Проверка полноты  ")

        nb.bind("<<NotebookTabChanged>>", lambda e: self._on_tab_change(nb))

    def _on_tab_change(self, nb):
        tab = nb.nametowidget(nb.select())
        if hasattr(tab, "refresh"):
            tab.refresh()


def _frame(parent, **kw):
    return tk.Frame(parent, bg=BG, **kw)

def _label(parent, text, bold=False, color=None):
    font = ("Segoe UI", 10, "bold") if bold else ("Segoe UI", 10)
    return tk.Label(parent, text=text, font=font, bg=BG, fg=color or TEXT_DARK)

def _btn(parent, text, command, primary=True):
    bg = BLUE_MID if primary else BLUE_LIGHT
    fg = WHITE if primary else TEXT_DARK
    abg = BLUE_DARK if primary else BLUE_MID
    return tk.Button(
        parent, text=text, command=command,
        font=("Segoe UI", 10), bg=bg, fg=fg,
        activebackground=abg, activeforeground=WHITE,
        relief="flat", padx=12, pady=5, cursor="hand2"
    )

def _listbox(parent, height=14):
    return tk.Listbox(
        parent, font=("Segoe UI", 10), height=height,
        selectmode="single", relief="solid", bd=1,
        bg=WHITE, fg=TEXT_DARK,
        selectbackground=BLUE_MID, selectforeground=WHITE
    )


class WoodTypesTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        _label(self, "Список видов древесины:", bold=True).pack(anchor="w", padx=12, pady=(10, 4))

        mid = _frame(self)
        mid.pack(fill="both", expand=True, padx=12)

        self._lb = _listbox(mid)
        self._lb.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(mid, command=self._lb.yview)
        sb.pack(side="left", fill="y")
        self._lb.configure(yscrollcommand=sb.set)

        input_row = _frame(self)
        input_row.pack(fill="x", padx=12, pady=(8, 4))
        self._name_var = tk.StringVar()
        tk.Entry(input_row, textvariable=self._name_var, width=24,
                 font=("Segoe UI", 10), relief="solid", bd=1).pack(side="left", padx=(0, 8))
        _btn(input_row, "Добавить", self._add).pack(side="left")

        btn_row = _frame(self)
        btn_row.pack(fill="x", padx=12, pady=(0, 8))
        _btn(btn_row, "Удалить выбранное", self._delete, primary=False).pack(side="left")

        self.refresh()

    def refresh(self):
        self._lb.delete(0, "end")
        self._woods = db.get_wood_types()
        for wood in self._woods:
            self._lb.insert("end", f"  {wood['name']}")

    def _add(self):
        name = self._name_var.get().strip()
        if not name:
            return
        try:
            db.add_wood_type(name)
            self._name_var.set("")
            self.refresh()
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def _delete(self):
        sel = self._lb.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите вид для удаления.")
            return
        wood = self._woods[sel[0]]
        if messagebox.askyesno("Удаление", f'Удалить "{wood["name"]}"? Это удалит все связанные знания.'):
            db.delete_wood_type(wood["id"])
            self.refresh()


class PropertiesTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        _label(self, "Список свойств:", bold=True).pack(anchor="w", padx=12, pady=(10, 4))

        mid = _frame(self)
        mid.pack(fill="both", expand=True, padx=12)

        self._lb = _listbox(mid)
        self._lb.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(mid, command=self._lb.yview)
        sb.pack(side="left", fill="y")
        self._lb.configure(yscrollcommand=sb.set)

        input_row = _frame(self)
        input_row.pack(fill="x", padx=12, pady=(8, 4))
        self._name_var = tk.StringVar()
        tk.Entry(input_row, textvariable=self._name_var, width=24,
                 font=("Segoe UI", 10), relief="solid", bd=1).pack(side="left", padx=(0, 8))
        _btn(input_row, "Добавить числовое", lambda: self._add("numeric")).pack(side="left", padx=(0, 8))
        _btn(input_row, "Добавить категориальное", lambda: self._add("categorical")).pack(side="left")

        btn_row = _frame(self)
        btn_row.pack(fill="x", padx=12, pady=(0, 8))
        _btn(btn_row, "Удалить выбранное", self._delete, primary=False).pack(side="left")

        self.refresh()

    def refresh(self):
        self._lb.delete(0, "end")
        self._props = db.get_properties()
        for prop in self._props:
            kind = "числовое" if prop["type"] == "numeric" else "категориальное"
            self._lb.insert("end", f"  {prop['name']}  [{kind}]")

    def _add(self, prop_type):
        name = self._name_var.get().strip()
        if not name:
            return
        try:
            db.add_property(name, prop_type)
            self._name_var.set("")
            self.refresh()
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def _delete(self):
        sel = self._lb.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите свойство для удаления.")
            return
        prop = self._props[sel[0]]
        if messagebox.askyesno("Удаление", f'Удалить свойство "{prop["name"]}"? Все значения будут удалены.'):
            db.delete_property(prop["id"])
            self.refresh()


class PossibleValuesTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._props = []
        self._values = []
        self._build()

    def _build(self):
        top = _frame(self)
        top.pack(fill="x", padx=12, pady=(10, 4))
        _label(top, "Свойство:", bold=True).pack(side="left")
        self._prop_var = tk.StringVar()
        self._prop_cb = ttk.Combobox(
            top, textvariable=self._prop_var,
            state="readonly", width=28, font=("Segoe UI", 10)
        )
        self._prop_cb.pack(side="left", padx=8)
        self._prop_cb.bind("<<ComboboxSelected>>", lambda e: self._load_editor())

        self._editor_frame = _frame(self)
        self._editor_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.refresh()

    def refresh(self):
        self._props = db.get_properties()
        names = [p["name"] for p in self._props]
        self._prop_cb["values"] = names
        if names and self._prop_var.get() not in names:
            self._prop_var.set(names[0])
        self._load_editor()

    def _selected_prop(self):
        return next((p for p in self._props if p["name"] == self._prop_var.get()), None)

    def _load_editor(self):
        for widget in self._editor_frame.winfo_children():
            widget.destroy()

        prop = self._selected_prop()
        if not prop:
            return

        if prop["type"] == "numeric":
            self._build_numeric_editor(prop)
        else:
            self._build_categorical_editor(prop)

    def _build_numeric_editor(self, prop):
        _label(self._editor_frame, "Допустимый диапазон значений:", bold=True).pack(
            anchor="w", pady=(8, 8))

        stored = db.get_numeric_range(prop["id"])

        row = _frame(self._editor_frame)
        row.pack(anchor="w")

        _label(row, "от").pack(side="left", padx=(0, 4))
        self._range_min_var = tk.StringVar(value=str(stored.get("min", "")) if stored else "")
        tk.Entry(row, textvariable=self._range_min_var, width=10,
                 font=("Segoe UI", 10), relief="solid", bd=1).pack(side="left")
        _label(row, "до").pack(side="left", padx=(8, 4))
        self._range_max_var = tk.StringVar(value=str(stored.get("max", "")) if stored else "")
        tk.Entry(row, textvariable=self._range_max_var, width=10,
                 font=("Segoe UI", 10), relief="solid", bd=1).pack(side="left")

        _btn(self._editor_frame, "Сохранить", lambda: self._save_numeric_range(prop)).pack(
            anchor="w", pady=10)

    def _build_categorical_editor(self, prop):
        _label(self._editor_frame, "Возможные значения:", bold=True).pack(
            anchor="w", pady=(8, 4))

        input_row = _frame(self._editor_frame)
        input_row.pack(fill="x", pady=(0, 8))

        self._new_value_var = tk.StringVar()
        tk.Entry(input_row, textvariable=self._new_value_var, width=20,
                 font=("Segoe UI", 10), relief="solid", bd=1).pack(side="left", padx=(0, 8))
        _btn(input_row, "Добавить", lambda: self._add_categorical(prop)).pack(side="left")

        mid = _frame(self._editor_frame)
        mid.pack(fill="both", expand=True)
        self._lb = _listbox(mid, height=10)
        self._lb.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(mid, command=self._lb.yview)
        sb.pack(side="left", fill="y")
        self._lb.configure(yscrollcommand=sb.set)

        _btn(self._editor_frame, "Удалить выбранное", lambda: self._delete_categorical(prop),
             primary=False).pack(anchor="w", pady=8)

        self._load_categorical_values(prop)

    def _load_categorical_values(self, prop):
        self._lb.delete(0, "end")
        self._values = db.get_categorical_values(prop["id"])
        for value in self._values:
            self._lb.insert("end", f"  {value}")

    def _save_numeric_range(self, prop):
        try:
            range_min = float(self._range_min_var.get().replace(",", "."))
            range_max = float(self._range_max_var.get().replace(",", "."))
            if range_min > range_max:
                raise ValueError("Минимум не может быть больше максимума")
        except ValueError as error:
            messagebox.showerror("Ошибка", f"Неверный диапазон: {error}")
            return

        wood_types = db.get_wood_types()
        violations = []
        for wood in wood_types:
            stored = db.get_property_values(wood["id"], prop["id"])
            if not stored:
                continue
            if stored["min"] < range_min or stored["max"] > range_max:
                violations.append(
                    f'  - "{wood["name"]}": [{stored["min"]}; {stored["max"]}]'
                )

        if violations:
            messagebox.showerror(
                "Невозможно сохранить",
                f'Следующие виды уже имеют значения вне нового диапазона [{range_min}; {range_max}]:\n\n'
                + "\n".join(violations)
                + "\n\nСначала скорректируйте значения этих видов во вкладке \"Значение для вида\"."
            )
            return

        db.set_numeric_range(prop["id"], range_min, range_max)
        messagebox.showinfo("Сохранено", "Диапазон сохранён.")

    def _add_categorical(self, prop):
        value = self._new_value_var.get().strip()
        if not value:
            return
        db.add_categorical_value(prop["id"], value)
        self._new_value_var.set("")
        self._load_categorical_values(prop)

    def _delete_categorical(self, prop):
        sel = self._lb.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите значение для удаления.")
            return
        db.delete_categorical_value(prop["id"], self._values[sel[0]])
        self._load_categorical_values(prop)


class WoodPropertiesTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._woods = []
        self._props = []
        self._check_vars = []
        self._build()

    def _build(self):
        top = _frame(self)
        top.pack(fill="x", padx=12, pady=(10, 4))
        _label(top, "Вид древесины:", bold=True).pack(side="left")
        self._wood_var = tk.StringVar()
        self._wood_cb = ttk.Combobox(
            top, textvariable=self._wood_var,
            state="readonly", width=28, font=("Segoe UI", 10)
        )
        self._wood_cb.pack(side="left", padx=8)
        self._wood_cb.bind("<<ComboboxSelected>>", lambda e: self._load_props())

        _label(self, "Отметьте свойства, характерные для этого вида:", bold=True).pack(
            anchor="w", padx=12, pady=(8, 4))

        self._checks_frame = _frame(self)
        self._checks_frame.pack(fill="both", expand=True, padx=20)

        _btn(self, "Сохранить", self._save).pack(anchor="w", padx=12, pady=8)

        self.refresh()

    def refresh(self):
        self._woods = db.get_wood_types()
        self._props = db.get_properties()
        names = [w["name"] for w in self._woods]
        self._wood_cb["values"] = names
        if names and self._wood_var.get() not in names:
            self._wood_var.set(names[0])
        self._load_props()

    def _selected_wood(self):
        return next((w for w in self._woods if w["name"] == self._wood_var.get()), None)

    def _load_props(self):
        for w in self._checks_frame.winfo_children():
            w.destroy()
        self._check_vars.clear()

        wood = self._selected_wood()
        if not wood:
            return

        assigned = set(db.get_wood_property_ids(wood["id"]))
        for prop in self._props:
            var = tk.BooleanVar(value=prop["id"] in assigned)
            tk.Checkbutton(
                self._checks_frame, text=prop["name"],
                variable=var, font=("Segoe UI", 10),
                bg=BG, fg=TEXT_DARK,
                activebackground=BG, selectcolor=WHITE
            ).pack(anchor="w", pady=2)
            self._check_vars.append((prop["id"], var))

    def _save(self):
        wood = self._selected_wood()
        if not wood:
            return
        db.set_wood_properties(wood["id"], [pid for pid, var in self._check_vars if var.get()])
        messagebox.showinfo("Сохранено", f'Свойства вида "{wood["name"]}" сохранены.')


class KnowledgeValuesTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._woods = []
        self._props = []
        self._build()

    def _build(self):
        top = _frame(self)
        top.pack(fill="x", padx=12, pady=(10, 4))

        _label(top, "Вид:", bold=True).pack(side="left")
        self._wood_var = tk.StringVar()
        self._wood_cb = ttk.Combobox(
            top, textvariable=self._wood_var,
            state="readonly", width=22, font=("Segoe UI", 10)
        )
        self._wood_cb.pack(side="left", padx=(4, 16))
        self._wood_cb.bind("<<ComboboxSelected>>", lambda e: self._load_prop_list())

        _label(top, "Свойство:", bold=True).pack(side="left")
        self._prop_var = tk.StringVar()
        self._prop_cb = ttk.Combobox(
            top, textvariable=self._prop_var,
            state="readonly", width=22, font=("Segoe UI", 10)
        )
        self._prop_cb.pack(side="left", padx=4)
        self._prop_cb.bind("<<ComboboxSelected>>", lambda e: self._load_value_editor())

        self._editor_frame = _frame(self)
        self._editor_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.refresh()

    def refresh(self):
        self._woods = db.get_wood_types()
        self._props = db.get_properties()
        wnames = [w["name"] for w in self._woods]
        self._wood_cb["values"] = wnames
        if wnames and self._wood_var.get() not in wnames:
            self._wood_var.set(wnames[0])
        self._load_prop_list()

    def _selected_wood(self):
        return next((w for w in self._woods if w["name"] == self._wood_var.get()), None)

    def _selected_prop(self):
        return next((p for p in self._props if p["name"] == self._prop_var.get()), None)

    def _load_prop_list(self):
        wood = self._selected_wood()
        if not wood:
            return
        pid_set = set(db.get_wood_property_ids(wood["id"]))
        available = [p for p in self._props if p["id"] in pid_set]
        names = [p["name"] for p in available]
        self._prop_cb["values"] = names
        if names:
            if self._prop_var.get() not in names:
                self._prop_var.set(names[0])
            self._load_value_editor()
        else:
            self._prop_var.set("")
            for w in self._editor_frame.winfo_children():
                w.destroy()
            _label(
                self._editor_frame,
                "Для данного вида нет назначенных свойств.\nПерейдите на вкладку \"Описание свойств вида\".",
                color=TEXT_MID
            ).pack(pady=20)

    def _load_value_editor(self):
        for w in self._editor_frame.winfo_children():
            w.destroy()

        wood = self._selected_wood()
        prop = self._selected_prop()
        if not wood or not prop:
            return

        vals = db.get_property_values(wood["id"], prop["id"])

        if prop["type"] == "numeric":
            _label(self._editor_frame, f'Диапазон для "{prop["name"]}":', bold=True).pack(
                anchor="w", pady=(8, 4))

            row = _frame(self._editor_frame)
            row.pack(anchor="w")

            _label(row, "от").pack(side="left", padx=(0, 4))
            self._min_var = tk.StringVar(value=str(vals.get("min", "")) if vals else "")
            tk.Entry(row, textvariable=self._min_var, width=10,
                     font=("Segoe UI", 10), relief="solid", bd=1).pack(side="left")
            _label(row, "до").pack(side="left", padx=(8, 4))
            self._max_var = tk.StringVar(value=str(vals.get("max", "")) if vals else "")
            tk.Entry(row, textvariable=self._max_var, width=10,
                     font=("Segoe UI", 10), relief="solid", bd=1).pack(side="left")

            _btn(self._editor_frame, "Сохранить", self._save_numeric).pack(anchor="w", pady=10)

        else:
            _label(self._editor_frame,
                   f'Значения "{prop["name"]}" для "{wood["name"]}":', bold=True).pack(
                anchor="w", pady=(8, 4))

            all_vals = db.get_categorical_values(prop["id"])
            current = set(vals.get("values", []))
            self._cat_vars = []

            for v in all_vals:
                var = tk.BooleanVar(value=v in current)
                tk.Checkbutton(
                    self._editor_frame, text=v, variable=var,
                    font=("Segoe UI", 10), bg=BG,
                    activebackground=BG, selectcolor=WHITE, fg=TEXT_DARK
                ).pack(anchor="w", pady=1)
                self._cat_vars.append((v, var))

            _btn(self._editor_frame, "Сохранить", self._save_categorical).pack(anchor="w", pady=10)

    def _save_numeric(self):
        wood = self._selected_wood()
        prop = self._selected_prop()
        try:
            lo = float(self._min_var.get().replace(",", "."))
            hi = float(self._max_var.get().replace(",", "."))
            if lo > hi:
                raise ValueError("Минимум не может быть больше максимума")
        except ValueError as error:
            messagebox.showerror("Ошибка", f"Неверный диапазон: {error}")
            return

        general_range = db.get_numeric_range(prop["id"])
        if general_range:
            if lo < general_range["min"] or hi > general_range["max"]:
                messagebox.showerror(
                    "Невозможно сохранить",
                    f'Диапазон [{lo}; {hi}] выходит за допустимые пределы '
                    f'[{general_range["min"]}; {general_range["max"]}] '
                    f'для свойства "{prop["name"]}".\n\n'
                    f'Введите значение в пределах допустимого диапазона.'
                )
                return

        db.set_numeric_value(wood["id"], prop["id"], lo, hi)
        messagebox.showinfo("Сохранено", "Значение сохранено.")

    def _save_categorical(self):
            wood = self._selected_wood()
            prop = self._selected_prop()
            if not wood or not prop:
                return
            selected_values = [value for value, var in self._cat_vars if var.get()]
            db.set_categorical_values(wood["id"], prop["id"], selected_values)
            messagebox.showinfo("Сохранено", "Значения сохранены.")


class CompletenessTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        _label(self, "Проверка полноты базы знаний:", bold=True).pack(
            anchor="w", padx=12, pady=(12, 4))
        _btn(self, "Проверить", self._check).pack(anchor="w", padx=12, pady=(0, 8))
        self._result_frame = _frame(self)
        self._result_frame.pack(fill="both", expand=True, padx=12)

    def refresh(self):
        pass

    def _check(self):
        for w in self._result_frame.winfo_children():
            w.destroy()

        errors = db.check_completeness()

        if not errors:
            tk.Label(
                self._result_frame,
                text="База знаний полна. Все виды и свойства заполнены.",
                font=("Segoe UI", 11), bg=BG, fg="#2E7D32"
            ).pack(anchor="w", pady=8)
        else:
            tk.Label(
                self._result_frame,
                text=f"Обнаружено ошибок: {len(errors)}",
                font=("Segoe UI", 11, "bold"), bg=BG, fg="#B71C1C"
            ).pack(anchor="w", pady=(8, 4))
            for err in errors:
                tk.Label(
                    self._result_frame, text=f"  {err}",
                    font=("Segoe UI", 10), bg=BG, fg=TEXT_MID
                ).pack(anchor="w")