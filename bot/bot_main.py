import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, ApplicationBuilder

from dataBase.db import DBAPI
from bot.messages import *
from cipher.cipher import xor_encrypt_decrypt

DELAY = 60

class Bot:
    def __init__(self, token : str, db_file : str) -> None:
        self.db = DBAPI(db_file)
        # self.updater = Updater(token=self.token, use_context=True)
        # self.dispatcher = self.updater.dispatcher
        self.bot = ApplicationBuilder().token(token).build()

        start_handler = CommandHandler("start", self.start)
        set_handler = CommandHandler("set", self.set_password)
        get_handler = CommandHandler("get", self.get_password)
        del_handler = CommandHandler("del", self.del_password)
        help_handler = CommandHandler("help", self.help)
        button_handler = CallbackQueryHandler(self.button_handler)

        self.bot.add_handler(start_handler)
        self.bot.add_handler(set_handler)
        self.bot.add_handler(get_handler)
        self.bot.add_handler(del_handler)
        self.bot.add_handler(help_handler)
        self.bot.add_handler(button_handler)
        # self.bot.add_handler(CallbackQueryHandler(self.button_handler))

        self._update_data_keyboard = [[
            InlineKeyboardButton(YES_MESSAGE, callback_data=DATA_UPDATE_ACCEPTED),
            InlineKeyboardButton(NO_MESSAGE, callback_data=CANCLED),
        ]]
        self._delete_data_keyboard = [[
            InlineKeyboardButton(YES_MESSAGE, callback_data=DATA_DELETE_ACCEPTED),
            InlineKeyboardButton(NO_MESSAGE, callback_data=CANCLED),
        ]]

    
    async def set_password(self, update: Update, context: CallbackContext):
        """Обработчик команды /set"""
        user_id = update.effective_user.id
        args = context.args
        key = ""
        if len(args) == 4:
            key = args[3]

        if len(args) != 3 and len(args) != 4:
            await context.bot.send_message(chat_id=user_id, text=INVALID_SET_FORMAT_MESSAGE)
            return
        
        service, login, password = args[0], args[1], args[2]
        if self.db.get_password(user_id, service, login):
            await context.bot.send_message(chat_id=user_id, text=DATA_EXIST_MESSAGE.format(login, service))
            context.user_data["user_args"] = args
            context.user_data["user_id"] = user_id
            await update.message.reply_text(text=DATA_UPDATE_CONFIRM_MESSAGE.format(login, service),
                                      reply_markup=InlineKeyboardMarkup(self._update_data_keyboard))

        else:
            self.db.add_password(user_id, service, login, password, key)
            await context.bot.send_message(chat_id=user_id, text=DATA_ADDED_MESSAGE.format(login, service))


    async def del_password(self, update: Update, context: CallbackContext):
        """Обработчик команды /del"""
        user_id = update.effective_user.id
        args = context.args
        if len(args) != 2:
            await context.bot.send_message(chat_id=user_id, text=INVALID_DEL_FORMAT_MESSAGE)
            return
        service = args[0]
        login = args[1]
        if self.db.get_password(user_id, service, login):
            # self.db.delete_password(user_id, service, login)
            context.user_data["user_args"] = args
            context.user_data["user_id"] = user_id
            await update.message.reply_text(text = DATA_DELETE_CONFIRM_MESSAGE.format(login, service),
                                      reply_markup=InlineKeyboardMarkup(self._delete_data_keyboard))
        else:
            await context.bot.send_message(chat_id=user_id, text=DATA_NOT_FOUND_MESSAGE.format(login,service))
            


    async def get_password(self, update: Update, context: CallbackContext):
        """Обработчик команды /get"""
        user_id = update.effective_user.id
        args = context.args
        key = ""
        
        if len(args) == 3:
            key = args[2]

        if len(args) != 2 and len(args) != 3:
            await context.bot.send_message(chat_id=user_id, text=INVALID_GET_FORMAT_MESSAGE)
            return
        
        service = args[0]
        login = args[1]
        password = self.db.get_password(user_id, service, login)    

        if password:    
            if password[2] == False or (password[2] and key):
                enc_password = xor_encrypt_decrypt(password[1], key)
                asyncio.create_task(self.delete_message(
                    await context.bot.send_message(chat_id=user_id, text=DATA_MESSAGE.format(login, service, enc_password)),
                    service=service,
                    login=login,
                    delay=DELAY
                ))
            else :
                await context.bot.send_message(chat_id=user_id, text=NO_KEY_MESSAGE)
        else:
            await context.bot.send_message(chat_id=user_id, text=DATA_NOT_FOUND_MESSAGE.format(login, service))

    async def start(self, update: Update, context: CallbackContext):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        await context.bot.send_message(chat_id=user_id, text=WELCOME_MESSAGE)


    async def help(self, update: Update, context: CallbackContext):
        """Обработчик команды /help"""
        await update.message.reply_text(HELP_MESSAGE)


    async def button_handler(self, update: Update, context: CallbackContext):
        query = update.callback_query
        args = context.user_data.get("user_args")
        user_id = context.user_data.get("user_id")
        query.answer()

        if query.data == DATA_UPDATE_ACCEPTED:
            key = ""
            if len(args) == 4:
                key = args[3]
            service, login, password = args[0], args[1], args[2]
            self.db.update_password(user_id, service, login, password, key)
            await update.callback_query.message.edit_text(text=DATA_UPDATED_MESSAGE.format(login, service))
        elif query.data == DATA_DELETE_ACCEPTED:
            service, login = args
            self.db.delete_password(user_id, service, login)
            await update.callback_query.message.edit_text(text=DATA_DELETED_MESSAGE.format(login, service))
        else :
            await update.callback_query.message.edit_text(text=CANCLED_MESSAGE)

    @staticmethod
    async def delete_message(message: Message, service: str, login :str, delay: int):
        await asyncio.sleep(delay)
        await message.edit_text(text=MESSAGE_DELETED.format(login, service))