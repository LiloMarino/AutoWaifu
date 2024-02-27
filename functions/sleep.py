import threading
import time
import config

stop_event = threading.Event()

def sleep(time_to_sleep : float) -> bool:
    for _ in range(int((time_to_sleep // config.THREAD_VERIFICATION_TIME) + 1)):
        time.sleep(config.THREAD_VERIFICATION_TIME)
        if stop_event.is_set():
            return True
    return False
