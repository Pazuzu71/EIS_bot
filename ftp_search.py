from ftplib import FTP
import os
import datetime
import zipfile


def create_dir(directory_name = 'Temp'):
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)


def clean_dir(directory_name):
    for path, dirs, files in os.walk(directory_name):
        if files:
            for file in files:
                os.unlink(os.path.join(path, file))
    for path, dirs, files in os.walk(directory_name):
        if dirs:
            for dir in dirs:
                os.unlink(os.path.join(path, dir))



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


def ftp_search(region = 'Tulskaja_obl', doctype='orderplan', eisdocno='202203663000336001', last_publication_date = datetime.datetime.strptime('26.05.2022 11:56', '%d.%m.%Y %H:%M')):
    '''Поиск файлов на ФТП и закачка их во временную папку'''

    '''Словарь типов документов (ключ: часть ссылки в адресной строке, значение: папка на фтп)'''
    doctype_dict = {
        'order': 'notifications',
        'contract': 'contracts',
        'orderplan': 'plangraphs2020',
        'protocol': 'protocols'
    }
    '''Словарь имен документов (ключ: часть ссылки в адресной строке, значение: начало имени файла на фтп)'''
    filename_dict = {
        'order': 'notification',
        'contract': 'contract',
        'orderplan': 'tenderPlan2020',
        'protocol': 'Protocol'
    }
    '''Подключение к ФТП'''
    ftp = FTP('ftp.zakupki.gov.ru')
    ftp.login('free', 'free')
    ftp.set_pasv(True)
    '''Рабочая папка на фтп '''
    directory = dir_choice(last_publication_date = last_publication_date)
    ftp.cwd(f'fcs_regions//{region}//{doctype_dict.get(doctype)}//{directory}')

    if directory in ('currMonth', 'prevMonth'):
        last_publication_date_str = datetime.datetime.strftime(last_publication_date, '%Y%m%d')
    else:
        last_publication_date_str = datetime.datetime.strftime(last_publication_date, '%Y%m')

    create_dir(directory_name='Temp')
    create_dir(directory_name=f'Temp//{doctype_dict.get(doctype)}')
    create_dir(directory_name=f'Temp//{doctype_dict.get(doctype)}//{eisdocno}')
    create_dir(directory_name=f'Temp//{doctype_dict.get(doctype)}//{eisdocno}//{last_publication_date_str}')
    # clean_dir(directory_name='Temp')
    # clean_dir(f'Temp//{eisdocno}')
    clean_dir(f'Temp//{eisdocno}//{last_publication_date_str}')

    '''Создаем список файлов работчей папки ФТП'''
    files = []
    ftp.dir(files.append)
    '''Перебираем каждый архив из списка файлов - скачиваем в темп, ищем нужный файл в архиве'''
    # print('****************ftp_search*****************')
    # print(files)
    for file in files:
        tokens = file.split()
        file_name = tokens[8]
        if file_name.startswith(f'{filename_dict.get(doctype).lower()}_{region}_{last_publication_date_str}'):
            with open(f'Temp//{doctype_dict.get(doctype)}//{eisdocno}//{last_publication_date_str}//{file_name}', 'wb') as f:
                ftp.retrbinary('RETR ' + file_name, f.write)
            z = zipfile.ZipFile(f'Temp//{doctype_dict.get(doctype)}//{eisdocno}//{last_publication_date_str}//{file_name}', 'r')
            for item in z.namelist():
                if item.endswith('.xml') and eisdocno in item and ('Notification' in item or 'contract_' in item or 'tenderPlan2020' in item or 'Protocol' in item):
                    z.extract(item, f'Temp//{doctype_dict.get(doctype)}//{eisdocno}//{last_publication_date_str}')
                    print(f'Файл {item} распакован')

    ftp.close()
    return last_publication_date_str


if __name__ == '__main__':
    ftp_search()




