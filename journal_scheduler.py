from ftplib import FTP
import os
import datetime
import zipfile
from db import sql_connection, insert, selectz, conn_close, selectz_distinct
import json


def journal_update():

    region = 'Tulskaja_obl'
    print(f'Запуск задания по обновлению базы в {datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%Y %H:%M")}')
    '''Словарь типов документов (ключ: часть ссылки в адресной строке, значение: папка на фтп)'''

    with open('dicts.json', 'r') as file:
        dicts = json.load(file)
    doctype_dict = dicts.get('doctype_dict')

    a = datetime.datetime.now()
    conn = sql_connection()
    zips_in_base = selectz_distinct(conn)
    conn_close(conn)
    b = datetime.datetime.now()
    print('выборка', zips_in_base)
    print('вермя на выборку', b - a)
    zips_in_base = [x[0] for x in zips_in_base]
    print('выборка 2', zips_in_base)

    '''Рабочая папка на фтп '''
    for doctype in doctype_dict.values():
        '''Подключение к ФТП'''
        ftp = FTP('ftp.zakupki.gov.ru')
        ftp.login('free', 'free')
        ftp.set_pasv(True)
        files = []
        ftp.cwd(f'fcs_regions//{region}//{doctype}')
        ftp.dir(files.append)
        # print(files)
        print(f'Сейчас выполняется планировщик {doctype}')

        # Перебираем каждый файл с фтп (список files)
        for file in files:
            tokens = file.split()
            file_name = tokens[8]

            print(f'Разыскиваем {file_name}')
            if file_name not in zips_in_base and file_name not in ('currMonth', 'prevMonth'):
                print(f'{file_name} не найден, дописываем в базу')
                conn = sql_connection()
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
        print(f'Папка Temp//{doctype} очищена')
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print('задание выполнено')


if __name__ == '__main__':
    journal_update()