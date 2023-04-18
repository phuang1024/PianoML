import os


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
