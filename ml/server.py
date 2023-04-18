"""
Protocol: Objects serialized using json.
First 4byte little endian integer is the length of the json string.
Then the json string as bytes.
No enter between those two.

Client sends request of the form:
{
    "type": "autocomplete",
    "data": [
        [note1, start1, end1],
        [note2, start2, end2],
        ...
    ]
}
Response is:
{
    "data": [
        [note1, start1, end1],
        [note2, start2, end2],
        ...
    ]
}
"""

import json
import os
import struct
import sys
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "gui"))

from midi import *
from net import recv
from results import load_latest_model, run_model

PORT = 7611
GEN_LENGTH = 20


def handle_client(conn, model):
    length = struct.unpack("<I", conn.recv(4))[0]
    data = json.loads(recv(conn, length).decode())
    if data["type"] == "autocomplete":
        messages = []
        for msg in data["data"]:
            messages.append(AbsMessage(msg[0], 0.8, msg[1], msg[2]))
        tokens = msgs_to_tokens(messages)

        output = run_model(model, tokens, GEN_LENGTH)
        messages = []
        for msg in tokens_to_msgs(output):
            messages.append([msg.note, msg.start, msg.end])

        data = json.dumps({"data": messages})
        conn.send(struct.pack("<I", len(data)))
        conn.send(data.encode())


def main():
    model = load_latest_model("runs")

    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(("", PORT))
    sock.listen()
    print("Listening on port", PORT)
    while True:
        conn, addr = sock.accept()
        print("Connection from", addr)
        Thread(target=handle_client, args=(conn, model)).start()
        

if __name__ == "__main__":
    main()
