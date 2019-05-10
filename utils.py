from random import choice

from clarifai.rest import ClarifaiApp
from emoji import emojize
from telegram import ReplyKeyboardMarkup, KeyboardButton

import settings

def get_user_emo(user_data):
    if 'emo' in user_data:
        return user_data['emo']
    else:
        user_data['emo'] = emojize(choice(settings.USER_EMOJI), use_aliases=True)
        return user_data['emo']

def get_keyboard():
    contact_button = KeyboardButton('Прислать контакты', request_contact=True)
    location_button = KeyboardButton('Прислать координаты', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([
                                       ['Прислать эмоцию', 'Сменить аватарку'],
                                       [contact_button,location_button],
                                       ['Заполнить анкету']
                                       ], resize_keyboard=True
                                       )
    return my_keyboard

def is_emot(file_name):
    image_has_emot = False
    app = ClarifaiApp(api_key=settings.CLARIFAI_API_KEY)
    model = app.public_models.general_model
    response = model.predict_by_filename(file_name, max_concepts=5)
    if response['status']['code'] == 10000:
        for concepts in response['outputs'][0]['data']['concepts']:
            if concepts['name'] == 'sketch':
                image_has_emot = True
    return image_has_emot


if __name__ == "__main__":
    print(is_emot('images/emotion-1.jpeg'))
    print(is_emot('images/tree.jpeg'))