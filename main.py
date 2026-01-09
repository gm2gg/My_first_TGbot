# -*- coding: utf-8 -*-
import sqlite3
import telebot
import requests
import random
import os

from pygments.lexers import markup
from telebot import types
from cities_data import ALL_CITIES

BOT_TOKEN = os.getenv(ENTER_BOT_TOKEN)
bot = telebot.TeleBot(ENTER_BOT_TOKEN)
OWNER_ID = 8281653308

# Глобальные переменные
USED = []
GAME_ACTIVE = False
current_city = ""
first_text_trash = "Окей тогда я начинаю - "


# Функции
def req(city):
    last_char = city[-1].lower()
    if last_char in ['ь', 'ъ', 'ы']:
        return city[-2].lower()
    return last_char


@bot.message_handler(commands=['start'])
def start(message):
    global first_text_trash
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🛍️ Заказать услугу", callback_data='order_service')
    btn2 = types.InlineKeyboardButton("⭐ Посмотреть отзывы", url='https://t.me/+-PQ71xNSddhmZjQ6')
    btn3 = types.InlineKeyboardButton("🎮 Мини-игра", callback_data='start_game')
    btn4 = types.InlineKeyboardButton("❤️ Поддержать автора", url='https://www.donationalerts.com/r/s_gm')
    btn5 = types.InlineKeyboardButton("💬 Поддержка", callback_data='support')
    markup.add(btn1, btn2, btn3, btn4, btn5)

    welcome_text = """👋 Привет! Я бот-помощник для заказа услуг."""
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    bot.answer_callback_query(call.id)

    if call.data == 'order_service':
        order_service(call.message)
    elif call.data == 'change_word':
        change_word(call.message)
    elif call.data == 'start_game':
        start_game(call.message)
    elif call.data == 'game_yes':
        game_yes(call.message)
    elif call.data == 'start':
        start(call.message)
    elif call.data == 'support':
        support(call.message)


def order_service(message):
    bot.send_message(message.chat.id, "🛍️ Функция заказа услуги в разработке...")


def start_game(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("✅ Да", callback_data='game_yes', )
    btn2 = types.InlineKeyboardButton("❌ Нет", callback_data='start')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "🎮 Поиграем в города России?", reply_markup=markup)
def game_yes(message):
    global USED, GAME_ACTIVE, current_city, first_text_trash
    USED = []
    GAME_ACTIVE = True

    # Определяем текст в зависимости от того, откуда вызвана функция
    if hasattr(message, 'data') and message.data == 'game_yes':
        first_text_trash = "Вот ваше новое слово: "
    else:
        first_text_trash = "Окей тогда я начинаю - "

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Поменять слово", callback_data='change_word')
    markup.add(btn1)

    available_cities = [city for city in ALL_CITIES if city not in USED]
    current_city = random.choice(available_cities)
    USED.append(current_city)
    bot.send_message(message.chat.id,f"{first_text_trash}{current_city}. Если хочешь выйти из игры, напиши /exit", reply_markup=markup)
@bot.message_handler(func=lambda message: GAME_ACTIVE)
def all_messages(message):
    global USED, GAME_ACTIVE, current_city, first_text_trash

    first_text_trash = "Ваше новое слово: "
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Главное меню", callback_data='start')
    btn2 = types.InlineKeyboardButton("Поменять слово", callback_data='game_yes')
    markup.add(btn1, btn2)

    user_message = message.text.strip().lower()

    if user_message == "/exit":
        USED = []
        GAME_ACTIVE = False
        bot.send_message(message.chat.id, "Игра завершена!")
        return
    elif user_message in USED:
        bot.send_message(message.chat.id, "Вы уже использовали этот город", reply_markup=markup)
        return
    elif user_message.lower() not in [city.lower() for city in ALL_CITIES]:
        bot.send_message(message.chat.id, "Извините. В моем списке нет такого города. Напишите существующий город России", reply_markup=markup)
        return
    elif user_message[0].lower() != req(current_city):
        bot.send_message(message.chat.id, f"Буквы не совпадают! Нужна буква '{req(current_city)}'", reply_markup=markup)
        return

    # Город подходит
    USED.append(user_message)
    current_city = user_message

    # Бот делает ход
    required_letter = req(current_city)
    available_cities = [city for city in ALL_CITIES if city not in USED and city[0].lower() == required_letter]

    if not available_cities:
        bot.send_message(message.chat.id, f"Я не могу найти город на букву '{required_letter}'. Вы победили!")
        USED = []
        GAME_ACTIVE = False
        return

    bot_city = random.choice(available_cities)
    USED.append(bot_city)
    current_city = bot_city
    bot.send_message(message.chat.id,f"{bot_city}. Тебе на букву '{req(bot_city)}'. Если хочешь выйти из игры, напиши /exit", reply_markup=markup)
# Новая функция для смены слова
def change_word(message):
    global USED, GAME_ACTIVE, current_city

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Поменять слово", callback_data='change_word')
    markup.add(btn1)

    available_cities = [city for city in ALL_CITIES if city not in USED]
    current_city = random.choice(available_cities)
    USED.append(current_city)

    bot.send_message(message.chat.id, f"Вот ваше новое слово: {current_city}. Если хочешь выйти из игры, напиши /exit", reply_markup=markup)

def support(message):
    bot.send_message(message.chat.id, "💬 Связь с поддержкой временно недоступна")

if __name__ == '__main__':
    # Запускаем бота. none_stop=True означает, что бот будет перезапускаться после сбоев.
    print("Бот запущен и работает на GitVerse!")

    bot.polling(none_stop=True, interval=0)


