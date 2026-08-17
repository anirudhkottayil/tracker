import difflib
from sql_commands import INSERT_TOPIC

def add_topic(topics=None, connector):
    topic = input("Enter new topic: ")
    if topics != None:
        matches = difflib.get_close_matches(topic, topics, n=3, cutoff=0.65)
        if matches != []:
            final_string = f"These topics already exist: "
            for i in range (len(matches)):
                final_string + f"{i+1}.{matches[i]} "
            print(final_string)

            while True:
                user_input = input("Did you mean to use one of these topics (y/n)").lower()
                if user_input == 'n':
                    break
                if user_input == 'y':
                    topic_idx = int(input("Enter topic no: "))
                    if topic_idx > 0 and topic_idx <= len(matches)
                    topic = matches[topoic_idx]
    topic_id = -1
    try:
        cursor = connector.cursor()
        cursor.execute(INSERT_TOPIC, topic)
        topic_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        print("Topic added")
    except sqlite3.OperationalError as e:
        print("Failed to insert topic: ", e)
    finally:
        if cursor:
            cursor.close()
        return topic_id

                


