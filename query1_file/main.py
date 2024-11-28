from query1_file import QueryOneFile
from common.query_file_main import QueryFileMain

def main():
    worker = QueryFileMain(QueryOneFile)
    worker.start()

if __name__ == "__main__":
    main()