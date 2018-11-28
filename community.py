#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
import codecs
import logging
import json
import time
import random
import ConfigParser
import thread
from telegram import *
from telegram.ext import *
from threading import Thread
from points import Points

reload(sys)  
sys.setdefaultencoding('utf8')


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


globalconfig = ConfigParser.ConfigParser()

# Read config
globalconfig.read(sys.argv[1])

# set bot conf
bottoken = globalconfig.get("bot","token")
botid=int(bottoken.split(":")[0])
botname = globalconfig.get("bot","name")

updater = Updater(token=bottoken, request_kwargs={'read_timeout': 30, 'connect_timeout': 10})

ALLGROUPS = {}
GROUPS = {}
GROUPADMINS = {}
CONFADMINS= [420909210]
DATAADMINS= [420909210]

pointscore= Points('_data/points.db')

def loadConfig(globalconfig,first=True):
    globalconfig.read(sys.argv[1])

    global bottoken
    global botid
    global botname
    global CONFADMINS
    global DATAADMINS
    global GROUPS
    global ALLGROUPS
    global GROUPADMINS
    global updater


    # read ADMINS
    if globalconfig.has_section("confadmins"):
        for confadmin in globalconfig.items("confadmins"):
            if not int(confadmin[0]) in CONFADMINS:
                CONFADMINS.append(int(confadmin[0]))
    if globalconfig.has_section("dataadmins"):
        for dataadmin in globalconfig.items("dataadmins"):
            if not int(dataadmin[0]) in DATAADMINS:
                DATAADMINS.append(int(dataadmin[0]))

    # parse groups info
    for groupinfo in globalconfig.items("groups"):
        groupid = int(groupinfo[0])
        if re.search("\.json$",groupinfo[1]) is None:
            ALLGROUPS[groupid]=groupinfo[1]
            if groupid in GROUPS:
                del GROUPS[groupid]
            logger.warning("doesn't watch %s",groupid)
            continue
        try:
            file=open(groupinfo[1],"r")
            puzzles = json.load(file)
            file.close()
        except Exception as error:
            ALLGROUPS[groupid]=groupinfo[1]
            if groupid in GROUPS:
                del GROUPS[groupid]
            print(error)
            logger.warning("doesn't watch %s",groupid)
            continue
        if first:
            GROUPS[groupid]=puzzles
            GROUPS[groupid]['lasthintid']=0
            GROUPS[groupid]['ENTRANCE_PROGRESS']={}
            GROUPS[groupid]['kickjobs'] = {}
        else:
            GROUPS[groupid].update(puzzles)
        ALLGROUPS[groupid]=GROUPS[groupid]['groupname']
        logger.warning("start watching %s",groupid)

def refreshAdmins(bot,job):
    global ALLGROUPS
    global GROUPADMINS
    logger.warning("start refreshing")
    for groupid in ALLGROUPS:
        GROUPADMINS[groupid]=getAdminsInThisGroup(groupid)
    logger.warning("admins refreshed")

def reportInAllGroups(userid,fullname):
    global DATAADMINS
    for adminid in DATAADMINS:
        updater.bot.sendMessage(
            adminid,
            "Someone reported [{}](tg://user?id={})".format(fullname,userid),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(
                        'Ban',
                        callback_data="banInAllGroups({},True)".format(userid))
                    ],
                    [InlineKeyboardButton(
                        'unban',
                        callback_data="banInAllGroups({},False)".format(userid))
                    ]
                ]
            ),
            parse_mode=ParseMode.MARKDOWN
        )

def banInAllGroups(userid,op=True):
    thread = Thread(target = actualBanInAllGroups, args=[userid,op])
    thread.start()

def actualBanInAllGroups(userid,op):
    try:
        file=open("_data/blacklist_ids.json","r")
        BLACKLIST=json.load(file)["ids"]
        file.close()
    except IOError:
        BLACKLIST=[]
    if op:
        if not userid in BLACKLIST:
            BLACKLIST.append(userid)
    else:
        if userid in BLACKLIST:
            BLACKLIST.remove(userid)

    BLACKLIST=list(set(BLACKLIST))

    file = codecs.open("_data/blacklist_ids.json","w","utf-8")
    file.write(json.dumps({"ids":BLACKLIST}))
    file.flush()
    file.close()
    logger.warning("blacklist_ids updated")

    global ALLGROUPS
    for groupid in ALLGROUPS:
        try:
            if op:
                ban(groupid,userid)
                logger.warning("{} banned in {}".format(userid,groupid))
            else:
                unban(groupid,userid)
                logger.warning("{} unbanned in {}".format(userid,groupid))
        except:
            pass

def ban(chatid,userid):
    updater.bot.kickChatMember(chatid,userid)
def unban(chatid,userid):
    updater.bot.unbanChatMember(chatid,userid)
