from worker_review_indie import IndieReviewWorker
from common.worker_main import WorkerMain

def main():
    worker = WorkerMain(IndieReviewWorker)
    worker.start()

if __name__ == "__main__":
    main()