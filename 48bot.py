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
import ConfigParser
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
from redpacket import RedPacket
from auction import Auction
from ppt2img import genPNG
from sendweibo import init_weibo, send_pic


reload(sys)  
sys.setdefaultencoding('utf8')


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.WARNING)
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logger = logging.getLogger(__name__)


BLACKLIST= set()
PRICES={"promote":50000,"restrict":500,"unrestrict":1000,"query":10}

file=open("_data/flushwords.json","r")
FLUSHWORDS = json.load(file)["words"]
file.close()

file=open("_data/blacklist_names.json","r")
SPAMWORDS=json.load(file)["words"]
file.close()

file=open("_data/silents.json","r")
SILENTGROUPS = json.load(file)['groups']
file.close()


SirIanM=420909210

BNB48=-1001136778297
BNB48PUBLISH=-1001180859399
BNB48CN= -1001345282090
BNB48C2C = -1001491897749

BNB48MEDIA=-1001180438510
BinanceCN=-1001136071376
BNB48CASINO=-1001319319354
BNB48CASINOLINK="https://t.me/joinchat/GRaQmk6jNzpHjsRCbRN8kg"
CASINO_IS_BETTING=False
SLOT_BETTING=True
#BNB48CASINO=SirIanM
#BNB48PUBLISH=SirIanM
BINANCE_ANNI = 1531526400
ENTRANCE_THRESHOLDS={BNB48:100000}
KICK_THRESHOLDS={BNB48:100000}
SAY_THRESHOLDS={BNB48:200000}
KICKINSUFFICIENT = {BNB48:True}
SAYINSUFFICIENT = {BNB48:False}

kogeconfig = ConfigParser.ConfigParser()
kogeconfig.read("conf/koge48.conf")
koge48core = Koge48(
  kogeconfig.get("mysql","host"),
  kogeconfig.get("mysql","user"),
  kogeconfig.get("mysql","passwd"),
  kogeconfig.get("mysql","database")
)


global_longhu_casinos = {}
global_redpackets = {}
global_auctions = {}
CASINO_INTERVAL = 7

CASINO_MARKUP = None
CASINO_CONTINUE = True

weiboclient = init_weibo('BNB48Club')

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


SLOTICONS=["🍎","🍇","🍓","🍒","🍊","🍐","🍑","🎰","🍉","🥭"]

def slotDesc():
    res="三列图标，每列随机出现10个图标中的一个，结果中出现如下组合(从第一列开始)可以获得不同倍数的奖金。"
    res+="当下注100Koge并转出250倍奖金时，额外获得奖池奖金， /jackpot 查看奖池规则"
    res+=(SLOTICONS[7]*3 + " 250倍\n")
    res+=(SLOTICONS[1]*3 + " 30倍\n")
    res+=(SLOTICONS[2]*3 + " 30倍\n")
    res+=(SLOTICONS[3]*3 + " 30倍\n")
    res+=(SLOTICONS[4]*3 + " 30倍\n")
    res+=(SLOTICONS[5]*3 + " 30倍\n")
    res+=(SLOTICONS[6]*3 + " 30倍\n")
    res+=(SLOTICONS[8]*3 + " 30倍\n")
    res+=(SLOTICONS[9]*3 + " 30倍\n")
    res+=(SLOTICONS[0]*3 + " 30倍\n")
    res+=(SLOTICONS[7]*2 + "  20倍\n")
    res+=(SLOTICONS[7] + "   3倍")
    return res

def slotPlay():
    result = int(random.random()*1000)
    number = 0
    if result == 777:
        number = 250
    elif result%111 == 0:
        number = 30
    elif result/10 ==77:
        number = 20
    elif result/100 ==7:
        number = 3
    return (number,SLOTICONS[result/100]+SLOTICONS[result/10%10]+SLOTICONS[result%10])

