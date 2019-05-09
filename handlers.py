from glob import glob
from random import choice
import os
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, Filters

from utils import get_keyboard, get_user_emo, is_emot

def greet_user(bot, update, user_data):
    emo = get_user_emo(user_data)
    text = 'Привет {}'.format(emo)
    update.message.reply_text(text, reply_markup=get_keyboard())

def talk_to_me(bot, update, user_data):
    emo = get_user_emo(user_data)
    user_text = "Привет {} {}! Ты написал {}".format(update.message.chat.first_name,\
                                             emo, update.message.text)

    logging.info("User: %s, Chat id: %s, Message: %s", update.message.chat.username, \
                                                       update.message.chat.id, update.message.text)
    update.message.reply_text(user_text, reply_markup=get_keyboard())

def send_emotion_pictures(bot, update, user_data):
    emotion_list = glob('images/emotion*.jpeg')
    emotion_pic = choice(emotion_list)
    bot.send_photo(chat_id=update.message.chat.id, photo=open(emotion_pic, 'rb'),reply_markup=get_keyboard())

def change_avatar(bot,update,user_data):
    if 'emo' in user_data:
        del user_data['emo']
    emo = get_user_emo(user_data)
    update.message.reply_text('Готово: {}'.format(emo),reply_markup=get_keyboard())

def get_contact(bot, update, user_data):
    print(update.message.contact)
    update.message.reply_text('Готово: {}'.format(get_user_emo(user_data)),reply_markup=get_keyboard())

def get_location(bot, update, user_data):
    print(update.message.location)
    update.message.reply_text('Готово: {}'.format(get_user_emo(user_data)),reply_markup=get_keyboard())

def check_user_photo(bot, update, user_data):
    update.message.reply_text("Обрабатываю фото")
    os.makedirs('downloads', exist_ok=True)
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', '{}.jpg'.format(photo_file.file_id))
    photo_file.download(filename)
    if is_emot(filename):
        update.message.reply_text("Обнаружен скэтч, добавляю в библиотеку")
        new_filename = os.path.join('images', 'emot_{}.jpg'.format(photo_file.file_id))
        os.rename(filename, new_filename)
    else:
        os.remove(filename)
        update.message.reply_text("Тревога, скэтч не обнаружен!")

