from worker_2010 import DecadeWorker
from common.worker_main import WorkerMain

def main():
    worker = WorkerMain(DecadeWorker)
    worker.start()

if __name__ == "__main__":
    main()