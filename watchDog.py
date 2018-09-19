# -*- coding: utf-8 -*-
import sys
import re
import logging
import json
import time
import codecs
import random
import ConfigParser
from threading import Thread
from telegram import *
#KeyboardButton, ParseMode, ReplyKeyboardMarkup
from telegram.ext import *
# import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from selectBot import selectBot
from botsapi import bots
#import schedule

reload(sys)  
sys.setdefaultencoding('utf8')


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


file=open("puzzles.json","r")
PUZZLES = json.load(file)['puzzles']
file.close()

coinrumorbot=405689392
BinanceCN=-1001136071376

BNB48TEST = -1001395548149
WATCHDOGGROUP=BNB48TEST

def unrestrict(update,chatid, user, targetuser, reply_to_message):


    bot.sendMessage(chatid, text=u"{}解除禁言,费用{} Koge48积分由{}支付".format(targetuser.full_name,price,user.full_name), reply_to_message_id=reply_to_message.message_id)

    
def restrict(update,chatid, user, targetuser, duration, reply_to_message):

    bot.sendMessage(chatid, text=u"{}被禁言{}分钟".format(targetuser.full_name,duration), reply_to_message_id=reply_to_id)


def callbackhandler(bot,update):
    message_id = update.callback_query.message.message_id
    activeuser = update.callback_query.from_user
    if not activeuser.id in ENTRANCE_PROGRESS:
        bot.sendMessage(activeuser.id,"请输入 /start 重新作答")
        return
    thedata = update.callback_query.data
    lasttext = PUZZLES[ENTRANCE_PROGRESS[activeuser.id]]['question']
    if thedata == PUZZLES[ENTRANCE_PROGRESS[activeuser.id]]['answer']:
        #回答正确
        if ENTRANCE_PROGRESS[activeuser.id] == len(PUZZLES) - 1:
            #全部回答完毕
            unrestrict(WATCHDOGGROUP,activeuser.id)
            bot.sendMessage(activeuser.id,"您已全部作答正确，可以正常参与讨论")
        else:
            bot.sendMessage(activeuser.id,"正确，下一题")
            ENTRANCE_PROGRESS[activeuser.id]+=1
            bot.sendMessage(activeuser.id,PUZZLES[ENTRANCE_PROGRESS[activeuser.id]]['question'],reply_markup=buildpuzzlemarkup(PUZZLES[ENTRANCE_PROGRESS[activeuser.id]]['options']))
            
    else:
        #错误
            bot.sendMessage(activeuser.id,"答案不正确 请输入 /start 重新作答")
            del ENTRANCE_PROGRESS[activeuser.id]

    update.callback_query.edit_message_text( text = lasttext)
            
def buildpuzzlemarkup(options):
    keys = []
    random.shuffle(options)
    for each in options:
        keys.append([InlineKeyboardButton(each[1],callback_data=each[0])])
    return InlineKeyboardMarkup(keys)
    

ENTRANCE_PROGRESS={}
def botcommandhandler(bot,update):
    if "/join" in update.message.text:
        update.message.reply_text(bot.exportChatInviteLink(BNB48TEST))
        return
    #start in private mode
    if update.message.chat_id != update.message.from_user.id:
        return
    update.message.reply_text(PUZZLES[0]['question'],reply_markup=buildpuzzlemarkup(PUZZLES[0]['options']))
    ENTRANCE_PROGRESS[update.message.chat_id] = 0
        

def welcome(bot, update):
    if update.message.chat_id  == WATCHDOGGROUP:
        update.message.reply_markdown("新进成员需私聊[机器人](tg://user?id={})完成入群测试后方可正常参与聊天".format(coinrumorbot))
        for newUser in update.message.new_chat_members:
            restrict(update.message.chat_id,newUser.id,0.4)

def ban(chatid,userid):
    updater.bot.kickChatMember(chatid,userid)

def kick(chatid,userid):
    updater.bot.kickChatMember(chatid,userid)
    updater.bot.unbanChatMember(chatid,userid)

def restrict(chatid,userid,minutes):
    updater.bot.restrictChatMember(chatid,user_id=userid,can_send_messages=False,until_date=time.time()+int(float(minutes)*60))

def unrestrict(chatid,userid):
    updater.bot.restrictChatMember(chatid,user_id=userid,can_send_messages=True,can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)



mytoken = selectBot(bots)
updater = Updater(token=mytoken)

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CallbackQueryHandler(callbackhandler))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))#'''处理新成员加入'''
    #dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, onleft))#'''处理成员离开'''

    dp.add_handler(CommandHandler(
        [
            "start",
            "join"
        ],
        botcommandhandler))# '''处理大群中的直接消息'''

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