def callbackhandler(bot,update):
    message_id = update.callback_query.message.message_id
    activeuser = update.callback_query.from_user
    logger.warning("{} callback, content: {}".format(activeuser.full_name,update.callback_query.data))
    if "escrow" in update.callback_query.data:
        thedatas = update.callback_query.data.split('#')
        if thedatas[0] != "escrow":
            return
        if thedatas[1] == "confirm":
            if activeuser.id != float(thedatas[2]):
                update.callback_query.answer("只有发起者才能确认")
                return
            koge48core.transferChequeBalance(Koge48.BNB48BOT,int(thedatas[3]),float(thedatas[4]),"escrow confirm, from {} to {}".format(thedatas[2],thedatas[3]))
            update.callback_query.message.edit_reply_markup(reply_markup=buildtextmarkup('已确认'),timeout=60)
            update.callback_query.answer("{}已确认".format(activeuser.full_name))

        elif thedatas[1] == "cancel":
            if activeuser.id != float(thedatas[3]):
                update.callback_query.answer("只有接受者才能取消")
                return
            koge48core.transferChequeBalance(Koge48.BNB48BOT,int(thedatas[2]),float(thedatas[4]),"escrow cancel, from {} to {}".format(thedatas[2],thedatas[3]))
            update.callback_query.message.edit_reply_markup(reply_markup=buildtextmarkup('已取消'),timeout=60)
            update.callback_query.answer("{}已取消".format(activeuser.full_name))
            
    elif SLOT_BETTING and "SLOT#" in update.callback_query.data:
        thedatas = update.callback_query.data.split('#')

        betsize=int(thedatas[1])

        slotresults = slotPlay()

        koge48core.transferChequeBalance(activeuser.id,Koge48.BNB48BOT,betsize,"{} bet SLOT on casino".format(activeuser.id))

        display = slotresults[1]

        if slotresults[0] > 0:
            display += " 中{}倍".format(slotresults[0])
            koge48core.transferChequeBalance(Koge48.BNB48BOT,activeuser.id,betsize*slotresults[0],"SLOT casino pay to {}".format(activeuser.full_name))
            if slotresults[0] == 250:
                bot.sendMessage(BNB48CASINO,"{} \n {}在水果机转出{}倍奖金\n发送 /slot 试试手气".format(slotresults[1],activeuser.full_name,slotresults[0]))
                bot.sendMessage(activeuser.id,"{}倍奖金".format(slotresults[0]))

                if betsize >=100:
                    jackpot = koge48core.getJackpot(activeuser.id)
                    bot.sendMessage(BNB48CASINO,"{}从奖池拉下：{} Koge".format(activeuser.full_name,jackpot))
                    bot.sendMessage(BNB48CN,"{}从奖池拉下：{} Koge".format(activeuser.full_name,jackpot))
                    bot.sendMessage(BNB48,"{}从奖池拉下：{} Koge".format(activeuser.full_name,jackpot))
                    display+="获得奖池金额{} Koge".format(jackpot)

            update.callback_query.answer(display)
        else:
            update.callback_query.answer()

        updater.bot.edit_message_text(
                chat_id=update.callback_query.message.chat_id,
                message_id=message_id,
                text = display,
                reply_markup=buildslotmarkup()
            )


    elif message_id in global_redpackets:
        redpacket_id = message_id
        redpacket = global_redpackets[redpacket_id]
        thisdraw = redpacket.draw(activeuser)
        if thisdraw > 0:
            koge48core.transferChequeBalance(Koge48.BNB48BOT,activeuser.id,thisdraw,"collect redpacket from {}".format(redpacket._fromuser.full_name))
            update.callback_query.answer("你抢到{} Koge48积分".format(thisdraw))
            update.callback_query.edit_message_text(text=redpacket.getLog(),reply_markup=buildredpacketmarkup(),parse_mode=ParseMode.MARKDOWN,disable_web_page_preview=True)
            if redpacket.left() < 1:
                update.callback_query.message.edit_reply_markup(timeout=60)
                del global_redpackets[redpacket_id]
        elif thisdraw < 0:
            update.callback_query.message.edit_reply_markup(timeout=60)
            del global_redpackets[redpacket_id]
        else:
            update.callback_query.answer("每人只能领取一次")
    elif message_id in global_longhu_casinos:
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
            update.callback_query.answer("押注失败，已停止下注")
            return

        if bet_target in ["LONG","HE","HU"] and casino_id in global_longhu_casinos:
            koge48core.transferChequeBalance(activeuser.id,Koge48.BNB48BOT,casino_betsize,"{} bet {} on casino".format(activeuser.id,bet_target))
            global_longhu_casinos[casino_id].bet(activeuser,bet_target,casino_betsize)
            update.callback_query.edit_message_text(
                text=LonghuCasino.getRule()+"\n------------\n"+global_longhu_casinos[casino_id].getLog(),
                reply_markup=CASINO_MARKUP,
                parse_mode='Markdown'
            )
            update.callback_query.answer("押注成功")
        else:
            update.callback_query.answer("不存在的押注信息")
            bot.deleteMessage(update.callback_query.message.chat_id, update.callback_query.message.message_id)
    else:
        update.callback_query.answer()


def delayAnswer(query,content=None):
    thread = Thread(target = actualAnswer, args=[query,content])
    thread.start()
def actualAnswer(query,content=None):
    time.sleep(0.1)
    if content is None:
        query.answer()
    else:
        query.answer(text=content)
def buildredpacketmarkup():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('打开红包',callback_data="VOID")]
        ]
    )
def buildslotmarkup():
    keys = [
            [
                InlineKeyboardButton("10",callback_data="SLOT#10"),
                InlineKeyboardButton("20",callback_data="SLOT#20"),
                InlineKeyboardButton("50",callback_data="SLOT#50"),
                InlineKeyboardButton("100",callback_data="SLOT#100"),
            ]
           ]
    return InlineKeyboardMarkup(keys)

def casinobuttons(number):
    return [
                InlineKeyboardButton('{}:'.format(number), callback_data='FULL'),
                InlineKeyboardButton('🐲', callback_data='LONG#{}'.format(number)),
                InlineKeyboardButton('🐯', callback_data='HU#{}'.format(number)),
                InlineKeyboardButton('🕊', callback_data='HE#{}'.format(number))
            ]

