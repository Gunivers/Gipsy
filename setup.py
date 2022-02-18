from array import array
import os
from pathlib import Path
import subprocess
import sys
from typing import Literal

import pkg_resources


python_required_major_version: int = 3

def p(msg: str, type: Literal["info", "error"] = "info"):
    if type == "error":
        print(f"\033[91m[Setup] ⚠️  {msg}\033[0m")
        return
    
    print(f"\033[94m[Setup] {msg}\033[0m")

def insall_module():
    
    _REQUIREMENTS_PATH = Path(__file__).with_name("requirements.txt")
    pip_command: array = ["pip", "install" ,"-r", str(_REQUIREMENTS_PATH)]

    # terminal style
    terminal_size = os.get_terminal_size()
    terminal_separator = '═' * (terminal_size.columns - 3)
    def print_line(text: str, color: str = '\033[94m'):
        size = terminal_size.columns - 5
        lines = [ text[i:i+size] for i in range(0, len(text), size) ]
        printing = [ (f"\033[94m║\033[0m {color}{line}{' ' * (size - len(line))}\033[0m \033[94m║\033[0m") for line in lines ]
        return '\n'.join(printing)


    print(f"""
\033[94m╔{terminal_separator}╗
{print_line("Pip - module installation process")}
\033[94m╠{terminal_separator}╣
{print_line('Checking installed modules...')}
{print_line(' ')}\033[0m""")

    # Check if required modules is satisfied
    try:
        with open(str(_REQUIREMENTS_PATH), 'r') as file:
            packages = pkg_resources.parse_requirements(file.readlines())
    except:
        print_line('Unable to parse requirements.txt')
    try: 
        pkg_resources.working_set.resolve(packages)
    except pkg_resources.DistributionNotFound as e:
        print( print_line(str(e), '\033[91m') )
        print( print_line(" "))
        print( print_line("Some modules are required, do you want to execute an installation from requirements.txt ?", '\033[0m') )
        user_res = input("  (yes) >")
        if not user_res.lower() in ["Yes", "y", "", " "]:
            sys.exit(1)

        # Installation from pip
        try:
            print(print_line('> ' + ' '.join(pip_command))+ '\n')
            subprocess.check_call([sys.executable, "-m"] + pip_command)
        except subprocess.CalledProcessError:
            print(f"""\033[94m
{print_line("Exit with error")}
\033[94m╚{terminal_separator}╝

\033[0m""")
            sys.exit(1)
        print("\n" + print_line("End of installation"))
    print(f"""\033[94m{print_line("required modules are satisfied")}
\033[94m╚{terminal_separator}╝
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
        p("⚙️  Module installation process, use --skip-pip to skip the module installation process")
        insall_module()

    p('End of setup')

if __name__ == "__main__":
    setup()