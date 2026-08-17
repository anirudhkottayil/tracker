from pathlib import Path
import datetime as dt
from utils import add_topic

def init(TRACKER_DIR) -> int:
    import sqlite3
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
        with open((TRACKER_DIR / ".in_session.txt"), "r") as file:
            if file.readline() != "":
                print("Already in session")
                return
            curr_time = dt.datetime.now(dt.timezone.utc)
            print(f"Started at: {curr_time.astimezone().strftime('%H:%M')}")
            file.write(curr_time.isoformat())
    except OSError as e:
        print(f"Write failed on start: {e}")
        return 1
    return 0

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
    return 0

    time_spent = end_time - dt.datetime.fromisoformat(start_time)

    if time_spent.total_secods() >= 10800: # Check for 3 hour mark
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
            rows = curosr.fetchall()
            topics = []
            for i in range(len(rows)):
                topics.append(rows[i][1])
            if topics == []:
                topic_id = add_topic(topics, connector) 
            # Use picker to get topic id
            if topic_id < 0:
                cursor.close()
                connector.close()
                return 1
            cursor.execute(sql_commands.INSERT_SESSION, (topic_id, start_time, end_time.isoformat()))
            cursor.commit()
            cursor.close()
            connector.close()
    except sqlite3.OperationalError as e:
        print(f"Failed to insert session: {e}")
        return 1
    finally:
        if connector:
            connector.close()



def args_run(args,TRACKER_DIR, is_db):
    # if not args.init and is_db == 0:
    #     print("No db initialised. (Run --init)")
    #     return 1 # Exit no db
    # elif args.init and is_db == 1:
    #     print("db already initialised")
    #     return 1
    # else:
    #     if init(TRACKER_DIR):
    #         return 1
    #     is_db = 1
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
    else:
        print("No db initialised")
    # if args.stop:
    #     stop(TRACKER_DIR)
    # if args.filter and not args.remove:
    #     print("--filter requires --remove")
    # if args.save or args.add or args.random or args.remove or args.filter or args.where:
    #     return 1
    return 0
