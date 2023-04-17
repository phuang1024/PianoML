import argparse
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from tqdm import tqdm

from torch.nn.utils import clip_grad_norm_
from torch.utils.data import DataLoader, random_split
from torch.utils.tensorboard import SummaryWriter

from constants import *
from model import TokenDataset, Model


def get_run_directory(runs_dir):
    """
    Runs are runs_dir/000, /001, ...
    """
    max_num = None
    for run in os.listdir(runs_dir):
        if run.isdigit():
            num = int(run)
            if max_num is None or num > max_num:
                max_num = num
    if max_num is None:
        max_num = -1
    return os.path.join(runs_dir, f"{max_num+1:03d}")


def forward_batch(loader, model, criterion, scheduler, epoch: int, train: bool):
    """
    :param scheduler, epoch, train: For printing only.
    """
    name = "Train" if train else "Test"
    pbar = tqdm(enumerate(loader), total=len(loader), desc=name)
    for i, (x, y) in pbar:
        x, y = x.to(DEVICE), y.to(DEVICE)
        pred = model(x, y[:, :-1])
        pred = pred.view(-1, ONEHOT_SIZE)

        ans = y[:, 1:].reshape(-1)
        ans = torch.nn.functional.one_hot(ans, ONEHOT_SIZE).float()

        loss = criterion(pred, ans)

        lr = scheduler.get_last_lr()[0]
        pbar.set_description(f"{name}: Epoch {epoch+1}/{EPOCHS} | Batch {i+1}/{len(loader)} | Loss {loss.item():.5f} | LR {lr:.5f}")
        yield loss


def train(model, dataset, logdir):
    train_len = int(len(dataset) * 0.9)
    test_len = len(dataset) - train_len
    train_dataset, test_dataset = random_split(dataset, [train_len, test_len])
    loader_args = {
        "batch_size": BATCH_SIZE,
        "shuffle": True,
    }
    train_loader = DataLoader(train_dataset, **loader_args)
    test_loader = DataLoader(test_dataset, **loader_args)

    criterion = torch.nn.BCELoss()
    optim = torch.optim.SGD(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.StepLR(optim, step_size=LR_DECAY_STEPS, gamma=LR_DECAY_FAC)
    log = SummaryWriter(logdir)
    print("Saving tensorboard logs to", logdir)

    step = 0
    for epoch in range(EPOCHS):
        model.train()
        for loss in forward_batch(train_loader, model, criterion, scheduler, epoch, True):
            loss.backward()
            clip_grad_norm_(model.parameters(), 0.5)
            optim.step()
            optim.zero_grad()
            scheduler.step()

            log.add_scalar("Train loss", loss.item(), step)
            log.add_scalar("LR", scheduler.get_last_lr()[0], step)

            step += 1

        with torch.no_grad():
            model.eval()
            total_loss = 0
            for loss in forward_batch(test_loader, model, criterion, scheduler, epoch, False):
                total_loss += loss.item()
            avg_loss = total_loss / len(test_loader)
            log.add_scalar("Test loss", avg_loss, step)

        torch.save(model.state_dict(), os.path.join(logdir, f"epoch{epoch+1}.pt"))

    #sample = next(iter(test_loader))[0]
    #log.add_graph(model, sample.to(DEVICE))
    log.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to data directory")
    parser.add_argument("--runs", default="runs", help="Path to tensorboard runs directory")
    args = parser.parse_args()

    model = Model().to(DEVICE)
    num_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    dataset = TokenDataset(args.data)
    logdir = get_run_directory(args.runs)

    print(f"Dataset: {len(dataset)} samples of length {SEQ_LEN}")
    print(f"Model: {num_params} learnable parameters")
    train(model, dataset, logdir)


if __name__ == "__main__":
    main()
