import sqlite3
import time

import datetime

import re

from tkinter import *

from PIL import ImageTk, Image

from tkinter import messagebox

from tkinter import YView

import sys
print(sys.executable)

root = Tk()
root.title("Task Manager")
# icon
root.iconbitmap("images/icon.ico")
root.geometry("1180x436")
root.configure(bg = "#330066")
root.resizable(False, False)

con = sqlite3.connect("task_manager")
cursor  = con.cursor()

# user data table
cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_data(
                    user TEXT UNIQUE PRIMARY KEY,
                    password TEXT NOT NULL
                    )
             ''')

# tasks details table
cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_task(
                    user TEXT,
                    task_name VARCHAR UNIQUE PRIMARY KEY,
                    task_dets VARCHAR NOT NULL,
                    date_added TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    is_complete TEXT NOT NULL,
                    FOREIGN KEY(user)
                        REFERENCES user_data(user)
                    )
                ''')

# defining global variables to be used ad values for function parameters
users = "user_data"
tasks = "user_task"

# show_hide icons
hide_icon = PhotoImage(file = "images/hide.png")
show_icon = PhotoImage(file = "images/show.png")
add_user = PhotoImage(file = "images/register.png")
add_task = PhotoImage(file = "images/add task.png")
view_all = PhotoImage(file = "images/view all tasks.png")
view_my = PhotoImage(file = "images/view my tasks.png")
report = PhotoImage(file = "images/report.png")
tasks_users = PhotoImage(file = "images/tasks and users.png")
exit = PhotoImage(file = "images/exit.png")

def tasks_total(table2 = tasks):
    '''
    tasks_total function calculates and returnd the total amount of tasks in the file. 
    param: table2: takes the name of the table containing the tasks data as an argument
    '''
    cursor.execute(f"SELECT * FROM {table2}")
    total = len(cursor.fetchall())
    return total

def users_total(table1 = users):
    '''
    users_total function calculates and returnd the total amount of users in the table. 
    param: table1: takes the name of the file containing the users data as an argument
    '''
    cursor.execute(f"SELECT * FROM {table1}")
    total = len(cursor.fetchall())
    return total

def tasks_complete(table2 = tasks):
    '''
    tasks_complete function calculates and returns the total amount of completed tasks in the file
    param: table2: takes the name of the tablr containing tasks data as an argument
    '''
    cursor.execute(f"SELECT * FROM {table2}")
    # variable storingt the number of completed tasks
    completed = 0
    # looping over the task rows and checking for completed tasks
    for row in cursor:
        if row[-1].lower() == "yes":
            completed += 1
    return completed 

def tasks_noncomplete(table2 = tasks):
    '''
    tasks_uncomplete function calculates and returns the total amount of uncompleted tasks in the file
    param: table2: takes the name of the table containing tasks data as an argument
    '''
    cursor.execute(f"SELECT * FROM {table2}")
    # variable storingt the number of completed tasks
    noncompleted = 0
    # looping over the task rows and checking for not completed tasks
    for row in cursor:
        if row[-1].lower() == "no":
            noncompleted += 1 
    return noncompleted

def uncomp_overdue(table2 = tasks):
    '''
    uncomp_overdue function calculates and returns the amount of uncompleted tasks that are also overdue
    param: table2: takes the name of the table containing table data as an argument
    '''
    cursor.execute(f"SELECT * from {table2}")
    #variable storing the number of incomplete and overdue tasks
    result = 0
    for row in cursor:
        today = datetime.datetime.today()
        due_date = datetime.datetime.strptime(row[-2], "%Y-%m-%d")
        # if BOTH the last item in the task line is "no" and the date is in the past
        # adding 1 to the result variable
        if row[-1].lower() == "no" and today > due_date:
            result += 1
    return result

def uncom_percentage(table2 = tasks):
    '''
    uncom_percentage function calculates and returns the percentage of the uncompleted tasks
    param: table2: taken a name of the table containing tasks data as an argument
    '''
    percentage = (tasks_noncomplete(table2) / tasks_total(table2)) * 100
    return percentage

def overdue_percentage(table2 = tasks):
    '''
    overdue_percentage function calculated and returns the percentage of overdue tasks in the tasks list
    param: table2: takes the name of the table containing the tasks data as an argument
    '''
    cursor.execute(f"SELECT * FROM {table2}")
    # variable to store the amount of overdue tasks
    overdue = 0
    for row in cursor:
        today = datetime.datetime.today()
        due_date = datetime.datetime.strptime(row[-2], "%Y-%m-%d")
        if today > due_date:
            overdue += 1
    #calculating the percentage of overdue tasks out of the total tasks            
    percentage = (overdue / tasks_total(table2)) * 100
    return percentage

def show_hide_password():
    '''
    show_hide_password function changes the display in the password entry box either hiding it or showing the content on button click
    '''
    if password_box["show"] == "":
        show_hide_btn.config(image = show_icon)
        password_box.config(show = "●")

    else:
        show_hide_btn.config(image = hide_icon)
        password_box.config(show = "")

def new_show_hide():
    '''
    new_show_hide_password function changes the display in the password entry box either hiding it or showing the content on button click
    '''
    if new_password_box["show"] == "":
        show_hide_btn.config(image = show_icon)
        new_password_box.config(show = "●")
        confirm_password_box.config(show = "●")

    elif new_password_box["show"] == "●":
        show_hide_btn.config(image = hide_icon)
        new_password_box.config(show = "")
        confirm_password_box.config(show = "")

def submit(table1 = users):
    '''
    submit function checks the entered username and password againts the database records
    and shows error message if incorrect
    '''
    user_name = user_box.get().lower()
    user_password = password_box.get().lower()
    cursor.execute(f"SELECT user, password FROM {table1}")
    upd_dict = {user : password for user, password in cursor}
    if user_name not in upd_dict.keys():
        response = messagebox.showerror("Error", "Username doesn't exist.")
        user_box.delete(0, END)
        password_box.delete(0, END)
    elif user_password != upd_dict[user_name]:
        response = messagebox.showerror("Error", "Wrong password. Try again.")
        user_box.delete(0, END)
        password_box.delete(0, END)
    else:
        if user_name == "admin":
            response = admin_menu_page()
        else:
            response = user_menu_page()

    return response

