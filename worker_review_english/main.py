from worker_review_english import EnglishWorker
from common.worker_main import WorkerMain

def main():
    worker = WorkerMain(EnglishWorker)
    worker.start()

if __name__ == "__main__":
    main()