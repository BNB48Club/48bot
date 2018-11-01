#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import codecs
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
globalconfig = ConfigParser.ConfigParser()
globalconfig.read(sys.argv[1])

# set bot conf
bottoken = globalconfig.get("bot","token")
botid=int(bottoken.split(":")[0])
botname = globalconfig.get("bot","name")

updater = Updater(token=bottoken)
jobqueue = updater.job_queue


# read ADMINS
CONFADMINS= [420909210]
DATAADMINS= [420909210]
for confadmin in globalconfig.items("confadmins"):
    CONFADMINS.append(int(confadmin[0]))
for dataadmin in globalconfig.items("dataadmins"):
    DATAADMINS.append(int(dataadmin[0]))

# parse groups info
ALLGROUPS = {}
GROUPS = {}
GROUPADMINS = {}
for groupinfo in globalconfig.items("groups"):
    groupid = int(groupinfo[0])
    if not ".json" in groupinfo[1]:
        ALLGROUPS[groupid]="Othergroup"
        continue
    file=open(groupinfo[1],"r")
    puzzles = json.load(file)
    file.close()
    GROUPS[groupid]=puzzles
    GROUPS[groupid]['lasthintid']=0
    GROUPS[groupid]['ENTRANCE_PROGRESS']={}
    GROUPS[groupid]['kickjobs'] = {}
    ALLGROUPS[groupid]=GROUPS[groupid]['groupname']
    logger.warning("start watching %s",groupid)

print(ALLGROUPS)
print("---------")
print(GROUPS)
def refreshAdmins(bot,job):
    global ALLGROUPS
    global GROUPADMINS
    logger.warning("start refreshing")
    for groupid in ALLGROUPS:
        GROUPADMINS[groupid]=getAdminsInThisGroup(bot,groupid)
    logger.warning("admins refreshed")

def banInAllGroups(userid):

    file=open("_data/blacklist_ids.json","r")
    BLACKLIST=json.load(file)["ids"]
    file.close()

    file = codecs.open("_data/blacklist_ids.json","w","utf-8")
    BLACKLIST.append(userid)
    BLACKLIST=list(set(BLACKLIST))
    file.write(json.dumps({"ids":BLACKLIST}))
    file.flush()
    file.close()
    logger.warning("blacklist_ids updated")

    global ALLGROUPS
    for groupid in ALLGROUPS:
        try:
            ban(groupid,userid)
            logger.warning("{} banned in {}".format(userid,groupid))
        except:
            pass

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
    if "banInAllGroups" in update.callback_query.data:
        eval(update.callback_query.data)
        update.callback_query.answer('banned')
        return
    thedata = update.callback_query.data.split("#")
    groupid = int(thedata[0])
    answer = thedata[1]
    message_id = update.callback_query.message.message_id
    activeuser = update.callback_query.from_user
    if not activeuser.id in GROUPS[groupid]['ENTRANCE_PROGRESS']:
        bot.sendMessage(activeuser.id,GROUPS[groupid]['onstart'])
        update.callback_query.answer()
        return

    ENTRANCE_PROGRESS = GROUPS[groupid]['ENTRANCE_PROGRESS']
    PUZZLES = GROUPS[groupid]['puzzles']

    currentpuzzleindex = ENTRANCE_PROGRESS[activeuser.id]
    #lasttext = PUZZLES[ENTRANCE_PROGRESS[activeuser.id]]['question']

    if answer == GROUPS[groupid]['puzzles'][currentpuzzleindex]['answer']:
    #correct answer
        update.callback_query.answer(GROUPS[groupid]['puzzles'][currentpuzzleindex]['postcorrect'])
        if ENTRANCE_PROGRESS[activeuser.id] + 1>= len(GROUPS[groupid]['puzzles']):
            #all questions done
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
            ENTRANCE_PROGRESS[activeuser.id]+=1
            bot.sendMessage(activeuser.id,PUZZLES[ENTRANCE_PROGRESS[activeuser.id]]['question'],reply_markup=buildpuzzlemarkup(groupid,PUZZLES[ENTRANCE_PROGRESS[activeuser.id]]['options']))
            
    else:
        #wrong answer
        update.callback_query.answer(GROUPS[groupid]['puzzles'][currentpuzzleindex]['postincorrect'])
        bot.sendMessage(activeuser.id,GROUPS[groupid]['onfail'])
        del ENTRANCE_PROGRESS[activeuser.id]

    #update.callback_query.edit_message_text( text = lasttext)
            
def buildpuzzlemarkup(groupid,options):
    keys = []
    random.shuffle(options)
    for each in options:
        keys.append([InlineKeyboardButton(each[1],callback_data="{}#{}".format(groupid,each[0]))])
    return InlineKeyboardMarkup(keys)
    

def replybanallhandler(bot,update):
    if not isAdmin(bot,update):
        return
    #ban(update.message.chat_id,update.message.reply_to_message.from_user.id)
    banInAllGroups(update.message.reply_to_message.from_user.id)
    update.message.reply_text("banned in all groups")

