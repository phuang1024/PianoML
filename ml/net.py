import time


def recv(conn, length: int):
    data = b""
    tries = 0
    while len(data) < length:
        time.sleep(0.005)
        data += conn.recv(length - len(data))
        tries += 1
        if tries > 1000:
            raise Exception("recv timeout")
    return data
