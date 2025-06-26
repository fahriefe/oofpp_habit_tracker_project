import sys
import sqlite3
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTextEdit
)

def init_db():
    conn = sqlite3.connect('monthly_habit_tracker.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS monthly_habit_tracker 
              ( id INTEGER PRIMARY KEY AUTOINCREMENT, 
                week INTEGER NOT NULL, 
                date_str TEXT NOT NULL,
                healthy_eating TEXT NOT NULL,
                daily_exercise TEXT NOT NULL,
                no_smoke TEXT NOT NULL,
                time_outdoors TEXT NOT NULL,
                blogging TEXT NOT NULL
                 )''')
    conn.commit()
    conn.close()

def add_or_update_table(week, date_str, healthy_eating, daily_exercise, no_smoke, time_outdoors, blogging):
    conn = sqlite3.connect('monthly_habit_tracker.db')
    c = conn.cursor()
    c.execute('''SELECT id FROM monthly_habit_tracker
                 WHERE week = ?
                 AND date_str = ?''',
              (week, date_str))
    result = c.fetchone()

    if result:
        c.execute('''UPDATE monthly_habit_tracker
                     SET healthy_eating = ?,
                         daily_exercise = ?,
                         no_smoke = ?,
                         time_outdoors = ?,
                         blogging = ?
                         WHERE id = ?''',
                  (healthy_eating, daily_exercise, no_smoke, time_outdoors, blogging, result[0]))
        print(f"Updated habits on {date_str} in {week}.")
    else:
        c.execute('''INSERT INTO monthly_habit_tracker(week,date_str,healthy_eating,daily_exercise,no_smoke,time_outdoors,blogging)
                     VALUES(?,?,?,?,?,?,?)''',
                  (week, date_str, healthy_eating, daily_exercise, no_smoke, time_outdoors, blogging))
        print(f"Added habits on {date_str} in {week}.")
    conn.commit()
    conn.close()

def get_record(week: int, date_str: str):
    try:
        week = int(week)
    except ValueError:
        return None
    conn = sqlite3.connect('monthly_habit_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM monthly_habit_tracker WHERE week = ? AND date_str = ?', (week, date_str))
    row = c.fetchone()
    conn.close()
    return row

def delete_row(week, date_str):
    conn = sqlite3.connect('monthly_habit_tracker.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM monthly_habit_tracker
                 WHERE week = ? AND date_str = ?''',
              (week, date_str))
    row = c.fetchone()
    if row:
        c.execute('''DELETE FROM monthly_habit_tracker 
                     WHERE week = ? AND date_str = ?''',
                  (week, date_str))
        conn.commit()
        print(f'Deleted habits on {date_str} in {week}.')
    else:
        print(f"No habits found for {date_str} in {week}.")
    conn.close()

def best_streak():
    conn = sqlite3.connect('monthly_habit_tracker.db')
    c = conn.cursor()
    c.execute('''
        SELECT healthy_eating, daily_exercise, no_smoke, time_outdoors, blogging 
        FROM monthly_habit_tracker
        ORDER BY id ASC
    ''')
    rows = c.fetchall()
    conn.close()
    streak = 0
    for row in rows:
        if all(col == "checked-off" for col in row):
            streak += 1
        else:
            break
    print(f"You have a {streak} day streak!")
    return streak

def best_habit_streak():
    conn = sqlite3.connect('monthly_habit_tracker.db')
    c = conn.cursor()
    habits = ["healthy_eating", "daily_exercise", "no_smoke", "time_outdoors", "blogging"]
    results = {}
    for habit in habits:
        c.execute(f'''SELECT COUNT(*) FROM monthly_habit_tracker
                      WHERE {habit} = "checked-off"''')
        count = c.fetchone()[0]
        results[habit] = count
    conn.close()
    if results:
        best_habit = max(results, key=results.get)
        best_count = results[best_habit]
        return best_habit, best_count
    else:
        return None

class HabitTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Habit Tracker")
        self.setGeometry(200, 200, 600, 400)

        init_db()

        layout = QVBoxLayout()

        week_date_layout = QHBoxLayout()
        self.week_input = QLineEdit()
        self.week_input.setPlaceholderText("Week number")
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("Date (e.g. 06.06.2025)")
        week_date_layout.addWidget(QLabel("Week:"))
        week_date_layout.addWidget(self.week_input)
        week_date_layout.addWidget(QLabel("Date:"))
        week_date_layout.addWidget(self.date_input)
        layout.addLayout(week_date_layout)

        self.habit_inputs = {}
        habits = ["healthy_eating", "daily_exercise", "no_smoke", "time_outdoors", "blogging"]
        for habit in habits:
            h_layout = QHBoxLayout()
            label = QLabel(habit.replace("_", " ").title() + ":")
            edit = QLineEdit()
            edit.setPlaceholderText("checked-off / not checked-off")
            h_layout.addWidget(label)
            h_layout.addWidget(edit)
            self.habit_inputs[habit] = edit
            layout.addLayout(h_layout)

        btn_layout = QHBoxLayout()
        self.view_btn = QPushButton("View Record")
        self.view_btn.clicked.connect(self.view_record)
        self.save_btn = QPushButton("Add/Update Record")
        self.save_btn.clicked.connect(self.save_record)
        self.delete_btn = QPushButton("Delete Record")
        self.delete_btn.clicked.connect(self.delete_record)
        self.streak_btn = QPushButton("Show Streak")
        self.streak_btn.clicked.connect(self.show_streak)
        self.best_habit_btn = QPushButton("Show Best Habit Streak")
        self.best_habit_btn.clicked.connect(self.show_best_habit_streak)

        btn_layout.addWidget(self.view_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.streak_btn)
        btn_layout.addWidget(self.best_habit_btn)
        layout.addLayout(btn_layout)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        self.setLayout(layout)

    def view_record(self):
        week = self.week_input.text().strip()
        date = self.date_input.text().strip()
        if not week or not date:
            QMessageBox.warning(self, "Input Error", "Please enter both week and date.")
            return
        record = get_record(week, date)
        if record:
            text = (
                f"Week: {record[1]}, Date: {record[2]}\n"
                f"Healthy Eating: {record[3]}\n"
                f"Daily Exercise: {record[4]}\n"
                f"No Smoke: {record[5]}\n"
                f"Time Outdoors: {record[6]}\n"
                f"Blogging: {record[7]}"
            )
            self.result_display.setPlainText(text)
            for idx, habit in enumerate(["healthy_eating", "daily_exercise", "no_smoke", "time_outdoors", "blogging"], start=3):
                self.habit_inputs[habit].setText(record[idx])
        else:
            self.result_display.setPlainText("No record found for this week and date.")
            for field in self.habit_inputs.values():
                field.clear()

    def save_record(self):
        week = self.week_input.text().strip()
        date = self.date_input.text().strip()
        if not week or not date:
            QMessageBox.warning(self, "Input Error", "Please enter both week and date.")
            return

        values = []
        valid_values = {"checked-off", "not checked-off"}
        for habit in ["healthy_eating", "daily_exercise", "no_smoke", "time_outdoors", "blogging"]:
            val = self.habit_inputs[habit].text().strip()
            if val not in valid_values:
                QMessageBox.warning(self, "Input Error",
                                    f"'{habit.replace('_', ' ').title()}' must be 'checked-off' or 'not checked-off'.")
                return
            values.append(val)

        add_or_update_table(week, date, *values)
        QMessageBox.information(self, "Saved", "Record added/updated successfully.")
        self.view_record()

    def delete_record(self):
        week = self.week_input.text().strip()
        date = self.date_input.text().strip()
        if not week or not date:
            QMessageBox.warning(self, "Input Error", "Please enter both week and date.")
            return

        confirmed = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the record for week {week} and date {date}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmed == QMessageBox.Yes:
            delete_row(week, date)
            self.result_display.setPlainText(f"Record for week {week}, date {date} deleted (if existed).")
            for field in self.habit_inputs.values():
                field.clear()

    def show_streak(self):
        streak = best_streak()
        self.result_display.setPlainText(f"Current streak (all habits checked-off consecutively): {streak} day(s)")

    def show_best_habit_streak(self):
        result = best_habit_streak()
        if result:
            habit_name, count = result
            formatted_name = habit_name.replace("_", " ").title()
            self.result_display.setPlainText(
                f"Best habit streak is '{formatted_name}' with {count} day(s) checked-off.")
        else:
            self.result_display.setPlainText("No habit streak data found.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HabitTrackerApp()
    window.show()
    sys.exit(app.exec())
