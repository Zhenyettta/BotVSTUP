import json
import os
import telebot
from telebot import types
from google_currency import convert

TOKEN = os.environ["TOKEN"]
bot = telebot.TeleBot(TOKEN)

chat_states = {}
chat_currency = {}
chat_language = {}


def handle_currency_conversion(message, currency, amount, language):
    if currency == 'USD 🇺🇸':
        converted_currency = 'usd'
    elif currency == 'EUR 🇪🇺':
        converted_currency = 'eur'
    elif currency == 'GBP 🇬🇧':
        converted_currency = 'gbp'
    elif currency == 'CHF 🇨🇭':
        converted_currency = 'chf'

    converted_amount = convert(converted_currency, 'uah', amount)
    converted_amount = json.loads(converted_amount)['amount']
    converted_amount = float(converted_amount)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(
        '😛 Скористатись знову (тут може бути менюшка)') if language == 'uk' else types.KeyboardButton(
        '😛 Use again (here can be menu)')
    markup.add(btn1)
    bot.send_message(message.from_user.id, f'{amount} {converted_currency.upper()} = {converted_amount:.2f} UAH',
                     reply_markup=markup)
    del chat_states[message.chat.id]


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🇺🇦 Українська")
    btn2 = types.KeyboardButton('🇬🇧 English')
    markup.add(btn1, btn2)
    username = message.from_user.username
    print(username)

    if username == 'malashokk':
        bot.send_message(message.from_user.id, """
Натафка Малафок Ласкаво просимо до нашого телеграм бота! 🤖
Вас вітаємо у нашій системі. Будь ласка, оберіть мову, якою ви хочете користуватися.

Welcome to our Telegram bot! 🤖
You are greeted in our system. Please select the language you want to use.

🇺🇦 Виберіть мову / 🇬🇧 Choose your language""", reply_markup=markup)

    else:
        bot.send_message(message.from_user.id, """
Ласкаво просимо до нашого телеграм бота! 🤖
Вас вітаємо у нашій системі. Будь ласка, оберіть мову, якою ви хочете користуватися.
        
Welcome to our Telegram bot! 🤖
You are greeted in our system. Please select the language you want to use.

🇺🇦 Виберіть мову / 🇬🇧 Choose your language""", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '🇺🇦 Українська':
        chat_language[message.chat.id] = 'uk'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Всі доступні валюти!!')
        markup.add(btn1)
        bot.send_message(message.from_user.id, '❓ Що ви хочете побачити?',
                         reply_markup=markup)
    elif message.text == '🇬🇧 English':
        chat_language[message.chat.id] = 'en'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Available currencies!!')
        markup.add(btn1)
        bot.send_message(message.from_user.id,
                         '❓ What do you want?',
                         reply_markup=markup)

    elif message.text in ['Available currencies!!', 'Всі доступні валюти!!', '🤔 Змінити валюту', '🤔 Change currency',
                          '😛 Скористатись знову (тут може бути менюшка)', '😛 Use again (here can be menu)']:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('USD 🇺🇸')
        btn2 = types.KeyboardButton('EUR 🇪🇺')
        btn3 = types.KeyboardButton('GBP 🇬🇧')
        btn4 = types.KeyboardButton('CHF 🇨🇭')
        markup.add(btn2, btn3, btn4, btn1)
        language = chat_language.get(message.chat.id, 'uk')
        if language == 'uk':
            bot.send_message(message.from_user.id,
                             '🤑 Оберіть потрібну валюту',
                             reply_markup=markup)
        elif language == 'en':
            bot.send_message(message.from_user.id,
                             '🤑 Choose the currency you want to use',
                             reply_markup=markup)
    elif message.text in ['EUR 🇪🇺', 'USD 🇺🇸', 'GBP 🇬🇧', 'CHF 🇨🇭']:
        language = chat_language.get(message.chat.id, 'uk')
        if language == 'uk':
            chat_currency[message.chat.id] = message.text
            bot.send_message(message.from_user.id,
                             '💰 Введіть потрібну суму для конвертації в гривні 🇺🇦',
                             reply_markup=types.ReplyKeyboardRemove())
            chat_states[message.chat.id] = 'waiting_for_value'
        elif language == 'en':
            chat_currency[message.chat.id] = message.text
            bot.send_message(message.from_user.id,
                             '💰 Enter the amount you want to convert to UAH 🇺🇦',
                             reply_markup=types.ReplyKeyboardRemove())
            chat_states[message.chat.id] = 'waiting_for_value'


    elif chat_states.get(message.chat.id) == 'waiting_for_value':
        if message.text.isdigit():
            handle_currency_conversion(message, chat_currency[message.chat.id], int(message.text),
                                       chat_language.get(message.chat.id, 'uk'))
            del chat_currency[message.chat.id]
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

            language = chat_language.get(message.chat.id, 'uk')
            if language == 'uk':
                btn1 = types.KeyboardButton('🤔 Змінити валюту')
                markup.add(btn1)
                bot.send_message(message.from_user.id,
                                 '😞 Некоректний ввід, повторіть спробу!',
                                 parse_mode="Markdown", reply_markup=markup)
            elif language == 'en':
                btn1 = types.KeyboardButton('🤔 Change currency')
                markup.add(btn1)
                bot.send_message(message.from_user.id,
                                 '😞 Incorrect input, please try again!',
                                 parse_mode="Markdown", reply_markup=markup)


bot.infinity_polling()
