import argparse
import os
import requests
from multiprocessing import Process

import mido
import torch
from tqdm import tqdm

from midi import *

URL = "https://www.midiworld.com/download/{}"


def file_counter(directory, ext):
    def func():
        return len([f for f in os.listdir(directory) if f.endswith(ext)])
    return func


def multiprocess(target, num_jobs, args, total, progress, desc=""):
    """
    Start concurrent processes.
    :param target: Worker function.
    :param num_jobs: Number of processes to start.
    :param args: List of arguments for each process.
    :param total: Total number of items to process.
    :param progress: Function that returns how many things currently done.
    :param desc: Description for progress bar.
    """
    procs = []
    for i in range(num_jobs):
        p = Process(target=target, args=args[i])
        p.start()
        procs.append(p)

    pbar = tqdm(total=total, desc=desc)
    while any(p.is_alive() for p in procs):
        num_done = progress()
        pbar.update(num_done - pbar.n)
    pbar.close()


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

def download_worker(outdir, jobs):
    """
    Download MIDI files.
    """
    for i in jobs:
        url = URL.format(i)
        try:
            r = requests.get(url)
        except EOFError:
            print(f"Failed to retrieve MIDI {i}")
            continue

        if r.status_code == 200:
            path = os.path.join(outdir, f"{i}.mid")
            with open(path, "wb") as f:
                f.write(r.content)

            # Check consistency
            try:
                mido.MidiFile(path)
            except Exception as e:
                os.remove(path)
                print(f"Error on MIDI {i}: {e}")

                if isinstance(e, KeyboardInterrupt):
                    raise

def download(args):
    count = args.c
    if count < 0:
        print("Searching for number of MIDI files...")
        count = binsearch()
    print(f"Downloading {count} MIDI files.")

    files = list(range(1, count+1))
    worker_args = [files[i::args.j] for i in range(args.j)]
    worker_args = list(zip([args.output]*args.j, worker_args))

    multiprocess(download_worker, args.j, worker_args, count, file_counter(args.output, ".mid"), "Downloading")


def tokenize_worker(files):
    """
    Saves tokens as pytorch tensor to file+".pt"
    """
    for f in files:
        midi = mido.MidiFile(f)
        tokens = msgs_to_tokens(midi_to_msgs(midi))
        with open(f+".pt", "wb") as fp:
            torch.save(tokens, fp)

def tokenize(args):
    files = [f for f in os.listdir(args.output) if f.endswith(".mid")]
    print(f"Tokenizing {len(files)} MIDI files.")
    files = [os.path.join(args.output, f) for f in files]
    worker_args = [[files[i::args.j]] for i in range(args.j)]
    multiprocess(tokenize_worker, args.j, worker_args, len(files), file_counter(args.output, ".pt"), "Tokenizing")

    print(f"Combining tokens into {args.output}/tokens.pt")
    tokens = torch.zeros((0, 131))
    for f in files:
        with open(f+".pt", "rb") as fp:
            curr_tokens = torch.load(fp)
            tokens = torch.cat((tokens, curr_tokens), dim=0)
    with open(os.path.join(args.output, "tokens.pt"), "wb") as fp:
        torch.save(tokens, fp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("download", "tokenize"))
    parser.add_argument("output", help="Output directory (download) or file (tokenize).")
    parser.add_argument("-c", type=int, default=-1, help="Num of files to process. Negative = all.")
    parser.add_argument("-j", type=int, default=8)
    args = parser.parse_args()

    if args.action == "download":
        download(args)
    elif args.action == "tokenize":
        tokenize(args)


if __name__ == "__main__":
    main()
