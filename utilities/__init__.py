import os, socket, re
from ._timer import Timer


try:
    #For console text coloring
    import colorama
    from colorama import Fore, Style
    colorama.init()
    USE_COLORAMA = True
except:
    print("The 'Colorama' module is not installed. Colored output will be " \
          "printed without color. To fix this, do:\n'pip install colorama'\n")
    USE_COLORAMA = False


def color_print(msg: str, color, **kwargs):
    """Print using the given Fore color"""
    if USE_COLORAMA:
        print(f'{color}{msg}{Style.RESET_ALL}', **kwargs)
    else:
        print(msg, **kwargs)
    
class StringColor():
    
    @classmethod
    def c_str(cls, msg: str, color: Fore) -> str:
        """Returns the given string surrounded by colorama tags

        Args:
            msg (str): The string to color
            color (Fore): The color of the string

        Returns:
            str: A string usable in a print statement
        """
        if USE_COLORAMA:
            return f'{color}{msg}{Style.RESET_ALL}'
        else:
            return msg
    
    @classmethod
    def red(cls, msg):
        return cls.c_str(msg, Fore.RED)
    
    @classmethod
    def green(cls, msg):
        return cls.c_str(msg, Fore.GREEN)
    
    @classmethod
    def yellow(cls, msg):
        return cls.c_str(msg, Fore.YELLOW)
    
    @classmethod
    def blue(cls, msg):
        return cls.c_str(msg, Fore.BLUE)
    
    
def verify_dir(file_name: str):
    """Accepts a file path (with or without file name) and creates the full 
    folder structure of that path if it doesn't exist.

    Args:
        file_name (str): The filepath
    """
    file_dir = os.path.dirname(file_name)
    if file_dir: os.makedirs(file_dir, exist_ok=True)
        
        
def cls():
    """Clear the terminal"""
    os.system('cls' if os.name=='nt' else 'clear')