def login_page():
    '''
    login_page function 
    '''
    global password_box
    global show_hide_btn
    global user_box

    login_frame = Frame(root, bg = "#330066")

    # labels
    login = Label(login_frame, text = "Login", font= ("Arial", 15),
                  fg = "#ffffe6", bg = "#330066")
    login.grid(row = 0, column = 0, columnspan=2, padx = 570, pady = 40, sticky = NSEW)
    user = Label(login_frame, text = "Enter username", font =  15,
                 fg = "#ffffe6", bg = "#330066")
    user.grid(row = 3, column = 0, padx =  (300, 15), pady = 5, ipady = 3, sticky = W+E)
    password = Label(login_frame, text = "Enter password", font = 15,
                     fg = "#ffffe6", bg = "#330066")
    password.grid(row = 4, column = 0, padx = (300, 15), pady = 5, ipady = 3, sticky = EW)

    # entry fields
    user_box = Entry(login_frame, font = ("bold", 12), 
                    bd = 0, highlightcolor="#000066", highlightthickness = 1, highlightbackground="#e0e0eb")
    user_box.grid(row = 3, column = 1, padx = (5, 500), pady = 5, sticky = NSEW)
    password_box = Entry(login_frame, font = ("bold", 12), 
                        bd = 0,  highlightcolor="#000066", highlightthickness = 1, highlightbackground="#e0e0eb",
                        show = "●")
    password_box.grid(row = 4, column = 1, padx = (5, 500), pady = 5, sticky = NSEW)

    # buttons
    submit_btn = Button(login_frame, text = "Submit", command = submit,
                        font = ("Arial", 10, "bold"), bg = "#ff5c33", fg = "#ffffe6", width = 16)
    submit_btn.grid(row = 5, column = 1, padx = 45, pady = 15, ipady = 3, sticky = W)
    show_hide_btn = Button(login_frame, image = hide_icon, bd = 0, bg = "#330066", command = show_hide_password)
    show_hide_btn.grid(row = 4, column = 1, sticky = W, padx = 235)

    login_frame.grid(row = 0, column=0, sticky = NSEW)

def reg_user(table1 = users):
    '''
    reg_user function checks if the user is admin, if so allows to enter the details of a new user, making sure the same password has been entered twice
    param: table2: takes the name of the table containing user data as an argument
    '''
    global register_window
    global new_user_box
    global new_password_box
    global confirm_password_box

    register_window = Toplevel()
    # setting the icon and the title for the new user window
    register_window.title("Register new user")
    register_window.iconbitmap("images/icon.ico")
    register_window.geometry("800x350")
    register_window.configure(bg = "#330066")

    # labels
    header = Label(register_window, text = "Enter the new user details", font= ("Arial", 14),
                  fg = "#ffffe6", bg = "#330066")
    header.grid(row = 0, column = 0, columnspan=2, padx = (100, 70), pady = 35, sticky = NSEW)
    new_user = Label(register_window, text = "Enter username", font =  15,
                 fg = "#ffffe6", bg = "#330066")
    new_user.grid(row = 3, column = 0, padx =  (200, 15), pady = 5, ipady = 3, sticky = W+E)
    new_password = Label(register_window, text = "Enter password", font = 15,
                     fg = "#ffffe6", bg = "#330066")
    new_password.grid(row = 4, column = 0, padx = (200, 15), pady = 5, ipady = 3, sticky = EW)
    confirm_password = Label(register_window, text = "Confirm password", font = 15,
                     fg = "#ffffe6", bg = "#330066")
    confirm_password.grid(row = 5, column = 0, padx = (200, 15), pady = 5, ipady = 3, sticky = EW)

    # entry fields
    new_user_box = Entry(register_window, font = ("bold", 12), 
                    bd = 0, highlightcolor="#000066", highlightthickness = 1, highlightbackground="#e0e0eb")
    new_user_box.grid(row = 3, column = 1, padx = 10, pady = 5, sticky = NSEW)
    new_password_box = Entry(register_window, font = ("bold", 12), 
                        bd = 0,  highlightcolor="#000066", highlightthickness = 1, highlightbackground="#e0e0eb",
                        show = "●")
    new_password_box.grid(row = 4, column = 1, padx = 10, pady = 5, sticky = NSEW)
    confirm_password_box = Entry(register_window, font = ("bold", 12), 
                    bd = 0,  highlightcolor="#000066", highlightthickness = 1, highlightbackground="#e0e0eb",
                    show = "●")
    confirm_password_box.grid(row = 5, column = 1, padx = 10, pady = 5, sticky = NSEW)

    # buttons
    submit_btn = Button(register_window, text = "Submit", command = lambda: submit_new(table1),
                        font = ("Arial", 10, "bold"), bg = "#ff5c33", fg = "#ffffe6", width = 16)
    submit_btn.grid(row = 6, column = 1, padx = 32, pady = 15, ipady = 3, sticky = W)
    show_hide_btn = Button(register_window, image = hide_icon, bd = 0, bg = "#330066", command = new_show_hide)
    show_hide_btn.grid(row = 4, column = 2, sticky = E, padx = 10)

def submit_new(table1 = users):
    '''
    submit_new function is triggered when the submit button of register new user is clicked
    checks whether the uername is unique
    and that password is confirmed
    after all checks adds new username into the database
    param: table1: takes the name of the tale containing user information as an argument
    '''
    new_username = new_user_box.get()
    new_password = new_password_box.get()
    password_conf = confirm_password_box.get()
    # clearing all entry boxes
    new_user_box.delete(0, END)
    new_password_box.delete(0, END)
    confirm_password_box.delete(0, END)
    # checking username is unique
    users = all_users()
    if new_username in users:
        response = messagebox.showerror("Error", f"Username {new_username} already exists. Try again.")
        register_window.tkraise()    
    else:
        # checking if passwords match, if they do, adding a new username and new password to the user file
        if new_password != password_conf:
            response = messagebox.showerror("Error", "Passwords don't match. Try again.")
            register_window.tkraise()
        elif new_password == password_conf:
            cursor.execute(f'''INSERT INTO {table1}(user, password)
                                    VALUES(?, ?)''', (new_username, new_password) )
            con.commit()
            register_window.destroy()
            response = messagebox.showinfo("User added.", f"New user {new_username} added to the database.")

