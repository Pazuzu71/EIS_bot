from crawler import search_last_publication_date
from ftp_search import ftp_search
import os
import telebot
from telebot import types
from config import token


def main():

    parameters = {}

    '''Сам бот и хэндлеры к нему'''

    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def start(msg):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add('Хочу скачать что-нибудь с фтп ЕИС')
        bot.send_message(msg.chat.id, 'Бот для скачивания интернета запущен!', reply_markup=kb)

    @bot.message_handler(func=lambda msg: msg.text == 'Хочу скачать что-нибудь с фтп ЕИС')
    def download_from_ftp(msg):
        kb = types.InlineKeyboardMarkup(row_width=5)
        btn1 = types.InlineKeyboardButton('Тульская область', callback_data='Tulskaja_obl')
        kb.add(btn1)
        bot.send_message(msg.chat.id, text='Выбрать регион', reply_to_message_id=msg.id, reply_markup=kb)

    @bot.callback_query_handler(func=lambda callback: True)
    def callbacks(callback):

        if callback.data == 'Tulskaja_obl':
            parameters['region'] = callback.data
            kb = types.InlineKeyboardMarkup(row_width=5)
            btn1 = types.InlineKeyboardButton('Извещение', callback_data='order')
            btn2 = types.InlineKeyboardButton('Сведения о контракте', callback_data='contract')
            kb.add(btn1, btn2)
            bot.edit_message_text(text='Выбрать тип документа', chat_id=callback.message.chat.id, message_id=callback.message.id,reply_markup=kb)

        if callback.data in ('order', 'contract'):
            parameters['doctype'] = callback.data
            sent = bot.edit_message_text(text='👇👇👇 Введите номер документа: 👇👇👇', chat_id=callback.message.chat.id, message_id=callback.message.id)
            bot.register_next_step_handler(sent, get_data)
        #
        # if callback.data == 'contract':
        #     parameters['doctype'] = callback.data
        #     sent = bot.edit_message_text(text='👇👇👇 Введите номер документа: 👇👇👇', chat_id=callback.message.chat.id, message_id=callback.message.id)
        #     bot.register_next_step_handler(sent, get_data)




    def get_data(msg):
        '''По полученным данным делаем дела'''
        parameters['eisdocno'] = msg.text
        print(parameters)

        last_publication_date = search_last_publication_date(doctype=parameters['doctype'],
                                                             eisdocno=parameters['eisdocno'])
        last_publication_date_str = ftp_search(region=parameters['region'], doctype=parameters['doctype'],
                                               eisdocno=parameters['eisdocno'],
                                               last_publication_date=last_publication_date)

        '''Удаляем архивы после поиска xml'''
        if parameters['doctype'] == 'contract':
            x = 'contracts'
        if parameters['doctype'] == 'order':
            x = 'notifications'
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
            else:
                print('Документов с такими типом и номером не найдено для указанного региона. Увы...')
                bot.send_message(msg.chat.id, 'Документов с такими типом и номером не найдено для указанного региона. Увы...')

    # while True:
    #     try:
    #         bot.polling(none_stop=True, interval=0, timeout=20)
    #     except:
    #         print("Exception")
    bot.polling()


if __name__ == '__main__':
    main()