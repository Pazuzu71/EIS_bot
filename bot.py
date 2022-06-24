import threading
from crawler import search_last_publication_date
from ftp_search import ftp_search
import os
import telebot
from telebot import types
from config import token
import schedule
from journal_scheduler import journal_update
import time
from datetime import datetime


def main():

    parameters = {}

    '''Сам бот и хэндлеры к нему'''
    bot = telebot.TeleBot(token)
    # bot = telebot.TeleBot(token, threaded=True)
    # bot.worker_pool = telebot.util.ThreadPool(bot, num_threads=1)


    @bot.message_handler(commands=['start'])
    def start(msg):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add('Хочу скачать что-нибудь с фтп ЕИС 2')
        # kb.add('Хочу скачать что-нибудь с фтп ЕИС', 'Хочу скачать что-нибудь с фтп ЕИС 2')
        bot.send_message(msg.chat.id, 'Бот для скачивания интернета запущен!', reply_markup=kb)

    @bot.message_handler(func=lambda msg: msg.text == 'Хочу скачать что-нибудь с фтп ЕИС 2')
    def download_from_ftp_2(msg):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        btn1 = types.KeyboardButton('Тульская область')
        kb.add(btn1)
        bot.send_message(msg.chat.id, text='Пожалуйста выберите регион', reply_to_message_id=msg.id, reply_markup=kb)

    @bot.message_handler(func=lambda msg: msg.text in ('Тульская область'))
    def document_type_choice(msg):
        parameters['region'] = 'Tulskaja_obl'
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
        btn1 = types.KeyboardButton('Извещение')
        btn2 = types.KeyboardButton('Все протоколы по закупке')
        btn3 = types.KeyboardButton('Сведения о контракте')
        btn4 = types.KeyboardButton('План-график 2020')
        kb.add(btn1, btn2, btn3, btn4)
        bot.send_message(msg.chat.id, text='Пожалуйста выберите тип документа', reply_to_message_id=msg.id, reply_markup=kb)

    @bot.message_handler(func=lambda msg: msg.text in ('Извещение', 'Все протоколы по закупке', 'Сведения о контракте', 'План-график 2020'))
    def eisdocno_request(msg):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
        kb.add('Хочу скачать что-нибудь с фтп ЕИС 2')
        if msg.text == 'Извещение':
            parameters['doctype'] = 'order'
        if msg.text == 'Все протоколы по закупке':
            parameters['doctype'] = 'protocol'
        if msg.text == 'Сведения о контракте':
            parameters['doctype'] = 'contract'
        if msg.text == 'План-график 2020':
            parameters['doctype'] = 'orderplan'
        sent = bot.send_message(msg.chat.id, text='👇👇👇 Введите номер документа: 👇👇👇', reply_markup=kb)
        bot.register_next_step_handler(sent, get_data)


    def get_data(msg):
        '''По полученным данным делаем дела'''
        print(f'{datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M")} {msg.from_user.first_name} {msg.from_user.last_name} {msg.from_user.username} ищет {parameters["doctype"]} {msg.text}')
        parameters['eisdocno'] = msg.text
        print(parameters)
        last_publication_dates, y, z = search_last_publication_date(doctype=parameters['doctype'],
                                                             eisdocno=parameters['eisdocno'])
        print('last_publication_dates', last_publication_dates)
        # last_publication_date = search_last_publication_date(doctype=parameters['doctype'],
        #                                                      eisdocno=parameters['eisdocno'])[0]
        '''Удаляем архивы после поиска xml'''
        if y == 'contract':
            x = 'contracts'
        if y == 'order':
            x = 'notifications'
        if y == 'orderplan':
            x = 'plangraphs2020'
        if y == 'protocol':
            x = 'protocols'

        for last_publication_date in last_publication_dates:
            last_publication_date_str = ftp_search(region=parameters['region'], doctype=y,
                                                   eisdocno=z,
                                                   last_publication_date=last_publication_date)


            for path, dirs, files in os.walk(f'Temp//{x}//{parameters["eisdocno"]}//{last_publication_date_str}'):
                if files:
                    for file in files:
                        if file.endswith('.zip'):
                            os.unlink(os.path.join(path, file))
                        else:
                            # bot.send_message(msg.chat.id, f'Нашел {file}')
                            file_to_send = open(os.path.join(path, file), 'rb')
                            bot.send_document(msg.chat.id, document=file_to_send)
                            file_to_send.close()
                elif msg.text in ('Извещение', 'Все протоколы по закупке', 'Сведения о контракте', 'План-график 2020'):
                    bot.send_message(msg.chat.id, 'Харош жмать на кнопки! Номер некорректный')
                elif msg.text in ('Хочу скачать что-нибудь с фтп ЕИС 2'):
                    bot.send_message(msg.chat.id, 'Ха, очень смешно. Еще раз нажми.')
                else:
                    print('Документов с такими типом и номером не найдено для указанного региона. Увы...')
                    bot.send_message(msg.chat.id,
                                     'Документов с такими типом и номером не найдено для указанного региона. Увы...')
                if not os.listdir(f'Temp//{x}//{parameters["eisdocno"]}//{last_publication_date_str}'):
                    bot.send_message(msg.chat.id,
                                     f'Возможно документ опубликован сегодня и на фтп еще не выложен. Дата публикации: {last_publication_date_str}')

    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as ex:
            print('Exception')
            print('Exception', ex)
            print("Exception", parameters)

    # bot.polling()

def journal_update_start():
    schedule.every().day.at("10:30").do(journal_update)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as ex:
            print('Ошибка обновления журнала',ex)


if __name__ == '__main__':
    thr1 = threading.Thread(target=journal_update_start)
    thr1.start()
    main()
