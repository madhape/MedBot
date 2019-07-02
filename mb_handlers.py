from peewee import *#Для работы с бд
import random
import smtplib, ssl #для работы с почтой
import sqlite3

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, ConversationHandler

import db_peewee as dbp
import mb_settings as mbs


#Стартовавшие бота пользователи
bot_not_user = set()
query_nu = dbp.User.select().where(dbp.User.id_status < 3)
for not_user in query_nu:
    bot_not_user.add(int(not_user.telegram_chat_id))

#Авторизированные пользователи
bot_user = set()
query = dbp.User.select().where(dbp.User.id_status >= 3)
for user in query:
    bot_user.add(int(user.telegram_chat_id))


#Приветствуем пользователя, проверяем автоматизирован ли он
def greet_user (bot, update, user_data):
    user_chat = int(update.message.chat.id)
    user_name = update.message.chat.first_name
    user_data['user_chat'] = user_chat
    update.message.reply_text(f'Привет, {user_name}')
    if user_chat in bot_user:
        user_menu(bot=bot, update=update, user_data=user_data)
    elif user_chat in bot_not_user:
        print('Пользователь уже есть')
        aut_start(bot,update,user_data=user_data)
    else:
        #Последний id пользователя
        max_user_id = dbp.User.select(fn.MAX(dbp.User.id)).scalar()
        dbp.User.create(id=max_user_id+1, name=user_name, telegram_chat_id=user_chat, id_status=0)
        aut_start(bot,update,user_data=user_data)

#Появление кнопки [Авторизация] у неавтоматизированного пользователя
def aut_start(bot, update, user_data):
    aut_keyboard = [['Авторизироваться']]
    update.message.reply_text('Необходимо пройти авторизацию в системе', 
                              reply_markup = ReplyKeyboardMarkup(aut_keyboard, 
                              one_time_keyboard=True, 
                              resize_keyboard=True))
    return 'user_email'
   

#Запрашиваем email у пользователя
def user_email(bot, update, user_data):
    update.message.reply_text('Введите email', reply_markup=ReplyKeyboardRemove())
    return 'user_get_email'


#Получаем email от пользователя
def user_get_email(bot, update, user_data):
    user_email = update.message.text
    if '@' in user_email:
        user_data['user_email']=user_email
        print(user_data['user_email'])
        # dbp.User.id_status.update(id_status = 1).where(telegram_chat_id == user_data['user_chat'])
        send_code(bot=bot, update=update, user_data=user_data)
        # return 'send_code'
    else:
        update.message.reply_text('Некорректный email. Введите email')
        print(3)
        print(user_data)
        return 'user_get_email'
        

#Отправляем на email код авторизации
def send_code (bot, update, user_data):
    print(4.1)
    port = 465
    smtp_server = 'smtp.gmail.com'
    sender_email = mbs.email
    receiver_email = 'lena.korzinkina@mail.ru'
    password = mbs.email_password
    email_code = random.randint(1111,9999)
    massage = f'Код авторизации: {email_code}'
    massage = massage.encode('utf-8')
    context = ssl.create_default_context()
    print(4)
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, massage)
    update.message.reply_text('Введите код авторизации')
    print('я все сделал в send_code')
    # user_code(bot=bot, update=update, user_data=user_data, email_code= email_code)
    return 'user_code'
    


def user_code(bot, update, user_data, email_code): 
    user_data = update.message.text
    user_data['user_code'] = user_data
    print(user_data)
    print('ага, я это сделал')
    return ConversationHandler.END
    test_code(bot=bot, update=update, user_data=user_data, email_code=email_code)
    # print(user_data)
    # return 'user_code'


#Проверяем соответствие присланного на почту кода введенного пользователем
def test_code(bot, update, user_data, email_code):
    print(user_data)

#Пользовательское меню
def user_menu (bot, update, user_data):
    mt_keyboard = [['Внести результат','Получить график']]
    update.message.reply_text('Выберите пункт меню', 
                              reply_markup = ReplyKeyboardMarkup(mt_keyboard, 
                              one_time_keyboard=True, 
                              resize_keyboard=True))




    

    
    
