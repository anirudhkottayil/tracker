"""SQL commands used by tracker.py.

Schema (CREATE TABLE / CREATE INDEX) lives separately in schema.sql --
this file holds only the statements run routinely while the program
is in use. See DESIGN.md Sec 7 for the reasoning behind each one.

Every placeholder is a positional '?', bound in the order noted above
each query -- sqlite3 fills these in safely, so a raw value should
never be f-string'd or %-formatted into any of these strings directly.
"""

# --- Topic list: used by --stop, --edit's topic change, and --rename-topic ---
# no params. Most-recently-used topic first; a topic with no sessions yet
# sorts last, since SQLite orders NULL last in a DESC sort.
TOPICS_BY_RECENCY = """
    SELECT t.id, t.name
    FROM topics t
    LEFT JOIN sessions s ON s.topic_id = t.id
    GROUP BY t.id
    ORDER BY MAX(s.start_time) DESC
"""

# --- --stop ---
# params: (name,)
INSERT_TOPIC = "INSERT INTO topics (name) VALUES (?)"

# params: (topic_id, start_time, end_time)
INSERT_SESSION = "INSERT INTO sessions (topic_id, start_time, end_time) VALUES (?, ?, ?)"

# --- Reporting: --today / --yesterday / --week / etc. (default, aggregated by topic) ---
# params: (range_start, range_end) -- range_end is exclusive
# Duration isn't stored, so it's computed here: julianday() gives a
# difference in days as a float, * 86400 converts that to seconds.
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

# --- Reporting: --list modifier (individual sessions, IDs included) ---
# params: (range_start, range_end) -- range_end is exclusive
SESSIONS_BY_RANGE = """
    SELECT s.id, t.name AS topic, s.start_time, s.end_time
    FROM sessions s
    JOIN topics t ON t.id = s.topic_id
    WHERE s.start_time >= ? AND s.start_time < ?
    ORDER BY s.start_time
"""

# --- Shared lookup for --edit and --delete (confirming what's about to change) ---
# params: (id,)
SESSION_BY_ID = """
    SELECT s.id, t.name AS topic, s.start_time, s.end_time
    FROM sessions s
    JOIN topics t ON t.id = s.topic_id
    WHERE s.id = ?
"""

# --- --edit ---
# params: (topic_id, id)
UPDATE_SESSION_TOPIC = "UPDATE sessions SET topic_id = ? WHERE id = ?"

# params: (start_time, id)
UPDATE_SESSION_START = "UPDATE sessions SET start_time = ? WHERE id = ?"

# params: (end_time, id)
UPDATE_SESSION_END = "UPDATE sessions SET end_time = ? WHERE id = ?"

# --- --delete ---
# params: (id,)
DELETE_SESSION = "DELETE FROM sessions WHERE id = ?"

# --- --rename-topic ---
# params: (name, id)
UPDATE_TOPIC_NAME = "UPDATE topics SET name = ? WHERE id = ?"

# --merge-topics was dropped (see DESIGN.md Sec 7.7) -- if two topics ever
# genuinely need consolidating, that section has the two-statement manual
# fallback rather than a maintained command here.
