# -*- coding: utf-8 -*-
import logging
import json

from telegram import KeyboardButton, ParseMode, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from selectBot import selectBot
from botsapi import bots


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BLACKLIST= set()

BNB48=-1001136778297
SPAMWORDS=["Deleted", u"拉人",u"电报群",u"水军",u"增粉"];
SirIanM=420909210
Gui=434121211
coinrumorbot=405689392
bnb48_bot=571331274
NOTIFYADMINS="有新成员加入，需要审批:) "

COIN_BALANCES={};

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def digcoin(bot,update):
    return
    
def botcommandhandler(bot, update):
    message_text = update.message.text
    if "#SellBNBAt48BTC" in message_text:
        logger.warning('botcommandhandler')
        file=open("/var/www/html/sell48","r")
        content = json.load(file)
        response="目前48BTC挂单量为{}BNB".format(content['amt'])
        bot.sendMessage(update.message.chat_id, text=response, reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
        file.close()

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

    # If directly reply the newmember msg
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
            
    if update.message.chat_id == BNB48:
        bot.sendMessage(update.message.chat_id, text=u"欢迎。新成员默认禁言，请私聊 [BNB48 - 静静](tg://user?id=571331274)  发送持仓截图(1583BNB或以上，Photo形式，非File形式)，审核通过后开启权限成为正式会员。持仓截图会被机器人自动转发进群，请注意保护个人隐私。", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
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
    dp.add_handler(MessageHandler(Filters.photo & Filters.private, callback=photoHandler))#'''处理私发的图片'''
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))#'''处理新成员加入'''
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, onleft))#'''处理成员离开'''
    dp.add_handler(MessageHandler(Filters.group & Filters.text & Filters.reply, replyCommand))# '''处理大群中的回复'''
    dp.add_handler(MessageHandler(Filters.group & Filters.text & (~Filters.reply) & (~Filters.status_update),botcommandhandler))# '''处理大群中的直接消息'''

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
