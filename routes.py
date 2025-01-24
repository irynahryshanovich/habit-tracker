import datetime
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, current_app


pages = Blueprint("habits", __name__, template_folder="templates", static_folder="static")


@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime.datetime):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates

    return {"date_range": date_range}

def today_at_midnight():
    today = datetime.datetime.today()
    # by default time, min, sec are 0 - midnight
    return datetime.datetime(today.year, today.month, today.day)


@pages.route("/")
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()

    # find 'added' property, and then pass a query, that has a key of $lte less than or equal to
    # then we're passing the 'selected_data' as the value, it give us all habits
    # they added date either today or earlier
    habits_on_date = current_app.db.habits.find({"added": {"$lte": selected_date}})

    completions = [
        habit["habit"]
        for habit in current_app.db.completions.find({"date": selected_date})
    ]
    return render_template(
        "index.html",
        habits=habits_on_date,
        completions=completions,
        title="Habit Tracker - Home",
        selected_date=selected_date,
    )


@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()

    if request.form:
        current_app.db.habits.insert_one(
            {"_id": uuid.uuid4().hex, "added": today, "name": request.form.get("habit")}
        )

    return render_template(
        "add_habit.html",
        title="Habit Tracker - Add Habit",
        selected_date=today
    )


@pages.post("/complete")
def complete():
    date_string = request.form.get("date")
    # habitId linking two collections in MongoDB
    habit = request.form.get("habitId")
    date = datetime.datetime.fromisoformat(date_string)

    current_app.db.completions.insert_one({"date": date, "habit": habit})

    # With url_for say habits.index because accessing a sub route of the blueprint
    # For two endpoints in the same blueprint you can do habits.index = .index
    return redirect(url_for(".index", date=date_string))
