import argparse
import json
import os
import struct
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "ml"))

from net import recv

PORT = 7610


def parse_input(path):
    msgs = []
    with open(path, "r") as f:
        for line in f.read().strip().split("\n"):
            parts = line.split(" ")
            msgs.append((int(parts[0]), float(parts[1]), float(parts[2])))
    return msgs

def write_output(path, data):
    with open(path, "w") as f:
        for d in data:
            f.write(" ".join(map(str, d)))
            f.write("\n")


def recv(conn, length: int):
    data = b""
    tries = 0
    while len(data) < length:
        time.sleep(0.002)
        data += conn.recv(length - len(data))
        tries += 1
        if tries > 1000:
            raise Exception("recv timeout")
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input messages file parsed by a function")
    parser.add_argument("output")
    parser.add_argument("--ip", default="localhost")
    args = parser.parse_args()

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((args.ip, PORT))
    msgs = parse_input(args.input)
    data = json.dumps({"type": "autocomplete", "data": msgs}).encode("utf-8")
    sock.send(struct.pack("<I", len(data)))
    sock.send(data)
    length = struct.unpack("<I", sock.recv(4))[0]
    pred = recv(sock, length)
    data = json.loads(pred.decode("utf-8"))
    write_output(args.output, data["data"])


if __name__ == "__main__":
    main()