def db_task(table2 = tasks):
    '''
    db_task function takes all details entered in the new task window and adds the data to the database
    param: table2: takes the name of the table holding tasks data as an argument
    '''
    user = username_box.get()
    task_title = task_title_box.get()
    task_desc = task_desc_box.get()
    due_date = due_date_box.get()
    # automatic today's date and pre-filled completon status
    today = time.strftime("%Y-%m-%d")
    complete = "No"

    cursor.execute(f'''INSERT INTO {table2}(user, task_name, task_dets, date_added, due_date, is_complete)
                            VALUES(?, ?, ?, ?, ?, ?)''', (user, task_title, task_desc, today, due_date, complete))
    response = messagebox.showinfo("Task added.", f"Task '{task_title}' added to the database for '{user}'.")
    con.commit()

def data_check(*args):
    '''
    name_check function checks whether the username entered in the entry box already exists.
    Shows the error message if it doesn't and enables the "add task" button if it does
    '''
    my_flag = False

    # checking the username is in the database
    users = all_users()
    if d1.get() not in users:
        my_flag = True
        # placing error mesage to the screen
        name_error.grid(row = 1, column = 2, padx = 5, pady = 5, sticky = NSEW)
    else: 
        name_error.grid_remove()

    # making sure all entry boxes are filled
    if len(d1.get()) == 0:
        my_flag = True

    if len(tt1.get()) == 0:
        my_flag = True

    if len(td1.get()) == 0:
        my_flag = True

    # checking the date was entered correctly
    ref_date = "%Y-%m-%d"    
    try:
        date = time.strptime(c1.get(), ref_date)
        date_error.grid_remove()
    except ValueError:
        my_flag = True
        date_error.grid(row = 4, column = 2, padx = 5, pady = 5, sticky = NSEW)

    # changing the button    
    if my_flag != True:
        add_btn.config(state = NORMAL, bg = "#ff5c33")
    else:
        add_btn.config(state = DISABLED, bg = "#ffd1b3")

def new_task():
    '''
    new_task function opens a new window for the user to add a new task to the database
    '''
    global d1
    global c1
    global tt1
    global td1
    global add_btn
    global task_window
    global name_error
    global date_error
    global username_box
    global task_title_box
    global task_desc_box
    global due_date_box

    task_window = Toplevel()
    # setting the icon and the title for the new task window
    task_window.title("Add new task")
    task_window.iconbitmap("images/icon.ico")
    task_window.geometry("800x350")
    task_window.configure(bg = "#330066")

    # labels
    header = Label(task_window, text = "Enter the task details", font= ("Arial", 14),
                  fg = "#ffffe6", bg = "#330066")
    header.grid(row = 0, column = 0, columnspan=2, padx = (330, 70), pady = 20, sticky = NSEW)
    username = Label(task_window, text = "Enter username", font =  15,
                 fg = "#ffffe6", bg = "#330066")
    username.grid(row = 1, column = 0, padx =  (120, 15), pady = 5, ipady = 3, sticky = W+E)
    task_title = Label(task_window, text = "Task title", font = 15,
                     fg = "#ffffe6", bg = "#330066")
    task_title.grid(row = 2, column = 0, padx = (120, 15), pady = 5, ipady = 3, sticky = EW)
    task_desc = Label(task_window, text = "Task description", font = 15,
                     fg = "#ffffe6", bg = "#330066")
    task_desc.grid(row = 3, column = 0, padx = (120, 15), pady = 5, ipady = 3, sticky = EW)
    due_date = Label(task_window, text = "Due date (YYYY-MM-DD)", font = 15,
                     fg = "#ffffe6", bg = "#330066")
    due_date.grid(row = 4, column = 0, padx = (120, 15), pady = 5, ipady = 3, sticky = EW)
    # hidden name error message that only appears when invalid username is entered
    name_error = Label(task_window, text = "Username not in the db", bd = 0, fg = "#ff0000", bg = "#330066", font = 10)
    # hidden date rror message 
    date_error = Label(task_window, text = "Date format YYYY-MM-DD", bd = 0, fg = "#ff0000", bg = "#330066", font = 10)

    # entry fields
    d1 = StringVar(task_window)
    username_box = Entry(task_window, font = ("bold", 12), textvariable = d1,
                    bd = 0, highlightcolor="#000066", highlightthickness = 1, highlightbackground="#e0e0eb")
    username_box.grid(row = 1, column = 1, padx = 10, pady = 5, sticky = NSEW)
    d1.trace("w", data_check)
    tt1 = StringVar(task_window)
    task_title_box = Entry(task_window, font = ("bold", 12), textvariable=tt1, 
                    bd = 0, highlightcolor="#000066", highlightthickness = 1, highlightbackground="#e0e0eb")
    task_title_box.grid(row = 2, column = 1, padx = 10, pady = 5, sticky = NSEW)
    tt1.trace("w", data_check)
    td1 = StringVar(task_window)
    task_desc_box = Entry(task_window, font = ("bold", 12), textvariable = td1,
                    bd = 0, highlightcolor="#000066", highlightthickness = 1, highlightbackground="#e0e0eb")
    task_desc_box.grid(row = 3, column = 1, padx = 10, pady = 5, sticky = NSEW)
    td1.trace("w", data_check)
    c1 = StringVar(task_window)
    due_date_box = Entry(task_window, font = ("bold", 12), textvariable = c1,
                    bd = 0, highlightcolor="#000066", highlightthickness = 1, highlightbackground="#e0e0eb")
    due_date_box.grid(row = 4, column = 1, padx = 10, pady = 5, sticky = NSEW)
    c1.trace("w", data_check)
    # buttons
    add_btn = Button(task_window, text = "Add task", state = DISABLED, command = db_task,
                        font = ("Arial", 10, "bold"), bg = "#ffd1b3", fg = "#ffffe6", width = 16)
    add_btn.grid(row = 6, column = 1, padx = 60, pady = 15, ipady = 3, sticky = W)

def list_tasks(table2 = tasks):
    '''
    funstion list_tasks returns the list cintaining all tasks data
    param: table: takes the name of the file containing the utask data as an argument
    '''
    cursor.execute(f"SELECT * FROM {table2}")
    # creating a list coontaining each line of tasks file in a separate list
    titem_list = [row for row in cursor]
    return titem_list

