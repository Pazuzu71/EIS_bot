import requests
from bs4 import BeautifulSoup
import lxml
import re


def search(doctype='order', eisdocno='0366300038722000139'):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
        }
    url = f'https://zakupki.gov.ru/epz/{doctype}/extendedsearch/results.html?searchString={eisdocno}'
    # r = requests.get(url, headers=headers)
    # with open('index.html', 'w', encoding='utf-8') as file:
    #     file.write(r.text)
    # with open('index.html', encoding='utf-8') as file:
    #     src = file.read()
    # soup = BeautifulSoup(src, 'lxml')
    # doc_history = 'https://zakupki.gov.ru/' + soup.find(class_="registry-entry__header-mid__number").find('a').get('href').replace('common-info','event-journal')
    # r = requests.get(doc_history, headers=headers)
    # with open('doc_history.html', 'w', encoding='utf-8') as file:
    #     file.write(r.text)
    # doc_info = 'https://zakupki.gov.ru/' + soup.find(class_="registry-entry__header-mid__number").find('a').get('href')
    # r = requests.get(doc_info, headers=headers)
    # with open('doc_info.html', 'w', encoding='utf-8') as file:
    #     file.write(r.text)
    with open('doc_history.html', encoding='utf-8') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')
    wrapper = soup.find('div', class_="cardWrapper outerWrapper").find('div', class_="wrapper").find_all('script')
    res = re.findall(r'sid: .*?,', wrapper[-1].text, re.DOTALL)[0].replace('sid: ', '').replace(',', '')
    print(res, type(res))
    url_history = f'https://zakupki.gov.ru/epz/order/notice/card/event/journal/list.html?sid={res}&page=1&pageSize=10'
    u ='https://zakupki.gov.ru/epz/order/notice/card/event/journal/list.html?sid=' + res + '&page=1&pageSize=10'
    print(u)
    print(url_history)
    r = requests.get(u, headers=headers)
    print(r.text)


if __name__ == '__main__':
    search()
