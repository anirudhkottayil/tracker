from utils import add_topic, confirm, pick_topic
from period_flag import get_period_data, period_bounds
from edits import delete_session, edit_session
from pathlib import Path
import curses
import sql_commands
import sqlite3
import datetime as dt

def init(TRACKER_DIR) -> int:
    (TRACKER_DIR / "db/").mkdir(parents=True, exist_ok=True)

    try:
        with sqlite3.connect((TRACKER_DIR / "db/tracker.db")) as connection:
            cursor = connection.cursor()
            cursor.executescript((Path(__file__).parent / "schema.sql").read_text())
    except sqlite3.OperationalError as e:
        print("Failed to open db: ", e)
        return 1
    return 0

def start(TRACKER_DIR):
    try:
        with open((TRACKER_DIR / ".in_session.txt"), "r+") as file:
            if file.readline() != "":
                print("Already in session")
                return
            curr_time = dt.datetime.now(dt.timezone.utc)
            print(f"Session started at: {curr_time.astimezone().strftime('%H:%M')}")
            file.write(curr_time.isoformat())
    except OSError as e:
        print(f"Write failed on start: {e}")
        return 1
    return 0

def format_duration(delta: dt.timedelta) -> str:
    total_minutes = int(delta.total_seconds()) // 60
    hours, minutes = divmod(total_minutes, 60)
    if hours and minutes:
        return f"{hours} hr{'s' if hours != 1 else ''} and {minutes} min{'s' if minutes != 1 else ''}"
    if hours:
        return f"{hours} hr{'s' if hours != 1 else ''}"
    return f"{minutes} min{'s' if minutes != 1 else ''}"


def stop(TRACKER_DIR):
    start_time = 0
    end_time = dt.datetime.now(dt.timezone.utc)
    try:
        with open((TRACKER_DIR / ".in_session.txt"), "r+") as file:
            start_time = file.readline()
            if start_time == "":
                print("Not in session")
                return
            file.seek(0)
            file.truncate(0)
    except OSError as e:
        print(f"Write failed on stop: {e}")
        return 1

    time_spent = end_time - dt.datetime.fromisoformat(start_time)

    if time_spent.total_seconds() >= 10800: # Check for 3 hour mark
        inp = confirm("Are you sure you want to add this session")
        if not inp:
            print("Session Aborted")
            return
    try:
        with sqlite3.connect((TRACKER_DIR / "db/tracker.db")) as connector:
            topic_id = pick_topic(connector)
            if topic_id < 0:
                return 1
            cursor = connector.cursor()
            cursor.execute(sql_commands.INSERT_SESSION, (topic_id, start_time, end_time.isoformat()))
            print(f"Session added {format_duration(time_spent)}")
    except sqlite3.OperationalError as e:
        print(f"Failed to insert session: {e}")
        return 1
    finally:
        if connector:
            connector.close()

def args_run(args,TRACKER_DIR, is_db):
    if args.init:
        if is_db:
            print("db already initialised")
            return 
        if init(TRACKER_DIR):
            return
        is_db = 1
    elif is_db == 0:
        print("No db initialised. (Run --init)")
        return

    if is_db == 1:
        if args.start:
            start(TRACKER_DIR)
        elif args.stop:
            stop(TRACKER_DIR)
        elif args.edit is not None:
            edit_session(TRACKER_DIR, args.edit) 
        elif args.delete is not None:
            delete_session(TRACKER_DIR, args.delete)
        bounds = period_bounds(args)
        if bounds:
            get_period_data(TRACKER_DIR, bounds, args)
        return 0
    else:
        print("No db initialised")
    return 0
