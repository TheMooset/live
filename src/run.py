from multiprocessing import Process
import sentry_sdk
from config.settings import config
from workers.remove_inactive_rooms_worker import run_worker as remove_inactive_rooms_worker
from workers.update_room_participants_worker import run_worker as update_room_participants_worker

sentry_sdk.init(config.sentry_dsn)


config.app_title = "worker"

if __name__ == '__main__':
    print(config.app_title)
    all_processes = []

    for i in range(1):
        p_user = Process(target=remove_inactive_rooms_worker)
        p_user.start()
        all_processes.append(p_user)

    for i in range(1):
        p_user = Process(target=update_room_participants_worker)
        p_user.start()
        all_processes.append(p_user)

    for process in all_processes:
        process.join()
