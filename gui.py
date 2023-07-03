import os
from db_manager import Database
import time
import datetime
from datetime import date
import re

import customtkinter as ctk
from PIL import Image
import tkinter as tk
from tkinter import messagebox
from tkcalendar import *
import sys

DATABASE = Database("user_data", "user_task")
ctk.set_default_color_theme(r"C:\Users\rishk\tsk maanger CLASS BASED GUI\custom_style.json")

HEADER_FONT = ("Arial", 20)
ENTRY_FONT = ("Arial", 16)
ENTRY_WIDTH = 180
BUTTON_WIDTH = 160
BUTTON_HEIGHT = 35
BUTTON_FONT = ("Arial", 14, "bold")
DATA_FONT = ("Arial", 14)


class TaskManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager")
        # icon
        self.iconbitmap("images/icon.ico")
        self.geometry("1180x436")
        self.resizable(False, False)
        self.login_frame = None
        self.admin_menu_frame = None
        self.user_menu_frame = None

        self.login()

    def login(self):
        if self.admin_menu_frame is not None:
            self.admin_menu_frame.destroy()

        if self.user_menu_frame is not None:
            self.user_menu_frame.destroy()

        self.login_frame = LogIn(self)

    def create_admin_menu(self):
        if self.login_frame is not None:
            self.login_frame.destroy()

        self.admin_menu_frame = AdminMenu(self)

    def create_user_menu(self):
        if self.login_frame is not None:
            self.login_frame.destroy()

        self.user_menu_frame = UserMenu(self)


class ImageManager:
    def __init__(self, image_folder):
        self.image_folder = image_folder
        self.images = {}

    def load_image(self, image_name, size=(80, 80)):
        image_path = os.path.join(self.image_folder, image_name)
        image = ctk.CTkImage(Image.open(image_path), size=size)
        self.images[image_name] = image
        return image

    def get_image(self, image_name, size=(80, 80)):
        if image_name in self.images:
            return self.images[image_name]
        else:
            self.load_image(image_name, size=size)


class ShowHideButton:
    """
    class manages the show_hide button images and password entry field display
    """
    def __init__(self, image_manager):
        self.image_manager = image_manager
        self.show_image = self.image_manager.get_image("show.png", size="24x24")
        self.hide_image = self.image_manager.get_image("hide.png", size="24x24")

    def show_hide_password(self, password_entries, show_hide_btn):
        for entry in password_entries:
            if entry.cget("show") == "●":
                entry.configure(show="")
                show_hide_btn.configure(image=self.hide_image)
            else:
                entry.configure(show="●")
                show_hide_btn.configure(image=self.show_image)


