from pathlib import Path
import subprocess
import sys
from typing import List, Literal
import pkg_resources


python_required_major_version: int = 3

def p(msg: str, type: Literal["info", "error"] = "info"):
    if type == "error":
        print(f"\033[91m[Setup] ⚠️  {msg}\033[0m")
        return
    
    print(f"\033[94m[Setup] {msg}\033[0m")

def insall_module():
    
    _REQUIREMENTS_PATH = Path(__file__).with_name("requirements.txt")
    pip_command: List = ["pip", "install" ,"-r", str(_REQUIREMENTS_PATH)]

    terminal = TerminalTable(title="Pip - module installation process")
    terminal.print('Checking installed modules...')
    # Check if required modules is satisfied
    try:
        with open(str(_REQUIREMENTS_PATH), 'r') as file:
            packages = pkg_resources.parse_requirements(file.readlines())
    except:
        terminal.print('Unable to parse requirements.txt')
    try: 
        pkg_resources.working_set.resolve(packages)
    except pkg_resources.DistributionNotFound as e:
        terminal.print("Some modules are required, do you want to execute an installation from requirements.txt ?", '\033[0m')
        user_res = input("  (yes) > ")
        if not user_res.lower() in ["yes", "y", "", " "]:
            terminal.end()
            sys.exit(0)

        # Installation from pip
        try:
            terminal.print('> ' + ' '.join(pip_command))
            subprocess.check_call([sys.executable, "-m"] + pip_command)
        except subprocess.CalledProcessError:
            terminal.print("Exit with error")
            terminal.end()
            sys.exit(1)

        terminal.print("End of installation")

    terminal.print("required modules are satisfied")
    terminal.end()


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