def user_inc_od(table2 = tasks):
    '''
    user_inc_od function calculates and returns the dictionary showing the percentage of the tasks assigned to each user that have not yet been completed and are overdue
    param: table1: takes the name of the table containing user information as an argument
    param: table2: takes the name of the table containing task information as an argument
    '''
    uitem_list = all_users()
    # dictionary where user name is a key and value is [user total tasks : user incomplete AND overdue tasks]
    user_dict = {user : [0, 0] for user in uitem_list}
    titem_list = list_tasks(table2)
    for user in user_dict:
        for item in titem_list:
            today = datetime.datetime.today()
            due_date = datetime.datetime.strptime(item[-2], "%Y-%m-%d")
            # checking if task in the tasks list is for the user
            if user in item[0]:
                user_dict[user][0] += 1
                # checking if the user task is incomplete AND overdue
                if item[-1].lower() == "no" and today > due_date:
                    user_dict[user][1] += 1
    # # dictionary with user name as key and percentage result for that user a value                
    percentage = {i: (user_dict[i][1] / user_dict[i][0]) * 100 for i in user_dict if user_dict[i][0] != 0 }
    return percentage

def user_incomplete(table2 = tasks):
    '''
    user_incomplete function calculates and returns the dictionaty showing the percentage of the tasks assigned to that user that have not been completed
    param: table1: takes the name of the table containing user information as an argument
    param: table2: takes the name of the table containing task information as an argument
    '''
    uitem_list = all_users()
    # dictionary where user name is a key and value is [user total tasks : user incomplete tasks]
    user_dict = {user : [0, 0] for user in uitem_list}
    titem_list = list_tasks(table2)
    for user in user_dict:
        for item in titem_list:
            # checking if task in the tasks list is for the user
            if user in item[0]:
                user_dict[user][0] += 1
                # checking if the user task is incomplete
                if item[-1].lower() == "no":
                    user_dict[user][1] += 1
    # dictionary with user name as key and percentage result for that user a value
    percentage = {i: (user_dict[i][1] / user_dict[i][0]) * 100 for i in user_dict if user_dict[i][0] != 0 }
    return percentage

def user_complete(table2 = tasks):
    '''
    user_complete function calculates and returns the dictionaty showing the percentage of the tasks assigned to that user that have been completed
    param: table1: takes the name of the file containing user information as an argument
    param: table2: takes the name of the file containing task information as an argument
    '''
    uitem_list = all_users()
    # dictionary where user name is a key and value is [user total tasks : user completed tasks]
    user_dict = {user : [0, 0] for user in uitem_list}
    titem_list = list_tasks(table2)
    for user in user_dict:
        for item in titem_list:
            # checking if task in the tasks list is for the user
            if user in item[0]:
                user_dict[user][0] += 1
                # checking if the user task is completed
                if item[-1].lower() == "yes":
                    user_dict[user][1] += 1
    # dictionary with user name as key and percentage result for that user a value
    percentage = {user: (user_dict[user][1] / user_dict[user][0]) * 100 for user in user_dict if user_dict[user][0] != 0}
    return percentage

def user_details(table2 = tasks): 
    '''
    user_details function calculates and returns total numbers of tasks assigned to each user
    param: table1: takes the name of the table containing user information as an argument
    param: table2: takes the name of the table containing task information as an argument
    '''
    uitem_list = all_users()
    # creating a dictionary that will store the username as key and count as value
    user_dict = {user : 0 for user in uitem_list}
    titem_list = list_tasks(table2)
    for user in user_dict:
        # if user is in tasks table, updating user's value by adding 1
        for item in titem_list:
            if user == item[0]:
                user_dict[user] += 1
    return user_dict

def percentage_total(table1 = users, table2 = tasks):
    '''
    precentage_total function calculates and returns the percentage of the total number of tasks that have been assigned to that user in a dictionary
    param: table1: takes the name of the table containing user information as an argument
    param: table2: takes the name of the table containing task information as an argument
    '''
    total_tasks = tasks_total(table2)
    user_dict = user_details(table2)
    # calculating what percentage user's tasks are of the total tasks
    # storing it in a new dictionary with user name as key an percentage result for that user a value
    perc_total = {user: (user_dict[user] / total_tasks) * 100 for user in user_dict}
    return perc_total  

def report_generator(table1 = users, table2 = tasks):
    '''
    report_generator function formats and prints out the report data about the tasks
    param:table2: takes a name of the table containing tasks data as an argument
    '''
    report_window = Toplevel()
    # setting the icon and the title for the new task window
    report_window.title("Database report")
    report_window.iconbitmap("images/icon.ico")
    report_window.geometry("800x700")
    report_window.configure(bg = "#330066")

    report_window.grid_columnconfigure(0, weight=1)
    report_window.grid_rowconfigure(0, weight=1)

    c = Canvas(report_window, bg = "blue")
    c.grid(row = 0, column = 0, sticky = NSEW)

    s = Scrollbar(report_window, orient = "vertical")
    s.grid(row = 0, column = 1, sticky = NSEW)

    s.configure(command = c.yview)

    # header
    c.create_text(400, 40, text = "Database Report:", fill = "#ffffe6", font= ("Arial", 14))

    # tasks report
    c.create_text(400, 150, text = f'''                       ═══════════   Overview of all tasks created and tracked   ═══════════\n
                            The total number of tasks is:                                            \t{tasks_total(table2)}
                            The total number of completed tasks is:                             \t{tasks_complete(table2)}
                            The total number of uncompleted tasks:                            \t{tasks_noncomplete(table2)}
                            The total number of uncompleted tasks that are overdue is:  \t{uncomp_overdue(table2)}
                            The percentage of tasks that are incomplete is:                    \t{round(uncom_percentage(table2))}%
                            The percentage of tasks that are overdue is:                       \t{round(overdue_percentage(table2))}%\n
 ════════════════════════════════════════════════════════════════════════''',
    fill = "#ffffe6", font = ("Arial", 10))

    # importing all user functions as variables for users report
    incomp_overdue = user_inc_od(table2)
    not_completed = user_incomplete(table2)
    completed = user_complete(table2)
    perc_total = percentage_total(table1, table2)
    user_total = user_details(table2)

    y = 200
    for user in user_total.keys():
        # for each user creating a formatted report, extracting that user's data from each dictionary that has individual user reports
        # adding every user's report separately to the user_statistics variable
        if user_total[user] > 0:
            y += 150
            c.create_text(400, y, text = f'''                       ─────────────  Overview of the tasks for {user} ─────────────\n
        The total number of tasks assigned to {user}:                                                                                   {user_total[user]}
        The percentage of the total number of tasks that have been assigned {user}:                                       {round(perc_total[user])}%
        The percentage of the tasks assigned to {user} that have been completed:                                          {round(completed[user])}%
        The percentage of the tasks assigned to {user} that haven't been completed:                                       {round(not_completed[user])}%
        The percentage of the tasks assigned to that user that have not yet been completed and are overdue:    {round(incomp_overdue[user])}%\n
─────────────────────────────────────────────────────────────────────────\n\n''',
        fill = "#ffffe6", font = ("Arial", 10), justify= LEFT)
        else:
            y += 150
            c.create_text(400, y, text = f'''                       ───────────── Overview of the tasks for {user} ─────────────\n
        No tasks exist for {user}\n
─────────────────────────────────────────────────────────────────────────\n\n''', 
        fill = "#ffa366", font = ("Arial", 10))

