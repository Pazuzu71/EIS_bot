from ftplib import FTP
import os
import datetime
from dateutil import parser

def ftp_search(region = 'Tulskaja_obl', doctype='order', eisdocno='0366200035622001408', last_publication_date = parser.parse('2022-12-04 17:26:00')):
    doctype_dict = {
        'order': 'notifications'
    }
    ftp = FTP('ftp.zakupki.gov.ru')
    ftp.login('free', 'free')
    ftp.set_pasv(True)
    print(ftp.dir(f'fcs_regions//{region}//{doctype_dict.get(doctype)}'))
    ftp.close()


if __name__ == '__main__':
    ftp_search()
