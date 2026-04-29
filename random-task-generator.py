import random
import json
import os
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

# === константы ===
history_file = "task_history.json"
tasks_file = "tasks.json"

# предопределённые задачи
default_tasks = [
    {"text": "Прочитать книгу", "category": "Учёба"},
    {"text": "Сделать зарядку", "category": "Спорт"},
    {"text": "Написать отчет", "category": "Работа"}
]

# === глобальные переменные ===
tasks = []
history = []
filter_var = None
history_text = None
current_task_label = None
new_task_entry = None
new_category_var = None
root = None
status_label = None
count_label = None


# === функции работы с файлами ===
def load_tasks():
    global tasks
    if os.path.exists(tasks_file):
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
                return
        except:
            pass
    tasks = default_tasks.copy()
    save_tasks()


def save_tasks():
    with open(tasks_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def load_history():
    global history
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                return
        except:
            pass
    history = []
    save_history()


def save_history():
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def update_status(message, is_error=False):
    status_label.config(text=message, fg="red" if is_error else "green")
    root.after(3000, lambda: status_label.config(text="Готов", fg="gray"))


# === основная логика ===
def generate_task():
    if not tasks:
        update_status("Ошибка: нет задач!", True)
        return

    task = random.choice(tasks)
    current_task = task.copy()
    current_task["timestamp"] = get_timestamp()

    history.append(current_task)
    save_history()

    current_task_label.config(text=f"{task['text']}")
    current_task_label.config(fg="#2c3e50")
    update_history_display()
    update_status(f"Сгенерирована: {task['text']}")


def update_history_display():
    history_text.delete(1.0, END)

    current_filter = filter_var.get()

    filtered_history = history
    if current_filter != "Все":
        filtered_history = [item for item in history
                            if item.get("category") == current_filter]

    if not filtered_history:
        history_text.insert(1.0, "История пуста\n")
    else:
        for idx, item in enumerate(reversed(filtered_history), 1):
            line = f"{idx}. {item['text']} [{item['category']}]\n"
            history_text.insert(END, line)

    count_label.config(text=f"Всего: {len(history)} | Показано: {len(filtered_history)}")


def apply_filter():
    update_history_display()
    update_status("Фильтр применён")


def add_new_task():
    task_text = new_task_entry.get().strip()
    category = new_category_var.get()

    if not task_text:
        update_status("Ошибка: введите задачу!", True)
        return

    for task in tasks:
        if task["text"].lower() == task_text.lower():
            update_status("Ошибка: задача уже есть!", True)
            return

    tasks.append({"text": task_text, "category": category})
    save_tasks()
    new_task_entry.delete(0, END)
    update_task_display()
    update_status(f"Добавлено: {task_text}")


def delete_task():
    if not tasks:
        update_status("Ошибка: нет задач для удаления!", True)
        return

    # создаём окно выбора задачи
    select_window = Toplevel(root)
    select_window.title("Удалить задачу")
    select_window.geometry("300x400")
    select_window.transient(root)
    select_window.grab_set()

    Label(select_window, text="Выберите задачу для удаления:", font=("arial", 10, "bold")).pack(pady=10)

    listbox = Listbox(select_window, font=("arial", 10))
    listbox.pack(fill=BOTH, expand=True, padx=10, pady=5)

    for idx, task in enumerate(tasks, 1):
        listbox.insert(END, f"{idx}. {task['text']} [{task['category']}]")

    def confirm_delete():
        selection = listbox.curselection()
        if not selection:
            update_status("Ошибка: выберите задачу!", True)
            return

        task_text = tasks[selection[0]]["text"]

        if messagebox.askyesno("Подтверждение", f"Удалить задачу?\n'{task_text}'?"):
            tasks.pop(selection[0])
            save_tasks()
            update_task_display()
            update_status(f"Удалено: {task_text}")
            select_window.destroy()

    Button(select_window, text="Удалить", command=confirm_delete,
           bg="#e74c3c", fg="white", font=("arial", 10)).pack(pady=10)


def update_task_display():
    # Обновляем отображение в специальном виджете
    task_display_text.delete(1.0, END)
    if not tasks:
        task_display_text.insert(1.0, "Список задач пуст\nДобавьте первую задачу!")
    else:
        for idx, task in enumerate(tasks, 1):
            line = f"{idx}. {task['text']} [{task['category']}]\n"
            task_display_text.insert(END, line)


def clear_history():
    if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
        global history
        history = []
        save_history()
        update_history_display()
        current_task_label.config(text="Нет задачи")
        update_status("История очищена")


def on_closing():
    save_history()
    save_tasks()
    root.destroy()


# Создание интерфейса
def create_ui():
    global filter_var, history_text, current_task_label
    global new_task_entry, new_category_var, root, status_label, count_label, task_display_text

    root = Tk()
    root.title("Генератор Задач")
    root.geometry("800x650")
    root.configure(bg="#f5f5f5")

    # === верхняя панель с текущей задачей ===
    header_frame = Frame(root, bg="#34495e", height=120)
    header_frame.pack(fill=X)
    header_frame.pack_propagate(False)

    Label(header_frame, text="ГЕНЕРАТОР ЗАДАЧ",
          font=("arial", 16, "bold"), bg="#34495e", fg="white").pack(pady=(15, 5))

    Label(header_frame, text="Текущая задача:",
          font=("arial", 10), bg="#34495e", fg="#bdc3c7").pack()

    current_task_label = Label(header_frame, text="Нет задачи",
                               font=("arial", 14, "bold"), bg="#34495e", fg="#ecf0f1")
    current_task_label.pack(pady=(0, 10))

    # Кнопка генерации
    Button(header_frame, text="СГЕНЕРИРОВАТЬ ЗАДАЧУ", command=generate_task,
           font=("arial", 12, "bold"), bg="#2ecc71", fg="white",
           padx=30, pady=8, bd=0, cursor="hand2").pack(pady=5)

    main_frame = Frame(root, bg="#f5f5f5")
    main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

    left_panel = Frame(main_frame, bg="#f5f5f5")
    left_panel.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

    add_card = Frame(left_panel, bg="white", relief=RAISED, bd=1)
    add_card.pack(fill=X, pady=(0, 15))

    Label(add_card, text="Добавить новую задачу",
          font=("arial", 11, "bold"), bg="white").pack(anchor=W, padx=15, pady=(10, 5))

    frame1 = Frame(add_card, bg="white")
    frame1.pack(fill=X, padx=15, pady=5)
    Label(frame1, text="Название:", bg="white", width=10, anchor=W).pack(side=LEFT)
    new_task_entry = Entry(frame1, width=30, font=("arial", 10))
    new_task_entry.pack(side=LEFT, padx=5)

    frame2 = Frame(add_card, bg="white")
    frame2.pack(fill=X, padx=15, pady=5)
    Label(frame2, text="Категория:", bg="white", width=10, anchor=W).pack(side=LEFT)
    new_category_var = StringVar(value="Учёба")
    ttk.Combobox(frame2, textvariable=new_category_var,
                 values=["Учёба", "Спорт", "Работа"],
                 state="readonly", width=27).pack(side=LEFT, padx=5)

    Button(add_card, text="Добавить задачу", command=add_new_task,
           font=("arial", 10), bg="#3498db", fg="white", bd=0, cursor="hand2",
           padx=15, pady=5).pack(pady=(10, 15))

    # Карточка списка задач
    tasks_card = Frame(left_panel, bg="white", relief=RAISED, bd=1)
    tasks_card.pack(fill=BOTH, expand=True)

    Label(tasks_card, text="Доступные задачи",
          font=("arial", 11, "bold"), bg="white").pack(anchor=W, padx=15, pady=(10, 5))

    tasks_scroll = Scrollbar(tasks_card)
    tasks_scroll.pack(side=RIGHT, fill=Y, padx=(0, 10), pady=5)

    global task_display_text
    task_display_text = Text(tasks_card, yscrollcommand=tasks_scroll.set,
                             font=("arial", 10), height=12, wrap=WORD)
    task_display_text.pack(side=LEFT, fill=BOTH, expand=True, padx=15, pady=5)
    tasks_scroll.config(command=task_display_text.yview)

    Button(tasks_card, text="Удалить задачу", command=delete_task,
           font=("arial", 10), bg="#e74c3c", fg="white", bd=0, cursor="hand2",
           padx=15, pady=5).pack(pady=(5, 15))

    # === правая панель - история ===
    right_panel = Frame(main_frame, bg="#f5f5f5")
    right_panel.pack(side=RIGHT, fill=BOTH, expand=True)

    history_card = Frame(right_panel, bg="white", relief=RAISED, bd=1)
    history_card.pack(fill=BOTH, expand=True)

    Label(history_card, text="История задач",
          font=("arial", 11, "bold"), bg="white").pack(anchor=W, padx=15, pady=(10, 5))

    # Фильтры
    filter_frame = Frame(history_card, bg="white")
    filter_frame.pack(fill=X, padx=15, pady=5)

    Label(filter_frame, text="Фильтр:", bg="white", font=("arial", 9)).pack(side=LEFT)
    filter_var = StringVar(value="Все")
    for cat in ["Все", "Учёба", "Спорт", "Работа"]:
        Radiobutton(filter_frame, text=cat, variable=filter_var,
                    value=cat, command=apply_filter, bg="white").pack(side=LEFT, padx=5)

    # Текстовая область истории с прокруткой
    history_scroll = Scrollbar(history_card)
    history_scroll.pack(side=RIGHT, fill=Y, padx=(0, 10), pady=5)

    history_text = Text(history_card, yscrollcommand=history_scroll.set,
                        font=("arial", 10), height=15, wrap=WORD)
    history_text.pack(side=LEFT, fill=BOTH, expand=True, padx=15, pady=5)
    history_scroll.config(command=history_text.yview)

    # Нижняя панель истории
    history_bottom = Frame(history_card, bg="white")
    history_bottom.pack(fill=X, padx=15, pady=(0, 10))

    count_label = Label(history_bottom, text="Всего: 0 | Показано: 0",
                        bg="white", font=("arial", 9))
    count_label.pack(side=LEFT)

    Button(history_bottom, text="Очистить историю", command=clear_history,
           font=("arial", 9), bg="#95a5a6", fg="white", bd=0, cursor="hand2",
           padx=10, pady=3).pack(side=RIGHT)

    # Строка состояния
    status_frame = Frame(root, bg="#ecf0f1", relief=SUNKEN, bd=1)
    status_frame.pack(fill=X, side=BOTTOM)

    status_label = Label(status_frame, text="Готов", anchor=W,
                         font=("arial", 9), bg="#ecf0f1", padx=10, pady=5)
    status_label.pack(fill=X)

    return root

load_tasks()
load_history()
root = create_ui()
update_task_display()
update_history_display()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()