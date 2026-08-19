import sqlite3
import sql_commands
import datetime as dt
from period_flag import display_list
from utils import confirm, pick_topic

def delete_session(TRACKER_DIR, session_id):
    try:
        with sqlite3.connect((TRACKER_DIR / "db/tracker.db")) as connector:
            cursor = connector.cursor()
            cursor.execute(sql_commands.SESSION_BY_ID, (session_id,))
            row = cursor.fetchone()

            if row is None:
                print(f"No session with id {session_id}")
                return
            display_list([row])

            if not confirm("Delete this session?"):
                print("Cancelled")
                return

            cursor.execute(sql_commands.DELETE_SESSION, (session_id,))
        print("Session deleted")
    except sqlite3.OperationalError as e:
        print(f"Couldn't reach the database: {e}")
    finally:
        if connector:
            connector.close()

def prompt_time(prompt: str, base: dt.datetime):
    while True:
        raw = input(f"{prompt} (blank to cancel): ").strip()
        if raw == "":
            return None
        try:
            hour, minute = map(int, raw.split(":"))
            return base.replace(hour=hour, minute=minute, second=0, microsecond=0)
        except ValueError:
            print("Didn't understand that -- use HH:MM")

def edit_session(TRACKER_DIR, session_id):
    try:
        with sqlite3.connect((TRACKER_DIR / "db/tracker.db")) as connector:
            cursor = connector.cursor()
            cursor.execute(sql_commands.SESSION_BY_ID, (session_id,))
            row = cursor.fetchone()

            if row is None:
                print(f"No session with id {session_id}")
                return
            display_list([row])

            while True:
                choice = input("Edit (t)opic, (s)tart, (e)nd, or (c)ancel: ").strip().lower()
                if choice in ("t", "s", "e", "c"):
                    break
            if choice == 'c':
                print("Cancelled")
                return
            try:
                if choice == "t":
                    new_topic_id = pick_topic(connector)
                    if new_topic_id < 0:
                        print("Cancelled")
                        return
                    cursor.execute(sql_commands.UPDATE_SESSION_TOPIC, (new_topic_id, session_id))
                else:
                    _, _, start_str, end_str = row
                    field = "start" if choice == "s" else "end"
                    current = dt.datetime.fromisoformat(start_str if choice == "s" else end_str).astimezone()
                    new_dt = prompt_time(f"New {field} time (HH:MM, currently {current:%H:%M})", current)
                    if new_dt is None:
                        print("Cancelled")
                        return
                    query = sql_commands.UPDATE_SESSION_START if choice == "s" else sql_commands.UPDATE_SESSION_END
                    cursor.execute(query, (new_dt.astimezone(dt.timezone.utc).isoformat(), session_id))
                print("Session updated")
            except sqlite3.IntegrityError as e:
                print(f"Couldn't update: {e}")
    except sqlite3.OperationalError as e:
        print(f"Couldn't read database: {e}")
    finally:
        if connector:
            connector.close()


