import requests
from bs4 import BeautifulSoup
import re
import datetime


def search_last_publication_date(doctype='protocol', eisdocno='0166300024722000170'):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
        }
    '''Ищем документ через штатный поиск ЕИС. В Ссылку подставляем тим документа и номер.'''

    if doctype in ('order', 'protocol') and len(eisdocno) == 19:
        url = f'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString={eisdocno}'
    elif doctype == 'contract' and len(eisdocno) == 19:
        url = f'https://zakupki.gov.ru/epz/contract/search/results.html?searchString={eisdocno}'
    elif doctype == 'orderplan' and len(eisdocno) == 18:
        url = f'https://zakupki.gov.ru/epz/orderplan/search/results.html?searchString={eisdocno}'
    else:
        url = f'https://zakupki.gov.ru/epz/orderplan/search/results.html?searchString=None'

    r = requests.get(url, headers=headers)
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(r.text)
    with open('index.html', encoding='utf-8') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')
    '''Проверяем результаты поиска на предмет "Поиск не дал результатов"'''
    no_result_in_search = soup.find('p', class_="noRecords")
    # print('no_result_in_search', no_result_in_search)
    if not no_result_in_search:
        '''Из супа предыдущего запроса вытакскиваем ссылку на журнал событий. Он формируется динамически. Однако имеется сид документа, который хранится в элементе wrapper'''
        doc_history = 'https://zakupki.gov.ru' + soup.find(class_="registry-entry__header-mid__number").find('a').get('href').replace('common-info','event-journal').replace('general-info','event-journal')
        # print(doc_history)
        r = requests.get(doc_history, headers=headers)
        with open('doc_history.html', 'w', encoding='utf-8') as file:
            file.write(r.text)
        with open('doc_history.html', encoding='utf-8') as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        wrapper = soup.find('div', class_="cardWrapper outerWrapper").find('div', class_="wrapper").find_all('script')
        sid = re.findall(r'sid: .*?,', wrapper[-1].text, re.DOTALL)[0].replace("sid: '", '').replace("',", '')
        # print(sid)
        '''Получаем ссылку на ту часть журнала, что формируется динамикой. Сохраняем ее в отдельный файл. Из супа вытаскиваем дату последней публикации.'''
        if doctype in ('order', 'protocol'):
            url_history = f'https://zakupki.gov.ru/epz/order/notice/card/event/journal/list.html?sid={sid}&page=1&pageSize=100'
        if doctype == 'contract':
            url_history = f'https://zakupki.gov.ru/epz/contract/card/event/journal/list.html?sid={sid}&page=1&pageSize=100'
        if doctype == 'orderplan':
            url_history = f'https://zakupki.gov.ru/epz/orderplan/card/event/journal/list.html?sid={sid}&entityId=&page=1&pageSize=100&qualifier=ES2020'
        r = requests.get(url_history, headers=headers)
        with open('journal.html', 'w', encoding='utf-8') as file:
            file.write(r.text)
        with open('journal.html', encoding='utf-8') as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        '''Тело таблицы'''
        tbody = soup.find('table', class_="table mb-0 displaytagTable").find('tbody')
        '''Список записей таблицы'''
        rows = tbody.find_all(class_="table__row")
        # print(rows)
        '''Перебираем список записей на предмет публикации извещения или изменения извещения'''
        res_rows = []
        dates = []
        last_publication_date = datetime.datetime.strptime('01.01.1970 00:00', '%d.%m.%Y %H:%M')

        for row in rows:
            date = row.find_all(class_="table__cell table__cell-body")[0].text.strip().replace(' (МСК)', '')
            date = datetime.datetime.strptime(date, '%d.%m.%Y %H:%M')
            event = row.find_all(class_="table__cell table__cell-body")[1].text.strip()
            # print(date, '+++', event)
            '''Все даты по указанным событиям'''
            '''Последнее событие в журнале событий, удовлетворяющее параметрам запроса'''

            if (doctype == 'protocol' and
                    ('Размещен «Протокол' in event)
            ):
                res_rows.append((date, event))
                dates.append(date)

            elif (doctype == 'order' and
                ('Размещен документ «Извещение о проведении' in event or 'Размещен документ «Изменение извещения о проведении' in event)
            ) or (doctype == 'contract' and
                   ('Размещена информация о заключенном контракте' in event or 'Размещена информация об изменении заключенного контракта' in event)
            ) or (doctype == 'orderplan' and
                    ('Размещен план-график закупок на' in event)
            ):
                if last_publication_date < date:
                    last_publication_date = date
                res_rows.append((date, event))
        if not dates:
            dates.append(last_publication_date)


        '''Отладка'''
        print('***************res_rows********************')
        print(res_rows)
        print('****************dates**********************')
        print(dates)
        print('*******************************************')
        print('(last_publication_date)', last_publication_date, '+++')

        return dates, doctype, eisdocno

        # return last_publication_date
    else:
        dates = []
        dates.append(datetime.datetime.strptime('01.01.1970 00:00', '%d.%m.%Y %H:%M'))
        return dates, doctype, eisdocno
        # return datetime.datetime.strptime('01.01.1970 00:00', '%d.%m.%Y %H:%M')


if __name__ == '__main__':
    search_last_publication_date()
