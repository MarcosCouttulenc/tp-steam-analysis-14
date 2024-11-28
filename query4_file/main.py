from query4_file import QueryFourFile
from common.query_file_main import QueryFileMain

def main():
    worker = QueryFileMain(QueryFourFile)
    worker.start()

if __name__ == "__main__":
    main()