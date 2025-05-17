# utils/terminal.py

import os
import subprocess


def configure_terminal():
    try:
        if os.name == "posix":
            subprocess.run(["stty", "-echoctl"], stderr=subprocess.DEVNULL)

            import atexit

            atexit.register(
                lambda: subprocess.run(["stty", "echoctl"], stderr=subprocess.DEVNULL)
            )
    except Exception:
        pass
