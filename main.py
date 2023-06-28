import asyncio

from bot.bot_main import Bot

TOKEN = '6162380761:AAFa4MXFL-_Glk1mraZk8RYelRlI3Ruq8h4'
DB_FILE = "passwords.db"

if __name__ == '__main__':
    bot = Bot(TOKEN, DB_FILE)
    # asyncio.run(bot.start_bot())
    bot.bot.run_polling()