from worker_mac import MACOSWorker
from common.worker_main import WorkerMain

def main():
    worker = WorkerMain(MACOSWorker)
    worker.start()

if __name__ == "__main__":
    main()