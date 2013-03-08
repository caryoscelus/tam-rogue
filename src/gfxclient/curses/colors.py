import curses

COLORS = [
    ('default', None),
    ('black', curses.COLOR_BLACK),
    ('blue', curses.COLOR_BLUE),
    ('cyan', curses.COLOR_CYAN),
    ('green', curses.COLOR_GREEN),
    ('magenta', curses.COLOR_MAGENTA),
    ('red', curses.COLOR_RED),
    ('white', curses.COLOR_WHITE),
    ('yellow', curses.COLOR_YELLOW),
]

NAMED_COLORS = {
    COLORS[i][0] : i
        for i in range(len(COLORS))
}
