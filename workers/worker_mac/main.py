from workers.worker_mac.worker_mac import MACOSWorker
import logging

def main():
    logging.info("action: MACOSWorker - start")
    macos_worker = MACOSWorker()
    macos_worker.start()


main()