# -*- coding: utf-8 -*-
import logging
import json
import time
import codecs
import random
import ConfigParser

from telegram import *
#KeyboardButton, ParseMode, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from selectBot import selectBot
from botsapi import bots
from koge48 import Koge48


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

BLACKLIST= set()

BNB48=-1001136778297

file=open("flushwords.json","r")
FLUSHWORDS = json.load(file)["words"]
file.close()

file=open("spamwords.json","r")
SPAMWORDS=json.load(file)["words"]
file.close()

SirIanM=420909210
Gui=434121211
coinrumorbot=405689392
bnb48_bot=571331274

kogeconfig = ConfigParser.ConfigParser()
kogeconfig.read("koge48.conf")
koge48core = Koge48(
  kogeconfig.get("mysql","host"),
  kogeconfig.get("mysql","user"),
  kogeconfig.get("mysql","passwd"),
  kogeconfig.get("mysql","database")
)

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False


def unmute(bot, chatid, user, targetuser, reply_to_message):
    admins = bot.get_chat_administrators(chatid)
    if reply_to_message is None:
        reply_to_id = None
    else:
        reply_to_id = reply_to_message.message_id 
    if user != None and not bot.getChatMember(chatid,user.id) in admins:
        bot.sendMessage(chatid, text=u"No sufficient privilege", reply_to_message_id=reply_to_id,parse_mode=ParseMode.MARKDOWN)
        return
    if bot.getChatMember(chatid,targetuser.id) in admins:
        bot.sendMessage(chatid, text=u"Don't need to unmute an admin", reply_to_message_id=reply_to_id,parse_mode=ParseMode.MARKDOWN)
        return
    bot.restrictChatMember(chatid,user_id=targetuser.id,can_send_messages=True,can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
    bot.sendMessage(chatid, text=u"[{}](tg://user?id={}) is unmuted".format(targetuser.full_name,targetuser.id), reply_to_message_id=reply_to_message.message_id,parse_mode=ParseMode.MARKDOWN)

    
def mute(bot, chatid, user, targetuser, duration, reply_to_message):
    admins = bot.get_chat_administrators(chatid)
    if reply_to_message is None:
        reply_to_id = None
    else:
        reply_to_id = reply_to_message.message_id 
    if user != None and not bot.getChatMember(chatid,user.id) in admins:
        bot.sendMessage(chatid, text=u"No sufficient privilege", reply_to_message_id=reply_to_id,parse_mode=ParseMode.MARKDOWN)
        return
    if bot.getChatMember(chatid,targetuser.id) in admins:
        bot.sendMessage(chatid, text=u"Can't restrict an admin", reply_to_message_id=reply_to_id,parse_mode=ParseMode.MARKDOWN)
        return
    bot.restrictChatMember(chatid,user_id=targetuser.id,can_send_messages=False,until_date=time.time()+int(float(duration)*3600))
    bot.sendMessage(chatid, text=u"[{}](tg://user?id={}) is muted for {} hour(s)".format(targetuser.full_name,targetuser.id,duration), reply_to_message_id=reply_to_id,parse_mode=ParseMode.MARKDOWN)


def botcommandhandler(bot,update):
    things = update.message.text.split(' ')

    if "/sync" in things[0] and not update.message.reply_to_message is None:
        if u"💰" in update.message.reply_to_message.text:
            bot.sendMessage(update.message.chat_id, text=update.message.reply_to_message.text, reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
    elif "/casino" in things[0]:
        #开始赌场
        btn1 = InlineKeyboardButton('Homepage', url='http://bnb48.club')
        btn2 = InlineKeyboardButton('Action', callback_data='Act Now')
        markup = InlineKeyboardMarkup(btn1,bt2)
        bot.send_message(message.chat.id, "InlineKeyboard: ", reply_markup=markup)
    elif "/bal" in things[0]:
        user = update.message.from_user

        if update.message.reply_to_message is None:
            targetuser = user
        else:
            targetuser = update.message.reply_to_message.from_user

        bot.sendMessage(update.message.chat_id, text="{} Koge48".format(koge48core.getBalance(targetuser.id)), reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)

    elif ("/unmute" in things[0] or "/mute" in things[0] ) and not update.message.reply_to_message is None:
        
        user = update.message.from_user
        targetuser = update.message.reply_to_message.from_user


        if "/mute" in things[0]:
            duration = 0.01
            if len(things) > 1 and is_number(things[1]):
                duration = things[1]
            mute(bot,update.message.chat_id,user,targetuser,duration,update.message)

        elif "/unmute" in things[0]:
            unmute(bot,update.message.chat_id,user,targetuser,update.message)

    elif ("/ban" in things[0] or "/kick" in things[0] ) and "from_user" in  dir(update.message.reply_to_message):
        if update.message.from_user.id != SirIanM:
            return
        try:
            bot.kickChatMember(update.message.chat_id,user_id=targetid)
        except:
            logger.warning("except when kicking")
        if "/kick" == things[0]:
            bot.unbanChatMember(update.message.chat_id,user_id=targetid)
        bot.sendMessage(update.message.chat_id, text=u"[{}](tg://user?id={}) is {}".format(update.message.reply_to_message.from_user.full_name,targetid,things[0]+"ed"), reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
        
    elif ("/promote" == things[0] or "/demote" == things[0]) and "from_user" in  dir(update.message.reply_to_message):
        if update.message.from_user.id != SirIanM:
            return
        targetid = update.message.reply_to_message.from_user.id

        if things[0] == "/promote":
            bot.promoteChatMember(update.message.chat_id, targetid,can_delete_messages=True)
            bot.sendMessage(update.message.chat_id, text=u"[{}](tg://user?id={}) is promoted".format(update.message.reply_to_message.from_user.full_name,targetid), reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
        if things[0] == "/demote":
            bot.promoteChatMember(update.message.chat_id, targetid, can_change_info=False,can_delete_messages=False, can_invite_users=False, can_restrict_members=False, can_pin_messages=False, can_promote_members=False)
            #bot.promoteChatMember(update.message.chat_id, targetid, can_delete_messages=None)
            bot.sendMessage(update.message.chat_id, text=u"[{}](tg://user?id={}) is demoted".format(update.message.reply_to_message.from_user.full_name,targetid), reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)

    elif "/flush"==things[0] or "/deflush"==things[0]:
        if update.message.from_user.id != SirIanM:
            return
            #SirIanM only
        thekeyword=""

        if "text" in dir(update.message.reply_to_message):
            thekeyword = update.message.reply_to_message.text
        else:
            thekeyword = things[1]

        if "/flush"==things[0]:
            if thekeyword in FLUSHWORDS:
                return
            FLUSHWORDS.append(thekeyword)
            bot.sendMessage(update.message.chat_id, text=u"增加\""+thekeyword+u"\"为刷屏关键词", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
        else:
            if not thekeyword in FLUSHWORDS:
                return
            FLUSHWORDS.remove(thekeyword)
            bot.sendMessage(update.message.chat_id, text=u"不再将\""+thekeyword+u"\"作为刷屏关键词", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)

        file = codecs.open("flushwords.json","w","utf-8")
        file.write(json.dumps({"words":FLUSHWORDS}))
        file.flush()
        file.close()
        logger.warning("flushwords updated")
    elif "/spam"==things[0] or "/despam"==things[0]:
        if update.message.from_user.id != SirIanM:
            return
            #SirIanM only
        thekeyword=""

        if "text" in dir(update.message.reply_to_message):
            thekeyword = update.message.reply_to_message.text
        else:
            thekeyword = things[1]

        if "/spam"==things[0]:
            if thekeyword in SPAMWORDS:
                return
            SPAMWORDS.append(thekeyword)
            bot.sendMessage(update.message.chat_id, text=u"增加\""+thekeyword+u"\"为垃圾账号关键词", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
        else:
            if not thekeyword in SPAMWORDS:
                return
            SPAMWORDS.remove(thekeyword)
            bot.sendMessage(update.message.chat_id, text=u"不再将\""+thekeyword+u"\"作为垃圾账号关键词", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)

        file = codecs.open("spamwords.json","w","utf-8")
        file.write(json.dumps({"words":SPAMWORDS}))
        file.flush()
        file.close()
        logger.warning("spamwords updated")
    return

def botmessagehandler(bot, update):
    message_text = update.message.text
    #logger.warning(message_text)
    if "#SellBNBAt48BTC" in message_text:
        logger.warning('botmessagehandler')
        file=open("/var/www/html/sell48","r")
        content = json.load(file)
        response="目前48BTC挂单量为{}BNB".format(content['amt'])
        bot.sendMessage(update.message.chat_id, text=response, reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
        file.close()
        return
    #elif update.message.chat_id != BNB48 and update.message.from_user.id == :
        #eface evidence
        #time.sleep(5)
    #    bot.deleteMessage( update.message.chat_id, update.message.message_id)

    else:
        # anti flush
        words = update.message.text.split(' ')
        chatid = update.message.chat_id
        for FLUSHWORD in FLUSHWORDS:
            if FLUSHWORD in update.message.text:
                mute(bot, update.message.chat_id, None, update.message.from_user, 0.1, update.message)
                logger.warning(update.message.from_user.full_name+u" muted because of " + update.message.text);
                return
        #mining
        user = update.message.from_user
        if koge48core.mine(user.id):
            bot.sendMessage(chatid, text=u"_{}_挖到一枚【Koge48】".format(user.full_name,user.id), reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)


'''
def replyCommand(bot,update):
    # Only take care of replys in BNB48
    if update.message.chat_id != BNB48:
        logger.warning('not this group')
        return
    # Only admins can reply
    talkingmember = bot.getChatMember(BNB48, update.effective_user.id)
    if talkingmember.status != 'creator' and talkingmember.status != 'administrator':
        #bot.sendMessage(update.message.chat_id, text="不是管理员不要捣蛋", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
        logger.warning(talkingmember.status)
        return

    #################
    #If directly reply the newmember msg
    replyed = update.message.reply_to_message
    # If message == pass && new members
    if hasattr(replyed,'new_chat_members') and len(replyed.new_chat_members)>0 and update.message.text == 'pass':
        for newUser in replyed.new_chat_members:
            bot.restrictChatMember(update.message.chat_id,user_id=newUser.id,can_send_messages=True,can_send_media_messages=True,can_send_other_messages=True, can_add_web_page_previews=True)
            logger.warning(newUser.full_name+" passed");
        return

    # If a normal forwarded pass process
    beingreplieduser = replyed.from_user
    if beingreplieduser.id != 571331274 and beingreplieduser.id != 405689392:
        logger.warning('not to me, to {}'.format(beingreplieduser.id))
        return

    try:
        newmember = replyed.forward_from
        newmemberid = replyed.forward_from.id
    except AttributeError:
        logger.warning('not a forward message')
        return

    if update.message.text == 'pass':
        newchatmember = bot.getChatMember(BNB48, newmemberid)
        if newchatmember.status == 'restricted':
            bot.restrictChatMember(update.message.chat_id,user_id=newmemberid,can_send_messages=True,can_send_media_messages=True,can_send_other_messages=True, can_add_web_page_previews=True)
            bot.sendMessage(newmemberid, text=u"您已通过审核，成为BNB48 Club正式会员")
            bot.sendMessage(update.message.chat_id, text=u"欢迎新成员"+newmember.full_name)#, reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
        else:
            bot.sendMessage(update.message.chat_id, text=newchatmember.status+u"该成员之前已经通过审核或已经离开本群", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
            

    elif update.message.text == 'unblock':
        BLACKLIST.remove(newmemberid)
        bot.sendMessage(update.message.chat_id, text=u"移出申请黑名单", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
    elif update.message.text == 'block':
        BLACKLIST.add(newmemberid)
        bot.sendMessage(update.message.chat_id, text=u"加入申请黑名单", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(newmemberid, text=update.message.text)
        #原样转发管理员的消息
    '''
def photoHandler(bot,update):
    userid = update.effective_user.id
    if userid in BLACKLIST:
        return

    chatmember = bot.getChatMember(BNB48,userid)
    logger.warning(chatmember.can_send_messages)
    sayingmember = bot.getChatMember(BNB48, userid)
    if sayingmember.status == 'restricted' or userid == SirIanM:
        forward = bot.forwardMessage(BNB48,update.effective_user.id,update.message.message_id)
        bot.sendMessage(update.message.chat_id, text=u"已提交持仓证明，请关注群内审批情况，耐心等待。如无必要，无需频繁重复发送。", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
        #给每名管理员私聊发送提醒
        admins = bot.getChatAdministrators(BNB48)
        for eachadmin in admins:
            try:
                bot.sendMessage(eachadmin.user.id, text=NOTIFYADMINS,parse_mode ="Markdown")
            except TelegramError:
                print('TelegramError, could be while send private message to admins')
                continue

    
def onleft(bot,update):
    for SPAMWORD in SPAMWORDS:
        if SPAMWORD in update.message.left_chat_member.full_name:
            bot.deleteMessage(update.message.chat_id,update.message.message_id)
            return

def welcome(bot, update):
    '''
    usernameMention = f"[{update.message.from_user.first_name}](tg://user?id={update.message.from_user.id})"
    text = f' {usernameMention}'
    keyboards = [[KeyboardButton(s)] for s in [*menu]]
    reply_markup2 = ReplyKeyboardMarkup(keyboards, one_time_keyboard=True, selective=True, resize_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN,reply_markup=reply_markup2)
    bot.sendMessage(update.message.chat_id, text=update.effective_user.full_name, reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
    '''
    #首先筛选垃圾消息
    isSpam = False
    for newUser in update.message.new_chat_members:
        for SPAMWORD in SPAMWORDS:
            if SPAMWORD in newUser.full_name:
                isSpam = True
                break;

    if isSpam:
        bot.deleteMessage(update.message.chat_id,update.message.message_id)
        for newUser in update.message.new_chat_members:
            bot.kickChatMember(update.message.chat_id,newUser.id)
            logger.warning('%s|%s is kicked because of spam',newUser.id,newUser.full_name)
            
    #if update.message.chat_id == BNB48:
        #bot.sendMessage(update.message.chat_id, text=u"欢迎。新成员默认禁言，请私聊 [BNB48 - 静静](tg://user?id=571331274)  发送持仓截图(1583BNB或以上，Photo形式，非File形式)，审核通过后开启权限成为正式会员。持仓截图会被机器人自动转发进群，请注意保护个人隐私。", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
        #for newUser in update.message.new_chat_members:
        #    bot.restrictChatMember(update.message.chat_id,user_id=newUser.id, can_send_messages=False)
        #使用Groupbutler完成这一功能，自己不写了


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
    #dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text and Filters.private, callback=botcommandhandler))#'''处理私聊文字'''
    #dp.add_handler(MessageHandler(Filters.photo & Filters.private, callback=photoHandler))#'''处理私发的图片'''
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))#'''处理新成员加入'''
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, onleft))#'''处理成员离开'''
    #dp.add_handler(MessageHandler(Filters.group & Filters.text & Filters.reply, replyCommand))# '''处理大群中的回复'''
    dp.add_handler(MessageHandler(Filters.group & Filters.text & (~Filters.status_update),botmessagehandler))# '''处理大群中的直接消息'''
    dp.add_handler(CommandHandler(
        [
            "bal",
            "casino",
            "spam",
            "despam",
            "ban",
            "kick",
            "promote",
            "demote",
            "deflush",
            "flush",
            "mute",
            "unmute",
            "sync"
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