def buildcasinomarkup(result=["",""]):
    global CASINO_MARKUP
    keys = [
            [
                InlineKeyboardButton(u'🐲:'+result[0],callback_data="FULLLONG"),
                InlineKeyboardButton(u'🐯:'+result[1],callback_data="FULLHU")
            ]
           ]
    if result[0] == "" :
        keys.append(casinobuttons(1000))
        keys.append(casinobuttons(5000))
        keys.append(casinobuttons(10000))
        keys.append(casinobuttons(20000))
        '''
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
    
def buildescrowmarkup(fromid,toid,transamount):
    keys = [
            [
                InlineKeyboardButton('✅',callback_data="escrow#confirm#{}#{}#{}".format(fromid,toid,transamount)),
                InlineKeyboardButton('❌',callback_data="escrow#cancel#{}#{}#{}".format(fromid,toid,transamount))
            ]
           ]
    return InlineKeyboardMarkup(keys)

def startcasino():
    #logger.warning("try to start starting")
    if not CASINO_CONTINUE:
        return
    try:
        message = updater.bot.sendMessage(BNB48CASINO, LonghuCasino.getRule()+"\n------------", reply_markup=buildcasinomarkup(),parse_mode="Markdown")
    except:
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
    time.sleep(3)
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
            parse_mode='Markdown',
            #disable_web_page_preview=False,
            reply_markup=buildcasinomarkup(result=results['result'])
        )
        if bigwin:
            displaytext+="\n去[大赌场]("+BNB48CASINOLINK+")试试手气"
            updater.bot.sendMessage(BNB48CN,displaytext,parse_mode='Markdown',disable_web_page_preview=False)
            updater.bot.sendMessage(BNB48,displaytext,parse_mode='Markdown',disable_web_page_preview=False)
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
    if "/mybinding" in things[0]:
        bindstatus = koge48core.getAirDropStatus(update.message.from_user.id)
        response = "当前绑定的ETH钱包地址:\n    {}\n\n".format(bindstatus['eth'])
        response +="当前绑定的币安APIkey(secret 不显示):\n    {}\n\n".format(bindstatus['api'][0])
        response +="末次快照BNB余额:\n    {}\n\n".format(bindstatus['bnb'][1])
        if len(bindstatus['airdrops']) >0 :
            response += "最近的空投记录:\n"
            for each in bindstatus['airdrops']:
                response += "    {}前 {} Koge48积分\n".format(each['before'],each['diff'])
        update.message.reply_text(response)
    elif "/send" in things[0] and len(things) >=3:
        if float(things[1]) <= 0:
            return
        if int(things[2]) <= 0:
            return
        user = update.message.from_user
        targetuserid = int(things[2])
        transamount = float(things[1])

        if not koge48core.getChequeBalance(user.id) > transamount:
            return
        koge48core.transferChequeBalance(user.id,targetuserid,transamount,"from {} send to {}".format(user.full_name,targetuserid))
        update.message.reply_markdown("{}向{}转账{} 永久{}".format(getusermd(user),targetuserid,transamount,getkoge48md()),disable_web_page_preview=True)
        '''
        elif "/redeem" in things[0]:
            change = koge48core.redeemCheque(update.message.from_user.id,things[1])
            if change > 0:
                update.message.reply_markdown("领取到{} {}".format(change,getkoge48md()),disable_web_page_preview=True)
            elif change == -1:
                update.message.reply_markdown("该奖励已被领取")
            elif change == 0:
                update.message.reply_markdown("不存在的奖励号码")
        '''
    elif "/changes" in things[0]:
        kogechanges=koge48core.getChequeRecentChanges(update.message.from_user.id)
        response = "最近的永久Koge变动记录:\n"
        for each in kogechanges:
            response += "        {}前,`{}`,{}\n".format(each['before'],each['number'],each['memo'])
        changes=koge48core.getRecentChanges(update.message.from_user.id)
        response = "+\n最近的活动变动记录:\n"
        for each in changes:
            response += "        {}前,`{}`,{}\n".format(each['before'],each['diff'],each['memo'])
        update.message.reply_markdown(response)
    elif "/start" in things[0] or "/join" in things[0]:
        if koge48core.getTotalBalance(update.message.from_user.id) >= ENTRANCE_THRESHOLDS[BNB48]:
            update.message.reply_markdown("欢迎加入[BNB48Club]({})".format(bot.exportChatInviteLink(BNB48)))
        else:
            update.message.reply_markdown("欢迎加入[BNB48Club](https://t.me/bnb48club_cn)")
    elif "/bind" in things[0]:
        update.message.reply_text(
            "持有1BNB，每天可以获得固定比例Koge48积分。\n\n所有绑定过程均需要私聊管家机器人完成，在群组内调用绑定命令是无效的。请注意，BNB48俱乐部是投资者自发组织的松散社群，BNB48俱乐部与币安交易所无任何经营往来，交易所账户的持仓快照是根据币安交易所公开的API实现的，管家机器人是开源社区开发的项目。俱乐部没有能力保证项目不存在Bug，没有能力确保服务器不遭受攻击，也没有能力约束开源项目参与者不滥用您提交的信息。\n\n您提交的所有信息均有可能被盗，进而导致您的全部资产被盗。\n\n如果您决定提交币安账户API，您承诺是在充分了解上述风险之后做出的决定。\n\n"+
            "输入apikey#apisecret绑定API\n"
        )
def groupadminhandler(bot,update):
    chatid = update.message.chat_id
    user = update.message.from_user
    admins = bot.get_chat_administrators(chatid)
    if not bot.getChatMember(chatid,user.id) in admins:
        update.message.reply_text("只有管理员可以调用")
        return
    if "mining" in update.message.text:
        top10 = koge48core.getGroupMiningStatus(chatid)
        text="过去一周(7\*24小时){}挖矿排行榜:\n".format(update.message.chat.title)
        for each in top10:
            text+="[{}](tg://user?id={})挖出{}个块\n".format(each[0],each[0],each[1])
        update.message.reply_markdown(text)
def richHandler(bot,update):
    top10 = koge48core.getTop(20)
    text="所有绑定API领KOGE空投的账户共计持有BNB {}\nKoge解锁部分(会衰减){}\nKoge永久部分(捐赠所得){}\nKoge富豪榜:\n".format(koge48core.getTotalBNB(),koge48core.getTotalFree(),koge48core.getTotalFrozen())
    for each in top10:
        text+="[{}](tg://user?id={})\t{}\n".format(each[0],each[0],each[1])
    update.message.reply_markdown(text,quote=False)
    
def donatorHandler(bot,update):
    top10 = koge48core.getTopDonator(20)
    text="捐赠发放的永久Koge总量:{}\n排行榜(隐去了具体金额):\n".format(koge48core.getTotalDonation())
    for each in top10:
        text+="[{}](tg://user?id={})\n".format(each[0],each[0])
    update.message.reply_markdown(text,quote=False)

def rollerHandler(bot,update):
    koge48core.transferChequeBalance(update.message.from_user.id,Koge48.BNB48BOT,PRICES['query'],'query roller')
    top20 = koge48core.getBetRecords(limit=20)
    text="本次查询费用由`{}`支付\n[点击进入KOGE虚拟赌场](https://t.me/joinchat/GRaQmk6jNzpHjsRCbRN8kg)\n\n".format(update.message.from_user.full_name)
    text+="赌场历史下注榜(豪客榜):\n"
    for each in top20:
        text+="[{}](tg://user?id={})\t{}\n".format(each[0],each[0],each[1])

    top10 = koge48core.getTopGainer()
    text+="赌神排行榜(净赢榜):\n"
    for each in top10:
        text+="[{}](tg://user?id={})\t{}\n".format(each[0],each[0],each[1])

    changes=koge48core.getChequeRecentChanges(Koge48.BNB48BOT)
    text+= "小秘书账户结余:{}\n".format(koge48core.getChequeBalance(Koge48.BNB48BOT))
    text+= "小秘书最近的变动记录:\n"
    for each in changes:
        text += "{}前,`{}`,{}\n".format(each['before'],each['number'],each['memo'])
    #update.message.reply_text(text=u"费用{}Koge48积分由{}支付".format(PRICES['query'],update.message.from_user.full_name))
    update.message.reply_markdown(text,quote=False,disable_web_page_preview=True)
    
def getusermd(user):
    #return "[`{}`](tg://user?id={})".format(user.full_name,user.id)
    return "`{}`".format(user.full_name)
def getkoge48md():
    return "[Koge48积分](http://bnb48.club/html/cn/governance.html)"
def siriancommandhandler(bot,update):
    global CASINO_CONTINUE
    if update.message.from_user.id != SirIanM:
        return
    things = update.message.text.split(' ')
    if not update.message.reply_to_message is None:
        targetuser = update.message.reply_to_message.from_user
    else:
        targetuser = None

    if "/kick" in things[0] and not targetuser is None:
        kick(update.message.chat_id,targetuser.id)
    elif "/kick" in things[0]:
        kick(long(things[1],long(things[2])))
    elif "/ban" in things[0] and not targetuser is None:
        ban(update.message.chat_id,targetuser.id)
    elif "/ban" in things[0]:
        ban(long(things[1],long(things[2])))
    elif "/kogebonus" in things[0] and len(things) >=2 and not update.message.reply_to_message is None:
        if float(things[1]) <= 0:
            return
        targetuser = update.message.reply_to_message.from_user
        transamount = float(things[1])

        #if not koge48core.getChequeBalance(Koge48.BNB48BOT) >= transamount:
        #    update.message.reply_text('小秘书永久Koge余额不足')
        #    return

        koge48core.transferChequeBalance(Koge48.BNB48BOT,targetuser.id,transamount,"Koge Bonus")
        update.message.reply_markdown("向{}发放{} 永久{}".format(getusermd(targetuser),transamount,getkoge48md()),disable_web_page_preview=True)
    elif "/unban" in things[0] and not targetuser is None:
        unban(update.message.chat_id,targetuser.id)
    elif "/unban" in things[0]:
        unban(long(things[1],long(things[2])))
    elif "/groupid" in things[0]:
        bot.sendMessage(SirIanM,"{}".format(update.message.chat_id))
    elif "/casino" in things[0] and update.message.from_user.id == SirIanM:
        CASINO_CONTINUE = True
        startcasino()
    elif "/flush" in things[0] or "/deflush" in things[0]:
        if update.message.from_user.id != SirIanM:
            return
            #SirIanM only
        thekeyword=""

        if "text" in dir(update.message.reply_to_message):
            thekeyword = update.message.reply_to_message.text
        else:
            thekeyword = things[1]

        if "/flush" in things[0]:
            if thekeyword in FLUSHWORDS:
                return
            FLUSHWORDS.append(thekeyword)
            bot.sendMessage(update.message.chat_id, text=u"增加\""+thekeyword+u"\"为刷屏关键词", reply_to_message_id=update.message.message_id)
        else:
            if not thekeyword in FLUSHWORDS:
                return
            FLUSHWORDS.remove(thekeyword)
            bot.sendMessage(update.message.chat_id, text=u"不再将\""+thekeyword+u"\"作为刷屏关键词", reply_to_message_id=update.message.message_id)

        file = codecs.open("_data/flushwords.json","w","utf-8")
        file.write(json.dumps({"words":FLUSHWORDS}))
        file.flush()
        file.close()
        logger.warning("flushwords updated")
    elif "/spam" in things[0] or "/despam" in things[0]:
        if update.message.from_user.id != SirIanM:
            return
            #SirIanM only
        thekeyword=""

        if "text" in dir(update.message.reply_to_message):
            thekeyword = update.message.reply_to_message.text
        else:
            thekeyword = things[1]

        if "/spam" in things[0]:
            if thekeyword in SPAMWORDS:
                return
            SPAMWORDS.append(thekeyword)
            bot.sendMessage(update.message.chat_id, text=u"增加\""+thekeyword+u"\"为垃圾账号关键词", reply_to_message_id=update.message.message_id)
        else:
            if not thekeyword in SPAMWORDS:
                return
            SPAMWORDS.remove(thekeyword)
            bot.sendMessage(update.message.chat_id, text=u"不再将\""+thekeyword+u"\"作为垃圾账号关键词", reply_to_message_id=update.message.message_id)

        file = codecs.open("_data/blacklist_name.json","w","utf-8")
        file.write(json.dumps({"words":SPAMWORDS}))
        file.flush()
        file.close()
        logger.warning("blacklist_name updated")

def botcommandhandler(bot,update):
    things = update.message.text.split(' ')

    if "/trans" in things[0] and len(things) >=2 and not update.message.reply_to_message is None:
        if float(things[1]) <= 0:
            return
        user = update.message.from_user
        targetuser = update.message.reply_to_message.from_user
        transamount = float(things[1])
        koge48core.transferChequeBalance(user.id,targetuser.id,transamount,"trans")
        update.message.reply_markdown("{}向{}转账{} 永久{}".format(getusermd(user),getusermd(targetuser),transamount,getkoge48md()),disable_web_page_preview=True)
    elif "/escrow" in things[0] and len(things) >=2 and not update.message.reply_to_message is None:
        if float(things[1]) <= 0:
            return
        if update.message.chat_id != BNB48C2C:
            update.message.reply_text("担保交易功能仅在场外交易群生效， /community 命令查看入群方式")
            return
        user = update.message.from_user
        targetuser = update.message.reply_to_message.from_user

        if targetuser.id == Koge48.BNB48BOT or targetuser.id == user.id:
            return
        transamount = float(things[1])
        koge48core.transferChequeBalance(user.id,Koge48.BNB48BOT,transamount,"escrow start, from {} to {}".format(user.id,targetuser.id))
        update.message.reply_markdown("{}向{}发起担保转账{}永久{}，由小秘书保管资金居间担保。\n发起者点击✅按钮，小秘书完成转账至接受者。\n接受者点击❌按钮，小秘书原路返还资金。\n如产生纠纷可请BNB48仲裁，如存在故意过错方，该过错方将终身无权参与BNB48一切活动。".format(getusermd(user),getusermd(targetuser),transamount,getkoge48md()),disable_web_page_preview=True,reply_markup=buildescrowmarkup(user.id,targetuser.id,transamount))
    elif "/slot" in things[0]:
        try:
            bot.sendMessage(update.message.from_user.id,text=slotDesc(),reply_markup=buildslotmarkup(),quote=False)
            #update.message.delete()
        except:
            update.message.reply_text(text=slotDesc(),reply_markup=buildslotmarkup(),quote=False)
    elif "/jackpot" in things[0]:
        update.message.reply_text(text="当前奖池余额为{}Koge 水果机 /slot 押100中250倍可拉下奖池的1/3".format(koge48core.getChequeBalance(Koge48.JACKPOT)))
            
    elif "/cheque" in things[0]:
        if SirIanM != update.message.from_user.id:
            return
        if len(things) != 2:
            update.message.reply_text("回复他人消息: /cheque 金额")
            return
        user = update.message.from_user
        
        number = float(things[1])
        targetuid = update.message.reply_to_message.from_user.id
        if number <= 0:
            update.message.reply_text("金额不合法")
            return

        latest = koge48core.signCheque(targetuid,number,"signed by SirIanM")
        update.message.reply_markdown("添加成功，目前最新余额{}".format(latest))
    elif "/community" in things[0]:
        markdown = "[BNB48 训练营](https://t.me/bnb48club_cn)"
        markdown += "\n"
        markdown += "[BNB48 Camp](https://t.me/bnb48club_en)"
        markdown += "\n"
        markdown += "[BNB48 公示](https://t.me/bnb48club_publish)"
        markdown += "\n"
        markdown+= "[BNB48 大赌场]("+BNB48CASINOLINK+")"
        markdown += "\n"
        markdown+= "[BNB48 场外交易](https://t.me/joinchat/GRaQmljsjZVAcaDOKqpAKQ)"
        if update.message.chat_id == BNB48:
            markdown += "\n"
            markdown+= "[BNB48 内部通知](https://t.me/joinchat/AAAAAFVOsQwKs4ev-pO2vg)"
            markdown += "\n"
            markdown+= "[BNB48 媒体宣传](https://t.me/joinchat/GRaQmkZcD-7Y4q83Nmyj4Q)"
            markdown += "\n"
            #markdown+= "[BNB48 技术开发](https://t.me/joinchat/GRaQmlISUPSpHFwVblxvxQ)"
            #markdown += "\n"
            #markdown+= "[BNB48 内部测试](https://t.me/joinchat/GRaQmlMuX_XdVSQgpxFT_g)"
            #markdown += "\n"
            markdown+= "[BNB48 孵化器](https://t.me/joinchat/GRaQmlWXCEJIJN3niyUUhg)"
            markdown += "\n"
            markdown+= "[BNB48 移民咨询](https://t.me/joinchat/GRaQmlAedWPaQFjyfoTDYg)"
            markdown += "\n"
            markdown+= "[BNB48 翻墙交流](https://t.me/joinchat/GRaQmkzYU3oJUphCcG4Y7Q)"
            markdown += "\n"
            markdown+= "[BNB48 离岸公司](https://t.me/joinchat/GRaQmlcgwROYjcmMbAu7NQ)"
        else:
            markdown += "\n"
            markdown += "更多群组仅对BNB48正式成员开放"
        update.message.reply_markdown(markdown,disable_web_page_preview=True)
    elif "/posttg" in things[0]:
        if update.message.chat_id != BNB48MEDIA:
            update.message.reply_text("该功能仅在BNB48 Media群内生效")
            return
        for group in [BNB48,BNB48PUBLISH]:
            #bot.forwardMessage(group,update.message.chat_id,update.message.reply_to_message.message_id)
            photoid = photo = update.message.reply_to_message.photo[-1].file_id
            bot.sendPhoto(group,photoid)
        update.message.reply_text("已转发")
    elif "/postweibo" in things[0]:
        if update.message.chat_id != BNB48MEDIA:
            update.message.reply_text("该功能仅在BNB48 Media群内生效")
            return
        if len(things) < 2:
            update.message.reply_text("必须提供发布标题")
            return
        del things[0]
        weibotitle = " ".join(things)
        photo = update.message.reply_to_message.photo[-1].get_file().download()
        weibourl = send_pic(weiboclient,photo,weibotitle)
        update.message.reply_text("已通过BNB48Club微博发送此条快讯: {}".format(weibourl))

    elif "/rapidnews" in things[0]:
        if update.message.chat_id != BNB48MEDIA:
            update.message.reply_text("该功能仅在BNB48 Media群内生效")
            return
        if len(things) < 3:
            update.message.reply_text("必须提供 标题 与 内容")
            return
        title = things[1]
        del things[0]
        del things[0]
        content = " ".join(things)
        update.message.reply_text("正在生成快讯图片...该操作较耗时也较耗费资源，请务必耐心，不要重复发送。")
        bot.sendPhoto(chat_id=update.message.chat_id,photo=open(genPNG(title,content), 'rb'),reply_to_message_id = update.message.message_id)
    elif "/criteria" in things[0]:
        update.message.reply_text("持仓Koge(永久+活动)大于等于{}可私聊机器人自助加入正式群\n持仓Koge不足{}会被移除出正式群".format(ENTRANCE_THRESHOLDS[BNB48],KICK_THRESHOLDS[BNB48],ENTRANCE_THRESHOLDS[BNB48]-KICK_THRESHOLDS[BNB48]));
    elif "/hongbao" in things[0] or "/redpacket" in things[0]:
        if update.message.chat.type == 'private':
            update.message.reply_text("需要在群内发送")
            return
        user = update.message.from_user

        if len(things) >1 and is_number(things[1]):
            balance = float(things[1])
        else:
            balance = 10

        if koge48core.getChequeBalance(user.id) < balance:
            update.message.reply_text("余额不足")
            return
        if balance <= 0:
            return


        if len(things) > 2 and is_number(things[2]):
            amount = int(things[2])
            if amount < 1:
                amount = 1
        else:
            amount = 10

        if amount > 10:
            update.message.reply_text("单个红包最多分成10份")
            return

        if balance/amount < 0.01:
            update.message.reply_text("单个红包平均应至少为0.01")
            return

        koge48core.transferChequeBalance(user.id,Koge48.BNB48BOT,balance,"send redpacket")
        
        if len(things) > 3:
            title = things[3]
        else:
            title = "恭喜发财"

        redpacket = RedPacket(update.message.from_user,balance,amount,title)
        message = update.message.reply_markdown(redpacket.getLog(),reply_markup=buildredpacketmarkup(),quote=False,disable_web_page_preview=True)
        redpacket_id = message.message_id
        global_redpackets[redpacket_id]=redpacket
        try:
            bot.deleteMessage(update.message.chat_id,update.message.message_id)
        except:
            pass

    elif "/bal" in things[0]:
        user = update.message.from_user

        if update.message.reply_to_message is None:
            targetuser = user
        else:
            targetuser = update.message.reply_to_message.from_user

        try:
            bot.sendMessage(user.id,"{}的{}永久余额为{}\n活动余额为{}".format(getusermd(targetuser),getkoge48md(),koge48core.getChequeBalance(targetuser.id),koge48core.getBalance(targetuser.id)),disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
        except:
            update.message.reply_text("为保护隐私，建议私聊机器人查询。{}的{}永久余额为{}\n活动余额为{}".format(getusermd(targetuser),getkoge48md(),koge48core.getChequeBalance(targetuser.id),koge48core.getBalance(targetuser.id)),disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)

    elif ("/unrestrict" in things[0] or "/restrict" in things[0] ) and not update.message.reply_to_message is None:
        
        user = update.message.from_user
        targetuser = update.message.reply_to_message.from_user


        if "/restrict" in things[0]:
            duration = 1
            if len(things) > 1 and is_number(things[1]):
                duration = things[1]
            restrict(bot,update,update.message.chat_id,user,targetuser,duration,update.message)

        elif "/unrestrict" in things[0]:
            unrestrict(bot,update,update.message.chat_id,user,targetuser,update.message)
    elif "/silent" in things[0] or "/desilent" in things[0]:
        if update.message.from_user.id != SirIanM:
            return
            #SirIanM only
        thegroup = update.message.chat_id
        if "/silent" in things[0]:
            if thegroup in SILENTGROUPS:
                return
            SILENTGROUPS.append(thegroup)
            bot.sendMessage(update.message.chat_id, text=u"本群切换为静默模式，出矿无消息提示", reply_to_message_id=update.message.message_id)
        else:
            if not thegroup in SILENTGROUPS:
                return
            SILENTGROUPS.remove(thegroup)
            bot.sendMessage(update.message.chat_id, text=u"本群解除静默模式", reply_to_message_id=update.message.message_id)

        file = codecs.open("_data/silents.json","w","utf-8")
        file.write(json.dumps({"groups":SILENTGROUPS}))
        file.flush()
        file.close()
        logger.warning("SILENTGROUPS updated")
    return
def cleanHandler(bot,update):
    if update.message.from_user.id == SirIanM:
        updater.job_queue.stop()
        for job in updater.job_queue.jobs():
            job.schedule_removal()
            if job.name in [ "dealAuction" ]:
                job.run(bot)
            logger.warning("job {} cleared".format(job.name))

        for each in global_redpackets:
            koge48core.transferChequeBalance(Koge48.BNB48BOT,each._fromuser.id,each.balance(),"redpacket return")       
        global CASINO_CONTINUE,CASINO_IS_BETTING,SLOT_BETTING
        CASINO_CONTINUE = False
        CASINO_IS_BETTING = False
        SLOT_BETTING = False

        update.message.reply_text('cleaned')
def ethhandler(bot,update):
    if update.message.chat_id != update.message.from_user.id:
        return
    eth = update.message.text
    ethrichlist=[]
    if eth in ethrichlist:
        update.message.reply_text("请不要拿链上富豪榜地址冒充，如果这个地址确实属于你，请私聊@SirIanM")
    else:
        koge48core.setEthAddress(update.message.from_user.id,eth)
        update.message.reply_text("eth绑定完成。请注意绑定过程不校验地址持仓BNB余额")


def apihandler(bot,update):
    if update.message.chat_id != update.message.from_user.id:
        return
    message_text = update.message.text
    api = message_text.split("#")
    koge48core.setApiKey(update.message.from_user.id,api[0],api[1])
    update.message.reply_text("apikey绑定完成，注意绑定过程不会验证api的有效性")
    return


BNBFAUCETLIST=[]
def bnbfaucetHandler(bot,update):
    words = update.message.text.split(' ')
    if len(words) != 2:
        update.message.reply_text("/bnbfaucettestnet <Your Address>")
        return
    address = words[1]
    if not re.search("^tbnb\w{39}$",address):
        update.message.reply_text("invalid address")
        return
    if address in BNBFAUCETLIST:
        update.message.reply_text("One application for each address")
    else:
        try:
            originout = os.popen("/home/ec2-user/sendBnb.sh {} 100 '100 BNB from FAUCET, BNB48 Club ®️'".format(address)).read()
            output = json.loads(originout)
            if 'code' in output and output['code'] != 0:
                update.message.reply_text(output['message'])
            else:
                update.message.reply_text("100 BNB Sent\nhttps://testnet-explorer.binance.org/tx/{}".format(output['TxHash']),disable_web_page_preview=True)
                BNBFAUCETLIST.append(address)
        except:
            update.message.reply_text(originout)

KOGEFAUCETLIST=[]
def kogefaucetHandler(bot,update):
    words = update.message.text.split(' ')
    if len(words) != 2:
        update.message.reply_text("/kogefaucettestnet <Your Address>")
        return
    address = words[1]
    if not re.search("^tbnb\w{39}$",address):
        update.message.reply_text("invalid address")
        return
    if address in KOGEFAUCETLIST:
        update.message.reply_text("One application for each address")
    else:
        try:
            originout = os.popen("/home/ec2-user/sendKoge.sh {} 1000 '1000 KOGE from FAUCET, BNB48 Club ®️'".format(address)).read()
            output = json.loads(originout)
            if 'code' in output and output['code'] != 0:
                update.message.reply_text(output['message'])
            else:
                update.message.reply_text("1000 KOGE Sent\nhttps://testnet-explorer.binance.org/tx/{}".format(output['TxHash']),disable_web_page_preview=True)
                KOGEFAUCETLIST.append(address)
        except:
            update.message.reply_text(originout)

def botmessagehandler(bot, update):
    if BNB48CASINO == update.message.chat_id:
        bot.deleteMessage(update.message.chat_id,update.message.message_id)
        return
    checkThresholds(update.message.chat_id,update.message.from_user.id)

    message_text = update.message.text
    #logger.warning(message_text)
    if "#SellBNBAt48BTC" in message_text:
        file=open("/var/www/html/sell48","r")
        content = json.load(file)
        response="目前48BTC挂单量为{}BNB".format(content['amt'])
        bot.sendMessage(update.message.chat_id, text=response, reply_to_message_id=update.message.message_id)
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
                restrict(bot, update,update.message.chat_id, None, update.message.from_user, 1, update.message)
                logger.warning(update.message.from_user.full_name+u" restricted because of " + update.message.text);
                return
        #mining
        user = update.message.from_user
        if len(update.message.text) > 5:
            mined=koge48core.mine(user.id,update.message.chat_id)
        else:
            mined = False
        if mined and not update.message.chat_id in SILENTGROUPS:
            update.message.reply_markdown("{}挖到{}个{}".format(getusermd(user),mined,getkoge48md()),disable_web_page_preview=True)


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
    sayingmember = bot.getChatMember(BNB48, userid)
    if sayingmember.status == 'restricted' or userid == SirIanM:
        forward = bot.forwardMessage(BNB48,update.effective_user.id,update.message.message_id)
        bot.sendMessage(update.message.chat_id, text=u"已提交持仓证明，请关注群内审批情况，耐心等待。如无必要，无需频繁重复发送。", reply_to_message_id=update.message.message_id)
        #给每名管理员私聊发送提醒
        admins = bot.getChatAdministrators(BNB48)
        for eachadmin in admins:
            try:
                bot.sendMessage(eachadmin.user.id, text=NOTIFYADMINS)
            except TelegramError:
                logger.warning('TelegramError, could be while send private message to admins')
                continue

    
def onleft(bot,update):
    for SPAMWORD in SPAMWORDS:
        if SPAMWORD in update.message.left_chat_member.full_name:
            bot.deleteMessage(update.message.chat_id,update.message.message_id)
    update.message.reply_markdown(text="`{}` 离开了本群".format(update.message.left_chat_member.full_name),quote=False)

def welcome(bot, update):
    if update.message.chat_id == BNB48:
        bot.exportChatInviteLink(BNB48)
    #筛选垃圾消息
    isSpam = False
    for newUser in update.message.new_chat_members:
        if  update.message.chat_id == BNB48CN and update.message.from_user.id != newUser.id and not newUser.is_bot and koge48core.getBalance(newUser.id) == 0 and koge48core.getChequeBalance(newUser.id) == 0:
            koge48core.transferChequeBalance(Koge48.BNB48BOT,newUser.id,Koge48.MINE_MIN_SIZE,"invited")
            koge48core.transferChequeBalance(Koge48.BNB48BOT,update.message.from_user.id,Koge48.MINE_MIN_SIZE,"inviting")
            update.message.reply_text("{}邀请{}，两人各挖到{}积分".format(update.message.from_user.full_name,newUser.full_name,Koge48.MINE_MIN_SIZE))
        for SPAMWORD in SPAMWORDS:
            if SPAMWORD in newUser.full_name:
                isSpam = True
                break;

    if isSpam:
        bot.deleteMessage(update.message.chat_id,update.message.message_id)
        for newUser in update.message.new_chat_members:
            bot.kickChatMember(update.message.chat_id,newUser.id)
            logger.warning('%s|%s is kicked from %s because of spam',newUser.id,newUser.full_name,update.message.chat.title)
            

def checkThresholds(chatid,userid):
    if not chatid in ENTRANCE_THRESHOLDS:
        return
    chatmember = updater.bot.getChatMember(chatid,userid)
    balance = koge48core.getTotalBalance(userid)
    if not chatmember.user.is_bot and chatmember.status in ['administrator','member','restricted']:
        if KICKINSUFFICIENT[chatid] and balance < KICK_THRESHOLDS[chatid]:
            try:
                kick(chatid,userid)
                #updater.bot.sendMessage(userid,"Koge持仓{}不足{}，被移除出群。".format(balance,KICK_THRESHOLDS[chatid]),disable_web_page_preview=True)
                updater.bot.sendMessage(chatid,"感觉{}Koge持仓{}不足{}，移除出群前看看对不对。".format(userid,balance,KICK_THRESHOLDS[chatid]),disable_web_page_preview=True)
                logger.warning("{}Koge持仓{}不足{}，被移除出群。".format(userid,balance,KICK_THRESHOLDS[chatid]))
                return True
            except:
                pass
            return
        if SAYINSUFFICIENT[chatid] and balance < SAY_THRESHOLDS[chatid]:
            try:
                updater.bot.sendMessage(userid,"Koge持仓不足{}，此消息将持续出现。不足{}将被移除出群。".format(SAY_THRESHOLDS[chatid],KICK_THRESHOLDS[chatid]),disable_web_page_preview=True)
            except:
                pass
        

def ban(chatid,userid):
    updater.bot.kickChatMember(chatid,userid)
def unban(chatid,userid):
    updater.bot.unbanChatMember(chatid,userid)
def kick(chatid,userid):
    if BNB48 == chatid:
        try:
            updater.bot.promoteChatMember(chatid, userid, can_change_info=False,can_delete_messages=False, can_invite_users=False, can_restrict_members=False, can_pin_messages=False, can_promote_members=False)
        except:
            pass
    updater.bot.kickChatMember(chatid,userid)
    updater.bot.unbanChatMember(chatid,userid)

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
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))#'''处理新成员加入'''
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, onleft))#'''处理成员离开'''
    dp.add_handler(MessageHandler(Filters.group & Filters.text & (~Filters.status_update),botmessagehandler))# '''处理大群中的直接消息'''
    dp.add_handler(RegexHandler("^\w{64}\s*#\s*\w{64}$",apihandler))
    #dp.add_handler(RegexHandler("^0(X|x)\w{40}$",ethhandler))


    dp.add_handler(CommandHandler(
        [
            "mining"
        ],
        groupadminhandler)#只对管理员账号的命令做出响应
    )
    dp.add_handler(CommandHandler(["rich"],richHandler))
    dp.add_handler(CommandHandler(["roller"],rollerHandler))
    dp.add_handler(CommandHandler(["donator"],donatorHandler))
    #dp.add_handler(CommandHandler(["kogefaucettestnet"],kogefaucetHandler))
    #dp.add_handler(CommandHandler(["bnbfaucettestnet"],bnbfaucetHandler))
    dp.add_handler(CommandHandler(
        [
            "casino",
            #"nocasino",
            "spam",
            "despam",
            "flush",
            "deflush",
            "kick",
            "ban",
            "unban",
            "groupid",
            #"slot",
            "kogebonus",
        ],
        siriancommandhandler)#
    )
    dp.add_handler(CommandHandler(
        [
            "mybinding",
            "bind",
            "redeem",
            "changes",
            #"kogechanges",
            "start",
            "send",
            #"slot",
            "join",
        ],
        pmcommandhandler)#处理私聊机器人发送的命令
    )

    #dp.add_handler(CommandHandler(["auction"],auctionHandler)) 
    dp.add_handler(CommandHandler(
        [
            "trans",
            #"kogetrans",
            "escrow",
            "bal",
            #"kogebal",
            #"promote",
            #"demote",
            #"restrict",
            #"unrestrict",
            "silent",
            "desilent",
            "hongbao",
            "redpacket",
            "criteria",
            "cheque",
            "community",
            "rapidnews",
            "posttg",
            "slot",
            "jackpot",
            "postweibo"
        ],
        botcommandhandler))# '''处理其他命令'''
    dp.add_handler(CommandHandler( [ "clean" ], cleanHandler))

    # log all errors
    dp.add_error_handler(error)


    #Start the schedule
    job_airdrop = j.run_repeating(airdropportal,interval=7200,first=0)
    #drop each 10 minutes,first time 5 minutes later, to avoid too frequent airdrop when debuging
    '''
    newthread = Thread(target = schedule_thread)
    newthread.start()
    '''

    startcasino()

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()




def airdropportal(bot,job):
    try:
        file=open("_data/bnb48.list","r")
        bnb48list = json.load(file)
        file.close()
    except:
        logger.warning("loading bnb48.list exception")
        bnb48list = []

    Koge48.BNB48LIST = bnb48list

    for eachuid in bnb48list:
        try:
            if checkThresholds(BNB48,eachuid):
                bnb48list.remove(eachuid)
        
        except Exception as e:
            print(e)
            print(eachuid)
            pass

    betrecords = koge48core.getBetRecords()
    lasttotalbet = float(koge48core.getTotalBet(last=True))
    lasttotaldiv = lasttotalbet/100

    if lasttotaldiv > 0:
        koge48core.transferChequeBalance(Koge48.BNB48BOT,Koge48.JACKPOT,lasttotaldiv,"jackpot")

        updater.bot.sendMessage(BNB48CASINO,"本区间小秘书接收到下注总额{} Koge, 向下注者返现{} Koge, 向核心群成员分红{} Koge, 向奖池注入{} KOGE, 奖池金额目前累计至{}Koge \n使用 /jackpot 命令查看奖池规则".format(lasttotalbet,lasttotaldiv,lasttotaldiv,lasttotaldiv,koge48core.getChequeBalance(Koge48.JACKPOT)))

        hisbet = float(koge48core.getTotalBet(last=False))
        for eachrecord in betrecords:
            eachuid = eachrecord[0]
            try:
                dividend = round(float(lasttotaldiv*eachrecord[1]/hisbet),2)
                if dividend < 0.01:
                    continue
                koge48core.transferChequeBalance(Koge48.BNB48BOT,eachuid,dividend,"bet dividend distribution")
                updater.bot.sendMessage(eachuid,"根据您历史下注{} Koge，占历史全部下注的{}%，本区间得到返利{} KOGE, /changes 查看变动详情, /roller 查看全局下注排行榜".format(eachrecord[1],round(100.0*eachrecord[1]/hisbet,2),dividend))
                logger.warning("distribute {} to {}".format(dividend,eachuid))
            except:
                logger.warning("exception while distribute to {}".format(eachuid))
                pass
        logger.warning(" gambler dividend distributed")


        if len(bnb48list) < 2:
            centdiv = 0
        else:
            centdiv = round(lasttotaldiv/(len(bnb48list)-1),2)

        if centdiv > 0:
            for eachuid in bnb48list:
                if eachuid != str(Koge48.BNB48BOT):
                    try:
                        koge48core.transferChequeBalance(Koge48.BNB48BOT,eachuid,centdiv,"48core dividend distribution")
                        updater.bot.sendMessage(eachuid,"本区间您收到核心群人均分红{} KOGE, /changes 查收".format(centdiv))
                    except:
                        logger.warning(eachuid)
                        logger.warning(centdiv)
                        pass
            logger.warning(" 48 dividend distributed")

    koge48core.KogeDecrease()
    koge48core.BNBAirDrop()
    return
if __name__ == '__main__':
    
    main()

