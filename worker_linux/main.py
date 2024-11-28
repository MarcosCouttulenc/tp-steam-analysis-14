from worker_linux import LinuxWorker
from common.worker_main import WorkerMain

def main():
    worker = WorkerMain(LinuxWorker)
    worker.start()

if __name__ == "__main__":
    main()