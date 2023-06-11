from bot.bot_main import Bot

TOKEN = '6259119388:AAFXkg3c_dSRBZjFgj7XWp9jgVCjukuCgwc'
DB_FILE = "passwords.db"

if __name__ == '__main__':
    bot = Bot(TOKEN, DB_FILE)
    bot.start_bot()
