from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import sqlite3
import time
import subprocess
import threading




def make_invisible(widget):
   widget.pack()
   widget.pack_forget()



window = Tk() 
window.title("Отток ЗП клиетов ФЛ") 
window.geometry('650x750') 
window.resizable(False, False)
window.iconbitmap("images/icon.ico")
#window["bg"] = "#20B2AA"
window.config(bg = 'green')
#ttk.Style().configure(".",  font="helvetica 13", foreground="#004D40", padding=8, background="#B2DFDB")
ttk.Style().configure('lefttab.TNotebook', tabposition='wn')
s = ttk.Style()
s.configure('my.TButton', font=('Helvetica', 12))

# создаем набор вкладок
notebook = ttk.Notebook(window, style='lefttab.TNotebook')
notebook.pack(expand=True, fill=BOTH, side=LEFT)

# создаем пару фреймвов
frame1 = ttk.Frame(notebook)
frame2 = ttk.Frame(notebook)
frame3 = ttk.Frame(notebook)

frame1.pack(fill=BOTH, expand=True)
frame2.pack(fill=BOTH, expand=True)
frame3.pack(fill=BOTH, expand=True)

home_logo = PhotoImage(file="./images/home.png")
report_logo = PhotoImage(file="./images/report.png")
graph_logo = PhotoImage(file="./images/graph.png")



# добавляем фреймы в качестве вкладок
notebook.add(frame1, image=home_logo, compound=LEFT)
notebook.add(frame2, image=report_logo,
             compound=LEFT)
notebook.add(frame3, image=graph_logo,
             compound=LEFT)


# result---------

frame2.rowconfigure(index=0, weight=1)
frame2.columnconfigure(index=0, weight=1)

# columns = ("id","name", "result")
tree = ttk.Treeview(frame2, columns=("id", "name", "result"), show="headings")
tree.grid(row=0, column=0, sticky="nsew")


def sort(col, reverse):
    # получаем все значения столбцов в виде отдельного списка
    l = [(tree.set(k, col), k) for k in tree.get_children("")]
    # сортируем список
    l.sort(reverse=reverse)
    # переупорядочиваем значения в отсортированном порядке
    for index,  (_, k) in enumerate(l):
        tree.move(k, "", index)
    # в следующий раз выполняем сортировку в обратном порядке
    tree.heading(col, command=lambda: sort(col, not reverse))


people_logo = PhotoImage(file="./images/people.png")
leave_logo = PhotoImage(file="./images/leave.png")
# определяем заголовки
ttk.Style().configure("Treeview.Heading", font=(None, 13))
ttk.Style().configure("Treeview", font=(None, 13))

tree.heading("id", text="№",  anchor=S,
             command=lambda: sort(0, False))
tree.column("id", minwidth=0, width=80, stretch=NO)
tree.heading("name", text="ФИО", anchor=S,  image=people_logo,
             command=lambda: sort(1, False))
tree.column("name", minwidth=0, width=400, stretch=NO)
tree.heading("result", text="Отток", anchor=S,
             image=leave_logo, command=lambda: sort(2, False))
tree.column("result", minwidth=0, width=100, stretch=NO)

def new_tree():
    connection = sqlite3.connect('data/data.sqlite3')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM clients')
    data = cursor.fetchall()
    for i in data:
        tree.insert("", END, values=i)
    connection.close()


