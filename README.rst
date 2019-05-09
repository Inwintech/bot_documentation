EmoBot
======

EmoBot - простой бот для Telegram

Установка
---------

создайте виртуальное окружение и активируйте его
.. code-block:: text
    pip install -r requirements/develope.text

Положите любые картинки в папку  images c формаматом jp*g

Настройка
---------
создайте файл settings.py и добавьте следующие настройки

.. code-block:: python

    API_KEY = 'API ключ, который вы получили у BotFather'

    USER_EMOJI = [':smiley_cat:', ':smiling_imp:', ':panda_face:', ':dog:']

Запуск
------

В активированном виртуальном окружении выполните:

.. code-block:: python

    python3 bot.py