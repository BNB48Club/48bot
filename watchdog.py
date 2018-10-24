#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import logging
import json
import time
import random
import ConfigParser
from telegram import *
from telegram.ext import *

reload(sys)  
sys.setdefaultencoding('utf8')


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Read config
watchdogconfig = ConfigParser.ConfigParser()
watchdogconfig.read("conf/watchdog.conf")

# set bot conf
bottoken = watchdogconfig.get("bot","token")
botid=int(bottoken.split(":")[0])
botname = watchdogconfig.get("bot","name")

# parse groups info
GROUPS = {}
for groupinfo in watchdogconfig.items("groups"):
    groupid = int(groupinfo[0])
    file=open(groupinfo[1],"r")
    puzzles = json.load(file)
    file.close()
    GROUPS[groupid]=puzzles
    GROUPS[groupid]['lasthintid']=0
    GROUPS[groupid]['ENTRANCE_PROGRESS']={}
    GROUPS[groupid]['kickjobs'] = {}
    logger.warning("start watching %s",groupid)

# parse puzzles.json

def ban(chatid,userid):
    updater.bot.kickChatMember(chatid,userid)

def kick(chatid,userid):
    updater.bot.kickChatMember(chatid,userid)
    updater.bot.unbanChatMember(chatid,userid)

def watchdogkick(bot,job):
    kick(job.context['groupid'],job.context['userid'])
    logger.warning("%s(%s) is kicked from %s",job.context['full_name'],job.context['userid'],job.context['groupid'])

def restrict(chatid,userid,minutes):
    updater.bot.restrictChatMember(chatid,user_id=userid,can_send_messages=False,until_date=time.time()+int(float(minutes)*60))

def unrestrict(chatid,userid):
    updater.bot.restrictChatMember(chatid,user_id=userid,can_send_messages=True,can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)

def callbackhandler(bot,update):
    global GROUPS
    thedata = update.callback_query.data.split("#")
    groupid = int(thedata[0])
    answer = thedata[1]
    message_id = update.callback_query.message.message_id
    activeuser = update.callback_query.from_user
    if not activeuser.id in GROUPS[groupid]['ENTRANCE_PROGRESS']:
        bot.sendMessage(activeuser.id,GROUPS[groupid]['onstart'])
        return

    ENTRANCE_PROGRESS = GROUPS[groupid]['ENTRANCE_PROGRESS']
    PUZZLES = GROUPS[groupid]['puzzles']

    currentpuzzleindex = ENTRANCE_PROGRESS[activeuser.id]
    #lasttext = PUZZLES[ENTRANCE_PROGRESS[activeuser.id]]['question']

    if answer == GROUPS[groupid]['puzzles'][currentpuzzleindex]['answer']:
    #回答正确
        if ENTRANCE_PROGRESS[activeuser.id] + 1>= len(GROUPS[groupid]['puzzles']):
            #全部回答完毕
            if activeuser.id in GROUPS[groupid]['kickjobs']:
                GROUPS[groupid]['kickjobs'][activeuser.id].schedule_removal()
                del GROUPS[groupid]['kickjobs'][activeuser.id]
            if bot.getChatMember(groupid,activeuser.id).can_send_messages == False:
                unrestrict(groupid,activeuser.id)
                logger.warning("%s(%s)Past the test in %s",activeuser.full_name,activeuser.id,groupid)
                bot.sendMessage(activeuser.id, GROUPS[groupid]['onpast'])
            else:
                pass
        else:
            bot.sendMessage(activeuser.id,GROUPS[groupid]['puzzles'][currentpuzzleindex]['postcorrect'])
            ENTRANCE_PROGRESS[activeuser.id]+=1
            bot.sendMessage(activeuser.id,PUZZLES[ENTRANCE_PROGRESS[activeuser.id]]['question'],reply_markup=buildpuzzlemarkup(groupid,PUZZLES[ENTRANCE_PROGRESS[activeuser.id]]['options']))
            
    else:
        #错误
            bot.sendMessage(activeuser.id,GROUPS[groupid]['puzzles'][currentpuzzleindex]['postincorrect'])
            bot.sendMessage(activeuser.id,GROUPS[groupid]['onfail'])
            del ENTRANCE_PROGRESS[activeuser.id]

    #update.callback_query.edit_message_text( text = lasttext)
            
def buildpuzzlemarkup(groupid,options):
    keys = []
    random.shuffle(options)
    for each in options:
        keys.append([InlineKeyboardButton(each[1],callback_data="{}#{}".format(groupid,each[0]))])
    return InlineKeyboardMarkup(keys)
    


def botcommandhandler(bot,update):
    #start in private mode
    if update.message.chat_id != update.message.from_user.id:
        return
    userid = update.message.from_user.id
    global GROUPS
    for groupid in GROUPS:
        try:
            chatmember = bot.getChatMember(groupid,userid)
            if chatmember.can_send_messages != False:
                continue
            else:
                update.message.reply_text(GROUPS[groupid]['puzzles'][0]['question'],reply_markup=buildpuzzlemarkup(groupid,GROUPS[groupid]['puzzles'][0]['options']))
                GROUPS[groupid]['ENTRANCE_PROGRESS'][userid] = 0
                break
        except:
            continue
        

def welcome(bot, update):
    global GROUPS
    groupid = update.message.chat_id
    if groupid in GROUPS:
        for newUser in update.message.new_chat_members:
            logger.warning("%s(%s)Joined %s",newUser.full_name,newUser.id,update.message.chat.title)
            restrict(update.message.chat_id,newUser.id,0.4)
            logger.warning("Muted")
            probation = GROUPS[groupid]['probation']
            GROUPS[groupid]['kickjobs'][newUser.id] = jobqueue.run_once(watchdogkick,probation*60,context = {"userid":newUser.id,"groupid":groupid,"full_name":newUser.full_name})
            logger.warning("%s minutes kicker timer started for %s in %s",GROUPS[groupid]['probation'],newUser.id,groupid)


            if GROUPS[groupid]['lasthintid'] != 0:
                try:
                    bot.deleteMessage(groupid,GROUPS[groupid]['lasthintid'])
                except:
                    logger.warning("deleting exception")

            GROUPS[groupid]['lasthintid'] = update.message.reply_text("{}: {}".format(GROUPS[groupid]['grouphint'],botname),quote=True).message_id

            update.message.delete()

            try:
                bot.sendMessage(newUser.id,GROUPS[groupid]['onstart'],parse_mode=ParseMode.MARKDOWN)
            except:
                #pass
                logger.warning("send to %s(%s) failure",newUser.full_name,newUser.id)
            

    

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)



updater = Updater(token=bottoken)
jobqueue = updater.job_queue

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
            "start"
        ],
        botcommandhandler))

    # log all errors
    dp.add_error_handler(error)



    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



if __name__ == '__main__':
    logger.warning("%s(%s) starts watching",watchdogconfig.get("bot","name"),watchdogconfig.get("bot","token"))
    main()
