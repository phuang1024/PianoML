import argparse
import os
import shutil
import tempfile
from subprocess import run

import mido
import torch

from midi import *
from utils import file_counter, multiprocess

URL = "https://storage.googleapis.com/magentadata/datasets/maestro/v3.0.0/maestro-v3.0.0-midi.zip"


def tokenize_worker(files):
    for f in files:
        midi = mido.MidiFile(f)
        tokens = msgs_to_tokens(midi_to_msgs(midi))
        tokens = torch.tensor(tokens, dtype=torch.int16)
        with open(f+".pt", "wb") as fp:
            torch.save(tokens, fp)

def tokenize(args):
    files = [f for f in os.listdir(args.data) if f.endswith(".mid")]
    print(f"Tokenizing {len(files)} MIDI files.")
    files = [os.path.join(args.data, f) for f in files]
    worker_args = [[files[i::args.j]] for i in range(args.j)]
    multiprocess(tokenize_worker, args.j, worker_args, len(files), file_counter(args.data, ".pt"), "Tokenizing")


def download(args):
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "maestro.zip")
        print("Downloading MIDI files.")
        run(["wget", "-O", zip_path, URL], check=True)
        print("Unzipping MIDI files.")
        run(["unzip", zip_path], cwd=tmpdir, check=True)
        print("Copying MIDI files.")
        i = 0
        for root, dirs, files in os.walk(tmpdir):
            for f in files:
                if f.endswith((".midi", ".mid")):
                    out_path = os.path.join(args.data, f"{i}.mid")
                    shutil.copy(os.path.join(root, f), out_path)
                    i += 1

    print(f"Downloaded {i} MIDI files.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["download", "tokenize"])
    parser.add_argument("--data", default="data", help="Output directory.")
    parser.add_argument("-j", type=int, default=8)
    args = parser.parse_args()

    if args.action == "download":
        download(args)
    elif args.action == "tokenize":
        tokenize(args)


if __name__ == "__main__":
    main()
