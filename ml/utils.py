import os
from multiprocessing import Process

from tqdm import tqdm


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


def _get_max_num(runs_dir) -> int:
    """
    Returns greatest numbered run directory.
    If empty, returns -1.
    """
    max_num = None
    for run in os.listdir(runs_dir):
        if run.isdigit():
            num = int(run)
            if max_num is None or num > max_num:
                max_num = num
    if max_num is None:
        max_num = -1
    return max_num

def get_new_run(runs_dir) -> str:
    """
    Returns path to new run directory.
    """
    num = _get_max_num(runs_dir) + 1
    return os.path.join(runs_dir, f"{num:03d}")

def get_last_run(runs_dir) -> str:
    """
    Returns path to last run directory.
    """
    num = _get_max_num(runs_dir)
    return os.path.join(runs_dir, f"{num:03d}")


def get_last_model(dir) -> str:
    """
    Returns path to last model in a single run directory.
    :param dir: e.g. runs/000
    :return: The models are saved as epoch.{x}.pt; the path with highest x is returned.
    """
    max_num = None
    path = None
    for file in os.listdir(dir):
        if file.endswith(".pt"):
            try:
                num = int(file.split(".")[1])
            except ValueError:
                continue
            if max_num is None or num > max_num:
                max_num = num
                path = os.path.join(dir, file)

    assert path is not None, f"No models found in {dir}"
    return path
