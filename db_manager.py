import sqlite3

class Database:
    def __init__(self, table1, table2):
        self.con = sqlite3.connect("task_manager")
        self.cursor = self.con.cursor()
        self.table1 = table1
        self.table2 = table2

        # user data table
        self.cursor.execute(f'''
                        CREATE TABLE IF NOT EXISTS {self.table1}(
                            user TEXT UNIQUE PRIMARY KEY,
                            password TEXT NOT NULL
                            )
                     ''')

        # tasks details table
        self.cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.table2}(
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

    def add_user(self, user_name, password):
        self.cursor.execute(f'''INSERT INTO {self.table1}(user, password)
                                            VALUES(?, ?)''', (user_name, password))
        self.con.commit()

    def delete_user(self, user_name):
        """
        method delete_user deletes the tuer specified by user
        """
        self.cursor.execute(f"DELETE FROM {self.table1} WHERE user=?", (user_name,))
        self.con.commit()

    def get_all_users(self):
        """
        method get_all_users returns the dictionary containing all users' data
        """
        # getting the list of all users
        self.cursor.execute(f"SELECT user, password FROM {self.table1}")
        user_dict = {user : password for user, password in self.cursor}
        return user_dict
        #### check SUBMIT function in the original gui.py

    def add_task(self, user_name, task_name, task_details, date_added, due_date, is_complete):
        """
        method add_task adds the data passed as parameters to the task_data table
        """
        self.cursor.execute(f'''INSERT INTO {self.table2}(user, task_name, task_dets, date_added, due_date, is_complete)
                                    VALUES(?, ?, ?, ?, ?, ?)''',
                       (user_name, task_name, task_details, date_added, due_date, is_complete))
        self.con.commit()

    def get_all_tasks(self):
        """
        method get_all_tasks returns the list containing all tasks data
        """
        self.cursor.execute(f"SELECT * FROM {self.table2}")
        # creating a list containing each row of tasks file in a separate list
        titem_list = [row for row in self.cursor]
        return titem_list

    def change_task_username(self, user, task_name):
        """method allows to change the name of the user that the task is assigned to"""
        self.cursor.execute(f'''UPDATE {self.table2}
                                SET user = ? WHERE task_name = ?''', (user, task_name))
        self.con.commit()

    def change_task_name(self, new_task_name, task_name):
        """method allows to change the name of the user that the task is assigned to"""
        self.cursor.execute(f'''UPDATE {self.table2}
                                SET task_name = ? WHERE task_name = ?''', (new_task_name, task_name))
        self.con.commit()

    def change_task_details(self, task_details, task_name):
        """method allows to change the name of the user that the task is assigned to"""
        self.cursor.execute(f'''UPDATE {self.table2}
                                SET task_dets = ? WHERE task_name = ?''', (task_details, task_name))
        self.con.commit()

    def change_due_date(self, new_due_date, task_name):
        """method allows to change the name of the user that the task is assigned to"""
        self.cursor.execute(f'''UPDATE {self.table2}
                                SET due_date = ? WHERE task_name = ?''', (new_due_date, task_name))
        self.con.commit()

    def update_completion(self, status, task_name):
        """
        method mark_complete changes the is_complete status of the task to 'Yes'
        """
        self.cursor.execute(f'''UPDATE {self.table2}
                                SET is_complete = ? WHERE task_name = ?''', (status, task_name))
        self.con.commit()

    def delete_task(self, task_name):
        """
        method delete_task deletes the task specified by user
        """
        self.cursor.execute(f"DELETE FROM {self.table2} WHERE task_name=?", (task_name,))
        self.con.commit()


db = Database("user_data", "user_task")
db.delete_user("cracken")
