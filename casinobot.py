# -*- coding: utf-8 -*-
import requests
import os
import sys
import re
import logging
import json
import time
import codecs
import random
import configparser
from threading import Thread
import threading
from telegram import *
#KeyboardButton, ParseMode, ReplyKeyboardMarkup
from telegram.ext import *
from telegram.ext.dispatcher import run_async
# import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from selectBot import selectBot
from botsapi import bots
from koge48 import Koge48
from casino import LonghuCasino
from jsonfile import *

#reload(sys)  
#sys.setdefaultencoding('utf8')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.WARNING)
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logger = logging.getLogger(__name__)


BLACKLIST= set()
PRICES={"promote":50000,"restrict":500,"unrestrict":1000,"query":10}

SirIanM=420909210

BNB48CASINO=-1001319319354
BNB48CASINOLINK="https://t.me/joinchat/GRaQmk6jNzpHjsRCbRN8kg"
CASINO_IS_BETTING=False

kogeconfig = configparser.ConfigParser()
kogeconfig.read("conf/koge48.conf")
koge48core = Koge48(
  kogeconfig.get("mysql","host"),
  kogeconfig.get("mysql","user"),
  kogeconfig.get("mysql","passwd"),
  kogeconfig.get("mysql","database")
)


global_longhu_casinos = {}
CASINO_INTERVAL = 10

CASINO_MARKUP = None
CASINO_CONTINUE = True
CASINO_DIVIDING = False

USERINFOMAP = loadJson("_data/userinfomap.json",{})
def clearUserInfo(uid,key):
    realuid = str(uid)
    realkey=str(key)
    if realuid in USERINFOMAP and realkey in USERINFOMAP[realuid]:
        del  USERINFOMAP[realuid][realkey]
def userInfo(uid,key,value=None):
    realuid = str(uid)
    realkey=str(key)
    if value is None:
        if realuid in USERINFOMAP and realkey in USERINFOMAP[realuid]:
            return USERINFOMAP[realuid][realkey]
        else:
            return None
    else:
        if not realuid in USERINFOMAP:
            USERINFOMAP[realuid]={}
        USERINFOMAP[realuid][realkey] = value


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


SLOTICONS=["🍎","🍇","🍓","🍒","🍊","🍐","🍑","🎰","🍉","🍋"]

def slotDesc():
    res=""
    res+=(SLOTICONS[7]*3 + " ✖️250 + JackPot\n")
    res+=(SLOTICONS[3]*3 + " ✖️30\n")
    res+=(SLOTICONS[1]*3 + " ✖️30\n")
    res+=(SLOTICONS[2]*3 + " ✖️30\n")
    res+=(SLOTICONS[4]*3 + " ✖️30\n")
    res+=(SLOTICONS[5]*3 + " ✖️30\n")
    res+=(SLOTICONS[6]*3 + " ✖️30\n")
    res+=(SLOTICONS[8]*3 + " ✖️30\n")
    res+=(SLOTICONS[9]*3 + " ✖️30\n")
    res+=(SLOTICONS[0]*3 + " ✖️30\n")
    res+=(SLOTICONS[7]*2 + "🔲 ✖️20\n")
    res+=(SLOTICONS[7] + "🔲🔲 ✖️3")
    return res

