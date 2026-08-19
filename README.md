# tracker

A personal command-line time tracker. Start and stop sessions, tag each one
with a topic, and see where the time actually went — today, this week, last
month — as a table or a quick terminal bar graph. Built to run from two
machines kept in sync with Syncthing, not a hosted service.

Every design decision behind this — the schema, why SQLite, why Syncthing
over the alternatives, what got tried and dropped along the way — lives in
`DESIGN.md`. This file is the short, practical version: how to install it
and how to use it day to day.

## Install

From inside the project directory:

```
pipx install .
```

This installs the `tracker` command into its own isolated environment, so
it won't collide with anything else on the system.

## First-time setup

The database has to be created exactly once, on exactly one machine, before
it's shared with the other one. Doing this out of order can let both
machines create their own independent database at the same path, which
Syncthing can't merge back together — see `DESIGN.md` §7.5 for the full
reasoning. The short version:

1. On one machine only: `tracker --init`
2. Share the folder it created (`~/.local/share/tracker/db/`) in Syncthing
   with the other machine.
3. On the second machine, accept the incoming folder and wait for Syncthing
   to report it fully synced.
4. Never run `--init` again, on either machine — everything after this is
   `--start` / `--stop` / the reporting flags.

## Commands

| Command | What it does |
|---|---|
| `tracker --init` | One-time database setup. Refuses if one already exists. |
| `tracker --start` | Starts a session. Refuses if one is already running. |
| `tracker --stop` | Stops the current session and prompts for a topic. |
| `tracker --status` | Shows whether a session is running, and for how long. |
| `tracker --today` | Time spent today, by topic. |
| `tracker --yesterday` | Time spent yesterday, by topic. |
| `tracker --week` | This week so far (Monday to now). |
| `tracker --lweek` | All of last week. |
| `tracker --month` | This month so far. |
| `tracker --lmonth` | All of last month. |
| `tracker --year` | This year so far. |
| `tracker --edit ID` | Change a session's topic, start time, or end time. |
| `tracker --delete ID` | Delete a session, after confirming. |

`--graph` and `--list` aren't commands on their own — they modify one of the
period flags above:

```
tracker --today --graph    # a bar per topic, instead of a table
tracker --today --list     # individual sessions with their IDs, instead
                            # of totals -- this is where the IDs for
                            # --edit and --delete come from
```

Sessions longer than 3 hours ask for confirmation before being saved, in
case the machine slept and the clock kept running without you.

## Where the data lives

The database is `~/.local/share/tracker/db/tracker.db` — this is the folder
to point Syncthing at. The file that tracks whether a session is currently
running (`~/.local/share/tracker/.in_session.txt`) deliberately lives
outside that folder and is never synced — a session is tied to whichever
machine it was started on. `DESIGN.md` §7.3 and §7.4 cover why.
