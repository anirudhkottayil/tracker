import sqlite3
import datetime as dt
import sql_commands
from rich.table import Table
from rich.console import Console
import hashlib
from rich.text import Text

console = Console()


PALETTE = ["bright_cyan", "bright_magenta", "bright_green", "bright_yellow", "bright_blue", "bright_red"]

def topic_color(topic: str) -> str:
    digest = hashlib.md5(topic.encode()).hexdigest()
    return PALETTE[int(digest, 16) % len(PALETTE)]

def format_duration_compact(delta: dt.timedelta) -> str:
    total_minutes = int(delta.total_seconds()) // 60
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h {minutes:02d}m"

def period_bounds(args, now=None):
    now = now or dt.datetime.now().astimezone()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    monday = today - dt.timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    if args.today:
        start, end = today, now
    elif args.yesterday:
        start, end = today - dt.timedelta(days=1), today
    elif args.week:
        start, end = monday, now
    elif args.lweek:
        start, end = monday - dt.timedelta(weeks=1), monday
    elif args.month:
        start, end = month_start, now
    elif args.lmonth:
        end = month_start
        start = (month_start - dt.timedelta(days=1)).replace(day=1)
    elif args.year:
        start, end = today.replace(month=1, day=1), now
    else:
        return None

    return start.astimezone(dt.timezone.utc), end.astimezone(dt.timezone.utc)

def display_table(rows):
    table = Table(header_style="bold cyan")
    table.add_column("Topic")
    table.add_column("Time", justify="right")
    for topic, total_seconds in rows:
        table.add_row(
            Text(topic, style=topic_color(topic)),
            format_duration_compact(dt.timedelta(seconds=total_seconds)),
        )
    console.print(table)


def display_graph(rows, width=30):
    total = sum(seconds for _, seconds in rows)
    grid = Table.grid(padding=(0, 1))
    grid.add_column()
    grid.add_column()
    grid.add_column(justify="right")
    for topic, seconds in rows:
        pct = (seconds / total * 100) if total else 0
        filled = round(width * pct / 100)
        color = topic_color(topic)
        bar = Text("█" * filled, style=color) + Text("░" * (width - filled), style="grey37")
        grid.add_row(Text(topic, style=color), bar, f"{pct:.0f}%")
    console.print(grid)


def display_list(rows):
    table = Table(header_style="bold cyan")
    for col in ("ID", "Topic", "Start", "End", "Time"):
        table.add_column(col)
    for session_id, topic, start_str, end_str in rows:
        start = dt.datetime.fromisoformat(start_str).astimezone()
        end = dt.datetime.fromisoformat(end_str).astimezone()
        table.add_row(
            str(session_id),
            Text(topic, style=topic_color(topic)),
            start.strftime("%H:%M"),
            end.strftime("%H:%M"),
            format_duration_compact(end - start),
        )
    console.print(table)


def get_period_data(TRACKER_DIR, bounds, args):
    start = bounds[0].isoformat()
    end = bounds[1].isoformat()

    try:
        with sqlite3.connect((TRACKER_DIR / "db/tracker.db")) as connector:
            connector.execute("PRAGMA foreign_keys = ON")
            cursor = connector.cursor()
            command = sql_commands.SESSIONS_BY_RANGE if args.list else sql_commands.SESSIONS_AGGREGATED_BY_RANGE
            cursor.execute(command, (start, end))
            rows = cursor.fetchall()
            if rows == []:
                print("No sessions to show in this period")
                return 1
            if args.list and args.graph:
                print("Use just --graph to see the graph")
            if args.list:
                display_list(rows)
            elif args.graph:
                display_graph(rows)
            else:
                display_table(rows)

    except sqlite3.OperationalError as e:
        print(f"Failed to get sessions: {e}")
        return 1
    finally:
        if connector:
            connector.close()



    
