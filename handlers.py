from glob import glob
from random import choice
import os
import logging

from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardButton,\
    InlineKeyboardMarkup, ParseMode, error
from telegram.ext import ConversationHandler, CallbackQueryHandler
from telegram.ext import messagequeue as mq

from emoji import emojize
from bot import subscribers
from db import db, get_or_create_user, get_user_emo, toggle_subscription, get_subscribed
from utils import get_keyboard, is_emot


def greet_user(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    emo = get_user_emo(db, user)
    user['emo'] = emo
    text = 'Привет {}'.format(emo)
    update.message.reply_text(text, reply_markup=get_keyboard())

def talk_to_me(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    emo = get_user_emo(db, user)
    user_text = "Привет {} {}! Ты написал {}".format(user['first_name'],\
                                             emo, update.message.text)

    logging.info("User: %s, Chat id: %s, Message: %s", user['username'], \
                                                       update.message.chat.id, update.message.text)
    update.message.reply_text(user_text, reply_markup=get_keyboard())

def send_emotion_pictures(bot, update, user_data):
    emotion_list = glob('images/emotion*.jpeg')
    emotion_pic = choice(emotion_list)
    inlinekeyboard = [[InlineKeyboardButton(emojize(":thumbs_up:"), callback_data='emotion_good'),
                InlineKeyboardButton(emojize(":thumbs_down:"), callback_data='emotion_bad')]]
    
    reply_markup = InlineKeyboardMarkup(inlinekeyboard)
    bot.send_photo(chat_id=update.message.chat.id, photo=open(emotion_pic, 'rb'),reply_markup=reply_markup)

def change_avatar(bot,update,user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    if 'emo' in user:
        del user['emo']
    emo = get_user_emo(db, user)
    update.message.reply_text('Готово: {}'.format(emo),reply_markup=get_keyboard())

def get_contact(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    print(update.message.contact)
    update.message.reply_text('Готово: {}'.format(get_user_emo(db, user)),reply_markup=get_keyboard())

def get_location(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    print(update.message.location)
    update.message.reply_text('Готово: {}'.format(get_user_emo(db, user)),reply_markup=get_keyboard())

def check_user_photo(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
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

def anketa_start(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    update.message.reply_text("Как вас зовут? Напишите имя и фамилию", reply_markup=ReplyKeyboardRemove())
    return "name"

def anketa_get_name(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    user_name = update.message.text
    if len(user_name.split(" ")) != 2:
        update.message.reply_text("Полажуйста введите имя и фамилию")
        return "name"
    else:
        user_data['anketa_name'] = user_name
        reply_keyboard = [["1", "2", "3", "4", "5"]]

        update.message.reply_text(
            "Оцените нашего бота от 1 до 5",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return "rating"

def anketa_rating(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    user_data['anketa_rating'] = update.message.text
    update.message.reply_text("""Пожалуйста напишит отзыв в свободной форме
или / cancel чтобы пропустить шаг""")
    return "comment"

def anketa_comment(bot, update, user_data):
    user_data['anketa_comment'] = update.message.text
    user_text = """
<b>Имя Фамилия:</b> {anketa_name}
<b>Оценка:</b> {anketa_rating}
<b>Комментарий:</b> {anketa_comment}""".format(**user_data)

    update.message.reply_text(user_text, reply_markup=get_keyboard(),
                                parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def anketa_skip_comment(bot, update, user_data):
    user_data = get_or_create_user(db, update.effective_user, update.message)
    user_text = """
    <b>Имя Фамилия:</b> {anketa_name}
    <b>Оценка:</b> {anketa_rating}""".format(**user_data)

    update.message.reply_text(user_text, reply_markup=get_keyboard(),
                                parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def dontknow(bot, update, user_data):
    user_data = get_or_create_user(db, update.effective_user, update.message)
    update.message.reply_text("Не понимаю")

def subscriber(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    if not user.get('subscribed'):
        toggle_subscription(db, user)
    update.message.reply_text('Вы подписались')

def inline_button_pressed(bot, update):
    query = update.callback_query
    if query.data in ['emotion_good','emotion_bad']:
        text = "Супер" if query.data == 'emotion_good' else "Будем стараться"
     
    bot.edit_message_caption(caption=text, chat_id=query.message.chat_id, message_id=query.message.message_id)

@mq.queuedmessage
def send_updates(bot, job):
    for user in get_subscribed(db):
        try:
            bot.sendMessage(chat_id=user['chat_id'], text="Уведомление")
        except error.BadRequest:
            print('Chat {} not found'.format (user['chat_id']))

def unsubscriber(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    if user.get('subscribed'):
        toggle_subscription(db, user)
        update.message.reply_text('Вы отписались')
    else:
        update.message.reply_text('Вы не подписаны, нажмите /subscriber чтобы подписаться')

def set_alarm(bot, update, args, job_queue):
    user = get_or_create_user(db, update.effective_user, update.message)
    try:
        seconds = abs(int(args[0]))
        job_queue.run_once(alarm, seconds, context=update.message.chat_id)
    except (IndexError, ValueError):
        update.message.reply_text("Введите число секунд после команды /alarm")

@mq.queuedmessage
def alarm(bot, job):
    bot.send_message(chat_id=job.context, text="Сработал будильник!")