def all_users(table1 = users):
    '''
    all_users function returns a list of all users in the database
    param: table 1 takes the name if the table with users data as an argument
    '''            
    cursor.execute(f"SELECT user FROM {table1}")
    all_users = [unit for item in cursor for unit in item] 
    return all_users

def mark_complete(*args, table2 = tasks):
    '''
    mark_complete function sets the completion status of the chosen task to "yes"
    '''
    task_name = var.get()
    status = ("Yes")

    cursor.execute(f'''UPDATE {table2}
                        SET is_complete = ? WHERE task_name = ?''', (status, task_name))
    con.commit()
    response = messagebox.showinfo("Updated", f"Task {task_name} set as complete.")

def get_task(*args, table2 = tasks):
    '''
    get_task function gets the full details of the task selected and displayys them on the screen
    param: table2: takes the name of the table containing tasks data as n argument
    '''
    global choice

    # getting the task selection
    task_name = str(var.get())

    # getting all information on that task from the db
    cursor.execute(f"SELECT * FROM {table2} WHERE task_name = ?", (task_name,))
    task_list = [unit for item in cursor for unit in item]

    task_info = Label(my_tasks_window, text = f'''           
    Task:                                             {task_list[1]}\n
    Assigned to:                                  {task_list[0]}\n
    Date assigned:                              {task_list[3]}\n
    Due date:                                       {task_list[4]}\n
    Task complete?                             {task_list[5]}\n
    Task description:                           {task_list[2]}\n
                                                ''',
    bg = "#330066", fg = "#ffffe6", font = ("Arial", 11), wraplength=550, justify=LEFT)
    task_info.grid(row = 2, column = 0, padx = (60, 30), pady = 5, sticky=NSEW)

    options = ["Mark this task as complete"]

    choice = StringVar()
    choice.set("Select an option")
    choice.trace("w", mark_complete)

    change_option = OptionMenu(my_tasks_window, choice, *options)
    change_option.grid(row = 3, column = 0, padx = 200, pady = 10, sticky = EW)
    change_option.config(width = 50, height=1, bg = "#ffffff", highlightbackground="#ffffff", bd = 0)

def view_mine(table2 = tasks):
    '''
    view_mine function finds the username in the list of tasks and prints out all the tasks for that user. 
    or prints out an error message if no tasks were found for the user.
    param: table2: takes the name of the table containing tasks data as an argument
    '''
    global var
    global my_tasks_window

    username = user_box.get()
    cursor.execute(f"SELECT * FROM {table2}")
    # variable storing all data from the table
    tasks_data = cursor.fetchall()
    # variable storing usernames
    users_with_task = [row[0] for row in tasks_data]
    # if username of logged in user not in the usernames list, message displayed
    # if it is AND it's in the 'user' column, printing all task data for that user
    if username not in users_with_task:
        response = messagebox.askquestion("My tasks", "No tasks found in the database.")
    else:
        my_tasks_window = Toplevel()
        # setting the icon and the title for the new task window
        my_tasks_window.title("My tasks")
        my_tasks_window.iconbitmap("images/icon.ico")
        my_tasks_window.geometry("750x530")
        my_tasks_window.configure(bg = "#330066")

        header = Label(my_tasks_window, text = f"{username} tasks:", font = 13,
                       fg = "#ffffe6", bg = "#330066")
        header.grid(row = 0, column = 0, padx = 100, pady = 40, sticky = NSEW)

        cursor.execute(F"SELECT user, task_name FROM {table2}")
        # list of tuples with user and task name
        tasks = [item for item in cursor]
        dd_options = []
        for item in tasks:
            if username == item[0]:
                dd_options.append(item[1])

        var = StringVar()
        var.set("Choose the task name.")
        var.trace("w", get_task)

        dropdown = OptionMenu(my_tasks_window, var, *dd_options)
        dropdown.grid(row = 1, column = 0, padx = 200, pady = 10, sticky = EW)
        dropdown.config(width = 50, height=1, bg = "#ffffff", highlightbackground="#ffffff", bd = 0)

def to_user_choice():
    '''
    to_users_choice function clears the canvas and gpes back to user choice options menu
    '''
    c.destroy()
    s.destroy()
    s1.destroy()

