import sqlite3


class Database:
    def __init__(self):
        self.con = sqlite3.connect('reminder.db')
        self.cursor = self.con.cursor()
        self.create_task_table()

    def create_task_table(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks(id integer PRIMARY KEY AUTOINCREMENT, task varcahr(50) NOT NULL, "
            "due_time varchar(50), completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)))")

    def create_task(self, task, due_time=None):
        self.cursor.execute("INSERT INTO tasks(task, due_time, completed) VALUES(?, ?, ?)", (task, due_time, 0))
        self.con.commit()

        # Getting the last entered item to add in the list
        created_task = self.cursor.execute("SELECT id, task, due_time FROM tasks WHERE task = ? and completed = 0",
                                           (task,)).fetchall()
        return created_task[-1]

    def get_tasks(self):
        complete_tasks = self.cursor.execute("SELECT id, task, due_time FROM tasks WHERE completed = 1").fetchall()

        incomplete_tasks = self.cursor.execute("SELECT id, task, due_time FROM tasks WHERE completed = 0").fetchall()

        return complete_tasks, incomplete_tasks

    def delete_task(self, taskid):
        self.cursor.execute("DELETE FROM tasks WHERE id=?", (taskid,))
        self.con.commit()

    def close_db_connection(self):
        self.con.close()
