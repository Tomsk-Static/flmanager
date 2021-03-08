import curses
commands = list()


class Command():
        def __init__(self, name, hotkey, descr, code):
                self.name = name
                self.hotkey = hotkey
                self.descr = descr
                self.code = code


help = Command('Help', 'h', 'Show helper', 104)
commands.append(help)
mkdir = Command('Make folder', 'm', 'Make new folder in current path', 109)
commands.append(mkdir)
delete = Command('Delete', 'd', 'Delete folder or file which specify pointer', 100)
commands.append(delete)
copy = Command('Copy', 'c', 'Copy file or all files in folder', 99)
commands.append(copy)
mkfile = Command('Make file', 'f', 'Make new empty file in current folder', 102)
commands.append(mkfile)
up = Command('Up', 'Arrow Up', 'Change pointer position up', curses.KEY_UP)
commands.append(up)
down = Command('Down', 'Arrow Down', 'Change pointer position down', curses.KEY_DOWN)
commands.append(down)
right = Command('Next Page', 'Arrow Right', 'Go to the next page', curses.KEY_RIGHT)
commands.append(right)
left = Command('Previos Page', 'Arrow Left', 'Go to the previos page', curses.KEY_LEFT)
commands.append(left)
esc = Command('Exit', 'ESC', 'Exit from manager', curses.ascii.ESC)
commands.append(esc)
enter = Command('Open', 'ENTER', 'Open folder/open file with nano', curses.ascii.NL)
commands.append(enter)
back = Command('Back', 'BACKSPASE', 'Back to previos folder', curses.KEY_BACKSPACE)
commands.append(back)