def submit_update(table2 = tasks):
    '''
    submit_update function takes the task selected by the user, the new data that was entered and updates the task table with new information
    param: table2: takes the name of the table containing tasks data as an argument
    '''
    # getting the picked task name
    task = click_var.get()
    users = all_users()

    # updating username
    if edit_var.get() == "Edit username":
        if new_data.get().lower() not in users:
            response = messagebox.showerror("Error", "User not in the database")
        else:
            cursor.execute(f"UPDATE {table2} SET user = ? WHERE task_name = ?", (new_data.get(), task))
            con.commit()
            response = messagebox.showinfo("Updated", "Task updated")
            new_details_window.destroy()

    # updating task name
    elif edit_var.get() == "Edit task name":
            cursor.execute(f"UPDATE {table2} SET task_name = ? WHERE task_name = ?", (new_data.get(), task))
            con.commit()
            response = messagebox.showinfo("Updated", "Task updated")
            new_details_window.destroy()

    # updating task description
    elif edit_var.get() == "Edit task description":
        cursor.execute(f"UPDATE {table2} SET task_dets = ? WHERE task_name = ?", (new_data.get(), task))
        con.commit()
        response = messagebox.showinfo("Updated", "Task updated")
        new_details_window.destroy()

    # updating due date    
    elif edit_var.get() == "Edit due date":
        ref_date = "%Y-%m-%d"    
        try:
            date = time.strptime(new_data.get(), ref_date)
            cursor.execute(f"UPDATE {table2} SET due_date = ? WHERE task_name = ?", (new_data.get(), task))
            con.commit()
            response = messagebox.showinfo("Updated", "Task updated")
            new_details_window.destroy()
        except ValueError:
            response = messagebox.showerror("Error", "Date format should be 'YYY-MM-DD")

    # updating completion status    
    elif edit_var.get() == "Edit completion status":
        if new_data.get().capitalize() == "Yes" or new_data.get().capitalize() == "No":
            cursor.execute(f"UPDATE {table2} SET is_complete = ? WHERE task_name = ?", (new_data.get(), task))
            con.commit()
            response = messagebox.showinfo("Updated", "Task updated")
            new_details_window.destroy()
        else:
            response = messagebox.showerror("Error", "Entry should be 'Yes' or 'No'")


def edit_task(*args, table2 = tasks):
    '''
    edit_task function opens a nes window and takes new task details based on users edition selection
    '''   
    global new_data
    global new_details_window

    # getting the picked task name
    task = click_var.get()

    # new window for entering new task details
    new_details_window = Toplevel()
    new_details_window.title("Edit task")
    new_details_window.iconbitmap("images/icon.ico")
    new_details_window.geometry("500x350")
    new_details_window.configure(bg = "#330066")

    entry_frame = Frame(new_details_window, bg = "#330066", width=500, height=350, border=0)
    entry_frame.grid(row = 0, column = 0, sticky = NSEW)

    header = Label(entry_frame, text = "New details to be added to the task:", font = ("Arial", 13, "bold"),
                    fg = "#ffffe6", bg = "#330066")
    header.grid(row = 0, column = 0, columnspan = 3, padx = 100, pady = 30, sticky = NSEW)
    
    new_data = Entry(entry_frame, font = ("Arial", 12),
                    bd = 0, highlightcolor="#000066", highlightthickness = 1, highlightbackground="#e0e0eb")
    new_data.grid(row = 1, column = 1, padx = 20, pady = 30, sticky = NSEW)

    change_btn = Button(entry_frame, text = "Save changes", command = submit_update,
                        font = ("Arial", 10, "bold"), bg = "#ff5c33", fg = "#ffffe6", width = 16)
    change_btn.grid(row = 2, column = 1, padx = 50, pady = 10, sticky = NSEW)

    # changing the entry window label based on user's change selection
    if edit_var.get() == "Edit username":
        new_data_label = Label(entry_frame, text = "Enter the new username", font = ("Arial", 10, "bold"),
                    fg = "#ffffe6", bg = "#330066")
        new_data_label.grid(row = 1, column = 0,  padx = 30, pady = 30, sticky = NSEW)
    elif edit_var.get() == "Edit task name":
        new_data_label = Label(entry_frame, text = "Enter the new task name", font = ("Arial", 10, "bold"),
                    fg = "#ffffe6", bg = "#330066")
        new_data_label.grid(row = 1, column = 0,  padx = 30, pady = 30, sticky = NSEW)
    elif edit_var.get() == "Edit task description":
        new_data_label = Label(entry_frame, text = "Enter the new task description", font = ("Arial", 10, "bold"),
                    fg = "#ffffe6", bg = "#330066")
        new_data_label.grid(row = 1, column = 0,  padx = 30, pady = 30, sticky = NSEW)
    elif edit_var.get() == "Edit due date":
        new_data_label = Label(entry_frame, text = "New due date (YYYY-MM-DD)", font = ("Arial", 10, "bold"),
                    fg = "#ffffe6", bg = "#330066")
        new_data_label.grid(row = 1, column = 0,  padx = 30, pady = 25, sticky = NSEW)
    elif edit_var.get() == "Edit completion status":
        new_data_label = Label(entry_frame, text = "Completed? Yes/No", font = ("Arial", 10, "bold"),
                    fg = "#ffffe6", bg = "#330066")
        new_data_label.grid(row = 1, column = 0,  padx = 30, pady = 25, sticky = NSEW)
    elif edit_var.get() == "Delete task":
        response = messagebox.askquestion("Delete", f"Delete '{task}' task?")
        if response == "yes":
            new_details_window.destroy()
            cursor.execute(f"DELETE FROM {table2} WHERE task_name = ?", (task,))
            con.commit()
            response = messagebox.showinfo("Deleted", "Task deleted")
            all_tasks_window.destroy()
            c.update()
        if response == "no":
            new_details_window.destroy()
            response = messagebox.showinfo("Info", "No changes were made to the task")
  
def on_radio_click():
    '''
    on_click function displays the dropdown to choose what part of the task to edit
    '''
    change_menu.grid(row = 1, column = 1)

