from worker_game_validator import WorkerGameValidator
from common.worker_main import WorkerMain

def main():
    worker = WorkerMain(WorkerGameValidator)
    worker.start()

if __name__ == "__main__":
    main()