def kick(chatid,userid):
    updater.bot.kickChatMember(chatid,userid)
    updater.bot.unbanChatMember(chatid,userid)
def watchdogkick(bot,job):
    logger.warning("%s(%s) is being kicked from %s",job.context['full_name'],job.context['userid'],job.context['groupid'])
    kick(job.context['groupid'],job.context['userid'])
    logger.warning("%s(%s) is kicked from %s",job.context['full_name'],job.context['userid'],job.context['groupid'])

def restrict(chatid,userid,minutes):
    updater.bot.restrictChatMember(chatid,user_id=userid,can_send_messages=False,until_date=time.time()+int(float(minutes)*60))

def unrestrict(chatid,userid):
    updater.bot.restrictChatMember(chatid,user_id=userid,can_send_messages=True,can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)

def callbackHandler(bot,update):
    global GROUPS
    if "banInAllGroups" in update.callback_query.data:
        eval(update.callback_query.data)
        update.callback_query.answer('Done')
        update.callback_query.message.reply_text('Done')
        update.callback_query.message.edit_reply_markup(text=update.callback_query.message.text)
        return
    if "reportInAllGroups" in update.callback_query.data:
        eval(update.callback_query.data)
        update.callback_query.answer('reported')
        update.callback_query.message.reply_text('reported')
        update.callback_query.message.edit_reply_markup(text=update.callback_query.message.text)
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
        update.callback_query.message.reply_text(GROUPS[groupid]['puzzles'][currentpuzzleindex]['postcorrect'])
        update.callback_query.message.edit_reply_markup(text=update.callback_query.message.text)
        

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
        update.callback_query.message.reply_text(GROUPS[groupid]['puzzles'][currentpuzzleindex]['postincorrect'])
        update.callback_query.message.edit_reply_markup(text=update.callback_query.message.text)
        update.callback_query.message.reply_text(GROUPS[groupid]['onfail'])
        del ENTRANCE_PROGRESS[activeuser.id]

    #update.callback_query.edit_message_text( text = lasttext)
            
def buildpuzzlemarkup(groupid,options):
    keys = []
    random.shuffle(options)
    for each in options:
        keys.append([InlineKeyboardButton(each[1],callback_data="{}#{}".format(groupid,each[0]))])
    return InlineKeyboardMarkup(keys)
    

def replybanallHandler(bot,update):
    if not isAdmin(update,False,True,True):
        return
    #ban(update.message.chat_id,update.message.reply_to_message.from_user.id)
    banInAllGroups(update.message.reply_to_message.from_user.id,True)
    update.message.reply_text("banned in all groups")

def idbanallHandler(bot,update):
    if not isAdmin(update,False,True,True):
        return
    things=update.message.text.split(" ")
    banInAllGroups(things[1],True)
    update.message.reply_text("banned in all groups")

def cleanHandler(bot,update):
    if isAdmin(update,False,True,False):
        updater.job_queue.stop()
        for job in updater.job_queue.jobs():
            job.schedule_removal()
            if job.name in [ "watchdogkick" ]:
                job.run(bot)
            logger.warning("job {} cleared".format(job.name))
        updater.stop()
        updater.is_idle = False
        os.exit()
def reloadHandler(bot,update):
    global DATAADMINS
    global globalconfig
    if not isAdmin(update,False,True,False):
        return
    if update.message.chat.type != 'private':
        return

    loadConfig(globalconfig)
    update.message.reply_text("reloaded")

def dataadminHandler(bot,update):
    global DATAADMINS
    global globalconfig
    targetuser = update.message.reply_to_message.from_user
    if not isAdmin(update,False,True,False):
        return
    if not targetuser.id in DATAADMINS:
        globalconfig.set("dataadmins",str(targetuser.id),targetuser.full_name)
        DATAADMINS.append(targetuser.id)
        with open(sys.argv[1], 'wb') as configfile:
            globalconfig.write(configfile)
        update.message.reply_text("{} is dataadmin now".format(targetuser.full_name))
    else:
        update.message.reply_text("was dataadmin before")
def superviseHandler(bot,update):
    if not isAdmin(update,False,True,False):
        return
    global globalconfig
    if not update.message.chat_id in ALLGROUPS:
        groupid = update.message.chat_id
        ALLGROUPS[groupid]=update.message.chat.title
        GROUPADMINS[groupid]=getAdminsInThisGroup(groupid)
        globalconfig.set("groups",str(update.message.chat_id),update.message.chat.title)
        with open(sys.argv[1], 'wb') as configfile:
            globalconfig.write(configfile)
        update.message.reply_text("supervised")
    else:
        update.message.reply_text("was supervised before")
def fwdbanallHandler(bot,update):
    if not isAdmin(update,False,True,True):
        return
    targetuser = update.message.reply_to_message.forward_from
    banInAllGroups(targetuser.id,True)
    update.message.reply_text("banned in all groups")

