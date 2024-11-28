from worker_review_positive import PositiveWorker
from common.worker_main import WorkerMain

def main():
    worker = WorkerMain(PositiveWorker)
    worker.start()

if __name__ == "__main__":
    main()