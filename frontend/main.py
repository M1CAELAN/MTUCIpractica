import os
import sys
import telebot
import requests
from telebot import types
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

region_id = None
name = None
salary_to = 2147483647
salary_from = 0
time_day = None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    btn = types.KeyboardButton("Найти вакансию")
    markup.add(btn)
    bot.send_message(message.chat.id, "Привтствую, это бот для посика вакансий, хотите найти вакансию?",
                     reply_markup=markup)
    bot.register_next_step_handler(message, open_search)


def open_search(message):
    if message.text == "Найти вакансию":
        bot.send_message(message.chat.id, "Введите регион, в котором ищете вакансии")
        bot.register_next_step_handler(message, get_id_region)
    else:
        bot.send_message(message.chat.id, "Команда не распознана")
        bot.register_next_step_handler(message, start)


def get_id_region(message):
    url = f"http://127.0.0.1:5000/region/{message.text}"
    data = requests.get(url).json()
    global region_id
    if data["id"] is not None:
        bot.send_message(message.chat.id, f"Регион установлен, {message.text}")
        region_id = data["id"]
        bot.send_message(message.chat.id, "Введите название профессии")
        bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(message.chat.id, "ошибка, региона не существует, попробуйте ещё раз")
        bot.register_next_step_handler(get_id_region)


def get_name(message):
    global name
    name = message.text.replace(" ", "+")
    markup = types.ReplyKeyboardMarkup()
    btn = types.KeyboardButton("Пропустить")
    markup.add(btn)
    bot.send_message(message.chat.id, "Введите нижнюю граниу ЗП",
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_salary_from)


def get_salary_from(message):
    global salary_from
    if message.text != "Пропустить":
        salary_from = message.text
    markup = types.ReplyKeyboardMarkup()
    btn = types.KeyboardButton("Пропустить")
    markup.add(btn)
    bot.send_message(message.chat.id, "Введите верхнюю граниу ЗП",
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_salary_to)


def get_salary_to(message):
    global salary_to
    if message.text != "Пропустить":
        salary_to = message.text
    markup = types.ReplyKeyboardMarkup()
    td1 = types.KeyboardButton("Полная занятость")
    td2 = types.KeyboardButton("Частичная занятость")
    markup.row(td1, td2)
    btn = types.KeyboardButton("Пропустить")
    markup.row(btn)
    bot.send_message(message.chat.id, "Выберете график",
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_time_day)


def get_time_day(message):
    global time_day
    if message.text != "Пропустить":
        time_day = message.text
    url = f"http://127.0.0.1:5000/vacancy?vacancy={name}&salaryFrom={salary_from}&salaryTo={salary_to}&" \
          f"timeDay={time_day}&area={region_id}"
    data = requests.get(url).json()
    bot.send_message(message.chat.id, data)


bot.polling(none_stop=True)