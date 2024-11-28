from query5_file import QueryFiveFile
from common.query_file_main import QueryFileMain

def main():
    worker = QueryFileMain(QueryFiveFile)
    worker.start()

if __name__ == "__main__":
    main()