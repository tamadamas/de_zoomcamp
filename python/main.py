import sys

import pandas as pd


def main():
    print(sys.argv)

    day = sys.argv[1]

    print(f"Job finished successfully for day = {day}!")


if __name__ == "__main__":
    main()
