from os import system
from os import name

def clear():
    """Clear user console."""

    if name == 'nt':
        system('cls')
    else:
        system('clear')