from otp import Otp
from unicredit import Unicredit
from revolut import Revolut
from szep import Szep
from wise import Wise

from timeit import default_timer as timer


def main():
    _start = timer()

    otp = Otp()
    print("processing OTP...")
    otp.execute()
    print("finished OTP.")

    # unicredit = Unicredit()
    print("processing Unicredit...")
    # unicredit.execute()
    print("finished Unicredit.")

    revolut = Revolut()
    print("processing Revolut...")
    revolut.execute()
    print("finished Revolut.")

    szep = Szep()
    print("processing Szep...")
    szep.execute()
    print("finished Szep.")

    wise = Wise()
    print("processing Wise...")
    wise.execute()
    print("finished Wise.")

    _end = timer()
    print(f"Job was taken {_end - _start} seconds.")


if __name__ == "__main__":
    main()
