# -*- coding: utf-8 -*-

"""
telegram bot for adding logo on photos and videos with register_next_step handler.
"""

import telebot #pip install pyTelegramBotAPI
from telebot import types
import jsonConverter
import multiple_json_converter
from pathlib import Path
import datetime
import logging
import zipfile
import subprocess
import os
import glob


logging.basicConfig(filename='tg_convert_bot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

API_TOKEN = os.environ.get('TGCONVERT')
print(API_TOKEN)
bot = telebot.TeleBot(API_TOKEN)

user_dict = {}

#TODO

class User: #get user data
    def __init__(self, id):
        self.id = id #string for the header
        self.firstname = None #string for the main text
        self.username = None #string for the main text

print("Listening...")
logging.debug("Listening...")


# Define menu structure
menu = {
    'main': [
        ['Конвертувати json файл у таблицю', 'option1'],
        ['Поєднати кілька таблиць в одну', 'option2'],
        ['Back', 'menu']
    ]
    # ,
    # 'submenu1': [
    #     ['Закиньте сюди json файл', 'option1'],
    #     ['Option 2', 'option2'],
    #     ['Back', 'main']
    # ],
    # 'submenu2': [
    #     ['Закиньте сюди таблиці', 'option3'],
    #     ['Option 4', 'option4'],
    #     ['Back', 'main']
    # ]
}

def make_keyboard(menu_name):
    markup = types.InlineKeyboardMarkup()
    for btn_text, callback_data in menu[menu_name]:
        button = types.InlineKeyboardButton(btn_text, callback_data=callback_data)
        markup.add(button)
    return markup

@bot.message_handler(commands=['start'])
def handle_message(message):
    bot.send_message(message.chat.id, 'Привіт! Я бот проекту nikcenter.org, я допоможу конвертувати json Телеграму у таблицю\n'
                                      'Вибери, що потрібно в меню:', reply_markup=make_keyboard('main'))
    user_id = message.chat.id
    firstname = message.from_user.first_name  # getting name of user
    username = message.from_user.username  # getting name of username

    user = User(message.chat.id)  # initialize class User
    user_dict[message.chat.id] = user
    user.id = user_id
    user.firstname = firstname  # writting to class User
    user.username = username  # writting to class User
    print(f'id: {user.id}, name: {user.firstname}, username: {user.username}')
    logging.debug(f'id: {user.id}, name: {user.firstname}, username: {user.username}')
    # print(f"User with id{user} and firstname {firstname} and username {username} "
    #       f" tried to get access")
    # logging.debug(f"User with id {user_id} and firstname {firstname} and username {username} "
    #               f" tried to get access")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'option1':
        convert(call.message) #calling function
    elif call.data == 'option2':
        combine(call.message) #calling function
    elif call.data in menu:
        bot.edit_message_text('You are in a submenu:', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=make_keyboard(call.data))
    else:
        bot.answer_callback_query(call.id, f"You chose {call.data}")


def convert(message):
    chat_id = message.chat.id  # getting user id
    user = user_dict[chat_id]
    print(user.id, user.username, user.firstname)
    bot.send_message(chat_id, f'Закинь сюди файл')


    @bot.message_handler(content_types=['document'])
    def document(message):
        chat_id = message.chat.id  # getting user id
        user_id = message.from_user.id
        firstname = message.from_user.first_name
        print(f"User has chat ID {chat_id} and user ID {user_id} and {firstname}")
        logging.debug(f"User has chat ID {chat_id} and user ID {user_id} and {firstname}")
        directory, TIMESTAMP = makeFolder(message, chat_id)
        """Getting data"""
        bot.send_message(chat_id, f'Запит отримав')  # bot replying for a certain message

        print('message.document =', message.document)
        logging.debug('message.document =', message.document)
        fileID = message.document.file_id
        fileName = message.document.file_name
        if fileName.endswith('.json'):
            # Process the JSON document
            pass
        else:
            bot.send_message(chat_id, f'Це не json файл. Завантаж знову')
            convert(message)
        print('fileID, fileName =', fileID, fileName)
        logging.debug('fileID, fileName =', fileID, fileName)
        file_info = bot.get_file(fileID)
        print('file.file_path =', file_info.file_path)
        logging.debug('file.file_path =', file_info.file_path)
        downloaded_file = bot.download_file(file_info.file_path)
        # filename = f"{directory}/audio_{TIMESTAMP}.wav"
        filename = f"{directory}/{fileName}"
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)
        print(filename, directory, TIMESTAMP)
        logging.debug(filename, directory, TIMESTAMP)
        output_file = f'{directory}/output_{TIMESTAMP}.csv'
        jsonConverter.main(filename, directory, TIMESTAMP, output_file)
        finalRes(chat_id, output_file)

