import time


def recv(conn, length: int, timeout: float = 5):
    data = b""
    start = time.time()
    while len(data) < length:
        time.sleep(0.005)
        data += conn.recv(length - len(data))
        if time.time() - start > timeout:
            raise Exception("recv timeout")
    return data
