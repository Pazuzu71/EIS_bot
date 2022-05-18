from ftplib import FTP
import os
import datetime


def create_dir(directory_name = 'Temp'):
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)


def clean_dir(directory_name):
    for path, dirs, files in os.walk(directory_name):
        for file in files:
            os.unlink(os.path.join(path, file))


def dir_choice(last_publication_date, date_now = datetime.datetime.now()):

    if date_now.year - last_publication_date.year == 0:
        if date_now.month - last_publication_date.month == 0:
            directory = 'currMonth'
        elif date_now.month - last_publication_date.month == 1:
            directory = 'prevMonth'
        else:
            directory = ''
    elif date_now.year - last_publication_date.year == 1:
        if date_now.month == '01' and last_publication_date.month == '12':
            directory = 'prevMonth'
        else:
            directory = ''
    else:
        directory = ''

    return directory


def ftp_search(region = 'Tulskaja_obl', doctype='order', eisdocno='0366200035622001408', last_publication_date = datetime.datetime.strptime('12.04.2022 17:26', '%d.%m.%Y %H:%M')):
    '''Поиск файлов на ФТП и закачка их во временную папку'''
    '''Словарь типов документов (ключ: часть ссылки в адресной строке, значение: папка на фтп)'''
    doctype_dict = {
        'order': 'notifications'
    }
    '''Словарь имен документов (ключ: часть ссылки в адресной строке, значение: начало имени файла на фтп)'''
    filename_dict = {
        'order': 'notification'
    }
    '''Подключение к ФТП'''
    ftp = FTP('ftp.zakupki.gov.ru')
    ftp.login('free', 'free')
    ftp.set_pasv(True)
    '''Рабочая папка на фтп '''
    directory = dir_choice(last_publication_date = last_publication_date)
    ftp.cwd(f'fcs_regions//{region}//{doctype_dict.get(doctype)}//{directory}')

    files = []
    '''Создаем список файлов работчей папки ФТП'''
    ftp.dir(files.append)
    '''Перебираем каждый архив из списка файлов - скачиваем в темп, ищем нужный файл в архиве'''
    for file in files:
        tokens = file.split()
        file_name = tokens[8]
        if directory in ('currMonth', 'prevMonth'):
            last_publication_date_str = datetime.datetime.strftime(last_publication_date, '%Y%m%d')
            if file_name.startswith(f'{filename_dict.get(doctype)}_{region}_{last_publication_date_str}'):
                with open(file_name, 'wb') as f:
                    ftp.retrbinary('RETR ' + file_name, f.write)
        else:
            last_publication_date_str = datetime.datetime.strftime(last_publication_date, '%Y%m')

    ftp.close()

if __name__ == '__main__':
    create_dir(directory_name='Temp')
    clean_dir(directory_name='Temp')
    ftp_search()
