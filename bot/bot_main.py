from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

from dataBase.db import DBAPI
from bot.messages import *
from cipher.cipher import xor_encrypt_decrypt

class Bot:
    def __init__(self, token : str, db_file : str) -> None:
        self.token = token
        self.db = DBAPI(db_file)
        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher


        start_handler = CommandHandler("start", self.start)
        set_handler = CommandHandler("set", self.set_password)
        get_handler = CommandHandler("get", self.get_password)
        del_handler = CommandHandler("del", self.del_password)
        help_handler = CommandHandler("help", self.help)
        button_handler = CallbackQueryHandler(self.button_handler)

        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(set_handler)
        self.dispatcher.add_handler(get_handler)
        self.dispatcher.add_handler(del_handler)
        self.dispatcher.add_handler(help_handler)
        self.dispatcher.add_handler(button_handler)
        # self.bot.add_handler(CallbackQueryHandler(self.button_handler))

        self._update_data_keyboard = [[
            InlineKeyboardButton(YES_MESSAGE, callback_data=DATA_UPDATE_ACCEPTED),
            InlineKeyboardButton(NO_MESSAGE, callback_data=CANCLED),
        ]]
        self._delete_data_keyboard = [[
            InlineKeyboardButton(YES_MESSAGE, callback_data=DATA_DELETE_ACCEPTED),
            InlineKeyboardButton(NO_MESSAGE, callback_data=CANCLED),
        ]]

    
    def set_password(self, update: Update, context: CallbackContext):
        """Обработчик команды /set"""
        user_id = update.effective_user.id
        args = context.args
        key = ""
        if len(args) == 4:
            key = args[3]

        if len(args) != 3 and len(args) != 4:
            context.bot.send_message(chat_id=user_id, text=INVALID_SET_FORMAT_MESSAGE)
            return
        
        service, login, password = args[0], args[1], args[2]
        if self.db.get_password(user_id, service, login):
            context.bot.send_message(chat_id=user_id, text=DATA_EXIST_MESSAGE.format(login, service))
            context.user_data["user_args"] = args
            context.user_data["user_id"] = user_id
            update.message.reply_text(text=DATA_UPDATE_CONFIRM_MESSAGE.format(login, service),
                                      reply_markup=InlineKeyboardMarkup(self._update_data_keyboard))

        else:
            self.db.add_password(user_id, service, login, password, key)
            context.bot.send_message(chat_id=user_id, text=DATA_ADDED_MESSAGE.format(login, service))


    def del_password(self, update: Update, context: CallbackContext):
        """Обработчик команды /del"""
        user_id = update.effective_user.id
        args = context.args
        if len(args) != 2:
            context.bot.send_message(chat_id=user_id, text=INVALID_DEL_FORMAT_MESSAGE)
            return
        service = args[0]
        login = args[1]
        if self.db.get_password(user_id, service, login):
            # self.db.delete_password(user_id, service, login)
            context.user_data["user_args"] = args
            context.user_data["user_id"] = user_id
            update.message.reply_text(text = DATA_DELETE_CONFIRM_MESSAGE.format(login, service),
                                      reply_markup=InlineKeyboardMarkup(self._delete_data_keyboard))
            # context.bot.send_message(chat_id=user_id, text=DATA_DELETED_MESSAGE.format(login,service))
        else:
            context.bot.send_message(chat_id=user_id, text=DATA_NOT_FOUND_MESSAGE.format(login,service))
            


    def get_password(self, update: Update, context: CallbackContext):
        """Обработчик команды /get"""
        user_id = update.effective_user.id
        args = context.args
        key = ""
        
        if len(args) == 3:
            key = args[2]

        if len(args) != 2 and len(args) != 3:
            context.bot.send_message(chat_id=user_id, text=INVALID_GET_FORMAT_MESSAGE)
            return
        
        service = args[0]
        login = args[1]
        password = self.db.get_password(user_id, service, login)    

        if password:    
            if password[2] == False or (password[2] and key):
                enc_password = xor_encrypt_decrypt(password[1], key)
                context.bot.send_message(chat_id=user_id, text=DATA_MESSAGE.format(login, service, enc_password))
            else :
                context.bot.send_message(chat_id=user_id, text=NO_KEY_MESSAGE)
        else:
            context.bot.send_message(chat_id=user_id, text=DATA_NOT_FOUND_MESSAGE.format(login, service))

    def start(self, update: Update, context: CallbackContext):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        context.bot.send_message(chat_id=user_id, text=WELCOME_MESSAGE)


    def help(self, update: Update, context: CallbackContext):
        """Обработчик команды /help"""
        update.message.reply_text(HELP_MESSAGE)


    def start_bot(self):
        self.updater.start_polling()
        self.updater.idle()


    def button_handler(self, update: Update, context: CallbackContext) :
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
            update.callback_query.message.edit_text(text=DATA_UPDATED_MESSAGE.format(login, service))
        elif query.data == DATA_DELETE_ACCEPTED:
            service, login = args
            self.db.delete_password(user_id, service, login)
            update.callback_query.message.edit_text(text=DATA_DELETED_MESSAGE.format(login, service))
        else :
            update.callback_query.message.edit_text(text=CANCLED_MESSAGE)
