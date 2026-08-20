TOPICS_BY_RECENCY = """
    SELECT t.id, t.name
    FROM topics t
    LEFT JOIN sessions s ON s.topic_id = t.id
    GROUP BY t.id
    ORDER BY MAX(s.start_time) DESC
"""

INSERT_TOPIC = "INSERT INTO topics (name) VALUES (?)"

INSERT_SESSION = "INSERT INTO sessions (topic_id, start_time, end_time) VALUES (?, ?, ?)"

SESSIONS_AGGREGATED_BY_RANGE = """
    SELECT
        t.name AS topic,
        SUM((julianday(s.end_time) - julianday(s.start_time)) * 86400) AS total_seconds
    FROM sessions s
    JOIN topics t ON t.id = s.topic_id
    WHERE s.start_time >= ? AND s.start_time < ?
    GROUP BY t.id
    ORDER BY total_seconds DESC
"""

SESSIONS_BY_RANGE = """
    SELECT s.id, t.name AS topic, s.start_time, s.end_time
    FROM sessions s
    JOIN topics t ON t.id = s.topic_id
    WHERE s.start_time >= ? AND s.start_time < ?
    ORDER BY s.start_time
"""

SESSION_BY_ID = """
    SELECT s.id, t.name AS topic, s.start_time, s.end_time
    FROM sessions s
    JOIN topics t ON t.id = s.topic_id
    WHERE s.id = ?
"""

UPDATE_SESSION_TOPIC = "UPDATE sessions SET topic_id = ? WHERE id = ?"

UPDATE_SESSION_START = "UPDATE sessions SET start_time = ? WHERE id = ?"

UPDATE_SESSION_END = "UPDATE sessions SET end_time = ? WHERE id = ?"

DELETE_SESSION = "DELETE FROM sessions WHERE id = ?"

UPDATE_TOPIC_NAME = "UPDATE topics SET name = ? WHERE id = ?"
