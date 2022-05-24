from crawler import search_last_publication_date
from ftp_search import ftp_search
import os
import telebot
from config import token


doctype='order'
eisdocno='0366200035622001014'
region = 'Tulskaja_obl'


def main():

    last_publication_date = search_last_publication_date(doctype=doctype, eisdocno=eisdocno)
    ftp_search(region = region, doctype=doctype, eisdocno=eisdocno, last_publication_date=last_publication_date)
    '''Удаляем архивы после поиска xml'''
    for path, dirs, files in os.walk(f'Temp//{eisdocno}'):
        if files:
            for file in files:
                if file.endswith('.zip'):
                    os.unlink(os.path.join(path, file))

    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def start(msg):
        bot.send_message(msg.chat.id, 'Бот для скачивания интернета запущен!')

    bot.polling()


if __name__ == '__main__':
    main()