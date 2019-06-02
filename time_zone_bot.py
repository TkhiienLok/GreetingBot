#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A telegram bot that lets you pick and a timezone
@author Guy Sheffer (GuySoft) <guysoft at gmail dot com>
"""
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler, RegexHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup
import logging

import pytz
import datetime

def get_timezones():
    return_value = {}
    for tz in pytz.common_timezones:
        c = tz.split("/")
        if len(c) > 1:
            if c[0] not in return_value.keys():
                return_value[c[0]] = []
            return_value[c[0]].append(c[1])

        for i in ["GMT"]:
            if i in return_value.keys():
                return_value.pop(i)

    return return_value


def handle_cancel(update):
    query = update.message.text
    if query == "Close" or query == "/cancel":
        reply = "Perhaps another time"
        update.message.reply_text(reply)
        return reply
    return None


class Bot:
    def __init__(self, token):
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        
        # The states in the timezone conversation
        self.TIMEZONE_CONTINENT, self.TIMEZONE_TIME = range(2)
        
        set_timezone_handler = ConversationHandler(
            entry_points=[CommandHandler('timezone', self.set_timezone)],
            states={
                self.TIMEZONE_CONTINENT: [RegexHandler('^(' + "|".join(get_timezones().keys()) + '|/cancel)$', self.timezone_continent)],

                self.TIMEZONE_TIME: [RegexHandler('^(.*)$', self.timezone_time)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
        self.dispatcher.add_handler(set_timezone_handler)
        
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)
        self.offset = 0
        return
        
    def start(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="I'm timezone setting bot, please type /timezone to set a timezone")
        return
    
    def set_timezone(self, bot, update):
        keyboard = []

        for continent in sorted(get_timezones().keys()):
            keyboard.append([InlineKeyboardButton(continent)])

        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('Please select a continent, or /cancel to cancel:', reply_markup=reply_markup)
        return self.TIMEZONE_CONTINENT
    
    def timezone_continent(self, bot, update):
        reply = handle_cancel(update)
        if reply is None:
            keyboard = []
            self.selected_continent = update.message.text
            for continent in sorted(get_timezones()[self.selected_continent]):
                keyboard.append([InlineKeyboardButton(continent)])
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            update.message.reply_text('Please select a timezone, or /cancel to cancel:', reply_markup=reply_markup)

            return self.TIMEZONE_TIME
        return ConversationHandler.END

    def timezone_time(self, bot, update):
        reply = handle_cancel(update)
        if reply is None:
            timezone = self.selected_continent + "/" + update.message.text
            est = pytz.timezone(timezone)
            now = datetime.datetime.utcnow()
            self.offset = str(est.localize(now).utcoffset()).split(':')[0]

            update.message.reply_text('Timezone set set to: ' + timezone + ', time offset is '+ self.offset + ' hours')
            return ConversationHandler.END
        return ConversationHandler.END
    
    def cancel(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Perhaps another time")
        return
    
    def run(self):
        self.updater.start_polling()
        return int(self.offset)
        


if __name__ == "__main__":
    TOKEN = "745509612:AAEjf4_YIecDyxFI_dllAqcdO31lzeV26RM"
    a = Bot(TOKEN)
    a.run()
