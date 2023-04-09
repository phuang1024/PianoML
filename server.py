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
import time
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
from subprocess import Popen

import mido

from midi import events_to_midi
from run import main as run_main

PORT = 7608


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


def handle_client(conn):
    length = struct.unpack("<I", conn.recv(4))[0]
    data = json.loads(conn.recv(length).decode())
    if data["type"] == "autocomplete":
        events = []
        for note in data["data"]:
            events.append((note[1], note[0], 1))
            events.append((note[2], note[0], 0))
        events.sort(key=lambda x: x[0])
        midi = events_to_midi(events)
        midi.save("server.mid")
        run_main("server.mid", "pred.mid")

        midi = mido.MidiFile("pred.mid")
        messages = []
        starts = {}
        for msg in midi:
            if msg.type == "note_on":
                starts[msg.note] = msg.time
            elif msg.type == "note_off":
                if msg.note in starts:
                    messages.append((msg.note, starts[msg.note], msg.time))
                    del starts[msg.note]

        data = json.dumps({"data": messages})
        conn.send(struct.pack("<I", len(data)))
        conn.send(data.encode())


def main():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(("", PORT))
    sock.listen()
    while True:
        conn, addr = sock.accept()
        print("Connection from", addr)
        Thread(target=handle_client, args=(conn,)).start()
        

if __name__ == "__main__":
    main()
