import json
import logging
import threading
from datetime import datetime

from sections.reader import reader
from sections.saver import saver


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

SCHEDULE = 60
UI_PORT = 8084
UI_DIRECTORY = "/opt/powerWatcher/web/dist"
DATABASE = "/opt/powerWatcher/database.db"
DEVICE = "/dev/hidraw0"
SOCKET_HOST = "localhost"
SOCKET_PORT = 8085

read = reader(DEVICE)
save = saver(DATABASE)


# r = read.read()
# s = save.save(r)

def run_webserver():
    print("run webserver")
    # weber.run()

def run_reading():
    print("run reading")
    r = read.read()
    save.save(r)

def run_socket():
    print("run socket")
    # socket.run()


if __name__ == '__main__':


    exit_thread = threading.Event()


    try:
        while True:
            thread = threading.Thread(target=run_reading, daemon=True)
            thread.start()
            thread.join()

            if exit_thread.wait(timeout=SCHEDULE):
                break
            # x = threading.Thread(target=thread_function, args=(1,))


    except:
        # web_thread.join()
        exit_thread.set()
    print("Stopped")
