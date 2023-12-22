import sys
import os

_current_dir = os.path.dirname(__file__)
sys.path.append(f"{_current_dir}/src/processor")
sys.dont_write_bytecode = True  # Prevent the creation of __pycache__ directories

from src.processor import main

operation = str(sys.argv[1])

match operation:
    case "process":
        main.main()

    case _:
        print("invalid operation!")