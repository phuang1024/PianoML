import argparse

from tqdm import tqdm

from torch.utils.data import DataLoader, random_split
from torch.utils.tensorboard import SummaryWriter

from constants import *
from model import TokenDataset, Model


def foreach_batch(epoch, loader, model, criterion, optim, train: bool):
    total_loss = 0
    pbar = tqdm(enumerate(loader), total=len(loader), desc="Training" if train else "Testing", ascii=True)
    for i, (x, y) in pbar:
        x, y = x.to(DEVICE), y.to(DEVICE)
        print(x.shape, y.shape)
        y_hat = model(x, x)
        loss = criterion(y_hat, y)
        if train:
            loss.backward()
            optim.step()
            optim.zero_grad()

        total_loss += loss.item()
        pbar.set_description(f"Epoch {epoch}/{EPOCHS} | Batch {i}/{len(loader)} | Loss {loss.item()}")

    return total_loss

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
    optim = torch.optim.SGD(model.parameters(), lr=1)
    log = SummaryWriter()

    for epoch in range(EPOCHS):
        model.train()
        total_loss = foreach_batch(epoch, train_loader, model, criterion, optim, True)
        log.add_scalar("TrainLoss", total_loss, epoch)

        with torch.no_grad():
            model.eval()
            total_loss = foreach_batch(epoch, test_loader, model, criterion, optim, False)
            log.add_scalar("TestLoss", total_loss, epoch)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="Path to .pt data file")
    args = parser.parse_args()

    model = Model()
    dataset = TokenDataset(args.data)
    print(f"Dataset: {len(dataset)} batches of length {SEQ_LEN}")
    train(model, dataset)


if __name__ == "__main__":
    main()
