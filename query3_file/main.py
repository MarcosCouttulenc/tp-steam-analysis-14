from query3_file import QueryThreeFile
from common.query_file_main import QueryFileMain

def main():
    worker = QueryFileMain(QueryThreeFile)
    worker.start()

if __name__ == "__main__":
    main()