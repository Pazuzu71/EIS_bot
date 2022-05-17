from ftplib import FTP
import os
import datetime
from dateutil import relativedelta


def ftp_search(region = 'Tulskaja_obl', doctype='order', eisdocno='0366200035622001408', last_publication_date = datetime.datetime.strptime('12.04.2022 17:26', '%d.%m.%Y %H:%M')):

    doctype_dict = {
        'order': 'notifications'
    }
    month_now = datetime.datetime.now().month

    ftp = FTP('ftp.zakupki.gov.ru')
    ftp.login('free', 'free')
    ftp.set_pasv(True)
    print(ftp.dir(f'fcs_regions//{region}//{doctype_dict.get(doctype)}'))
    ftp.close()
    # last_publication_date = datetime.datetime.strptime('01.01.1970 00:00', '%d.%m.%Y %H:%M')
    print(month_now)
    print(last_publication_date.month)
    print(month_now - last_publication_date.month)
    print(datetime.datetime.now() - last_publication_date)
    print(relativedelta.relativedelta(datetime.datetime.now(), last_publication_date))

if __name__ == '__main__':
    ftp_search()
