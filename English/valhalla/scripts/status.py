import runpy
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def run_script(name):
    runpy.run_path(str(SCRIPT_DIR / name), run_name="__main__")


def main():
    print("## System Status")
    run_script("os_status.py")
    print()
    print("## Knowledge-Base Status")
    run_script("kb_status.py")


if __name__ == "__main__":
    main()