def pick_task_win():
    '''
    pick_task_win undyion closes the window of task selection and opes a new window with the list of all the tasks and radio buttons to chose the task to be edited
    '''
    global click_var
    global pick_task_window
    global change_menu
    global edit_var
    # destroying last window
    all_tasks_window.destroy()

    # opening a new window
    pick_task_window = Toplevel()
    pick_task_window.title("Edit task")
    pick_task_window.iconbitmap("images/icon.ico")
    pick_task_window.geometry("765x548")
    pick_task_window.configure(bg = "#330066")
    pick_task_window.resizable(False, False)

    # first frame for the pick task window
    pick = Frame(pick_task_window, bg = "#330066", width=742, height=525, border=0)
    pick.grid(row = 0, column = 0)

    header = Label(pick, text = "Select a task to be edited:", font = ("Arial", 13, "bold"),
                    fg = "#ffffe6", bg = "#330066")
    header.grid(row = 0, column = 0, columnspan = 2, padx = 300, pady = 35, sticky = NSEW)

    radio_buttons = []
    y = 1
    click_var = StringVar()
    for task in view_all_task_list:
        radio = Radiobutton(pick, text = f"Task name:\n\n{task[1]}", variable = click_var, value = f"{task[1]}", indicatoron= True, command= on_radio_click, 
                            justify=LEFT, padx = 80, pady = 8, wraplength=150,
                            fg="#ffffe6", font = ("Arial", 11), anchor=W, background = "#330066", activebackground="#5900b3", selectcolor="#47476b")
        radio.grid(row = y, column =0, sticky = NSEW)
        radio_buttons.append(radio)
        y += 1

    # options menu
    options = ["Edit username", "Edit task name", "Edit task description", "Edit due date", "Edit completion status", "Delete task"]

    edit_var = StringVar()
    # set the default value of the options menu
    edit_var.set("Edit task")  
    edit_var.trace("w", edit_task)

    change_menu = OptionMenu(pick, edit_var, *options)
    
    change_menu.configure(bg = "#8585ad", highlightbackground="#8585ad", relief = RAISED, height = 1, font = ("Arial", 10, "bold"), fg = "#ffffe6",
                          anchor = W, padx=10)

def get_user_task(*args, table2 = tasks):
    '''
    get_user_task function gets the full details of the all tasks for the selecter user
    param: table2: takes the name of the table containing tasks data as n argument
    '''
    global c
    global s
    global s1
    global view_all_task_list

    # getting the task selection
    user_name = u_choice.get()

    c = Canvas(all_tasks_window, bg = "#330066", width=742, height=525, border=0)
    c.grid(row = 0, column = 0)

    # back button
    back_button = Button(all_tasks_window, text = "Back to user search", command = to_user_choice,
                    font = ("Arial", 10, "bold"), bg = "#ff5c33", fg = "#ffffe6", width = 16, height = 1)
    back_button_window = c.create_window(295, 50, anchor=NW, window=back_button)
   
    if user_box.get() == "admin":
        edit_button = Button(all_tasks_window, text = "Edit task", command = pick_task_win,
                         font = ("Arial", 10, "bold"), bg = "#8585ad", fg = "#ffffe6", width = 10, height = 1)
        edit_button_window = c.create_window(20, 50, anchor=NW, window=edit_button)

    # vertical scrollbar
    s = Scrollbar(all_tasks_window, orient = "vertical")
    s.grid(row = 0, column = 1, sticky = NSEW)

    s.configure(command = c.yview)

    c.create_text(375, 36, text = f"List of all tasks for {user_name}:\n", fill = "#ffffe6", font = ("Arial", 14, "bold"), justify= CENTER)

    # horizontal scrollbar
    s1 = Scrollbar(all_tasks_window, orient = "horizontal")
    s1.grid(row = 1, column = 0, columnspan=2, sticky = NSEW)

    s1.configure(command = c.xview)
    
    # getting all information on tasks for picked user from the db
    cursor.execute(f"SELECT * FROM {table2} WHERE user = ?", (user_name,))
    view_all_task_list = [unit for unit in cursor]
    num = 230
    x = 380

    # task display
    for task in view_all_task_list:
        c.create_text(x, num, text = f''' ═══════════════════════════════════════════════════════ 
        Task:                                             {task[1]}\n
        Assigned to:                                  {task[0]}\n
        Date assigned:                              {task[3]}\n
        Due date:                                       {task[4]}\n
        Task complete?                             {task[5]}\n
        Task description:                           {task[2]}\n
                                                    ''',
        fill = "#ffffe6", font = ("Arial", 11), justify=LEFT)
        num += 230

def view_all_tasks():
    '''
    view_all_tasks function displays all tasks filtered by username. 
    or prints out a message if no tasks were found for the user.
    param: table2: takes the name of the table containing tasks data as an argument
    param: table1: takes the name of the table containing user data as an argument
    '''

    global u_choice
    global all_tasks_window

    all_tasks_window = Toplevel()
    # setting the icon and the title for the new task window
    all_tasks_window.title("My tasks")
    all_tasks_window.iconbitmap("images/icon.ico")
    all_tasks_window.geometry("765x548")
    all_tasks_window.configure(bg = "#330066")
    all_tasks_window.resizable(False, False)

    dropdown_frame = Frame(all_tasks_window, padx = 0, pady = 0, bg = "#330066")
     
    header = Label(dropdown_frame, text = f"View all tasks for:", font = 13,
                    fg = "#ffffe6", bg = "#330066")
    header.grid(row = 0, column = 0, padx = 100, pady = 40, sticky = NSEW)

    # list of usere names
    user_options = all_users()
 
    u_choice = StringVar()
    u_choice.set("Choose the username")
    u_choice.trace("w", get_user_task)

    dropdown = OptionMenu(dropdown_frame, u_choice, *user_options)
    dropdown.grid(row = 1, column = 0, padx = 200, pady = 10, sticky = EW)
    dropdown.config(width = 50, height=1, bg = "#ffffff", highlightbackground="#ffffff", bd = 0)

    dropdown_frame.grid(row = 0, column=0, sticky = NSEW)

def statistics(table1 = users, table2 = tasks):
    '''
    statistics function displays the total number of tasks and the total number of users
    param: table1: takes th name of the table containing user data as an argument
    param: table2: takes the name of the table containing tasks data as an argument
    '''
    stats_window = Toplevel()
    # setting the icon and the title for the new task window
    stats_window.title("Task and user statistics")
    stats_window.iconbitmap("images/icon.ico")
    stats_window.geometry("759x530")
    stats_window.configure(bg = "#330066")
    stats_window.resizable(False, False)

    header = Label(stats_window, text = "Database statistics:", font = ("Arial", 14, "bold"),
                    fg = "#ffffe6", bg = "#330066", padx = 280, pady = 20)
    header.grid(row = 0, column = 0, sticky = NSEW)

    stats = Label(stats_window, text = f'''
┌──────────────────────────────┐
    Total number us users in the database: {users_total(table1)}
    Total number of tasks in the database: {tasks_total(table2)}
└──────────────────────────────┘
    ''', 
    bg = "#330066", fg = "#ffffe6", font = ("Arial", 11), padx = 200, pady = 20)
    stats.grid(row = 1, column = 0, sticky = NSEW)


