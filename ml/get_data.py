import os
import re
from threading import Thread

import requests
from tqdm import tqdm

THREADS = 32
OUTDIR = "data"


def extract_urls(url, extension):
    page = requests.get(url).text
    pattern = r"https\:\/\/www.midiworld.com\/.*?\." + extension
    return re.compile(pattern).findall(page)

def generate_urls():
    midis = []
    midis.extend(extract_urls("https://www.midiworld.com/classic.htm", "mid"))
    for subpage in extract_urls("https://www.midiworld.com/classic.htm", "htm"):
        midis.extend(extract_urls(subpage, "mid"))
    return set(midis)


def download(tasks):
    for i, url in tasks:
        filename = os.path.join(OUTDIR, f"{i}.mid")
        if not os.path.exists(filename):
            with open(filename, "wb") as f:
                f.write(requests.get(url).content)

def main():
    urls = generate_urls()
    tasks = list(zip(range(len(urls)), urls))
    thread_tasks = [tasks[i::THREADS] for i in range(THREADS)]
    threads = []
    for i in range(THREADS):
        thread = Thread(target=download, args=(thread_tasks[i],))
        thread.start()
        threads.append(thread)
    pbar = tqdm(total=len(urls))
    while any([thread.is_alive() for thread in threads]):
        num_done = len(os.listdir(OUTDIR))
        pbar.update(num_done - pbar.n)
    pbar.close()


if __name__ == "__main__":
    main()
