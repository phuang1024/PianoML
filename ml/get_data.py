import argparse
import requests

import ipyparallel as ipp

URL = "https://www.midiworld.com/download/{}"


def binsearch():
    """
    Find number of MIDI files available.
    """
    def works(n):
        url = URL.format(n)
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            return False
        return r.status_code == 200

    min = 1
    max = 8000
    while True:
        if max - min <= 1:
            if works(max):
                return max
            return min
        mid = (min + max) // 2
        if works(mid):
            min = mid
        else:
            max = mid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", help="Output directory.")
    parser.add_argument("-j", type=int, default=8)
    args = parser.parse_args()

    print("Searching for number of MIDI files...")
    n = binsearch()
    print(f"Found {n} MIDI files.")


if __name__ == "__main__":
    main()
