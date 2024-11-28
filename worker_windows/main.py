from worker_windows import WINDOWSWorker
from common.worker_main import WorkerMain

def main():
    worker = WorkerMain(WINDOWSWorker)
    worker.start()

if __name__ == "__main__":
    main()