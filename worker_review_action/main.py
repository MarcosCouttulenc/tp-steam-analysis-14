from worker_review_action import ActionWorker
from common.worker_main import WorkerMain

def main():
    worker = WorkerMain(ActionWorker)
    worker.start()

if __name__ == "__main__":
    main()
    