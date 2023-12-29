import traceback

from otp import Otp
from unicredit import Unicredit
from revolut import Revolut
from szep import Szep
from wise import Wise

from timeit import default_timer as timer


def main():
    _start = timer()

    processors = [Otp(), Revolut(), Szep(), Wise()]
    for processor in processors:
        _class_name = processor.__class__.__name__
        print(f"processing {_class_name}...")
        try:
            processor.execute()
        except Exception:
            traceback.print_exc()
        print(f"finished {_class_name}.")

    _end = timer()
    print(f"Processing accounts was taken {_end - _start} seconds.")


if __name__ == "__main__":
    main()
