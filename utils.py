import difflib
from sql_commands import INSERT_TOPIC
import sqlite3

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
                topic_idx = int(input("Enter topic no: "))
                if topic_idx > 0 and topic_idx <= len(matches):
                    topic = matches[topic_idx]
    topic_id = -1
    try:
        curr = connector.cursor()
        curr.execute(INSERT_TOPIC, (topic,))
        topic_id = curr.lastrowid
        connector.commit()
        curr.close()
        print("Topic added")
    except sqlite3.Error as e:
        print("Failed to insert topic: ", e)
    finally:
        if curr:
            curr.close()
    return topic_id

                


