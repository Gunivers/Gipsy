import os
from time import sleep
from setup import setup


def main():
    print('hello world !')

if __name__ == "__main__":
    try:
        print('\n🛫  Starting...\n')
        setup()
        print('\033[94m📠  Starting main script..\033[0m\n')
        main()
    except KeyboardInterrupt:
        print('\n\033[94mKeyboard Interrupt\033[0m')
    print('\n😴  Goodbye...\033[0m')
    os._exit(0)