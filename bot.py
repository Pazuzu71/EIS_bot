from crawler import search_last_publication_date
from ftp_search import ftp_search


def main():
    last_publication_date = search_last_publication_date()
    ftp_search(last_publication_date=last_publication_date)


if __name__ == '__main__':
    main()