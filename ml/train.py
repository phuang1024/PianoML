import argparse
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from tqdm import tqdm

from torch.nn.utils import clip_grad_norm_
from torch.utils.data import DataLoader, random_split
from torch.utils.tensorboard import SummaryWriter

from constants import *
from model import TokenDataset, Model


def forward_batch(loader, model, criterion, epoch: int, train: bool):
    name = "Train" if train else "Test"
    pbar = tqdm(enumerate(loader), total=len(loader), desc=name)
    for i, (x, y) in pbar:
        x, y = x.to(DEVICE), y.to(DEVICE)
        y_hat = model(x, x)
        loss = criterion(y_hat, y)
        pbar.set_description(f"{name}: Epoch {epoch+1}/{EPOCHS} | Batch {i+1}/{len(loader)} | Loss {loss.item():.5f}")

        yield loss

def train(model, dataset):
    train_len = int(len(dataset) * 0.9)
    test_len = len(dataset) - train_len
    train_dataset, test_dataset = random_split(dataset, [train_len, test_len])
    loader_args = {
        "batch_size": BATCH_SIZE,
        "shuffle": True,
    }
    train_loader = DataLoader(train_dataset, **loader_args)
    test_loader = DataLoader(test_dataset, **loader_args)

    criterion = torch.nn.MSELoss()
    optim = torch.optim.SGD(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.StepLR(optim, step_size=LR_DECAY_STEPS, gamma=LR_DECAY_FAC)
    log = SummaryWriter()

    step = 0
    for epoch in range(EPOCHS):
        model.train()
        for loss in forward_batch(train_loader, model, criterion, epoch, True):
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
            for loss in forward_batch(test_loader, model, criterion, epoch, False):
                total_loss += loss.item()
            avg_loss = total_loss / len(test_loader)
            log.add_scalar("Test loss", avg_loss, step)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="Path to data directory")
    args = parser.parse_args()

    model = Model().to(DEVICE)
    dataset = TokenDataset(args.data)
    print(f"Dataset: {len(dataset)} batches of length {SEQ_LEN}")
    train(model, dataset)


if __name__ == "__main__":
    main()
