import os
import telebot
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

@bot.mesenge_hendler(commands=['start'])
def start(mesenge):


bot.polling(none_stop=True)