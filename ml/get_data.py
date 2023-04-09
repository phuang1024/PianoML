import os
from threading import Thread

import mido
import requests
from tqdm import tqdm

THREADS = 32
OUTDIR = "data"


def download(offset):
    i = offset
    while True:
        try:
            r = requests.get(f"https://www.midiworld.com/download/{i}", timeout=1)
        except requests.exceptions.ConnectionError:
            break
        if r.status_code == 200:
            with open(f"{OUTDIR}/{i}.mid", "wb") as f:
                f.write(r.content)
        i += THREADS

def main():
    threads = []
    for i in range(THREADS):
        thread = Thread(target=download, args=(i,))
        thread.start()
        threads.append(thread)

    pbar = tqdm(desc="Downloading")
    while any([thread.is_alive() for thread in threads]):
        num_done = len(os.listdir(OUTDIR))
        pbar.update(num_done - pbar.n)
    pbar.close()

    bad = 0
    for f in tqdm(os.listdir(OUTDIR), desc="Checking consistency"):
        try:
            mido.MidiFile(os.path.join(OUTDIR, f))
        except:
            os.remove(os.path.join(OUTDIR, f))
            bad += 1
    print(f"Removed {bad} bad files")


if __name__ == "__main__":
    main()
