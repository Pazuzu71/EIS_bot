import requests
from bs4 import BeautifulSoup
import lxml
import re
import datetime


def search_last_publication_date(doctype='order', eisdocno='0366200035622001014'):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
        }
    '''Ищем документ через штатный поиск ЕИС. В Ссылку подставляем тим документа и номер.'''
    url = f'https://zakupki.gov.ru/epz/{doctype}/extendedsearch/results.html?searchString={eisdocno}'
    r = requests.get(url, headers=headers)
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(r.text)
    with open('index.html', encoding='utf-8') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')
    '''Из супа предыдущего запроса вытакскиваем ссылку на журнал событий. Он формируется динамически. Однако имеется сид документа, который хранится в элементе wrapper'''
    doc_history = 'https://zakupki.gov.ru/' + soup.find(class_="registry-entry__header-mid__number").find('a').get('href').replace('common-info','event-journal')
    r = requests.get(doc_history, headers=headers)
    with open('doc_history.html', 'w', encoding='utf-8') as file:
        file.write(r.text)
    with open('doc_history.html', encoding='utf-8') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')
    wrapper = soup.find('div', class_="cardWrapper outerWrapper").find('div', class_="wrapper").find_all('script')
    sid = re.findall(r'sid: .*?,', wrapper[-1].text, re.DOTALL)[0].replace("sid: '", '').replace("',", '')
    '''Получаем ссылку на ту часть журнала, что формируется динамикой. Сохраняем ее в отдельный файл. Из супа вытаскиваем дату последней публикации.'''
    url_history = f'https://zakupki.gov.ru/epz/order/notice/card/event/journal/list.html?sid={sid}&page=1&pageSize=100'
    # print(url_history)
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

    '''Перебираем список записей на предмет публикации извещения или изменения извещения'''
    res_rows = []
    last_publication_date = datetime.datetime.strptime('01.01.1970 00:00', '%d.%m.%Y %H:%M')

    for row in rows:
        date = row.find_all(class_="table__cell table__cell-body")[0].text.strip().replace(' (МСК)', '')
        event = row.find_all(class_="table__cell table__cell-body")[1].text.strip()
        print(date, '+++', event)

        '''Закупки'''
        if doctype == 'order' and (
            'Размещен документ «Извещение о проведении' in event or 'Размещен документ «Изменение извещения о проведении' in event
        ):
            if last_publication_date < datetime.datetime.strptime(date, '%d.%m.%Y %H:%M'):
                last_publication_date = datetime.datetime.strptime(date, '%d.%m.%Y %H:%M')
            res_rows.append((date, datetime.datetime.strptime(date, '%d.%m.%Y %H:%M'), event))

    '''Отладка'''
    print('*******************************************')
    print(res_rows)
    print('*******************************************')
    print(last_publication_date, type(last_publication_date), '+++' )

    return last_publication_date


if __name__ == '__main__':
    search_last_publication_date()
