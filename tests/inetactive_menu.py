import curses

def menu(stdscr, options):
    curses.curs_set(0)
    selected = 0

    while True:
        stdscr.clear()
        for i, option in enumerate(options):
            if i == selected:
                stdscr.addstr(i, 0, f"> {option}", curses.A_REVERSE)
            else:
                stdscr.addstr(i, 0, f"  {option}")
        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(options) - 1:
            selected += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            return options[selected]

curses.wrapper(lambda stdscr: print(f"Selected: {menu(stdscr, ['joyeuse', 'voluspa', 'charlemagne'])}"))