def combine(message):
    chat_id = message.chat.id  # getting user id
    user = user_dict[chat_id]
    print(user.id, user.username, user.firstname)
    bot.send_message(chat_id, f'Закинь сюди zip архів з кількох')

    @bot.message_handler(content_types=['document'])
    def document(message):
        chat_id = message.chat.id  # getting user id
        user_id = message.from_user.id
        firstname = message.from_user.first_name
        directory, TIMESTAMP = makeFolder(message, chat_id) #creating folder for user
        #creating subfolder for multiple json file
        subdirectory = f'{directory}/subdir_{chat_id}_{TIMESTAMP}/'
        Path(subdirectory).mkdir()  # creating a new directory if not exist
        print(f'Subdirectory is made... {subdirectory}')
        logging.debug(f'Subdirectory is made... {subdirectory}')
        inputFile = f'{subdirectory}input_file_{TIMESTAMP}.zip'
        print(f'Downloading file to {inputFile}')
        logging.debug(f'Downloading file to {inputFile}')
        fileID = message.document.file_id
        fileName = message.document.file_name
        print('fileID, fileName =', fileID, fileName)
        logging.debug('fileID, fileName =', fileID, fileName)
        file_info = bot.get_file(fileID)
        print('file.file_path =', file_info.file_path)
        logging.debug('file.file_path =', file_info.file_path)
        downloaded_file = bot.download_file(file_info.file_path)
        filename = f"{subdirectory}input_file_{TIMESTAMP}.zip"
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(chat_id, "Дякую, файл отриманий і опрацьовується... Треба почекати-:)")

        with zipfile.ZipFile(filename) as zip_file:  # extracting files
            print("zip_file.extractall")
            logging.debug("zip_file.extractall")
            zip_file.extractall(subdirectory)
        output_file = f'{subdirectory}output_{TIMESTAMP}.csv'
        multiple_json_converter.main(subdirectory, TIMESTAMP, output_file)
        finalRes(chat_id, output_file)

def makeFolder(message, chat_id):
    """Prepairing folder"""
    user_id = user_dict[chat_id].id
    firstname = user_dict[chat_id].firstname  # writting to class User
    username = user_dict[chat_id].username  # writting to class User
    """Prepairing directory with chat_id and output file with timestamp"""
    TIMESTAMP = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]  # with miliseconds
    directory = f'dir_{chat_id}_{firstname}_{username}'
    print(f'Directory: {directory}')
    logging.debug(f'Directory: {directory}')
    Path(directory).mkdir(exist_ok=True)  # creating a new directory if not exist
    print(f'Directory is made... {directory}')
    logging.debug(f'Directory is made... {directory}')
    return directory, TIMESTAMP


def finalRes(chat_id, output_file):
    file = open(output_file, 'rb')
    print(f'Bot sending file to {user_dict[chat_id].firstname} {user_dict[chat_id].id} {user_dict[chat_id].username}')
    logging.debug(f'Bot sending file to {user_dict[chat_id].firstname} {user_dict[chat_id].id} {user_dict[chat_id].username}')
    bot.send_document(chat_id, file)  # sending file to user
    bot.send_message(chat_id, 'Тримайте файл.'
                              '\nКолеги, будь ласка, якщо вам подобається цей бот,'
                              '\nподякуйте і тегніте нашу сторінку в ФБ'
                              '\nhttps://www.facebook.com/nikcenter'
                              '\nабо напишіть в особисті розробнику:)'
                              '\n https://t.me/d09ed0bbd0b5d0b3'
                              '\n')  # bot replying for a certain message

    """End of program"""


bot.infinity_polling()