def slotPlay():
    result = int(random.random()*1000)
    number = 0
    if result == 777:
        number = 250
    elif result%111 == 0:
        number = 30
    elif result//10 ==77:
        number = 20
    elif result//100 ==7:
        number = 3
    return (number,SLOTICONS[result//100]+SLOTICONS[result//10%10]+SLOTICONS[result%10])

def callbackhandler(bot,update):
    message_id = update.callback_query.message.message_id
    activeuser = update.callback_query.from_user
    logger.warning("{} callback, content: {}".format(activeuser.full_name,update.callback_query.data))
    if CASINO_CONTINUE and "SLOT#" in update.callback_query.data and not CASINO_DIVIDING:
        thedatas = update.callback_query.data.split('#')
        betsize=int(thedatas[1])
        bettimes = int(thedatas[2])
        playerbalance = koge48core.transferChequeBalance(activeuser.id,Koge48.BNB48BOT,betsize*bettimes,"{} bet SLOT on casino".format(activeuser.id))

        display = ""
        payout = 0
        totaljackpot = 0
        while bettimes > 0:
            bettimes -= 1
            slotresults = slotPlay()
            display += slotresults[1]
            if slotresults[0] > 0:
                display += " ✖️ {}".format(slotresults[0])
                payout += betsize*slotresults[0]
                if slotresults[0] == 250:
                    bot.sendMessage(BNB48CASINO,"{} \n{} ✖️{} \n/slot".format(slotresults[1],activeuser.full_name,slotresults[0]))
                    
                    jackpot = koge48core.getJackpot(activeuser.id,divideby=300/betsize)
                    if jackpot > 0:
                        playerbalance += jackpot
                        bot.sendMessage(BNB48CASINO,"{} 💰 JackPot :{} Koge".format(activeuser.full_name,jackpot))
                        display+=" 💰 JackPot :{} Koge".format(jackpot)
                        totaljackpot += jackpot

            display += "\n"

        if payout > 0:
            koge48core.transferChequeBalance(Koge48.BNB48BOT,activeuser.id,payout,"SLOT casino pay to {}".format(activeuser.full_name))
            playerbalance += payout

        display += "---\nWin {}, JackPot {}. Balance {} Koge".format(payout,totaljackpot,playerbalance)
        if totaljackpot > 0:
            update.callback_query.answer("---\nWin {}, JackPot {}. Balance {} Koge".format(payout,totaljackpot,playerbalance),show_alert=True)
        else:
            update.callback_query.answer()
        updater.bot.edit_message_caption(
                chat_id=update.callback_query.message.chat_id,
                message_id=message_id,
                caption = display,
                reply_markup=buildslotmarkup()
            )
    elif message_id in global_longhu_casinos and not CASINO_DIVIDING:
        casino_id = message_id
        thecasino = global_longhu_casinos[casino_id]

        if not "#" in update.callback_query.data:
            update.callback_query.answer()
            return

        thedatas = update.callback_query.data.split('#')
        bet_target = thedatas[0]
        if "ALLIN" == thedatas[1]:
            casino_betsize = koge48core.getChequeBalance(activeuser.id)
            if casino_betsize <= 0:
                update.callback_query.answer()
                return;
        else:
            casino_betsize = float(thedatas[1])

        if not CASINO_IS_BETTING :
            update.callback_query.answer()
            return

        bet_flag = False
        player_balance = 0
        if bet_target in ["LONG","HE","HU"]:
            player_balance = koge48core.transferChequeBalance(activeuser.id,Koge48.BNB48BOT,casino_betsize,"{} bet {} on casino".format(activeuser.id,bet_target))
            global_longhu_casinos[casino_id].bet(activeuser,bet_target,casino_betsize)
        elif bet_target == "LONGHU":
            player_balance = koge48core.transferChequeBalance(activeuser.id,Koge48.BNB48BOT,2*casino_betsize,"{} bet {} on casino".format(activeuser.id,bet_target))
            global_longhu_casinos[casino_id].bet(activeuser,"LONG",casino_betsize)
            global_longhu_casinos[casino_id].bet(activeuser,"HU",casino_betsize)
            '''
            elif bet_target == "LONGHUHE":
                koge48core.transferChequeBalance(activeuser.id,Koge48.BNB48BOT,2.04*casino_betsize,"{} bet {} on casino".format(activeuser.id,bet_target))
                global_longhu_casinos[casino_id].bet(activeuser,"LONG",casino_betsize)
                global_longhu_casinos[casino_id].bet(activeuser,"HU",casino_betsize)
                global_longhu_casinos[casino_id].bet(activeuser,"HE",casino_betsize/25)
            '''
        else:
            update.callback_query.answer()
            bot.deleteMessage(update.callback_query.message.chat_id, update.callback_query.message.message_id)
            return
        if not global_longhu_casinos[casino_id].needUpdate():
            global_longhu_casinos[casino_id].needUpdate(True)
            delayUpdateCasino(casino_id)

        update.callback_query.answer("👌 Balance: {} Koge".format(player_balance))
    else:
        update.callback_query.answer()


def delayUpdateCasino(casino_id):
    thread = Thread(target = actualUpdateCasino, args=[casino_id,])
    thread.start()

def actualUpdateCasino(casino_id):
    time.sleep(1)
    updater.bot.edit_message_text(
        text=LonghuCasino.getRule()+"\n---------------\n"+global_longhu_casinos[casino_id].getLog(),
        chat_id=BNB48CASINO,
        message_id=casino_id,
        reply_markup=CASINO_MARKUP,
    )
    global_longhu_casinos[casino_id].needUpdate(False)
def buildslotmarkup():
    keys = [
            [
                InlineKeyboardButton("10✖️1",callback_data="SLOT#10#1"),
                InlineKeyboardButton("10✖️10",callback_data="SLOT#10#10"),
                InlineKeyboardButton("10✖️100",callback_data="SLOT#10#100"),
            ],
            [
                InlineKeyboardButton("100✖️1",callback_data="SLOT#100#1"),
                InlineKeyboardButton("100✖️10",callback_data="SLOT#100#10"),
                InlineKeyboardButton("100✖️100",callback_data="SLOT#100#100"),
            ]
           ]
    return InlineKeyboardMarkup(keys)

def casinobuttons(number):
    #InlineKeyboardButton('{}'.format(number), callback_data='FULL'),
    res = []
    res.append(InlineKeyboardButton('🐲{}'.format(number), callback_data='LONG#{}'.format(number)))
    if number<5000:
        res.append(InlineKeyboardButton('🕊{}'.format(number), callback_data='HE#{}'.format(number)))
    res.append(InlineKeyboardButton('🐯{}'.format(number), callback_data='HU#{}'.format(number)))
    return res

def casinominings(number):
    return [
                [
                    InlineKeyboardButton('刷量:🐲🐯{}'.format(number), callback_data='LONGHU#{}'.format(number)),
                ],
            ]

    '''
    [
        InlineKeyboardButton('保险刷量:🐲🐯{}🕊{}'.format(number,number/25), callback_data='LONGHUHE#{}'.format(number))
    ]
    '''
def buildcasinomarkup(result=["",""]):
    global CASINO_MARKUP
    keys = []
    if result[0] != "":
        keys.append(
            [
                InlineKeyboardButton('🐲:'+result[0],callback_data="FULLLONG"),
                InlineKeyboardButton('🐯:'+result[1],callback_data="FULLHU")
            ]
        )
    else:
        keys.append(casinobuttons(50))
        keys.append(casinobuttons(250))
        keys.append(casinobuttons(1000))
        keys.append(casinobuttons(5000))
        keys.append(casinobuttons(20000))
        #keys+=casinominings(20000)
        '''
        for buttons in casinominings(1000):
            keys.append(buttons)
        for buttons in casinominings(20000):
            keys.append(buttons)
        keys.append(
            [
                InlineKeyboardButton(u'ALLIN:', callback_data='FULL'),
                InlineKeyboardButton(u'🐲', callback_data='LONG#ALLIN'),
                InlineKeyboardButton(u'🐯', callback_data='HU#ALLIN'),
                InlineKeyboardButton(u'🕊', callback_data='HE#ALLIN'),
            ]
        )
        '''
    CASINO_MARKUP = InlineKeyboardMarkup(keys)
    return CASINO_MARKUP
def buildtextmarkup(text):
    keys = [
            [
                InlineKeyboardButton(text,callback_data="TEXT")
            ]
           ]
    return InlineKeyboardMarkup(keys)
def startcasino():
    #logger.warning("try to start starting")
    if not CASINO_CONTINUE:
        return
    try:
        #message = updater.bot.sendPhoto(chat_id=BNB48CASINO, photo=open("longhu.jpg","rb"),caption=LonghuCasino.getRule()+"\n------------", reply_markup=buildcasinomarkup())
        #message = updater.bot.sendPhoto(chat_id=BNB48CASINO, photo="AgADBQADeqgxG14PyFYOh7ikQAIM-o-MAjMABAEAAwIAA3gAA8a7AAIWBA",caption=LonghuCasino.getRule()+"\n------------", reply_markup=buildcasinomarkup())
        #message = updater.bot.sendMessage(chat_id=BNB48CASINO, photo="AgADBQADfagxG14PyFarLTzZEpFimJOOAjMABAEAAwIAA3gAA1W4AAIWBA",text=LonghuCasino.getRule()+"\n------------", reply_markup=buildcasinomarkup())
        message = updater.bot.sendMessage(chat_id=BNB48CASINO, text=LonghuCasino.getRule()+"\n------------", reply_markup=buildcasinomarkup())
    except Exception as e:
        logger.warning(e)
        if not CASINO_CONTINUE:
            return
        thread = Thread(target = startcasino)
        time.sleep(CASINO_INTERVAL)
        thread.start()
        return
    #logger.warning("casino start")
    casino_id = message.message_id
    global_longhu_casinos[casino_id]=LonghuCasino()
    global CASINO_IS_BETTING
    CASINO_IS_BETTING=True
    thread = Thread(target = stopbetcasino, args=[casino_id])
    thread.start()

def stopbetcasino(casino_id):
    global CASINO_IS_BETTING
    time.sleep(CASINO_INTERVAL)
    thecasino = global_longhu_casinos[casino_id]
    while len(thecasino._bets["LONG"]) == 0 and len(thecasino._bets["HU"]) == 0 and len(thecasino._bets["HE"]) == 0:
        if CASINO_CONTINUE:
            time.sleep(CASINO_INTERVAL)
            continue
        elif not CASINO_CONTINUE and CASINO_IS_BETTING:
            CASINO_IS_BETTING = False
            time.sleep(1)
            continue
        elif not CASINO_CONTINUE and not CASINO_IS_BETTING:
            updater.bot.deleteMessage(BNB48CASINO,casino_id)
            updater.stop()
            updater.is_idle = False
            sys.exit()
            return
    

    #logger.warning("casino stop")
    CASINO_IS_BETTING=False
    thread = Thread(target = releaseandstartcasino, args=[casino_id])
    thread.start()
    
def releaseandstartcasino(casino_id):
    time.sleep(2)
    #logger.warning("casino release")
    thecasino = global_longhu_casinos[casino_id]
    #logger.warning("start releasing")
    results = thecasino.release()
    bigwin=False
    for each in results['payroll']:
        #if results['payroll'][each] > 200000:
        #    bigwin=True
        koge48core.transferChequeBalance(Koge48.BNB48BOT,each,results['payroll'][each],"casino pay to {}".format(each))

    displaytext = global_longhu_casinos[casino_id].getLog()
    del global_longhu_casinos[casino_id]

    try:
        #logger.warning(results['win'])
        updater.bot.edit_message_text(
            chat_id=BNB48CASINO,
            message_id=casino_id,
            text = displaytext,
            #disable_web_page_preview=False,
            reply_markup=buildcasinomarkup(result=results['result']),
            timeout=60
        )
        '''
        if bigwin:
            displaytext+="\n去[大赌场]("+BNB48CASINOLINK+")试试手气"
            updater.bot.sendMessage(BNB48CN,displaytext,parse_mode='Markdown',disable_web_page_preview=False)
            updater.bot.sendMessage(BNB48,displaytext,parse_mode='Markdown',disable_web_page_preview=False)
        '''
    except Exception as e:
        print(e)
        logger.warning("releaseandstartcasino exception above")
        pass

    thread = Thread(target=startcasino)
    thread.start()
    
def pmcommandhandler(bot,update):
    if update.message.chat.type != 'private':
        update.message.reply_text('该命令需私聊机器人')
        return

    things = update.message.text.split(' ')
    if "/start" in things[0]:
        update.message.reply_markdown("")

def rollerHandler(bot,update):
    #koge48core.transferChequeBalance(update.message.from_user.id,Koge48.BNB48BOT,PRICES['query'],'query roller')
    #text="本次查询费用由`{}`支付\n[点击进入KOGE虚拟赌场](https://t.me/joinchat/GRaQmk6jNzpHjsRCbRN8kg)\n\n".format(update.message.from_user.full_name)

    update.message.reply_markdown(rollerMarkDownGenerator(),quote=False,disable_web_page_preview=True)

def rollerMarkDownGenerator():
    text="JackPot {} Koge\n\n".format(round(koge48core.getChequeBalance(Koge48.JACKPOT),2))
    text+="累积奖池 {} Koge\n".format(round(koge48core.getChequeBalance(Koge48.PRIZEPOOL),2))
    text+="今日五大豪客(截至目前):\n".format(round(koge48core.getChequeBalance(Koge48.PRIZEPOOL),2))

    top3 = koge48core.getTotalBet(last=True)
    if len(top3) == 0:
        return ""
    prizepool = koge48core.getChequeBalance(Koge48.PRIZEPOOL)
    topaward=[]
    topaward.append(prizepool//3)
    topaward.append(prizepool//6)
    topaward.append(prizepool//12)
    awardicons=["🥇","🥈","🥉","",""]
    try:
        index = 0
        for each in top3:
            if index > 4:
                break
            fullname = userInfo(each[0],"FULLNAME")

            #text+="{} [{}](tg://user?id={})\t{}".format(awardicons[index],fullname,each[0],each[1])
            text+="{} [{}](tg://user?id={})\t{} Koge\n".format(awardicons[index],fullname,each[0],each[1])
            '''
            if index < 3:
                text += " {} Koge\n".format(min(round(topaward[index],2),each[1]))
            else:
                text += "\n"
            '''
            index += 1
    except:
        pass

    top10 = koge48core.getHisBetRecords(limit=10)
    text+="\n*历史累计下注榜(有分红)*:\n"
    for each in top10:
        fullname = userInfo(each[0],"FULLNAME")
        text+="{} Koge [{}](tg://user?id={})\n".format(round(each[1],1),fullname,each[0])


    top10 = koge48core.getTopGainer()
    text+="\n*赌神榜(净盈利)*:\n"
    for each in top10:
        fullname = userInfo(each[0],"FULLNAME")
        text+="{} Koge [{}](tg://user?id={})\n".format(round(each[1],1),fullname,each[0])

    text+= "\nHouse Balance:{}\n".format(koge48core.getChequeBalance(Koge48.BNB48BOT))
    '''
    changes=koge48core.getChequeRecentChanges(Koge48.BNB48BOT)
    text+= "小秘书最近的Koge变动记录:\n"
    for each in changes:
        text += "{}前,`{}`,{}\n".format(each['before'],each['number'],each['memo'])
    '''

    return text
    
def getusermd(user):
    #return "[`{}`](tg://user?id={})".format(user.full_name,user.id)
    return "`{}`".format(user.full_name)
def getkoge48md():
    return "[Koge](http://bnb48.club/html/cn/governance.html)"
def botcommandhandler(bot,update):
    things = update.message.text.split(' ')
    if "/slot" in things[0]:
        try:
            #bot.sendPhoto(update.message.from_user.id,photo=open("slot.jpg","rb"),caption=slotDesc(),reply_markup=buildslotmarkup(),quote=False)
            bot.sendPhoto(update.message.from_user.id,photo="AgADBQAD5agxGwFryFY9A1GWuRR3Gtt8-TIABAEAAwIAA3cAAxNSAgABFgQ",caption=slotDesc(),reply_markup=buildslotmarkup(),quote=False)
            #update.message.delete()
        except:
            #bot.sendPhoto(update.message.chat_id,photo=open("slot.jpg","rb"),caption=slotDesc(),reply_markup=buildslotmarkup(),quote=False)
            bot.sendPhoto(update.message.chat_id,photo="AgADBQAD5agxGwFryFY9A1GWuRR3Gtt8-TIABAEAAwIAA3cAAxNSAgABFgQ",caption=slotDesc(),reply_markup=buildslotmarkup(),quote=False)
    elif "/start" in things[0]:
        update.message.reply_text("1. 终身分红。每日下注总额的0.7%根据历史下注总额按比例向玩家分红(精确到小数点后两位)。\n2. 下注有奖。 每日下注总额的0.7%注入累积奖池。每日下注最多的前三名获得截止前一日累积奖池金额的 三分之一、六分之一、十二分之一，且不超过其当日已下注额。\n3. JackPot 每日下注总额的0.7%注入JackPot。老虎机单次下注100押中250倍可获得JackPot的三分之一，单次下注10押中250倍可获得三十分之一。\n 历史下注/每日下注/奖池金额等信息均可通过 /roller 命令查看")
    return
def cleanHandler(bot,update):
    if update.message.from_user.id == SirIanM:
        updater.job_queue.stop()
        for job in updater.job_queue.jobs():
            job.schedule_removal()
            if job.name in [ "dealAuction" ]:
                job.run(bot)
            logger.warning("job {} cleared".format(job.name))

        global CASINO_CONTINUE,CASINO_IS_BETTING
        CASINO_CONTINUE = False
        CASINO_IS_BETTING = False
        update.message.reply_text('cleaned')

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)



mytoken = selectBot(bots)
updater = Updater(token=mytoken, request_kwargs={'read_timeout': 30, 'connect_timeout': 15})
j = updater.job_queue



def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    #dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text and Filters.private, callback=botcommandhandler))#'''处理私聊文字'''
    #dp.add_handler(MessageHandler(Filters.photo & Filters.private, callback=photoHandler))#'''处理私发的图片'''
    dp.add_handler(CallbackQueryHandler(callbackhandler))
    #dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))#'''处理新成员加入'''
    #dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, onleft))#'''处理成员离开'''
    #dp.add_handler(MessageHandler(Filters.group & Filters.text & (~Filters.status_update),botmessagehandler))# '''处理大群中的直接消息'''
    #dp.add_handler(RegexHandler("^\w{64}\s*#\s*\w{64}$",apihandler))
    #dp.add_handler(RegexHandler("^0(X|x)\w{40}$",ethhandler))


    dp.add_handler(CommandHandler(["roller"],rollerHandler))
    '''
    dp.add_handler(CommandHandler(
        [
            "start",
        ],
        pmcommandhandler)#处理私聊机器人发送的命令
    )
    '''

    #dp.add_handler(CommandHandler(["auction"],auctionHandler)) 
    dp.add_handler(CommandHandler(
        [
            "slot",
            "start"
        ],
        botcommandhandler))# '''处理其他命令'''
    dp.add_handler(CommandHandler( [ "clean" ], cleanHandler))

    # log all errors
    dp.add_error_handler(error)


    #Start the schedule
    airdropinterval = 86400
    gap = airdropinterval - time.time()%airdropinterval
    rollergap = gap%43200
    logger.warning("will start airdrop in %s seconds",gap)
    logger.warning("will start roller in %s seconds",rollergap)
    job_airdrop = j.run_repeating(airdropportal,interval=airdropinterval,first=gap)
    job_airdrop = j.run_repeating(rollerbroadcast,interval=43200,first=rollergap)

    #casino
    startcasino()


    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()




def rollerbroadcast(bot,job):
    global USERINFOMAP
    USERINFOMAP = loadJson("_data/userinfomap.json",{})
    text = rollerMarkDownGenerator()
    if "" != text:
        announceid = bot.sendMessage(BNB48CASINO,rollerMarkDownGenerator(),parse_mode=ParseMode.MARKDOWN,disable_web_page_preview=True)

def airdropportal(bot,job):
    global CASINO_DIVIDING
    CASINO_DIVIDING = True
    try:
        file=open("_data/bnb48.list","r")
        bnb48list = json.load(file)
        file.close()
    except:
        logger.warning("loading bnb48.list exception")
        bnb48list = []

    Koge48.BNB48LIST = bnb48list

    lastbetrecords = koge48core.getTotalBet(last=True)
    lasttotalbet = 0

    for eachbet in lastbetrecords:
        lasttotalbet += eachbet[1]

    lasttotaldiv = lasttotalbet*0.9/100

    if lasttotaldiv > 0:

        try:
            prizepool = koge48core.getChequeBalance(Koge48.PRIZEPOOL)

            top1award = round(min(prizepool/3,lastbetrecords[0][1]),2)
            koge48core.transferChequeBalance(Koge48.PRIZEPOOL,lastbetrecords[0][0],top1award,"top1 award")
            updater.bot.sendMessage(BNB48CASINO,"豪客榜Top1 [{}](tg://user?id={}) 💰 {} Koge".format(userInfo(lastbetrecords[0][0],"FULLNAME"),lastbetrecords[0][0],top1award),parse_mode=ParseMode.MARKDOWN)

            top2award = round(min(prizepool/6,lastbetrecords[1][1]),2)
            koge48core.transferChequeBalance(Koge48.PRIZEPOOL,lastbetrecords[1][0],top2award,"top2 award")
            updater.bot.sendMessage(BNB48CASINO,"豪客榜Top2 [{}](tg://user?id={}) 💰 {} Koge".format(userInfo(lastbetrecords[1][0],"FULLNAME"),lastbetrecords[1][0],top2award),parse_mode=ParseMode.MARKDOWN)

            top3award = round(min(prizepool/12,lastbetrecords[2][1]),2)
            koge48core.transferChequeBalance(Koge48.PRIZEPOOL,lastbetrecords[2][0],top3award,"top3 award")
            updater.bot.sendMessage(BNB48CASINO,"豪客榜Top3 [{}](tg://user?id={}) 💰 {} Koge".format(userInfo(lastbetrecords[2][0],"FULLNAME"),lastbetrecords[2][0],top3award),parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(e)
            pass

        hisbet = float(koge48core.getTotalBet(last=False))
        betrecords = koge48core.getHisBetRecords()
        for eachrecord in betrecords:
            eachuid = eachrecord[0]
            try:
                dividend = round(float(lasttotaldiv*eachrecord[1]/hisbet),2)
                if dividend <=0:
                    continue
                koge48core.transferChequeBalance(Koge48.BNB48BOT,eachuid,dividend,"bet dividend distribution")
                logger.warning("distribute {} to {}".format(dividend,eachuid))
                updater.bot.sendMessage(eachuid,"💰 今日分红 {}KOGE".format(dividend))
            except:
                logger.warning("exception while distribute to {}".format(eachuid))

        logger.warning(" gambler dividend distributed")

        '''
        if len(bnb48list) < 2:
            centdiv = 0
        else:
            centdiv = round(lasttotaldiv/(len(bnb48list)-1),2)

        if centdiv > 0:
            for eachuid in bnb48list:
                if eachuid != str(Koge48.BNB48BOT):
                    try:
                        koge48core.transferChequeBalance(Koge48.BNB48BOT,eachuid,centdiv,"48core dividend distribution")
                        updater.bot.sendMessage(eachuid,"本区间您收到核心群人均分红{} KOGE".format(centdiv))
                    except:
                        logger.warning(eachuid)
                        logger.warning(centdiv)
                        pass
            logger.warning("48 dividend distributed")
        '''

        koge48core.transferChequeBalance(Koge48.BNB48BOT,Koge48.JACKPOT,lasttotaldiv,"deposit jackpot")
        koge48core.transferChequeBalance(Koge48.BNB48BOT,Koge48.PRIZEPOOL,lasttotaldiv,"deposit prizepool")
        #updater.bot.sendMessage(BNB48CASINO,"*Last Round*\nWager: {} Koge\nDividend distributed: {} Koge\nAdd to JackPot: {} KOGE\nCurrent JackPot: {} KOGE\nAdd to PrizePool: {} KOGE\nCurrent PrizePool: {} KOGE".format(lasttotalbet,lasttotaldiv,lasttotaldiv,round(koge48core.getChequeBalance(Koge48.JACKPOT),2),lasttotaldiv,round(koge48core.getChequeBalance(Koge48.PRIZEPOOL),2)),parse_mode=ParseMode.MARKDOWN)
        updater.bot.sendMessage(BNB48CASINO,"*今日*\n总下注: {} Koge\n今日分红: {} Koge\n注入JackPot: {} KOGE\nJackPot最新金额: {} KOGE\n注入每日豪客榜奖池: {} KOGE\n每日豪客榜奖池最新金额: {} KOGE".format(lasttotalbet,lasttotaldiv,lasttotaldiv,round(koge48core.getChequeBalance(Koge48.JACKPOT),2),lasttotaldiv,round(koge48core.getChequeBalance(Koge48.PRIZEPOOL),2)),parse_mode=ParseMode.MARKDOWN)

    CASINO_DIVIDING = False
    return
if __name__ == '__main__':
    
    main()

