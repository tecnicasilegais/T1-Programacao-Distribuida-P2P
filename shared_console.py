from threading import Lock

mutex = Lock()


def shared_print(data):
    mutex.acquire()
    try:
        print(data)
    finally:
        mutex.release()
