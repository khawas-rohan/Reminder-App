from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDTimePicker
from datetime import datetime
from kivy.clock import Clock
from plyer import notification
from kivymd.uix.list import TwoLineAvatarIconListItem
import winsound
import win32com.client as wincom
import random
from kivy.lang import Builder
import plyer.platforms
from database import Database

db = Database()

Window.size = (350, 600)


class Reminder:
    def __init__(self, time, text):
        self.time = time
        self.text = text


def speak(audio):
    speech = wincom.Dispatch("SAPI.SpVoice")
    speech.Speak(audio)


class DialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reminders = []
        self.ids.time_text.text = datetime.now().strftime("%I:%M:%p")

    def show_time_picker(self, *args):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.add_reminder)
        time_dialog.open()

    def add_reminder(self, instance, time):
        formatted_time = datetime.strptime(str(time), "%H:%M:%S").strftime("%I:%M:%p")
        self.ids.time_text.text = formatted_time
        reminder_text = self.ids.task_text.text
        reminder = Reminder(self.ids.time_text.text, reminder_text)
        self.reminders.append(reminder)
        self.schedule_reminders()

    def schedule_reminders(self):
        Clock.unschedule(self.check_reminders)
        Clock.schedule_interval(self.check_reminders, 1)

    def check_reminders(self, *args):
        current_time = datetime.now().strftime("%I:%M:%p")
        for reminder in self.reminders:
            if reminder.time == current_time:
                icon_path = 'reminder.ico'
                winsound.MessageBeep()
                speak(f"Reminder: {reminder.text}")
                notification.notify(title='Reminder', message=reminder.text,
                                    app_icon='reminder.ico', timeout=10)
                self.reminders.remove(reminder)


class Delete(TwoLineAvatarIconListItem):
    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        self.pk = pk

    def delete(self, the_list_item):
        self.parent.remove_widget(the_list_item)
        delete = [
            "Erasing the data.",
            "Deletion executed."]
        reminder_delete = random.choice(delete)
        speak(reminder_delete)
        db.delete_task(the_list_item.pk)


class KRApp(MDApp):
    task_list_dialog = None

    def __init__(self, **kwargs):
        super().__init__()

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_file("K_R.kv")

    def show_task_dialog(self):
        if not self.task_list_dialog:
            self.task_list_dialog = MDDialog(
                title="Reminder",
                type="custom",
                content_cls=DialogContent()
            )
        self.task_list_dialog.open()
        # speak("Please enter your reminder and time...")

    def on_start(self):
        try:
            completed_tasks, incompleted_tasks = db.get_tasks()

            if incompleted_tasks != []:
                for task in incompleted_tasks:
                    add_task = Delete(pk=task[0], text=task[1], secondary_text=task[2])
                    self.root.ids.container.add_widget(add_task)

            if completed_tasks != []:
                for task in completed_tasks:
                    add_task = Delete(pk=task[0], text='[s]' + task[1] + '[/s]', secondary_text=task[2])
                    self.root.ids.container.add_widget(add_task)

        except Exception as e:
            print(e)
            pass

    def close_dialog(self, *args):
        self.task_list_dialog.dismiss()

    def add_task(self, task, task_time):
        # print(task.text, task_date)
        created_task = db.create_task(task.text, task_time)
        self.root.ids['container'].add_widget(
            Delete(pk=created_task[0],
                   text='[b]' + created_task[1] + '[/b]',
                   secondary_text=created_task[2]))
        save = [f"Data stored", f"storing the data at {task_time}"]
        save_speech = random.choice(save)
        speak(save_speech)
        task.text = ''


if __name__ == "__main__":
    KRApp().run()
