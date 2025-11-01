import os
import sys
import termios
import tty

options = ['joyeuse', 'voluspa', 'charlemagne']
selected = 0

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == '\x1b':  # Escape sequence
            ch2 = sys.stdin.read(2)
            return ch1 + ch2
        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def render():
    os.system('clear')
    print("Select a user:\n")
    for i, option in enumerate(options):
        prefix = "➤ " if i == selected else "  "
        print(f"{prefix}{option}")

while True:
    render()
    key = get_key()

    if key == '\x1b[A':  # Up arrow
        selected = (selected - 1) % len(options)
    elif key == '\x1b[B':  # Down arrow
        selected = (selected + 1) % len(options)
    elif key in ['\n', '\r']:  # Enter
        break

print(f"\n[.menu.select.audit] Selected: {options[selected]}")