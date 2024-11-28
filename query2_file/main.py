from query2_file import QueryTwoFile
from common.query_file_main import QueryFileMain

def main():
    worker = QueryFileMain(QueryTwoFile)
    worker.start()

if __name__ == "__main__":
    main()