from worker_mac import MACOSWorker

def main():
    print("action: MACOSWorker - start")
    macos_worker = MACOSWorker()
    macos_worker.start()


if __name__ == "__main__":
    main()