import os
import subprocess
import sys
from typing import Literal


python_required_major_version: int = 3

def p(msg: str, type: Literal["info", "error"] = "info"):
    if type == "error":
        print(f"\033[91m[Setup] ⚠️  {msg}\033[0m")
        return
    
    print(f"\033[94m[Setup] {msg}\033[0m")

def insall_module():
    pip_command: str = "pip install -r ./requirements.txt"

    # terminal style
    terminal_size = os.get_terminal_size()
    terminal_separator = '═' * (terminal_size.columns - 3)
    def print_line(text: str):
        size = terminal_size.columns - 5
        lines = [ text[i:i+size] for i in range(0, len(text), size) ]
        printing = [ (f"║ {line}{' ' * (size - len(line))} ║") for line in lines ]
        return '\n'.join(printing)


    print(f"""\033[94m
╔{terminal_separator}╗
{print_line("Pip - module installation process")}
╠{terminal_separator}╣
{print_line('> ' + pip_command)}
\033[0m""")

    try:
        subprocess.check_call([sys.executable, "-m"] + pip_command.split())
    except subprocess.CalledProcessError:
        print(f"""\033[94m
{print_line("Exit with error")}
╚{terminal_separator}╝

\033[0m""")
        sys.exit(1)
    print(f"""\033[94m
{print_line("End of installation")}
╚{terminal_separator}╝
\033[0m""")


def setup():
    p('Setup starting')

    # check python version
    if not sys.version_info[0] == python_required_major_version:
        p(f"Wrong version of python ({sys.version_info[0]}), major version required : {str(python_required_major_version)}", "error")
        sys.exit(1)

    # module installation process
    if "--skip-pip" in sys.argv:
        p("⏭️  Skipping the module installation process")
    else:
        p("⚙️  Installation of required module, use --skip-pip to skip the module installation process")
        insall_module()

    p('End of setup')

if __name__ == "__main__":
    setup()