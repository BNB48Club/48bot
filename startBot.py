# -*- coding: utf-8 -*-
import logging

from telegram import KeyboardButton, ParseMode, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from Model import menu
from selectBot import selectBot
from botsapi import bots


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BLACKLIST= set()
ADMINS= [420909210,434121211]
NOTIFYADMINS="@SirIan_M @gscoin"
BNB48=-1001136778297

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def botcommandhandler(bot, update):
    """get message not mentioned and buttons response."""

    '''check if is button response'''
    message_text = update.message.text
    response = menu[message_text]
    bot.sendMessage(update.message.chat.id, text=response, reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)

def replyCommand(bot,update):
    if update.message.chat.id != BNB48:
        print('not this group')
        return
    if not update.effective_user.id in ADMINS:
        print update.effective_user.id
        print ADMINS
        print('not by admins')
        return
    replyed = update.message.reply_to_message
    newmemberid = replyed.forward_from.id
    print(newmemberid)
    targetmemberid = replyed.from_user.id
    print(targetmemberid)
    print(update.message.text)
    if update.message.text == 'pass':
        bot.restrictChatMember(update.message.chat.id,user_id=newmemberid,can_send_messages=True,can_send_media_messages=True,can_send_other_messages=True, can_add_web_page_previews=True)
        bot.sendMessage(newmemberid, text="您已通过审核，成为BNB48 Club正式会员")
        bot.sendMessage(update.message.chat.id, text="审核通过，欢迎新成员", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
    elif update.message.text == 'unblock':
        BLACKLIST.remove(newmemberid)
        bot.sendMessage(update.message.chat.id, text="移出申请黑名单", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
    elif update.message.text == 'block':
        BLACKLIST.add(newmemberid)
        bot.sendMessage(update.message.chat.id, text="加入申请黑名单", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
    
def photoHandler(bot,update):
    userid = update.effective_user.id
    if userid in BLACKLIST:
        return

    chatmember = bot.getChatMember(BNB48,userid)
    print(chatmember.can_send_messages)
    if None != chatmember.can_send_messages and True != chatmember.can_send_messages:
        forward = bot.forwardMessage(BNB48,update.effective_user.id,update.message.message_id)
        bot.sendMessage(update.message.chat.id, text="已提交持仓证明，请关注群内审批情况，耐心等待。如无必要，无需频繁重复发送。", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
        bot.sendMessage(BNB48, text=NOTIFYADMINS, reply_to_message_id=forward.message_id)

    
def welcome(bot, update):
    '''
    usernameMention = f"[{update.message.from_user.first_name}](tg://user?id={update.message.from_user.id})"
    text = f' {usernameMention}'
    keyboards = [[KeyboardButton(s)] for s in [*menu]]
    reply_markup2 = ReplyKeyboardMarkup(keyboards, one_time_keyboard=True, selective=True, resize_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.MARKDOWN,reply_markup=reply_markup2)
    bot.sendMessage(update.message.chat.id, text=update.effective_user.full_name, reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
    '''
    bot.sendMessage(update.message.chat.id, text="欢迎。新成员默认禁言，请私聊 @coinrumorbot 发送#SellBNBAt48BTC 的挂单截图(100BNB或以上)，审核通过后开启权限成为正式会员。持仓截图会被机器人自动转发进群，请注意保护个人隐私。", reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)
    for newUser in update.message.new_chat_members:
        bot.restrictChatMember(update.message.chat.id,user_id=newUser.id, can_send_messages=False)


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
    dp.add_handler(MessageHandler(Filters.reply & Filters.group, replyCommand)) '''处理大群中的回复'''
    dp.add_handler(MessageHandler(Filters.text and Filters.private, callback=botcommandhandler))
    dp.add_handler(MessageHandler(Filters.photo & Filters.private, callback=photoHandler)) '''处理私发的图片'''
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))'''处理新成员加入'''

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
