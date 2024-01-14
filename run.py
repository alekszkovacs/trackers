import sys
import os

CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(f"{CURRENT_DIR}/src/processors")
sys.dont_write_bytecode = True  # Prevent the creation of __pycache__ directories

import src.processors.main as processmain

operation = str(sys.argv[1])

match operation:
    case "process":
        processmain.main()

    case _:
        print("invalid operation!")
