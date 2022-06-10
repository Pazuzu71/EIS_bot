from ftplib import FTP
import os
import datetime
import zipfile
from db import sql_connection, insert, selectz, conn_close
import json


region = 'Tulskaja_obl'

with open('dicts.json', 'r') as file:
    dicts = json.load(file)
doctype_dict = dicts.get('doctype_dict')


'''Рабочая папка на фтп '''
for doctype in doctype_dict.values():
    '''Подключение к ФТП'''
    ftp = FTP('ftp.zakupki.gov.ru')
    ftp.login('free', 'free')
    ftp.set_pasv(True)
    files = []
    ftp.cwd(f'fcs_regions//{region}//{doctype}')
    ftp.dir(files.append)
    print(files)
    conn = sql_connection()
    for file in files:
        tokens = file.split()
        file_name = tokens[8]
        # print(file_name)
        if not selectz(conn, file_name) and file_name not in ('currMonth', 'prevMonth'):
            with open(f'Temp//{doctype}//{file_name}', 'wb') as f:
                ftp.retrbinary('RETR ' + file_name, f.write)
            z = zipfile.ZipFile(
                f'Temp//{doctype}//{file_name}', 'r')
            for item in z.namelist():
                entities = (file_name, item, datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))
                insert(conn, entities)
            z.close()

    conn_close(conn)
    ftp.close()
    '''Чистим папки'''
    for path, dirs, files in os.walk(f'Temp//{doctype}'):
        if files:
            for file in files:
                if file.endswith('.zip'):
                    os.unlink(os.path.join(path, file))
