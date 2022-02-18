
import os
from typing import List, Literal

BORDER_SIMPLE = {
    "x" : "─",
    "y" : "│",
    "top_left" : "┌",
    "top_right" : "┐",
    "middle_left" : "├",
    "middle_right" : "┤",
    "bottom_left" : "└",
    "bottom_right" : "┘",
}

BORDER_DOUBLE = {
    "x" : "═",
    "y" : "║",
    "top_left" : "╔",
    "top_right" : "╗",
    "middle_left" : "╠",
    "middle_right" : "╣",
    "bottom_left" : "╚",
    "bottom_right" : "╝",
}

class TerminalTable():
    """Print a beautiful table in the terminal"""

    def __init__(self, title: str = None, style=BORDER_DOUBLE, color="\033[94m") -> None:
        self.title = title
        self.border_style = style
        self.border_color = color

        self.line('top')
        self.print(title)
        self.line()
        pass

    def deco(self, position: str) -> str:
        """Get a decorator with the current style"""
        return self.border_color + self.border_style[position] + "\033[0m"

    def text_wrap(self, content: str) -> List[str]:
        """Get a list of the content at the size of the table"""
        terminal_size = os.get_terminal_size().columns
        size = terminal_size - 5
        return  [ content[i:i+size] + (' ' * (size - len(content[i:i+size]))) for i in range(0, len(content), size) ]

    def print(self, content: str, color: str = '\033[94m'):
        """Print a new line with a content in the table"""
        printing = [ (f"{self.deco('y')} {color}{line} {self.deco('y')}") for line in self.text_wrap(content) ]
        return print('\n'.join(printing))

    def line(self, position: Literal['top', 'middle', 'bottom'] = 'middle'):
        """Draw a line ine the table"""
        terminal_size = os.get_terminal_size()
        print(f"{self.deco(position + '_left')}{self.border_color}{self.deco('x') * (terminal_size.columns - 3) }{self.deco(position + '_right')}")

    def end(self):
        """End the table with a end line"""
        self.line('bottom')
        del self