new_tree()
scrollbar = ttk.Scrollbar(frame2, orient=VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")
# ------------------

# graphics ---------

h = ttk.Scrollbar(frame3, orient=HORIZONTAL)
v = ttk.Scrollbar(frame3, orient=VERTICAL)
canvas = Canvas(frame3, scrollregion=(0, 0, 1000, 1000), bg="white",
                yscrollcommand=v.set, xscrollcommand=h.set)
h["command"] = canvas.xview
v["command"] = canvas.yview

canvas.grid(column=0, row=0, sticky=(N, W, E, S))
h.grid(column=0, row=1, sticky=(W, E))
v.grid(column=1, row=0, sticky=(N, S))
frame3.grid_columnconfigure(0, weight=1)
frame3.grid_rowconfigure(0, weight=1)
def new_image():
    python_image = PhotoImage(file="data/gist.PNG")
    canvas.create_image(10, 10, anchor=NW, image=python_image)
new_image()
# ------------------



download_label = ttk.Label(frame1, text="Please, wait loading...")
make_invisible(download_label)
progressbar = ttk.Progressbar(
    frame1, orient="horizontal", length=250, mode="determinate")
make_invisible(progressbar)
update_button = ttk.Button(frame1, text="Обновить данные", style='my.TButton')
update_button.pack(side=BOTTOM, fill=X, padx=150, pady=10)
result_label = ttk.Label(frame1, text="")
make_invisible(result_label)


def is_progress():# здесь мы отслеживаем процесс работы модельки и меняем полоску загрузки
    connection = sqlite3.connect('data/data.sqlite3')
    cursor = connection.cursor()
    download_label.pack(side=BOTTOM, fill=X, padx=230, pady=5)
    progressbar.pack(side=BOTTOM, fill=X, padx=50, pady=10)
    while (progressbar['value'] != 100):
        cursor.execute('SELECT percent FROM tasks ORDER BY id DESC LIMIT 1')
        data = cursor.fetchone()
        progressbar['value'] = data[0]
        time.sleep(1)
    make_invisible(download_label)
    make_invisible(progressbar)
    cursor.execute('SELECT COUNT(*) FROM clients WHERE result=1')
    result_yes = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM clients WHERE result=0')
    result_no = cursor.fetchone()[0]
    result_label["text"] = f'{result_no} - планируют продолжить получать ЗП на карту текущего банка\n{result_yes} - будущий отток'
    result_label.pack(side=BOTTOM, fill=X, padx=50, pady=10)
    connection.close()
    new_image()
    new_tree()



def run_ML(): 
    subprocess.run("python data/test.py", shell=True)


def open_file():  # здесь окошко выбора данных, запуск ML и полоска загрузки
    filepath = filedialog.askopenfilename(title="Выбор источника данных", filetypes=[
                                          ('All files', '*.parquet')])  # если че поменять разрешение
    if filepath != "":
        connection = sqlite3.connect('data/data.sqlite3')
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO tasks (filename, percent) VALUES (?, ?)', (filepath, 0))
        connection.commit()
        connection.close()
        # запускаем 2 потока параллельно
        threading.Thread(target=run_ML).start()
        threading.Thread(target=is_progress).start()
        make_invisible(open_button)


open_button = ttk.Button(frame1, text="Открыть файл",
                         style='my.TButton', command=open_file)
open_button.pack(side =BOTTOM, fill=X, padx=150, pady=10)
hello_label = ttk.Label(frame1, text="Благодарим вам за выбор нашего решения :)\n\nПроект разработан в рамках хакатона 'IT Purple Hack' 13.03.2024\nкомандой начинающих разработчиков, студентов школы 21.\nТекущая версия - 1.0\n\nДанное приложение запускает модель машинного обучения, кот.\nпредсказывает на ежедневной основе отток зарплатных\nклиентов из банка до возникновения самого события оттока,\nиспользуя данные поведения клиента: транзакции, продукты,\nмобильное приложение, терминалы, прочее.\n\nОпределение типа клиента (где 0 - клиент планирует продолжить\nполучать ЗП на карту текущего банка, 1 - клиент сменить банк\nдля начисления ЗП - будущий отток).\n\n\nНесколько инструкций:\n- C помощью кнопки 'Открыть файл' выбираем источник данных\n- На вкладки со статистикой и графиками можно переключится\nкнопками на панели слева\n- Данные можно отсортировать нажатием на заголовок столбца", font=("Arial", 14))
hello_label.pack(side=TOP, fill=X, padx=5, pady=10)

window.mainloop()
