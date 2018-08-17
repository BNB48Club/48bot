# -*- coding: utf-8 -*-
import logging
import json
import time

from telegram import KeyboardButton, ParseMode, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from selectBot import selectBot
from botsapi import bots


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def deleteandmute(bot, update):
    #bot.restrictChatMember(update.message.chat_id,user_id=update.message.from_user.id,can_send_messages=False,until_date=time.time()+300)
    #bot.sendMessage(update.message.chat_id, text=u"[{}](tg://user?id={}) is muted for 5 minutes".format(update.message.from_user.full_name,update.message.from_user.id), reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
    bot.deleteMessage(update.message.chat_id,update.message.message_id)
    #logger.warning(update.message.from_user.full_name+u" muted");
    return

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)



def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    mytoken = selectBot(bots)
    updater = Updater(token=mytoken)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(MessageHandler(Filters.group & Filters.text,deleteandmute))# '''处理大群中的直接消息'''

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
