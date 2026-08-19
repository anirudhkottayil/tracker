import difflib
import sqlite3
import sql_commands
import curses
import datetime as dt
from picker import ui

def format_duration(delta: dt.timedelta) -> str:
    total_minutes = int(delta.total_seconds()) // 60
    hours, minutes = divmod(total_minutes, 60)
    if hours and minutes:
        return f"{hours} hr{'s' if hours != 1 else ''} and {minutes} min{'s' if minutes != 1 else ''}"
    if hours:
        return f"{hours} hr{'s' if hours != 1 else ''}"
    return f"{minutes} min{'s' if minutes != 1 else ''}"

def confirm(prompt:str):
    while True:
        user_input = input(f"{prompt} (y/n)").strip().lower()
        if user_input == 'y':
            return True
        if user_input == 'n':
            return False

def add_topic(topics=None, connector = None):
    topic = input("Enter new topic: ")
    if topics != None:
        matches = difflib.get_close_matches(topic, topics, n=3, cutoff=0.65)
        if matches != []:
            final_string = f"These topics already exist: "
            for i in range (len(matches)):
                final_string += f"{i+1}.{matches[i]} "
            print(final_string)

            inp = confirm("Did you mean to use one of these topics")
            if inp:
                while True:
                    try:
                        topic_idx = int(input("Enter topic no: "))
                        if isinstance(topic_idx, int):
                            if topic_idx > 0 and topic_idx <= len(matches):
                                topic = matches[topic_idx - 1]
                                break
                    except ValueError:
                        print("Enter a valid number")
    topic_id = -1
    try:
        curr = connector.cursor()
        curr.execute(sql_commands.INSERT_TOPIC, (topic,))
        topic_id = curr.lastrowid
        connector.commit()
        print("Topic added")
    except sqlite3.Error as e:
        print("Failed to insert topic: ", e)
    finally:
        if curr:
            curr.close()
    return topic_id

def pick_topic(connector):
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
        idx = curses.wrapper(ui, topics + ["Add topic"])
        if idx == -1:
            return -1
        if idx == len(topics):
            topic_id = add_topic(topics, connector)
        else:
            topic_id = rows[idx][0]
    cursor.close()
    return topic_id