def exit_admin_program():
    '''
    exit_program command closes the amdin menu window and goes back to login page
    '''
    admin_menu_frame.destroy()
    password_box.delete(0, END)
    user_box.delete(0, END)

def exit_user_program():
    '''
    exit_program command closes the user menu window and goes back to login page
    '''
    user_menu_frame.destroy()
    password_box.delete(0, END)
    user_box.delete(0, END)


###################  MAIN MENU #########################
########################################################
########################################################
def admin_menu_page():
    '''
    admin_menu page function displays the admin menu options and sends the admin to the appropriate page depending on his selection
    '''
    global admin_menu_frame

    admin_menu_frame = Frame(root, padx = 0, pady = 0)

    # admin menu label
    admin_menu_lbl = Label(admin_menu_frame, text = "══════════════════════════════════════════ ADMIN MENU ═════════════════════════════════════════", bg = "#330066", font = ("Verdana", 10), fg = "#f2e6ff")
    admin_menu_lbl.grid(row = 0, column = 0, columnspan= 4)

    # menu buttons
    # add user
    add_user_btn = Button(admin_menu_frame, text="Add User", command = reg_user,
                          image = add_user, compound = TOP, padx = 14, pady = 25, bg="#5900b3", 
                          activebackground = "#ccb3ff", bd = 0.5, font = ("Calibri", 14, "bold"), fg = "#ffffe6")
    add_user_btn.grid(row = 1, column = 0, sticky = NSEW)

    # add task
    add_task_btn = Button(admin_menu_frame, text="Add Task", command = new_task,
                          image = add_task, compound = TOP, padx = 63, pady = 25, bg = "#6600cc", 
                          activebackground = "#ccb3ff", font = ("Calibri", 14, "bold"), fg = "#ffffe6")
    add_task_btn.grid(row = 1, column = 1, columnspan=2, sticky = NSEW)

    # generate report
    report_btn = Button(admin_menu_frame, text="Generate Report", command = report_generator,
                        image = report, compound = TOP, padx = 5, pady = 35, bg = "#7300e6", 
                        activebackground = "#ccb3ff", font = ("Calibri", 14, "bold"), fg = "#ffffe6")
    report_btn.grid(row = 1, column = 3, sticky = NSEW)

    # view my tasks
    view_mine_btn = Button(admin_menu_frame, text="View My Tasks", command = view_mine,
                           image = view_my, compound = TOP, padx = 7, 
                           pady = 25, bg = "#7300e6", activebackground = "#ccb3ff", font = ("Calibri", 14, "bold"), fg = "#ffffe6")
    view_mine_btn.grid(row = 2, column = 0, sticky = NSEW)

    # view all tasks
    view_all_btn = Button(admin_menu_frame, text="View All Tasks", command = view_all_tasks,
                          image = view_all, compound = TOP, padx = 7, 
                          pady = 25, bg = "#6600cc", activebackground = "#ccb3ff", font = ("Calibri", 14, "bold"), fg = "#ffffe6")
    view_all_btn.grid(row = 2, column = 1, sticky = NSEW)

    # see total amount of tasks and users
    users_tasks_btn = Button(admin_menu_frame, text="Users and Tasks", command = statistics, 
                             image = tasks_users, compound = TOP,
                             padx = 7, pady = 25, bg = "#5900b3", activebackground = "#ccb3ff", font = ("Calibri", 14, "bold"), fg = "#ffffe6")
    users_tasks_btn.grid(row = 2, column = 2, sticky = NSEW)

    # exit
    exit_btn = Button(admin_menu_frame, text="Exit", command = exit_admin_program,
                      image = exit, compound = TOP, padx = 10, pady = 5, bg = "#330066", 
                      activebackground = "#cc0000", font = ("Calibri", 14, "bold"), fg = "#ffffe6")
    exit_btn.grid(row = 2, column = 3, sticky = NSEW)


    admin_menu_frame.grid(row = 0, column=0, sticky = W+E)

def user_menu_page():
    '''
    user_menu_page function displays the user menu in a new frame
    '''
    global user_menu_frame

    user_menu_frame = Frame(root, padx = 0, pady = 0)

    # user menu label
    user_menu_lbl = Label(user_menu_frame, text = "══════════════════════════════════════════ USER MENU ═════════════════════════════════════════", bg = "#330066", font = ("Verdana", 10), fg = "#f2e6ff")
    user_menu_lbl.grid(row = 0, column = 0, columnspan= 4)

    # buttons 
    add_task_btn = Button(user_menu_frame, text="Add Task", command = new_task,
                          image = add_task, compound = TOP,
                          padx = 14, pady = 99, bg="#6600cc", activebackground = "#ccb3ff", bd = 0.5, 
                          font = ("Calibri", 14, "bold"), fg = "#ffffe6")
    add_task_btn.grid(row = 1, column = 0, sticky = NSEW)

    # view my tasks
    view_mine_btn = Button(user_menu_frame, text="View My Tasks", command = view_mine,
                           image = view_my, compound = TOP,
                          padx = 14, pady = 99, bg="#7300e6", activebackground = "#ccb3ff", bd = 0.5, 
                          font = ("Calibri", 14, "bold"), fg = "#ffffe6")
    view_mine_btn.grid(row = 1, column = 1, sticky = NSEW)

    # view all tasks
    view_all_btn = Button(user_menu_frame, text="View All Tasks", command = view_all_tasks,
                          image = view_all, compound = TOP,
                          padx = 14, pady = 99, bg="#6600cc", activebackground = "#ccb3ff", bd = 0.5, 
                          font = ("Calibri", 14, "bold"), fg = "#ffffe6")
    view_all_btn.grid(row = 1, column = 2, sticky = NSEW)   

    # exit
    exit_btn = Button(user_menu_frame, text="Exit", command = exit_user_program,
                      image = exit, compound = TOP,
                      padx = 10, pady = 99, bg = "#330066", activebackground = "#cc0000",
                      font = ("Calibri", 14, "bold"), fg = "#ffffe6")
    exit_btn.grid(row = 1, column = 3, sticky = NSEW)

    user_menu_frame.grid(row = 0, column=0)

login_page()

root.mainloop()