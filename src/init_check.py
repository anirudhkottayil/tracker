import argparse
from pathlib import Path

TRACKER_DIR = Path("~/.local/share/tracker/").expanduser()

def is_db():
   if (TRACKER_DIR / "db/tracker.db").exists():
       return 1
   else:
       return 0

def init_files() -> None:
    (TRACKER_DIR / ".in_session.txt").touch(exist_ok=True)
    (TRACKER_DIR / ".initialized").touch(exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="This tool is to track your computer activites")
    parser.add_argument("--init", action="store_true", help="To create a database")
    parser.add_argument("--start", action="store_true", help="To start a session")
    parser.add_argument("--stop", action="store_true", help="To stop current session")
    parser.add_argument("--status", action="store_true", help="To display if in session or not")
    period = parser.add_mutually_exclusive_group()
    period.add_argument("--today", action="store_true", help="To show today's sessions")
    period.add_argument("--yesterday", action="store_true", help="To show yesterday's sessions")
    period.add_argument("--week", action="store_true", help="To show the sessions for this week (From Monday)")
    period.add_argument("--lweek", action="store_true", help="To show the sessions for last week (From previous Monday)")
    period.add_argument("--month", action="store_true", help="To show the sessions for the current month")
    period.add_argument("--lmonth", action="store_true", help="To show the sessions for last month")
    period.add_argument("--year", action="store_true", help="To show the sessions for the year")
    parser.add_argument("--graph", action="store_true", help="To show the graph for a session period")
    parser.add_argument("--list", action="store_true", help="To show individual sessions with id")
    parser.add_argument("--edit", type=int, metavar="ID", help="To edit a session by id")
    parser.add_argument("--delete", type=int, metavar="ID", help="To delete a session by id")
    return parser.parse_args()

def init_check():
    if not TRACKER_DIR.exists():
        TRACKER_DIR.mkdir(parents=True, exist_ok=True)
        init_files()
    if not (TRACKER_DIR / ".initialized").exists():
        init_files()

    return [parse_args(), TRACKER_DIR, is_db()]