def getAdminsInThisGroup(groupid):
    admins = updater.bot.get_chat_administrators(groupid)
    RESULTS=[]
    for admin in admins:
        RESULTS.append(admin.user.id)
    return RESULTS

def isAdmin(update,GROUPTrue=True,CONFTrue=True,DATATrue=True):
    global GROUPADMINS
    userid = update.message.from_user.id
    if GROUPTrue and update.message.chat_id in GROUPADMINS and userid in GROUPADMINS[update.message.chat_id]:
        return True
    elif CONFTrue and userid in CONFADMINS:
        return True
    elif DATATrue and userid in DATAADMINS:
        return True
    else:
        return False
def fileHandler(bot,update):
    filename = update.message.document.file_name
    if globalconfig.has_section("blackfiletypes"):
        for item in globalconfig.items("blackfiletypes"):
            if item[0] in filename:
                banInAllGroups(update.message.from_user.id,True)
                break
    if not ".mp4" in update.message.document.file_name:
        update.message.delete()
def debugHandler(bot,update):
    chatmember = bot.getChatMember(update.message.chat_id,update.message.reply_to_message.from_user.id)
    update.message.reply_text(chatmember.status)
    update.message.reply_text(chatmember.until_date)
def startHandler(bot,update):
    
    #must in private mode
    if update.message.chat.type != 'private':
        return
    userid = update.message.from_user.id
    global GROUPS
    for groupid in GROUPS:
        try:
            chatmember = bot.getChatMember(groupid,userid)
            if chatmember.status != 'restricted':
                #if banned, no reentry
                continue
            elif chatmember.can_send_messages != False:
                # can send but just not that kind of
                continue
            elif not chatmember.until_date is None:
                # must be forever
                continue
            else:
                update.message.reply_text(GROUPS[groupid]['puzzles'][0]['question'],reply_markup=buildpuzzlemarkup(groupid,GROUPS[groupid]['puzzles'][0]['options']))
                GROUPS[groupid]['ENTRANCE_PROGRESS'][userid] = 0
                return
        except:
            continue
    update.message.reply_text("You've no new group test pending")
        
def cleanHandler(bot,update):
    if isAdmin(update,False,True,False):
        updater.job_queue.stop()
        for job in updater.job_queue.jobs():
            job.schedule_removal()
            job.run(bot)
            logger.warning("job {} cleared".format(job.name))
        updater.stop()
        updater.is_idle = False
        os.exit()
        update.message.reply_text('cleaned')