def idbanallhandler(bot,update):
    if not isAdmin(bot,update):
        return
    things=update.message.text.split(" ")
    banInAllGroups(things[1])
    update.message.reply_text("banned in all groups")
def supervisehandler(bot,update):
    if not isAdmin(bot,update):
        return
    global globalconfig
    if not update.message.chat_id in ALLGROUPS:
        groupid = update.message.chat_id
        ALLGROUPS[groupid]=update.message.chat.title
        GROUPADMINS[groupid]=getAdminsInThisGroup(bot,groupid)
        globalconfig.set("groups",str(update.message.chat_id),update.message.chat.title)
        with open(sys.argv[1], 'wb') as configfile:
            globalconfig.write(configfile)
        update.message.reply_text("supervised")
    else:
        update.message.reply_text("was supervised before")
def fwdbanallhandler(bot,update):
    if not isAdmin(bot,update):
        return
    targetuser = update.message.reply_to_message.forward_from
    banInAllGroups(targetuser.id)
    update.message.reply_text("banned in all groups")

def getAdminsInThisGroup(bot,groupid):
    admins = bot.get_chat_administrators(groupid)
    RESULTS=[]
    for admin in admins:
        RESULTS.append(admin.user.id)
    return RESULTS

def isAdmin(bot,update):
    global GROUPADMINS
    userid = update.message.from_user.id
    if update.message.chat_id in GROUPADMINS and userid in GROUPADMINS[update.message.chat_id]:
        return True
    elif userid in CONFADMINS or userid in DATAADMINS:
        return True
    else:
        return False
def starthandler(bot,update):
    
    #must in private mode
    if update.message.chat_id != update.message.from_user.id:
        return
    userid = update.message.from_user.id
    global GROUPS
    for groupid in GROUPS:
        try:
            chatmember = bot.getChatMember(groupid,userid)
            if chatmember.status != 'restricted':
                #kicked can not,left can not
                continue
            elif chatmember.can_send_messages != False:
                # can send but just not that kind of
                continue
            else:
                update.message.reply_text(GROUPS[groupid]['puzzles'][0]['question'],reply_markup=buildpuzzlemarkup(groupid,GROUPS[groupid]['puzzles'][0]['options']))
                GROUPS[groupid]['ENTRANCE_PROGRESS'][userid] = 0
                return
        except:
            continue
    update.message.reply_text("You've no group to enter")
        
def forwardhandler(bot,update):
    global ALLGROUPS
    global GROUPADMINS
    if update.message.chat_id == update.message.from_user.id:
        fwduser = update.message.forward_from
        isAdmin = False
        for groupid in ALLGROUPS:
            if fwduser.id in GROUPADMINS[groupid]:
                update.message.reply_text("✅Admin in {}".format(ALLGROUPS[groupid]))
                isAdmin = True
        if not isAdmin:
            if update.message.from_user.id in DATAADMINS or update.message.from_user.id in CONFADMINS:
                update.message.reply_text("‼️ Be careful, this guy is not an admin",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Ban in all groups!',callback_data="banInAllGroups({})".format(fwduser.id))]]))
            else:
                update.message.reply_text("‼️ Be careful, this guy is not an admin")
        #send in private 
    #else:
        #send in group
    
def welcome(bot, update):
    global GROUPS
    
    file=open("_data/blacklist_names.json","r")
    SPAMWORDS=json.load(file)["words"]
    file.close()

    file=open("_data/blacklist_ids.json","r")
    BLACKLIST=json.load(file)["ids"]
    file.close()

    for newUser in update.message.new_chat_members:
        if newUser.id in BLACKLIST:
            update.message.delete()
            banInAllGroups(newUser.id)
            logger.warning('%s|%s is banned from all groups because of blacklist',newUser.id,newUser.full_name,update.message.chat.title)
            return
        for SPAMWORD in SPAMWORDS:
            if SPAMWORD in newUser.full_name:
                update.message.delete()
                banInAllGroups(newUser.id)
                logger.warning('%s|%s is banned from all groups because of spam',newUser.id,newUser.full_name,update.message.chat.title)
                return


    groupid = update.message.chat_id
    if groupid in GROUPS and "puzzles" in GROUPS[groupid]:
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




def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CallbackQueryHandler(callbackhandler))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))#'''处理新成员加入'''
    dp.add_handler(MessageHandler(Filters.forwarded, forwardhandler))#'''处理转发消息'''
    #dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, onleft))#'''处理成员离开'''

    dp.add_handler(CommandHandler( [ "start" ], starthandler))
    dp.add_handler(CommandHandler( [ "replybanall" ], replybanallhandler))
    dp.add_handler(CommandHandler( [ "idbanall" ], idbanallhandler))
    dp.add_handler(CommandHandler( [ "fwdbanall" ], fwdbanallhandler))
    dp.add_handler(CommandHandler( [ "supervise" ], supervisehandler))

    # log all errors
    dp.add_error_handler(error)

    # periodical refresh
    updater.job_queue.run_repeating(refreshAdmins,interval=3600,first=0)



    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()




if __name__ == '__main__':
    logger.warning("%s(%s) starts watching",globalconfig.get("bot","name"),globalconfig.get("bot","token"))
    main()