class LogIn(ctk.CTkFrame):
    """
    LogIn class creates a frame allowing to enter login details
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.password_entry = None
        self.show_hide_btn = None
        self.user_entry = None
        self.picked_user = None

        self.command = CommandHandler()

        # configure grid
        self.rowconfigure(0, weight=2)
        self.rowconfigure((1, 2), weight=1)
        self.rowconfigure(3, weight=4)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=3)

        self.image_manager = ImageManager(r"C:\Users\rishk\tsk maanger CLASS BASED GUI\images")
        self.image = self.image_manager.get_image("show.png", size=(24, 24))
        self.show_hide_btn_img = self.image_manager.get_image("show.png", size=(24, 24))

        self.show_hide_action = ShowHideButton(self.image_manager)

        self.create_login_widgets()

        self.pack(expand=True, fill="both")

    def create_login_widgets(self):
        # creating widgets
        # labels
        login_lbl = ctk.CTkLabel(self, text="Log In", font=HEADER_FONT, anchor="center")
        username_lbl = ctk.CTkLabel(self, text="Enter username", font=ENTRY_FONT)
        password_lbl = ctk.CTkLabel(self, text="Enter password", font=ENTRY_FONT)

        # entry widgets
        self.user_entry = ctk.CTkEntry(self, font=ENTRY_FONT, width=ENTRY_WIDTH)
        self.password_entry = ctk.CTkEntry(self, font=ENTRY_FONT, width=ENTRY_WIDTH, show="●")

        # buttons
        submit_btn = ctk.CTkButton(self, text="Submit", command=self.user_check,
                                   width=BUTTON_WIDTH, height=BUTTON_HEIGHT, font=BUTTON_FONT)
        show_hide_btn = ctk.CTkButton(self, image=self.show_hide_btn_img, text="",
                                      fg_color="transparent", hover_color="#330066",
                                      command=self.show_hide_password)

        # placing widgets
        login_lbl.grid(row=0, column=0, columnspan=3, sticky="nsew")
        username_lbl.grid(row=1, column=0, sticky="E", padx=(100, 0))
        password_lbl.grid(row=2, column=0, sticky="E", padx=(100, 0))
        self.user_entry.grid(row=1, column=1, sticky="EW", padx=(50, 0))
        self.password_entry.grid(row=2, column=1, sticky="EW", padx=(50, 0))
        submit_btn.grid(row=3, column=0, columnspan=3, sticky="N", padx=160, pady=10)
        show_hide_btn.grid(row=2, column=2, sticky="W")

        self.show_hide_btn = show_hide_btn

    def show_hide_password(self):
        """
        method passes information to the method changing the display of password entry field and show/hide button image
        """
        self.show_hide_action.show_hide_password([self.password_entry], self.show_hide_btn)

    def user_check(self):
        """
        passing arguments to check against the database
        """
        self.picked_user = self.user_entry.get()
        self.command.store_username(self.picked_user)

        self.command.user_login(self.user_entry, self.password_entry, self)



class CalendarPanel(ctk.CTkFrame):
    """
    CalendarPanel class is a frame containing date picker calendar and a button, that allows to grab the selected date
    """
    def __init__(self, task_window, parent, start_position, end_position):
        """
        task_window: widget: a window that will contain the frame
        start_position: position at which the frame widget containing calendar will be placed when hidden
        end_position: position at which the frame widget containing calendar will be placed when shown
        """
        super().__init__(parent)
        self.command = CommandHandler()
        self.task_window = task_window
        self.start_position = start_position
        self.end_position = end_position
        self.width = abs(self.start_position - self.end_position)

        self.command = CommandHandler()

        # sliding animation
        self.pos = start_position
        self.in_start_pos = True

        # always getting today's date to be default on the calendar
        today = date.today()
        today_string = today.strftime("%Y-%m-%d")
        year = int(today_string.split("-")[0])
        month = int(today_string.split("-")[1])
        day = int(today_string.split("-")[2])

        # date picked calendar
        self.cal = Calendar(self, selectmode="day", year=year, month=month, day=day)
        # picked date format
        self.cal.config(date_pattern="yyyy-mm-dd")
        self.cal.pack(fill="both", expand=True)
        self.picked_date = None

        submit_btn = ctk.CTkButton(self, text="Select", font=BUTTON_FONT, corner_radius=0, fg_color="#323438",
                                   command=self.get_picked_date)
        submit_btn.pack(fill="both", expand=True, anchor="center")

        self.place(relx=self.start_position, rely=0, relwidth=self.width, relheight=1)

    def get_picked_date(self):
        """
        method grabs the date that was picked in the calendar
        takes the parent window, which was passed as an parameter of the class and inserts the selected date into the
        parent's date entry field
        """
        self.picked_date = self.cal.get_date()

        self.task_window.due_date_e.delete(0, "end")
        self.task_window.due_date_e.insert(0, self.picked_date)

        self.task_window.calendar()


class AddUserWindow(ctk.CTkToplevel):
    """
        AddTaskWindow class opens a new toplevel window to get information containing new user details and it allows to add
        those details into the database.
        """
    def __init__(self):
        super().__init__()
        self.geometry("800x350")
        self.title("Register new user")
        self.iconbitmap("images/icon.ico")

        self.image_manager = ImageManager(
            r"C:\Users\rishk\tsk maanger CLASS BASED GUI\images")
        self.image = self.image_manager.get_image("show.png", size=(24, 24))
        self.show_hide_btn_img = self.image_manager.get_image("show.png", size=(24, 24))

        self.show_hide_action = ShowHideButton(self.image_manager)

        self.commands = CommandHandler()

        # creating frame widgets
        self.header = ctk.CTkLabel(self, text="Enter the new user details", font=HEADER_FONT)
        self.username_label = ctk.CTkLabel(self, text="Enter username", font=ENTRY_FONT)
        self.password_label = ctk.CTkLabel(self, text="Enter password", font=ENTRY_FONT)
        self.conf_pass_label = ctk.CTkLabel(self, text="Confirm password", font=ENTRY_FONT)

        self.username_entry = ctk.CTkEntry(self, font=ENTRY_FONT, width=ENTRY_WIDTH)
        self.password_entry = ctk.CTkEntry(self, font=ENTRY_FONT, width=ENTRY_WIDTH, show="●")
        self.conf_pass_entry = ctk.CTkEntry(self, font=ENTRY_FONT, width=ENTRY_WIDTH, show="●")

        self.show_hide_btn = ctk.CTkButton(self, text="", image=self.show_hide_btn_img,
                                           fg_color="transparent", hover_color="#330066",
                                           command=self.show_hide_password)
        self.submit_btn = ctk.CTkButton(self, text="Submit", command=self.add_new_user,
                                        width=BUTTON_WIDTH, height=BUTTON_HEIGHT, font=BUTTON_FONT)

        # placing widgets
        self.header.grid(row=0, column=0, columnspan=3, padx=(100, 70), pady=35, sticky="nsew")
        self.username_label.grid(row=1, column=0, padx=(200, 15), pady=5, ipady=3, sticky="ew")
        self.password_label.grid(row=2, column=0, padx=(200, 15), pady=5, ipady=3, sticky="ew")
        self.conf_pass_label.grid(row=3, column=0, padx=(200, 15), pady=5, ipady=3, sticky="ew")

        self.username_entry.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        self.password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")
        self.conf_pass_entry.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")

        self.show_hide_btn.grid(row=2, column=2, sticky="e", padx=10)
        self.submit_btn.grid(row=4, column=1, padx=32, pady=15, ipady=3, sticky="w")

        self.focus()

    def show_hide_password(self):
        """
        method passing local arguments to change password entry field display and the show_hide button image
        """
        self.show_hide_action.show_hide_password([self.password_entry, self.conf_pass_entry], self.show_hide_btn)

    def add_new_user(self):
        """
        method passes newly entered user information to be checked and added to the database
        """
        success = self.commands.add_user(self.username_entry, self.password_entry, self.conf_pass_entry)
        if success:
            self.destroy()


class AddTaskWindow(ctk.CTkToplevel):
    """
    AddTaskWindow class opens a new toplevel window to get information containing new task details and it allows to add
    those details into the database.
    """
    def __init__(self):
        super().__init__()
        self.geometry("800x350")
        self.title("Add new task")

        self.command = CommandHandler()

        # date picker initial settings
        self.cal_start_pos = 1
        self.cal_end_pos = 0.7
        self.calendar_panel = CalendarPanel(self, self, self.cal_start_pos, self.cal_end_pos)
        self.pos = self.calendar_panel.pos
        self.width = self.calendar_panel.width

        # creating window widgets
        # labels
        self.header = ctk.CTkLabel(self, text="Enter the task details", font=HEADER_FONT)
        self.username = ctk.CTkLabel(self, text="Enter username", font=ENTRY_FONT)
        self.task_title = ctk.CTkLabel(self, text="Task title", font=ENTRY_FONT)
        self.task_desc = ctk.CTkLabel(self, text="Task description", font=ENTRY_FONT)
        self.due_date = ctk.CTkLabel(self, text="Due date(YYYY-MM-DD)", font=ENTRY_FONT)
        self.username_warning = ctk.CTkLabel(self, text="Username doesn't exist", font=ENTRY_FONT, text_color="red")
        self.task_warning = ctk.CTkLabel(self, text="Task name must be unique", font=ENTRY_FONT, text_color="red")

        # entry widgets and stringvars
        self.user = tk.StringVar(self)
        self.username_e = ctk.CTkEntry(self, font=ENTRY_FONT, width=ENTRY_WIDTH,
                                       textvariable=self.user)
        self.user.trace("w", self.entry_check)

        self.title = tk.StringVar(self)
        self.task_title_e = ctk.CTkEntry(self, font=ENTRY_FONT, width=ENTRY_WIDTH,
                                         textvariable=self.title)
        self.title.trace("w", self.entry_check)

        self.description = tk.StringVar(self)
        self.task_desc_e = ctk.CTkEntry(self, font=ENTRY_FONT, width=ENTRY_WIDTH,
                                        textvariable=self.description)
        self.description.trace("w", self.entry_check)

        self.date = tk.StringVar(self)
        self.due_date_e = ctk.CTkEntry(self, font=ENTRY_FONT, width=ENTRY_WIDTH,
                                       textvariable=self.date)
        self.date.trace("w", self.entry_check)
        self.due_date_e.bind("<FocusIn>", self.calendar)

        # submit button
        self.submit_btn = ctk.CTkButton(self, text="Add task", width=BUTTON_WIDTH, height=BUTTON_HEIGHT, font=BUTTON_FONT,
                                        state="disabled", command=self.pass_task_dets)

        # # placing widgets
        self.header.place(relx=0.5, rely=0.1, anchor="center")
        self.username.place(relx=0.18, rely=0.26)
        self.task_title.place(relx=0.18, rely=0.36)
        self.task_desc.place(relx=0.18, rely=0.46)
        self.due_date.place(relx=0.18, rely=0.56)
        self.username_e.place(relx=0.45, rely=0.26)
        self.task_title_e.place(relx=0.45, rely=0.36)
        self.task_desc_e.place(relx=0.45, rely=0.46)
        self.due_date_e.place(relx=0.45, rely=0.56)
        self.submit_btn.place(relx=0.56, rely=0.77, anchor="center")

    def entry_check(self, *args):
        """
        method passing the new entered information to be checked
        """
        self.command.task_entry_check(self.user, self.username_warning, self.task_warning, self.title, self.description,
                                      self.date, self.submit_btn)

    def calendar(self, *args):
        """
        method passing calendar frame position arguments to display or hide the calendar frame
        """
        if self.calendar_panel.in_start_pos:
            self.command.show_cal(self.pos, self.cal_end_pos, self.width, self.calendar_panel, self)
        else:
            self.command.hide_cal(self.cal_end_pos, self.cal_start_pos, self.width, self.calendar_panel, self)

    def pass_task_dets(self):
        """
        method passing all new task information to be dded
        """
        self.command.add_new_task(self.username_e, self.task_title_e, self.task_desc_e, self.due_date_e)


class ReportCalculations:
    """
    Class combines all methods that are user to calculate statistics for the users and tasks, both general and
    user_specific, which are displayed in the 'Generate Report' menu option and are added to ReportWindow
    """
    def __init__(self):
        self.db = DATABASE
        self.tasks_data = self.db.get_all_tasks()
        self.dict = self.db.get_all_users()
        self.uitem_list = [user for user in self.dict]

    def tasks_total(self):
        """
        tasks_total method calculates and returns the total amount of tasks in the database.
        """
        total = len(self.tasks_data)

        return total

    def tasks_complete(self):
        """
        tasks_complete method calculates and returns the total amount of completed tasks in the file
        """
        # variable storingt the number of completed tasks
        completed = 0
        # looping over the task rows and checking for completed tasks
        for row in self.tasks_data:
            if row[-1].lower() == "yes":
                completed += 1
        return completed

    def tasks_noncomplete(self):
        """
        tasks_noncomplete method calculates and returns the total amount of uncompleted tasks in the file
        """
        # variable storingt the number of completed tasks
        noncompleted = 0
        # looping over the task rows and checking for completed tasks
        for row in self.tasks_data:
            if row[-1].lower() == "no":
                noncompleted += 1
        return noncompleted

    def uncomp_overdue(self):
        """
        uncomp_overdue method calculates and returns the amount of uncompleted tasks that are also overdue
        """
        # variable storing the number of incomplete and overdue tasks
        result = 0
        for row in self.tasks_data:
            today = datetime.datetime.today()
            due_date = datetime.datetime.strptime(row[-2], "%Y-%m-%d")
            # if BOTH the last item in the task line is "no" and the date is in the past
            # adding 1 to the result variable
            if row[-1].lower() == "no" and today > due_date:
                result += 1
        return result

    def uncomp_percentage(self):
        """
        uncomp_percentage method calculates and returns the percentage of the uncompleted tasks
        """
        percentage = (self.tasks_noncomplete() / self.tasks_total()) * 100
        return percentage

    def overdue_percentage(self):
        """
        overdue_percentage method calculated and returns the percentage of overdue tasks in the tasks list
        """
        # variable to store the amount of overdue tasks
        overdue = 0
        for row in self.tasks_data:
            today = datetime.datetime.today()
            due_date = datetime.datetime.strptime(row[-2], "%Y-%m-%d")
            if today > due_date:
                overdue += 1
        # calculating the percentage of overdue tasks out of the total tasks
        percentage = (overdue / self.tasks_total()) * 100
        return percentage

    def user_details(self):
        """
        user_details method calculates and returns total numbers of tasks assigned to each user
        """
        # creating a dictionary that will store the username as key and count as value
        user_dict = {user: 0 for user in self.uitem_list}
        for user in user_dict:
            # if user is in tasks table, updating user's value by adding 1
            for item in self.tasks_data:
                if user == item[0]:
                    user_dict[user] += 1
        return user_dict

    def user_inc_od(self):
        """
        user_inc_od method calculates and returns the dictionary showing the percentage of the tasks assigned to each
        user that have not yet been completed and are overdue
        """
        # dictionary where user name is a key and value is [user total tasks : user incomplete AND overdue tasks]
        user_dict = {user: [0, 0] for user in self.uitem_list}
        for user in user_dict:
            for item in self.tasks_data:
                today = datetime.datetime.today()
                due_date = datetime.datetime.strptime(item[-2], "%Y-%m-%d")
                # checking if task in the tasks list is for the user
                if user in item[0]:
                    user_dict[user][0] += 1
                    # checking if the user task is incomplete AND overdue
                    if item[-1].lower() == "no" and today > due_date:
                        user_dict[user][1] += 1
        # # dictionary with user name as key and percentage result for that user a value
        percentage = {i: (user_dict[i][1] / user_dict[i][0]) * 100 for i in user_dict if user_dict[i][0] != 0}
        return percentage

    def user_incomplete(self):
        """
        user_incomplete method calculates and returns the dictionary showing the percentage of the tasks assigned to
        that user that have not been completed
        """
        # dictionary where user name is a key and value is [user total tasks : user incomplete tasks]
        user_dict = {user: [0, 0] for user in self.uitem_list}
        for user in user_dict:
            for item in self.tasks_data:
                # checking if task in the tasks list is for the user
                if user in item[0]:
                    user_dict[user][0] += 1
                    # checking if the user task is incomplete
                    if item[-1].lower() == "no":
                        user_dict[user][1] += 1
        # dictionary with user name as key and percentage result for that user a value
        percentage = {i: (user_dict[i][1] / user_dict[i][0]) * 100 for i in user_dict if user_dict[i][0] != 0}
        return percentage

    def user_complete(self):
        """
        user_complete method calculates and returns the dictionary showing the percentage of the tasks assigned to that
        user that have been completed
        """
        # dictionary where user name is a key and value is [user total tasks : user completed tasks]
        user_dict = {user: [0, 0] for user in self.uitem_list}
        for user in user_dict:
            for item in self.tasks_data:
                # checking if task in the tasks list is for the user
                if user in item[0]:
                    user_dict[user][0] += 1
                    # checking if the user task is completed
                    if item[-1].lower() == "yes":
                        user_dict[user][1] += 1
        # dictionary with user name as key and percentage result for that user a value
        percentage = {user: (user_dict[user][1] / user_dict[user][0]) * 100 for user in user_dict if
                      user_dict[user][0] != 0}
        return percentage

    def percentage_total(self):
        """
        percentage_total function calculates and returns the percentage of the total number of tasks that have been
        assigned to that user in a dictionary
        """
        total_tasks = self.tasks_total()
        user_dict = self.user_details()
        # calculating what percentage user's tasks are of the total tasks
        # storing it in a new dictionary with user name as key an percentage result for that user a value
        perc_total = {user: (user_dict[user] / total_tasks) * 100 for user in user_dict}
        return perc_total


class UserReportTabs(ctk.CTkTabview):
    """
    Class handles a tabview widget, which holds and displays the information about every user's task statistics
    """
    def __init__(self, parent):
        super().__init__(parent)

        self.reports = ReportCalculations()

        # importing all user functions as variables for users report
        self.incomp_overdue = self.reports.user_inc_od()
        self.not_completed = self.reports.user_incomplete()
        self.completed = self.reports.user_complete()
        self.perc_total = self.reports.percentage_total()
        self.user_total = self.reports.user_details()

        # create tabs
        user_list = [user for user in DATABASE.get_all_users()]

        for user in user_list:
            # tab for each used in database
            self.add(f"{user}")

            # scroll frame for each tab and a label containing each user's stats in every scrollframe
            scroll_frame = ctk.CTkScrollableFrame(master=self.tab(f"{user}"))
            scroll_frame.pack(fill="both", expand=True)
            if self.user_total[user] > 0:
                # creating labels containing report info for each user
                total_tasks = ctk.CTkLabel(master=scroll_frame, font=DATA_FONT,
                                           text=f"The total number of tasks assigned to {user}: "
                                                                     f"\t\t\t\t\t\t       {self.user_total[user]}")
                percent_of_total = ctk.CTkLabel(master=scroll_frame, font=DATA_FONT,
                                                text=f"The percentage of the total number of tasks that have been "
                                                     f"assigned to {user}: \t\t      {round(self.perc_total[user])}%")
                percent_complete = ctk.CTkLabel(master=scroll_frame, font=DATA_FONT,
                                                text=f"The percentage of the tasks assigned to {user} that have been "
                                                     f"completed: \t\t\t      {round(self.completed[user])}%")
                percent_incomplete = ctk.CTkLabel(master=scroll_frame, font=DATA_FONT,
                                                  text=f"The percentage of the tasks assigned to {user} that haven't "
                                                       f"been completed: \t\t\t      {round(self.not_completed[user])}%")
                percent_incomplete_od = ctk.CTkLabel(master=scroll_frame, font=DATA_FONT,
                                                     text=f"The percentage of the tasks assigned to that user that have "
                                                          f"not yet been completed and are overdue: "
                                                          f"  {round(self.incomp_overdue[user])}%")
                # placing report widgets
                total_tasks.pack(anchor="w", ipadx=90, ipady=3)
                percent_of_total.pack(anchor="w", ipadx=90, ipady=3)
                percent_complete.pack(anchor="w", ipadx=90, ipady=3)
                percent_incomplete.pack(anchor="w", ipadx=90, ipady=3)
                percent_incomplete_od.pack(anchor="w", ipadx=90, ipady=3)
            else:
                no_tasks = ctk.CTkLabel(master=scroll_frame, font=DATA_FONT, text=f"No tasks exist for {user}")
                no_tasks.pack()


class ReportWindow(ctk.CTkToplevel):
    """
    Class opens a new toplevel window which contains and displays all of the report calculations for tasks and users in
    the database
    """
    def __init__(self):
        super().__init__()
        self.geometry("800x700")
        self.title("User task report")

        self.command = CommandHandler()
        self.reports = ReportCalculations()

        self.widget_creation()

    def widget_creation(self):
        """
        creating and placing widgets in the window
        """
        # frame widgets

        # 1st frame
        overall_tasks_report = ctk.CTkFrame(self)
        # creating 1st frame widgets
        header_1 = ctk.CTkLabel(overall_tasks_report, text="Database Report:", font=HEADER_FONT)
        tasks_report = ctk.CTkLabel(overall_tasks_report, font=DATA_FONT,
                                    text="══════════════   Overview of all tasks created and tracked   ══════════════")
        total_tasks = ctk.CTkLabel(overall_tasks_report, font=DATA_FONT,
                                   text=f"The total number of tasks is:                                 "
                                        f"                               {self.reports.tasks_total()}")
        compl_tasks = ctk.CTkLabel(overall_tasks_report, font=DATA_FONT,
                                   text=f"The total number of completed tasks is:                       "
                                        f"                    {self.reports.tasks_complete()}")
        incompl_tasks = ctk.CTkLabel(overall_tasks_report, font=DATA_FONT,
                                     text=f"The total number of uncompleted tasks is:                   "
                                          f"                   {self.reports.tasks_noncomplete()}")
        incompl_overdue = ctk.CTkLabel(overall_tasks_report, font=DATA_FONT,
                                       text=f"The total number of uncompleted tasks that are overdue is: "
                                            f"     {self.reports.uncomp_overdue()}")
        incompl_perc = ctk.CTkLabel(overall_tasks_report, font=DATA_FONT,
                                    text=f"The percentage of tasks that are incomplete is:            "
                                         f"            {round(self.reports.uncomp_percentage())}%")
        overdue_perc = ctk.CTkLabel(overall_tasks_report, font=DATA_FONT,
                                     text=f"The percentage of tasks that are overdue is:             "
                                          f"                {round(self.reports.overdue_percentage())}%")

        bottom_line = ctk.CTkLabel(overall_tasks_report,
                                   text="═══════════════════════════════════════════════")


        # placing 1st frame widgets
        header_1.pack(anchor="center", ipady=12)
        tasks_report.pack(anchor="center")
        total_tasks.pack(anchor="w", ipadx=220, ipady=3)
        compl_tasks.pack(anchor="w", ipadx=220, ipady=3)
        incompl_tasks.pack(anchor="w", ipadx=220, ipady=3)
        incompl_overdue.pack(anchor="w", ipadx=220, ipady=3)
        incompl_perc.pack(anchor="w", ipadx=220, ipady=3)
        overdue_perc.pack(anchor="w", ipadx=220, ipady=3)
        bottom_line.pack()

        overall_tasks_report.pack(expand=True, fill="both")

        #2nd frame header
        user_frame_header = ctk.CTkLabel(self, font=DATA_FONT,
                                         text="──────────────────  Overview of users' tasks: ─────────────────")
        user_frame_header.pack(ipadx=20)

        # 2nd frame
        self.user_reports = ctk.CTkFrame(self)
        # creating 2nd frame widgets
        self.tab_view = UserReportTabs(self.user_reports)
        self.tab_view.pack(expand=True, fill="both")


        self.user_reports.pack(expand=True, fill="both")


class MyTasksWindow(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

    def initialize(self, username):
        self.geometry("800x700")
        self.title("My tasks")
        self.username = username
        self.command = CommandHandler()

        self.columnconfigure(0, weight=1)

        self.username = username
        self.widget_creation()


    def widget_creation(self):
        """
        creating and placing widgets for MyTaskWindow
        """
        header = ctk.CTkLabel(self, text=f"{self.username} tasks:", font=HEADER_FONT)
        header.grid(row=0, column=0, sticky="nsew", pady=20)

        # creating and placing tasks dropdown menu
        self.user_tasks = [item for item in DATABASE.get_all_tasks() if item[0] == self.username]

        if len(self.user_tasks) == 0:
            no_tasks_msg = ctk.CTkLabel(self, text="No tasks in the database")
            no_tasks_msg.grid(row=1, column=0, sticky="nsew")
        else:
            task_names = [item[1] for item in self.user_tasks]
            self.option_var = ctk.StringVar()
            task_options_menu = ctk.CTkOptionMenu(self, values=task_names, variable=self.option_var, width=200,
                                                  anchor="center")
            task_options_menu.set("Choose task name")
            self.option_var.trace("w", self.display_chosen_task)
            task_options_menu.grid(row=1, column=0, pady=30)


    def display_chosen_task(self, *args):
        """
        method finds the details of the task title that user picked in the dropdown menu and a button that allows
        to mark the task as complete
        """
        # frame for task detail widgets
        task_details_fr = ctk.CTkFrame(self)
        for widget in task_details_fr.winfo_children():
            widget.destroy()

        # creating and placing task detail's widgets
        chosen_task_name = self.option_var.get()

        chosen_task = []
        for item in self.user_tasks:
            if item[1] == chosen_task_name:
                chosen_task.extend(item[1:])

        # creating and placing the chosen task's details
        task_name = chosen_task[0]
        assigned_to = self.username
        date_assigned = chosen_task[2]
        due_date = chosen_task[3]
        task_complete = chosen_task[4]
        task_description = chosen_task[1]

        task_lbl = ctk.CTkLabel(task_details_fr, text=f"Task: \t\t\t\t{task_name}", font=DATA_FONT)
        task_user_lbl = ctk.CTkLabel(task_details_fr, text=f"Assigned to: \t\t\t{assigned_to}", font=DATA_FONT)
        date_assigned_lbl = ctk.CTkLabel(task_details_fr, text=f"Date assigned: \t\t\t{date_assigned}", font=DATA_FONT)
        due_date_lbl = ctk.CTkLabel(task_details_fr, text=f"Due date: \t\t\t{due_date}", font=DATA_FONT)
        task_complete_lbl = ctk.CTkLabel(task_details_fr, text=f"Task complete?:\t\t\t {task_complete}", font=DATA_FONT)
        task_description_lbl = ctk.CTkLabel(task_details_fr, text=f"Task:\t\t\t\t {task_description}",
                                            wraplength=500, justify="center", font=DATA_FONT)

        task_lbl.pack(ipadx=20, anchor="w")
        task_user_lbl.pack(ipadx=20, anchor="w")
        date_assigned_lbl.pack(ipadx=20, anchor="w")
        due_date_lbl.pack(ipadx=20, anchor="w")
        task_complete_lbl.pack(ipadx=20, anchor="w")
        task_description_lbl.pack(ipadx=20, anchor="w")

        task_details_fr.grid(row=2, column=0, sticky="nsew", padx=120, pady=(30, 50))

        if task_complete == "No":
            mark_complete_btn = ctk.CTkButton(self, text="Mark task as complete", width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                              font=BUTTON_FONT, command=lambda: self.command.mark_complete(task_name))
            mark_complete_btn.grid(row=3, column=0)


class UsersTasksRep(ctk.CTkToplevel):
    """

    """
    def __init__(self):
        super().__init__()
        self.minsize(450, 300)
        self.resizable(False, False)
        self.title("Totals")
        self.attributes("-topmost", True)

        self.widget_creation()

    def widget_creation(self):
        """
        method user to create and place widgets inside the main class window
        """
        header = ctk.CTkLabel(self, text="Database statistics:", font=HEADER_FONT)
        header.pack(ipadx=120, ipady=20)

        # stats widgets
        total_users = len(DATABASE.get_all_users())
        total_tasks = len(DATABASE.get_all_tasks())

        stats_lbl = ctk.CTkLabel(self, text=f"""
        ┌──────────────────────────────┐
        Total number of users in the database: {total_users}
        Total number of tasks in the database: {total_tasks}
        └──────────────────────────────┘
        """, font=DATA_FONT)
        stats_lbl.pack(ipadx=20, ipady=40)


class ViewAllTasks(ctk.CTkToplevel):
    """
    class opens a new window allowing admin to
    """
    def __init__(self):
        super().__init__()
        self.geometry("800x700")
        self.title("View all tasks")
        self.command = CommandHandler()
        self.user_tasks_fr = None

        self.first_frame()

    def first_frame(self):
        """
        creating and placing the first displayed frame and it's widgets
        """
        if self.user_tasks_fr is not None:
            self.user_tasks_fr.destroy()

        self.user_choice_fr = ctk.CTkFrame(self)

        # first frame widgets
        header = ctk.CTkLabel(self.user_choice_fr, text="View all tasks for:", font=HEADER_FONT)
        header.pack(ipady=30)

        users_dict = DATABASE.get_all_users()
        users_list = [user for user in users_dict]
        user_choice_menu = ctk.CTkOptionMenu(self.user_choice_fr, values=users_list,
                                             command=self.second_frame)
        user_choice_menu.set("Select a user")
        user_choice_menu.pack(ipadx=50)

        self.user_choice_fr.pack()

    def second_frame(self, choice):
        """
        creating a second frame in view all tasks and all it's widgets
        """
        self.user_choice_fr.destroy()

        logged_in = self.command.retrieve_username()
        
        self.user_tasks_fr = ctk.CTkFrame(self)
        header = ctk.CTkLabel(self.user_tasks_fr, text=f"List of all tasks for {choice}", font=HEADER_FONT)
        header.pack(pady=15)

        back_btn = ctk.CTkButton(self.user_tasks_fr, text="Back to user search", font=BUTTON_FONT,
                           height=BUTTON_HEIGHT, width=BUTTON_WIDTH, command=self.first_frame)
        back_btn.pack(pady=15)

        # tabview with all user's tasks each in a single tab
        tasks_tabs = ctk.CTkTabview(self.user_tasks_fr)
        all_tasks = DATABASE.get_all_tasks()
        user_tasks = [task for task in all_tasks if task[0] == choice]
        # creating the tabs for each task user has and numbering them
        for i, line in enumerate(user_tasks, start=1):
            tasks_tabs.add(f"Task {i}")
            # frame for task details
            task_frame = ctk.CTkFrame(tasks_tabs.tab(f"Task {i}"))

            # task details label
            task_lbl = ctk.CTkLabel(task_frame, text=f"Task: \t\t\t{line[1]}", font=DATA_FONT)
            user_lbl = ctk.CTkLabel(task_frame, text=f"Assigned to: \t\t{line[0]}", font=DATA_FONT)
            date_lbl = ctk.CTkLabel(task_frame, text=f"Date assigned: \t\t{line[3]}", font=DATA_FONT)
            due_lbl = ctk.CTkLabel(task_frame, text=f" Due date:\t\t {line[4]}", font=DATA_FONT)
            complete_lbl = ctk.CTkLabel(task_frame, text=f"Task complete? \t\t{line[5]}", font=DATA_FONT)
            desc_lbl = ctk.CTkLabel(task_frame, text=f"Task description: \t\t{line[2]}", font=DATA_FONT)

            task_lbl.pack(expand=True, anchor="w", pady=10)
            user_lbl.pack(expand=True, anchor="w", pady=10)
            date_lbl.pack(expand=True, anchor="w", pady=10)
            due_lbl.pack(expand=True, anchor="w", pady=10)
            complete_lbl.pack(expand=True, anchor="w", pady=10)
            desc_lbl.pack(expand=True, anchor="w", pady=10)

            task_frame.pack(expand=True, fill="both", pady=30)

            logged_in_user = self.command.retrieve_username()
            # task edit options for admin user
            if logged_in_user == "admin":
                edit_options = ["Edit username", "Edit task name", "Edit description", "Edit due date",
                                "Edit completion status", "Delete task"]
                edit_menu = ctk.CTkOptionMenu(task_frame, values=edit_options, command=lambda choice=choice,
                                                task_name=line[1]: self.command.edit_task(choice, task_name))
                edit_menu.set("Edit task")
                edit_menu.pack(pady=25)

        tasks_tabs.pack()

        self.user_tasks_fr.pack()


class EditTaskWindow(ctk.CTkToplevel):
    """
    This class handles the window that is used to get user's input with the changes they want to make to the task in the
    database.
    params:

    """
    def __init__(self, change, choice, task_name):
        super().__init__()
        self.geometry("500x350")
        self.title("Edit task")
        self.attributes("-topmost", True)
        self.change = change
        self.choice = choice
        self.task_name = task_name
        self.command = CommandHandler()

        # date picker initial settings
        self.cal_start_pos = 1
        self.cal_end_pos = 0.6
        self.calendar_panel = CalendarPanel(self, self, self.cal_start_pos, self.cal_end_pos)
        self.pos = self.calendar_panel.pos
        self.width = self.calendar_panel.width

        self.widget_creation()

    def widget_creation(self):
        """
        method creates and places widgets within the edit task window
        """
        header = ctk.CTkLabel(self, text="New details to be added to the task", font=HEADER_FONT)
        header.grid(row=0, column=0, columnspan=2, padx=100, pady=40)

        entry_lbl = ctk.CTkLabel(self, text=f"Enter new {self.change}:", font=DATA_FONT)
        entry_lbl.grid(row=1, column=0, padx=(50, 5))

        # generic entry box for capturing change, but called 'due_date_e' for reusing purposes
        self.due_date_e = ctk.CTkEntry(self, font=ENTRY_FONT, width=ENTRY_WIDTH)
        if self.choice == "Edit due date":
            self.due_date_e.bind("<FocusIn>", self.calendar)
        self.due_date_e.grid(row=1, column=1)

        submit_btn = ctk.CTkButton(self, text="Submit change", font=BUTTON_FONT, width=BUTTON_WIDTH,
                                   height=BUTTON_HEIGHT, command=lambda: self.command.submit_change(self.choice,
                                                                                                    self.due_date_e,
                                                                                                    self.task_name))
        submit_btn.grid(row=2, column=1, pady=20)

    def calendar(self, *args):
        """
        method passing calendar frame position arguments to display or hide the calendar frame
        """
        if self.calendar_panel.in_start_pos:
            self.command.show_cal(self.pos, self.cal_end_pos, self.width, self.calendar_panel, self)
        else:
            self.command.hide_cal(self.cal_end_pos, self.cal_start_pos, self.width, self.calendar_panel, self)


class CommandHandler:
    """
    class defines all commands used in admin and user menu
    """
    def __init__(self):
        self.toplevel_window = None
        self.add_task_window = None
        self.new_position = None
        self.username = None
        logged_in_username = None

    def user_login(self, username, password, window):
        """
        method checks that usernme exists in the database and that the password entered matches the username
        username: widget: entry widget for username
        password: widget: entry widget for password
        window: widget: widget in which the username and password entries are placed
        """
        username_str = username.get()
        password_str = password.get()
        user_dict = DATABASE.get_all_users()

        if username_str.lower() not in user_dict.keys():
            response = messagebox.showerror("Error", "Username doesn't exist.")
            username.delete(0, "end")
            password.delete(0, "end")
        elif password_str.lower() != user_dict[username_str.lower()]:
            response = messagebox.showerror("Error", "Wrong password. Try again.")
            username.delete(0, "end")
            password.delete(0, "end")
        else:
            if username_str.lower() == "admin":
                response = window.parent.create_admin_menu()
            else:
                response = window.parent.create_user_menu()

        return username_str

    def store_username(self, username):
        CommandHandler.logged_in_username = username

        return CommandHandler.logged_in_username

    def retrieve_username(self):
        retrieved = CommandHandler.logged_in_username

        return retrieved

    def open_top_level(self, window_name):
        """
        opens a new window to add new user into database
        """
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = window_name()  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it

        return self.toplevel_window

    @staticmethod
    def add_user(username_entry, password_entry, conf_pass_entry):
        """
        checks username is unique, passwords match and adds the new user to the database
        """
        # dictionary of all users
        users = DATABASE.get_all_users()

        # getting all entered data
        username = username_entry.get()
        password = password_entry.get()
        conf_password = conf_pass_entry.get()

        # deleting all entry fields
        username_entry.delete(0, "end")
        password_entry.delete(0, "end")
        conf_pass_entry.delete(0, "end")

        if username in users.keys():
            # checking if username is unique
            response = messagebox.showerror("Error", f"Username {username} already exists. Try again.")
            return False
        else:
            # checking if passwords match
            if password != conf_password:
                response = messagebox.showerror("Error", "Passwords don't match. Try again.")
                return False
            elif password == conf_password:
                DATABASE.add_user(username, password)
                response = messagebox.showinfo("User added.", f"New user {username} added to the database.")
                return True

    def open_add_task(self):
        """
        method opening the add new task window
        """
        task_window = self.open_top_level(AddTaskWindow)

        return task_window

    @staticmethod
    def task_entry_check(txt_var, name_error_label, task_error_label, task_var, desc_var, date_var, button):
        """
        method to perform checks on new task entries.
        Checks username exists in the database, checks no entry fields are left empty.
        txt_var: string: StringVar storing username
        error_label: widget: label displaying name error message
        task_var: string: StringVar storing task name
        desc_var: string: StringVar storing task description
        date_var: string: StringVar storing due date
        button: widget: submit button for the new task
        """
        users = DATABASE.get_all_users()
        tasks = DATABASE.get_all_tasks()
        task_names = [item[1] for item in tasks]

        my_flag = False

        # checking username exists
        if txt_var.get() not in users.keys():
            my_flag = True
            name_error_label.place(relx=0.7, rely=0.26)
        else:
            name_error_label.place_forget()

        # checking task name is unique
        if task_var.get() in task_names:
            my_flag = True
            task_error_label.place(relx=0.7, rely=0.36)
        else:
            task_error_label.place_forget()

        # checking no fields are left blank
        if len(txt_var.get()) == 0:
            my_flag = True

        if len(task_var.get()) == 0:
            my_flag = True

        if len(desc_var.get()) == 0:
            my_flag = True

        if len(date_var.get()) == 0:
            my_flag = True

        # activating button if all checks are done
        if not my_flag:
            button.configure(state="normal")
        else:
            button.configure(state="disabled")

    @staticmethod
    def add_new_task(username, task_title, task_desc, due_date):
        """
        getting all the information entered and adding it as new task into the database
        """
        user = username.get()
        title = task_title.get()
        description = task_desc.get()
        date_added = date.today().strftime("%Y-%m-%d")
        due_date = due_date.get()
        is_complete = "No"

        DATABASE.add_task(user, title, description, date_added, due_date, is_complete)

        # success message
        response = messagebox.showinfo("Task added", f"New task for {user} added successfully.")

    def show_cal(self, position, end_position, width, calendar, window):
        """
        method that displays the frame containing date time picker calendar and button
        """
        if position > end_position:
            self.new_position = position - 0.008
            calendar.place(relx=position, rely=0, relwidth=width, relheight=1)
            calendar.lift()
            window.after(10, self.show_cal(self.new_position, end_position, width, calendar, window))
        else:
            calendar.in_start_pos = False

    def hide_cal(self, position, start_position, width, calendar, window):
        """
        method that hides the frame containing date time picker calendar and button
        """
        if position < start_position:
            new_position = position + 0.008
            calendar.place(relx=position, rely=0, relwidth=width, relheight=1)
            window.after(10, self.hide_cal(new_position, start_position, width, calendar, window))
        else:
            calendar.in_start_pos = True

    def open_reports(self):
        report_window = self.open_top_level(ReportWindow)

        return report_window

    def open_my_tasks(self, username):
        my_tasks_window = self.open_top_level(MyTasksWindow)
        my_tasks_window.initialize(username)

        return my_tasks_window

    @staticmethod
    def mark_complete(task_name):
        """
        methods calls update_completion method from the database class from db_manager and marks the chosen task as
        complete in the database
        """
        status = "Yes"
        DATABASE.update_completion(status, task_name)

        response = messagebox.showinfo("Success", "Task marked as complete")

    def open_users_tasks(self):
        users_tasks_w = self.open_top_level(UsersTasksRep)

        return users_tasks_w

    def open_all_tasks(self):
        all_tasks_window = self.open_top_level(ViewAllTasks)

        return all_tasks_window

    @staticmethod
    def edit_task(choice, task_name):
        """
        edit_task method changes the chosen task's details in the database or opens a new window to capture a change
        that user wants to apply
        """
        if choice == "Edit username":
            change = "username"
            EditTaskWindow(change, choice, task_name)
        elif choice == "Edit task name":
            change = "task name"
            EditTaskWindow(change, choice, task_name)
        elif choice == "Edit description":
            change = "task description"
            EditTaskWindow(change, choice, task_name)
        elif choice == "Edit due date":
            change = "due date"
            EditTaskWindow(change, choice, task_name)
        elif choice == "Edit completion status":
            tasks = DATABASE.get_all_tasks()
            task_to_change = [item for item in tasks if item[1] == task_name]
            if task_to_change[-1] == "Yes":
                status = "No"
                DATABASE.update_completion(status, task_name)
                response = messagebox.showinfo("Updated", "Task marked as not completed")
            else:
                status = "Yes"
                DATABASE.update_completion(status, task_name)
                response = messagebox.showinfo("Updated", "Task marked as completed")
        elif choice == "Delete task":
            DATABASE.delete_task(task_name)
            response = messagebox.showinfo("Success", "Task removed from database")

    @staticmethod
    def submit_change(choice, entry, task_name):
        """
        Method applies changes that the user has entered to the chosen task
        """
        new_data = entry.get()
        if choice == "Edit username":
            users = DATABASE.get_all_users()
            if new_data not in users:
                response = messagebox.showerror("Error", "User does not exist in the database")
                entry.delete(0, "end")
            else:
                DATABASE.change_task_username(new_data, task_name)
                response = messagebox.showinfo("Updated", "User changed successfully")
        elif choice == "Edit task name":
            tasks = DATABASE.get_all_tasks()
            task_names = [item[1] for item in tasks]
            if new_data in task_names:
                response = messagebox.showerror("Error", "Task name must be unique")
                entry.delete(0, "end")
            else:
                DATABASE.change_task_name(new_data, task_name)
                response = messagebox.showinfo("Updated", "Task name changed successfully")
        elif choice == "Edit description":
            DATABASE.change_task_details(new_data, task_name)
            response = messagebox.showinfo("Updated", "Task description changed successfully")
        elif choice == "Edit due date":
            DATABASE.change_due_date(new_data, task_name)
            response = messagebox.showinfo("Updated", "Task due date changed successfulle")


class AdminMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # uploading images for the menu buttons
        self.image_manager = ImageManager(
            r"C:\Users\rishk\tsk maanger CLASS BASED GUI\images"
        )
        self.upload_images()

        self.columnconfigure((0, 1, 2, 3), weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure((1, 2), weight=9)

        # header label
        header = ctk.CTkLabel(self,
                           text="════════════════════════════════════════════════════════ ADMIN MENU ═══════════════════════════════════════════════════════",
                           font=("Verdana", 10))
        header.grid(row=0, column=0, columnspan=4, sticky="nsew")

        self.admin_menu_buttons()

        self.pack(expand=True, fill="both")

    def upload_images(self):
        """
        method to upload all the required images for the menu buttons
        """
        images = {}

        images["register.png"] = self.image_manager.get_image("register.png")
        images["add task.png"] = self.image_manager.get_image("add task.png")
        images["report.png"] = self.image_manager.get_image("report.png")
        images["view my tasks.png"] = self.image_manager.get_image("view my tasks.png")
        images["view all tasks.png"] = self.image_manager.get_image("view all tasks.png")
        images["tasks and users.png"] = self.image_manager.get_image("tasks and users.png")
        images["exit.png"] = self.image_manager.get_image("exit.png")

        return images

    def admin_menu_buttons(self):
        """
        method creates and places all admin menu buttons in the admin menu frame
        """
        tasks = CommandHandler()
        images = self.upload_images()
        logged_in_user = tasks.retrieve_username()

        # creating menu buttons
        add_user_btn = ctk.CTkButton(self, text="Add User", corner_radius=0, border_width=1,
                                     command=lambda: tasks.open_top_level(AddUserWindow),
                                     image=images["register.png"], compound="top",
                                     fg_color="#5900b3", hover_color="#ccb3ff", font=("Calibre", 16, "bold"))

        add_task_btn = ctk.CTkButton(self, text="Add Task", corner_radius=0, border_width=1,
                                     command=tasks.open_add_task,
                                     image=images["add task.png"], compound="top",
                                     fg_color="#5900b3", hover_color="#ccb3ff", font=("Calibre", 16, "bold"))

        gen_report_btn = ctk.CTkButton(self, text="Generate Report",  corner_radius=0, border_width=1,
                                       command=tasks.open_reports,
                                       image=images["report.png"], compound="top",
                                       fg_color="#7300e6", hover_color="#ccb3ff", font=("Calibre", 16, "bold"))

        view_mine_btn = ctk.CTkButton(self, text="AView My Tasks", corner_radius=0, border_width=1,
                                      command=lambda: tasks.open_my_tasks(logged_in_user),
                                      image=images["view my tasks.png"], compound="top",
                                      fg_color="#7300e6", hover_color="#ccb3ff", font=("Calibre", 16, "bold"))

        view_all_btn = ctk.CTkButton(self, text="View All Tasks", corner_radius=0, border_width=1,
                                     command=tasks.open_all_tasks,
                                     image=images["view all tasks.png"], compound="top",
                                     fg_color="#6600cc", hover_color="#ccb3ff", font=("Calibre", 16, "bold"))

        users_tasks_btn = ctk.CTkButton(self, text="Users and Tasks", corner_radius=0, border_width=1,
                                        command=tasks.open_users_tasks,
                                        image=images["tasks and users.png"], compound="top",
                                        fg_color="#5900b3", hover_color="#ccb3ff", font=("Calibre", 16, "bold"))

        exit_btn = ctk.CTkButton(self, text="Exit", corner_radius=0, border_width=1,
                                 command=self.parent.login,
                                 image=images["exit.png"], compound="top",
                                 fg_color="#330066", hover_color="#cc0000", font=("Calibre", 16, "bold"))

        # placing menu buttons
        add_user_btn.grid(row=1, column=0, sticky="nsew")
        add_task_btn.grid(row=1, column=1, columnspan=2, sticky="nsew")
        gen_report_btn.grid(row=1, column=3, sticky="nsew")
        view_mine_btn.grid(row=2, column=0, sticky="nsew")
        view_all_btn.grid(row=2, column=1, sticky="nsew")
        users_tasks_btn.grid(row=2, column=2, sticky="nsew")
        exit_btn.grid(row=2, column=3, sticky="nsew")


class UserMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent


        self.columnconfigure((0, 1, 2, 3), weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=18)

        # uploading images for the menu buttons
        self.image_manager = ImageManager(
            r"C:\Users\rishk\tsk maanger CLASS BASED GUI\images"
        )
        self.upload_images()

        header = ctk.CTkLabel(self,
                              text="════════════════════════════════════════════════════════ USER MENU ════════════════"
                                   "═══════════════════════════════════════",
                              font=("Verdana", 10))
        header.grid(row=0, column=0, columnspan=4, sticky="nsew")

        self.user_menu_buttons()

        self.pack(expand=True, fill="both")

    def upload_images(self):
        """
        method to upload all the required images for the menu buttons
        """
        images = {}

        images["add task.png"] = self.image_manager.get_image("add task.png")
        images["view my tasks.png"] = self.image_manager.get_image("view my tasks.png")
        images["view all tasks.png"] = self.image_manager.get_image("view all tasks.png")
        images["exit.png"] = self.image_manager.get_image("exit.png")

        return images

    def user_menu_buttons(self):
        """
        method creates and places all user menu buttons in the user menu frame
        """
        tasks = CommandHandler()
        logged_in_user = tasks.retrieve_username()
        images = self.upload_images()

        # creating buttons
        add_task_btn = ctk.CTkButton(self, text="Add Task", corner_radius=0, border_width=1,
                                     command=tasks.open_add_task,
                                     image=images["add task.png"], compound="top",
                                     fg_color="#5900b3", hover_color="#ccb3ff", font=("Calibre", 16, "bold"))

        view_mine_btn = ctk.CTkButton(self, text="View My Tasks", corner_radius=0, border_width=1,
                                      command=lambda: tasks.open_my_tasks(logged_in_user),
                                      image=images["view my tasks.png"], compound="top",
                                      fg_color="#7300e6", hover_color="#ccb3ff", font=("Calibre", 16, "bold"))

        view_all_btn = ctk.CTkButton(self, text="View All Tasks", corner_radius=0, border_width=1,
                                     command=tasks.open_all_tasks,
                                     image=images["view all tasks.png"], compound="top",
                                     fg_color="#6600cc", hover_color="#ccb3ff", font=("Calibre", 16, "bold"))

        exit_btn = ctk.CTkButton(self, text="Exit", corner_radius=0, border_width=1,
                                 command=self.parent.login,
                                 image=images["exit.png"], compound="top",
                                 fg_color="#330066", hover_color="#cc0000", font=("Calibre", 16, "bold"))

        # placing buttons
        add_task_btn.grid(row=1, column=0, sticky="nsew")
        view_mine_btn.grid(row=1, column=1, sticky="nsew")
        view_all_btn.grid(row=1, column=2, sticky="nsew")
        exit_btn.grid(row=1, column=3, sticky="nsew")


task = TaskManager()
task.mainloop()