def forwardHandler(bot,update):
    global ALLGROUPS
    global GROUPADMINS
    fwduser = update.message.forward_from
    suspectScam = False
    if globalconfig.has_section("scamkeys"):
        for scamkey in globalconfig.items("scamkeys"):
            if not re.search(scamkey[0],str(fwduser.username),re.IGNORECASE) is None or not re.search(scamkey[0],fwduser.full_name,re.IGNORECASE) is None:
                logger.warning("{}/{} Hit scam key {}".format(fwduser.username,fwduser.full_name,scamkey))
                suspectScam = True
                break

    if update.message.chat.type == 'private' or suspectScam:
        #send in private 
        fwdisAdmin = False
        response=""
        for groupid in ALLGROUPS:
            if fwduser.id in GROUPADMINS[groupid]:
                fwdisAdmin = True
                response+="✅✅Admin in {}".format(ALLGROUPS[groupid])
                response+="\n"
        if fwdisAdmin:
            if update.message.chat.type == 'private':
                update.message.reply_text(response)
        else:
            if isAdmin(update,False,True,True):
                update.message.reply_text(
                    "‼️ Be careful, this guy is not an admin",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('Ban in all groups!',callback_data="banInAllGroups({},True)".format(fwduser.id))],
                        [InlineKeyboardButton('Unban in all groups!',callback_data="banInAllGroups({},False)".format(fwduser.id))]
                    ])
                )
            else:
                update.message.reply_text("‼️ Be careful, this guy is not an admin",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Report!',callback_data="reportInAllGroups({},'{}')".format(fwduser.id,fwduser.full_name))]]))
    
def textInGroupHandler(bot,update):
    if not isAdmin(update,True,False,False):
        pointscore.mine(update.message.from_user,update.message.chat_id)
def pointsHandler(bot,update):
    update.message.reply_text("💎{}".format(pointscore.getBalance(update.message.from_user.id,update.message.chat_id)))
def clearpointsHandler(bot,update):
    if not isAdmin(update,True,False,False):
        return
    pointscore.clearGroup(update.message.chat_id)
    update.message.reply_text("cleared")
def rankHandler(bot,update):
    if not isAdmin(update,True,False,False):
        return
    res=""
    for tuple in pointscore.getBoard(update.message.chat_id):
        res += "\n💎{}\t[{}](tg://user?id={})".format(tuple[3],tuple[1],tuple[0])
    if len(res) > 0:
        update.message.reply_markdown(res,quote=False)
def welcome(bot, update):
    global GROUPS
    
    try:
        file=open("_data/blacklist_names.json","r")
        SPAMWORDS=json.load(file)["words"]
        file.close()
    except IOError:
        SPAMWORDS=[]

    try:
        file=open("_data/blacklist_ids.json","r")
        BLACKLIST=json.load(file)["ids"]
        file.close()
    except IOError:
        BLACKLIST=[]

    for newUser in update.message.new_chat_members:
        if newUser.id in BLACKLIST:
            ban(update.message.chat_id,newUser.id)
            logger.warning('%s|%s is banned from %s because of blacklist',newUser.id,newUser.full_name,update.message.chat.title)
            return
        for SPAMWORD in SPAMWORDS:
            if SPAMWORD in newUser.full_name:
                banInAllGroups(newUser.id,True)
                logger.warning('%s|%s is banned from all groups because of spam',newUser.id,newUser.full_name)
                return


    groupid = update.message.chat_id
    if groupid in GROUPS and "puzzles" in GROUPS[groupid]:
        for newUser in update.message.new_chat_members:
            newChatMember = bot.getChatMember(groupid,newUser.id)
            logger.warning("%s(%s)Joined %s",newUser.full_name,newUser.id,update.message.chat.title)
            if 'restricted' in newChatMember.status and not newChatMember.until_date is None:
                # if muted before, do nothing
                continue
            restrict(update.message.chat_id,newUser.id,0.4)
            logger.warning("Muted")
            probation = GROUPS[groupid]['probation']
            GROUPS[groupid]['kickjobs'][newUser.id] = updater.job_queue.run_once(watchdogkick,probation*60,context = {"userid":newUser.id,"groupid":groupid,"full_name":newUser.full_name})
            logger.warning("%s minutes kicker timer started for %s in %s",GROUPS[groupid]['probation'],newUser.id,groupid)


            if GROUPS[groupid]['lasthintid'] != 0:
                try:
                    bot.deleteMessage(groupid,GROUPS[groupid]['lasthintid'])
                except:
                    logger.warning("deleting exception")

            GROUPS[groupid]['lasthintid'] = update.message.reply_text("{}: {}".format(GROUPS[groupid]['grouphint'],botname),quote=True).message_id


            try:
                bot.sendMessage(newUser.id,GROUPS[groupid]['onstart'],parse_mode=ParseMode.MARKDOWN)
            except:
                #pass
                logger.warning("send to %s(%s) failure",newUser.full_name,newUser.id)
            

    update.message.delete()
    

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)



class documentFilter(BaseFilter):
    def filter(self,message):
        if not message.document is None:
        #if message.animation is None and not message.document is None:
            return True
        else:
            return False

def main():
    """Start the bot."""
    loadConfig(globalconfig)
    logger.warning("%s(%s) starts watching",globalconfig.get("bot","name"),globalconfig.get("bot","token"))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram

    dp.add_handler(CommandHandler( [ "points" ], pointsHandler))
    dp.add_handler(CommandHandler( [ "rank" ], rankHandler))
    dp.add_handler(CommandHandler( [ "start" ], startHandler))
    dp.add_handler(CommandHandler( [ "debug" ], debugHandler))
    dp.add_handler(CommandHandler( [ "replybanall" ], replybanallHandler))
    dp.add_handler(CommandHandler( [ "idbanall" ], idbanallHandler))
    dp.add_handler(CommandHandler( [ "fwdbanall" ], fwdbanallHandler))
    dp.add_handler(CommandHandler( [ "supervise" ], superviseHandler))
    dp.add_handler(CommandHandler( [ "dataadmin" ], dataadminHandler))
    dp.add_handler(CommandHandler( [ "reload" ], reloadHandler))
    dp.add_handler(CommandHandler( [ "clean" ], cleanHandler))
    dp.add_handler(CommandHandler( [ "clearpoints" ], clearpointsHandler))

    dp.add_handler(CallbackQueryHandler(callbackHandler))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))#'''处理新成员加入'''
    dp.add_handler(MessageHandler(Filters.forwarded, forwardHandler))#'''处理转发消息'''
    dp.add_handler(MessageHandler(Filters.group, textInGroupHandler))#'''处理转发消息'''
    #dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, onleft))#'''处理成员离开'''
    dp.add_handler(MessageHandler(documentFilter(),fileHandler))#'''处理文件

    # log all errors
    dp.add_error_handler(error)

    # periodical refresh
    refreshAdmins(updater.bot,None)
    updater.job_queue.run_repeating(refreshAdmins,interval=3600,first=3600)



    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()




if __name__ == '__main__':
    main()
