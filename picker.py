import curses
import textwrap, tempfile, os
import json

# Remove end and adjust box size since end box is gone
def get_idx(curses, body, stdscr, width, height, topics, top, curr_len):
    current = 1
    i = top
    body.addstr(current, 2, f"{topics[i]}",
                curses.color_pair(1) | curses.A_REVERSE)
    body.refresh()
    while True:
        key = stdscr.getch() 
        if key == ord("q"):
            return -1
        if (key == 10) or (key == 13) or (key == curses.KEY_ENTER):
            return i
        if (key == curses.KEY_UP) or (key == ord("k")):
            if (i - 1) < top and (top > 0):
                return -3 #Key Up prev page
            if ((current - 1) < 1) or ((i - 1) < 0):
                continue
            body.addstr(current , 2, f"{topics[i]}"[:width - 4],
                        curses.color_pair(1))
            body.addstr(current - 1, 2, f"{topics[i-1]}"[:width - 4],
                        curses.color_pair(1) | curses.A_REVERSE)

            current -= 1
            i -= 1
            body.refresh()

        elif (key == curses.KEY_DOWN) or (key == ord("j")):
            if ((i + 1) > (len(topics) - 1)):
                continue

            if (i + 1) >= (top + curr_len) and ((top + curr_len) < len(topics)):
                return -2
            body.addstr(current, 2, f"{topics[i]}",
                        curses.color_pair(1))
            body.addstr(current + 1, 2, f"{topics[i + 1]}",
                        curses.color_pair(1) | curses.A_REVERSE)

            current += 1
            i += 1
            body.refresh()


def ui(stdscr, topics):
    if topics == []:
        return

    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.curs_set(0)

    height, width = stdscr.getmaxyx()
    header = stdscr.subwin(3, width, 0, 0)
    body = stdscr.subwin(height - 3, width, 3, 0)
    visible_rows = height - 3 - 2


    header.erase()
    header.bkgd(" ", curses.color_pair(1))
    title = "Select a topic"
    header.addstr(1, (width - len(title)) // 2, title, curses.color_pair(1) | curses.A_BOLD)
    header.refresh()

    body.erase()
    body.box()
    body.keypad(True)

    box_length = []
    top = 0
    itr = 1
    while True:
        length = min(visible_rows, len(topics) - top)
        body.erase()
        body.box()
        for i in range(length):
            body.addstr(i + 1, 2, f"{topics[top + i]}", curses.color_pair(1)) 
        body.refresh()

        idx = get_idx(curses, body, stdscr, width, height, topics, top, length)

        if idx >= -1: # either user press q or got the indx of quote
            return idx
        if idx == -2: # user went down to next screen of quotes
            top = top + length
            box_length.append(length)
        if idx == -3:
            top = top - box_length.pop()

