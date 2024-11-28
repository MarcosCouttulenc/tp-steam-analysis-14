from worker_indie import WorkerIndie
from common.worker_main import WorkerMain

def main():
    worker = WorkerMain(WorkerIndie)
    worker.start()

if __name__ == "__main__":
    main()