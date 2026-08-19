from pathlib import Path
import datetime as dt
from utils import add_topic
from picker import ui
from period_flag import get_period_data
from period_flag import period_bounds
import curses
import sql_commands
import sqlite3

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
        while(True):
            add_sesh = input("Are you sure you want to add this session (y/n): ").lower()
            if add_sesh == 'n':
                print("Session Aborted")
                return
            if add_sesh == 'y':
                break

    # Get topic first using picker with fuzzy filtering

    try:
        with sqlite3.connect((TRACKER_DIR / "db/tracker.db")) as connector:
            cursor = connector.cursor()
            cursor.execute(sql_commands.TOPICS_BY_RECENCY)
            rows = cursor.fetchall()
            topics = []
            topic_id = -1
            for i in range(len(rows)):
                topics.append(rows[i][1])
            if topics == []:
                print("No topics to choose from. Please add a new topic")
                topic_id = add_topic(topics, connector) 
            else:
            # Use picker to get topic id
                topics.append("Add topic")
                idx = curses.wrapper(ui, topics)
                if idx == -1:
                    return 1
                if idx == len(topics) - 1:
                    topic_id = add_topic(topics, connector)
                else:
                    topic_id = rows[idx][0]

            if topic_id < 0:
                return 1
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
            return 0
        if args.stop:
            stop(TRACKER_DIR)
        bounds = period_bounds(args)
        if bounds:
            get_period_data(TRACKER_DIR, bounds, args)
            return 0
    else:
        print("No db initialised")
    return 0
