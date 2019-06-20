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
from collect48 import collectFrom
from ppt2img import genPNG
from sendweibo import init_weibo, send_pic


reload(sys)  
sys.setdefaultencoding('utf8')


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
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

BNB48MEDIA=-1001180438510
BinanceCN=-1001136071376
BNB48CASINO=-1001319319354
BNB48CASINOLINK="https://t.me/joinchat/GRaQmk6jNzpHjsRCbRN8kg"
CASINO_IS_BETTING=False
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
#casino_betsize = 2
CASINO_INTERVAL = 10

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

'''
def unrestrict(bot, update,chatid, user, targetuser, reply_to_message):
    admins = bot.get_chat_administrators(chatid)
    if reply_to_message is None:
        reply_to_id = None
    else:
        reply_to_id = reply_to_message.message_id 
    if user != None and not bot.getChatMember(chatid,user.id) in admins:
        reply_to_message.reply_text("No sufficient privilege")
        return
    if bot.getChatMember(chatid,targetuser.id) in admins:
        reply_to_message.reply_text("Don't need to unrestrict an admin")
        return
    price = PRICES['unrestrict']
    if koge48core.getBalance(user.id) < price:
        reply_to_message.reply_text("余额不足{} Koge48积分,即此次解禁的费用".format(price))
        return


    bot.restrictChatMember(chatid,user_id=targetuser.id,can_send_messages=True,can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
    koge48core.changeBalance(user.id,-price,"unrestrict {}".format(targetuser.full_name),targetuser.id)

    bot.sendMessage(chatid, text=u"{}解除禁言,费用{} Koge48积分由{}支付".format(targetuser.full_name,price,user.full_name), reply_to_message_id=reply_to_message.message_id)

    
def restrict(bot, update,chatid, user, targetuser, duration, reply_to_message):
    admins = bot.get_chat_administrators(chatid)
    if reply_to_message is None:
        reply_to_id = None
    else:
        reply_to_id = reply_to_message.message_id 
    #if user != None and not bot.getChatMember(chatid,user.id) in admins:
    #    bot.sendMessage(chatid, text=u"只有管理员可以禁言别人", reply_to_message_id=reply_to_id)
    #    return
    if bot.getChatMember(chatid,targetuser.id) in admins:
        bot.sendMessage(chatid, text=u"管理员不能被禁言", reply_to_message_id=reply_to_id)
        return
    price = PRICES['restrict']*float(duration)
    if user != None and koge48core.getBalance(user.id) < price:
        update.message.reply_text("余额不足{} Koge48积分,即此次禁言的费用".format(price))
        return
    if duration < 1:
        update.message.reply_text("至少禁言1分钟")
        return

    bot.restrictChatMember(chatid,user_id=targetuser.id,can_send_messages=False,until_date=time.time()+int(float(duration)*60))

    if user != None:
        koge48core.changeBalance(user.id,-price,"restrict {}".format(targetuser.full_name),targetuser.id)
        bot.sendMessage(chatid, text=u"{}被禁言{}分钟，费用{} Koge48积分由{}支付".format(targetuser.full_name,duration,price,user.full_name), reply_to_message_id=reply_to_id)
    else:
        bot.sendMessage(chatid, text=u"{}被禁言{}分钟".format(targetuser.full_name,duration), reply_to_message_id=reply_to_id)
'''

def dealAuction(bot,job):
    auction_id = job.context
    auction = global_auctions[auction_id]
    del global_auctions[auction_id]
    if not auction['bidder'] is None:
        koge48core.changeChequeBalance(auction['asker'].id,auction['price'],"auction {} income".format(auction_id))
        try:
            updater.bot.sendMessage(BNB48PUBLISH,"拍卖成交",reply_to_message_id=auction_id)
            updater.bot.sendMessage(auction['asker'].id,"您的拍卖 https://t.me/bnb48club_publish/{} 已成交。已入账{} Koge".format(auction_id,auction['price'])) 
            updater.bot.sendMessage(auction['bidder'].id,"您已在拍卖 https://t.me/bnb48club_publish/{} 中标。最终价格{} Koge".format(auction_id,auction['price'])) 
            updater.bot.editMessageReplyMarkup(BNB48PUBLISH,auction_id)
        except TelegramError:
            pass
    else:
        try:
            updater.bot.sendMessage(auction['asker'].id,"您的拍卖 https://t.me/bnb48club_publish/{} 已流拍。".format(auction_id))
            updater.bot.sendMessage(BNB48PUBLISH,"拍卖流拍",reply_to_message_id=auction_id)
            updater.bot.editMessageReplyMarkup(BNB48PUBLISH,auction_id)
        except TelegramError:
            pass


def slotPlay():
    SLOTICONS=["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","🎰","8️⃣","9️⃣"]
    result = int(random.random()*1000)
    number = 0
    if result == 777:
        number = 500
    elif result >=770 and result <=779:
        number = 20
    elif result >=700 and result <=799:
        number = 3
    return (number,SLOTICONS[result/100]+SLOTICONS[result/10%10]+SLOTICONS[result%10])

def callbackhandler(bot,update):
    message_id = update.callback_query.message.message_id
    activeuser = update.callback_query.from_user
    if "SLOT#" in update.callback_query.data:
        thedatas = update.callback_query.data.split('#')
        betsize=int(thedatas[1])
        koge48core.changeChequeBalance(activeuser.id,-betsize,"bet SLOT on casino")
        koge48core.changeChequeBalance(Koge48.BNB48BOT,betsize,"bet SLOT on casino",activeuser.id)

        slotresults = slotPlay()
        display = slotresults[1]

        if slotresults[0] > 0:
            display += " 中{}倍".format(slotresults[0])
            koge48core.changeChequeBalance(activeuser.id,betsize*slotresults[0],"casino pay to {}".format(activeuser.full_name,activeuser.id))
            if slotresults[0] > 3:
                bot.sendMessage(BNB48CN,"{} \n {}在老虎机转出{}倍奖金\n发送 /slot 试试手气".format(slotresults[1],activeuser.full_name,slotresults[0]))

        update.callback_query.answer(display)

        updater.bot.edit_message_text(
            chat_id=update.callback_query.message.chat_id,
            message_id=message_id,
            text = display,
            reply_markup=buildslotmarkup()
        )
            

    elif message_id in global_auctions:
    	auction_id = message_id
        auction = global_auctions[auction_id]
        newprice = int(update.callback_query.data)
        if newprice <= auction['price']:
            update.callback_query.answer("必须超过{}".format(auction['price']))
            return
        if activeuser.id == auction['asker'].id:
            update.callback_query.answer("不得竞拍自己发布的拍卖品")
            return
        if not auction['bidder'] is None and activeuser.id == auction['bidder'].id:
            update.callback_query.answer("不得对自己加价")
            return

        koge48core.changeChequeBalance(activeuser.id,-newprice,"auction {} bid".format(auction_id))
        if not auction['bidder'] is None:
            koge48core.changeChequeBalance(auction['bidder'].id,auction['price'],"auction {} beated".format(auction_id))
            try:
                bot.sendMessage(auction['bidder'].id,"你在[拍卖](https://t.me/bnb48club_publish/{}) 中的出价刚刚被 {} 超越".format(auction_id,activeuser.mention_markdown()),parse_mode=ParseMode.MARKDOWN)
            except TelegramError:
                pass
        auction['bidder']=activeuser
        auction['price']=newprice
        update.callback_query.edit_message_text(text=auctionTitle(auction),reply_markup=buildAuctionMarkup(newprice),parse_mode=ParseMode.MARKDOWN)
        update.callback_query.answer()

    elif message_id in global_redpackets:
        redpacket_id = message_id
        redpacket = global_redpackets[redpacket_id]
        thisdraw = redpacket.draw(activeuser)
        if thisdraw > 0:
            koge48core.changeChequeBalance(activeuser.id,thisdraw,"collect redpacket from {}".format(redpacket._fromuser.full_name),redpacket._fromuser.id)
            update.callback_query.answer(text=u"你抢到{} Koge48积分".format(thisdraw))
            update.callback_query.edit_message_text(text=redpacket.getLog(),reply_markup=buildredpacketmarkup(),parse_mode=ParseMode.MARKDOWN,disable_web_page_preview=True)
            if redpacket.left() < 1:
                update.callback_query.message.edit_reply_markup(timeout=60)
                del global_redpackets[redpacket_id]
        elif thisdraw < 0:
            update.callback_query.message.edit_reply_markup(timeout=60)
            del global_redpackets[redpacket_id]
        else:
            update.callback_query.answer("每人只能领取一次")
    elif CASINO_IS_BETTING and message_id in global_longhu_casinos:
        casino_id = message_id
        thecasino = global_longhu_casinos[casino_id]

        if not "#" in update.callback_query.data:
            #answer=LonghuCasino.getRule(update.callback_query.data) + "\n你的可用余额:{} 永久Koge48积分".format(koge48core.getChequeBalance(activeuser.id))
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

        if bet_target in ["LONG","HE","HU"] and casino_id in global_longhu_casinos:
            #if koge48core.getChequeBalance(activeuser.id) < casino_betsize:
            #    update.callback_query.answer(text=u"余额不足",show_alert=True)
            #    return
            koge48core.changeChequeBalance(activeuser.id,-casino_betsize,"bet {} on casino".format(bet_target))
            koge48core.changeChequeBalance(Koge48.BNB48BOT,casino_betsize,"{} bet {} on casino".format(activeuser.id,bet_target),activeuser.id)
            global_longhu_casinos[casino_id].bet(activeuser,bet_target,casino_betsize)
            #CASINO_LOG+=u"\n{} 押注 {} {} Koge48积分".format(activeuser.full_name,LonghuCasino.TARGET_TEXTS[bet_target],casino_betsize)
            update.callback_query.edit_message_text(
                text=LonghuCasino.getRule()+"\n------------\n"+global_longhu_casinos[casino_id].getLog(),
                reply_markup=CASINO_MARKUP,
                parse_mode='Markdown'
            )
            update.callback_query.answer(text=u"押注成功")
        else:
            update.callback_query.answer(text=u"不存在的押注信息")
            bot.deleteMessage(update.callback_query.message.chat_id, update.callback_query.message.message_id)
    else:
        update.callback_query.answer()

def buildAuctionMarkup(price):
    p1 = max(1,int(price*0.01))
    p10 = max(10,int(price*0.1))
    p100 = max(100,price)
    p1000 = max(1000,price*10)
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("+{}".format(p1),callback_data=str(price+p1)),InlineKeyboardButton('+{}'.format(p10),callback_data=str(price+p10))],
            [InlineKeyboardButton('+{}'.format(p100),callback_data=str(price+p100)), InlineKeyboardButton('+{}'.format(p1000),callback_data=str(price+p1000))]
        ]
    )
def buildredpacketmarkup():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('打开红包',callback_data="VOID")]
        ]
    )
def buildslotmarkup():
    keys = [
            [
                InlineKeyboardButton("押拾個KOGE",callback_data="SLOT#10"),
                InlineKeyboardButton("押壹佰KOGE",callback_data="SLOT#100")
            ]
           ]
    return InlineKeyboardMarkup(keys)

def buildcasinomarkup(result=["",""]):
    global CASINO_MARKUP
    keys = [
            [
                InlineKeyboardButton(u'🐲:'+result[0],callback_data="FULL"),
                InlineKeyboardButton(u'🐯:'+result[1],callback_data="FULL")
            ]
           ]
    if result[0] == "" :
        '''
        keys.append(
            [
                InlineKeyboardButton(u'押拾个:', callback_data='FULL'),
                InlineKeyboardButton(u'🐲', callback_data='LONG#10'),
                InlineKeyboardButton(u'🐯', callback_data='HU#10'),
                InlineKeyboardButton(u'🕊', callback_data='HE#10'),
            ]
        )
        '''
        keys.append(
            [
                InlineKeyboardButton(u'押壹佰:', callback_data='FULL'),
                InlineKeyboardButton(u'🐲', callback_data='LONG#100'),
                InlineKeyboardButton(u'🐯', callback_data='HU#100'),
                InlineKeyboardButton(u'🕊', callback_data='HE#100'),
            ]
        )
        keys.append(
            [
                InlineKeyboardButton(u'押壹仟:', callback_data='FULL'),
                InlineKeyboardButton(u'🐲', callback_data='LONG#1000'),
                InlineKeyboardButton(u'🐯', callback_data='HU#1000'),
                InlineKeyboardButton(u'🕊', callback_data='HE#1000'),
            ]
        )
        keys.append(
            [
                InlineKeyboardButton(u'押壹萬:', callback_data='FULL'),
                InlineKeyboardButton(u'🐲', callback_data='LONG#10000'),
                InlineKeyboardButton(u'🐯', callback_data='HU#10000'),
                InlineKeyboardButton(u'🕊', callback_data='HE#10000'),
            ]
        )
        '''
        keys.append(
            [
                InlineKeyboardButton(u'押拾万:', callback_data='FULL'),
                InlineKeyboardButton(u'🐲', callback_data='LONG#100000'),
                InlineKeyboardButton(u'🐯', callback_data='HU#100000'),
                InlineKeyboardButton(u'🕊', callback_data='HE#100000'),
            ]
        )
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


def startcasino(bot=None):
    #logger.warning("try to start starting")
    if not CASINO_CONTINUE:
        return
    try:
        message = updater.bot.sendMessage(BNB48CASINO, LonghuCasino.getRule()+"\n------------", reply_markup=buildcasinomarkup(),parse_mode="Markdown")
    except:
        if not CASINO_CONTINUE:
            return
        thread = Thread(target = startcasino)
        time.sleep(10)
        thread.start()
        return
    logger.warning("casino start")
    casino_id = message.message_id
    global_longhu_casinos[casino_id]=LonghuCasino()
    global CASINO_IS_BETTING
    CASINO_IS_BETTING=True
    thread = Thread(target = stopbetcasino, args=[casino_id])
    thread.start()

def stopbetcasino(casino_id):
    time.sleep(CASINO_INTERVAL)
    thecasino = global_longhu_casinos[casino_id]
    while len(thecasino._bets["LONG"]) == 0 and len(thecasino._bets["HU"]) == 0 and len(thecasino._bets["HE"]) == 0 and CASINO_CONTINUE:
        time.sleep(CASINO_INTERVAL)

    logger.warning("casino stop")
    global CASINO_IS_BETTING
    CASINO_IS_BETTING=False
    thread = Thread(target = releaseandstartcasino, args=[casino_id])
    thread.start()
    
def releaseandstartcasino(casino_id):
    logger.warning("casino release")
    time.sleep(2)
    thecasino = global_longhu_casinos[casino_id]
    #logger.warning("start releasing")
    results = thecasino.release()
    bigwin=False
    for each in results['payroll']:
        if results['payroll'][each] > 5000:
            bigwin=True
        koge48core.changeChequeBalance(each,results['payroll'][each],"casino pay")
        koge48core.changeChequeBalance(Koge48.BNB48BOT,-results['payroll'][each],"casino pay to {}".format(each),each)

    displaytext = global_longhu_casinos[casino_id].getLog()
    del global_longhu_casinos[casino_id]

    try:
        if bigwin:
            displaytext+="\n去[大赌场]("+BNB48CASINOLINK+")试试手气"
        #logger.warning(results['win'])
        updater.bot.edit_message_text(
            chat_id=BNB48CASINO,
            message_id=casino_id,
            text = displaytext,
            parse_mode='Markdown',
            reply_markup=buildcasinomarkup(result=results['result'])
        )
        if bigwin:
            updater.bot.forwardMessage(BNB48CN,BNB48CASINO,casino_id)
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
        response +="当前绑定的币安API:\n    {}#{}\n\n".format(bindstatus['api'][0],bindstatus['api'][1])
        response +="末次快照BNB余额:\n    链上(钱包里){}\n    链下(交易所){}\n\n".format(bindstatus['bnb'][0],bindstatus['bnb'][1])
        if len(bindstatus['airdrops']) >0 :
            response += "最近的空投记录:\n"
            for each in bindstatus['airdrops']:
                response += "    {}前 {} Koge48积分\n".format(each['before'],each['diff'])
        update.message.reply_text(response)
    elif "/slot" in things[0]:
        update.message.reply_text(text="随机转出三列图标，777赢500倍，77x赢20倍，7xx赢3倍",reply_markup=buildslotmarkup(),quote=False)
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
        koge48core.changeChequeBalance(user.id,-transamount,"send to {}".format(targetuserid),targetuserid)
        koge48core.changeChequeBalance(targetuserid,transamount,"trans from "+user.full_name,user.id)
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
    elif "/kogechanges" in things[0]:
        changes=koge48core.getChequeRecentChanges(update.message.from_user.id)
        response = "最近的永久Koge变动记录:\n"
        for each in changes:
            response += "        {}前,`{}`,{}\n".format(each['before'],each['number'],each['memo'])
        update.message.reply_markdown(response)
    elif "/changes" in things[0]:
        changes=koge48core.getRecentChanges(update.message.from_user.id)
        response = "最近的变动记录:\n"
        for each in changes:
            response += "        {}前,`{}`,{}\n".format(each['before'],each['diff'],each['memo'])
        update.message.reply_markdown(response)
    elif "/start" in things[0] or "/join" in things[0]:
        if koge48core.getTotalBalance(update.message.from_user.id) >= ENTRANCE_THRESHOLDS[BNB48]:
            #koge48core.changeBalance(update.message.from_user.id,(KICK_THRESHOLDS[BNB48]-ENTRANCE_THRESHOLDS[BNB48]),"join")
            #*int((time.time() - BINANCE_ANNI)/3600/24):
            update.message.reply_markdown("欢迎加入[BNB48Club]({})".format(bot.exportChatInviteLink(BNB48)))
        else:
            update.message.reply_markdown("欢迎加入[BNB48Club](https://t.me/bnb48club_cn)")
            #update.message.reply_markdown("从2018.7.14起，Koge持仓超过{}枚方可加入。输入 /bind 查看如何绑定BNB持仓领取Koge48.".format(ENTRANCE_THRESHOLDS[BNB48]))
    elif "/bind" in things[0]:
        update.message.reply_text(
            #"持有1BNB，每天可以获得1 Koge48积分。\n\n持仓快照来自两部分，链上与链下。链上部分可以通过机器人提交存放BNB的钱包地址进行绑定，链下部分可以通过机器人提交币安交易所账户API进行绑定。所有绑定过程均需要私聊管家机器人完成，在群组内调用绑定命令是无效的。\n\n持仓快照每天进行。\n\n请注意，BNB48俱乐部是投资者自发组织的松散社群，BNB48俱乐部与币安交易所无任何经营往来，交易所账户的持仓快照是根据币安交易所公开的API实现的，管家机器人是开源社区开发的项目。俱乐部没有能力保证项目不存在Bug，没有能力确保服务器不遭受攻击，也没有能力约束开源项目参与者不滥用您提交的信息。\n\n您提交的所有信息均有可能被盗，进而导致您的全部资产被盗。\n\n如果您决定提交ETH地址或币安账户API，您承诺是在充分了解上述风险之后做出的决定。\n\n"+
            "持有1BNB，每天可以获得固定比例Koge48积分。\n\n所有绑定过程均需要私聊管家机器人完成，在群组内调用绑定命令是无效的。请注意，BNB48俱乐部是投资者自发组织的松散社群，BNB48俱乐部与币安交易所无任何经营往来，交易所账户的持仓快照是根据币安交易所公开的API实现的，管家机器人是开源社区开发的项目。俱乐部没有能力保证项目不存在Bug，没有能力确保服务器不遭受攻击，也没有能力约束开源项目参与者不滥用您提交的信息。\n\n您提交的所有信息均有可能被盗，进而导致您的全部资产被盗。\n\n如果您决定提交币安账户API，您承诺是在充分了解上述风险之后做出的决定。\n\n"+
            "输入apikey#apisecret绑定API\n"
            #"绑定ETH钱包地址请直接输入\n"
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
    koge48core.changeChequeBalance(update.message.from_user.id,-PRICES['query'],'query roller')
    koge48core.changeChequeBalance(Koge48.BNB48BOT,PRICES['query'],'query roller')
    top10 = koge48core.getTopCasino()
    text="本次查询费用由`{}`支付\n[点击进入KOGE虚拟赌场](https://t.me/joinchat/GRaQmk6jNzpHjsRCbRN8kg)\n\n".format(update.message.from_user.full_name)
    text+="赌场豪客榜(下注榜):\n"
    for each in top10:
        text+="[{}](tg://user?id={})\t{}\n".format(each[0],each[0],each[1])

    top10 = koge48core.getTopProfiter()
    text+="赌神排行榜(盈利榜):\n"
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
    return "[Koge48积分](http://bnb48.club/koge48)"
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
    elif "/slot" in things[0]:
        update.message.reply_text(text="随机转出三列图标，777赢500倍，77x赢20倍，7xx赢3倍",reply_markup=buildslotmarkup(),quote=False)
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

        if not koge48core.getChequeBalance(Koge48.BNB48BOT) >= transamount:
            update.message.reply_text('小秘书永久Koge余额不足')
            return

        koge48core.changeChequeBalance(Koge48.BNB48BOT,-transamount,u"trans to "+targetuser.full_name,targetuser.id)
        latestbalance = koge48core.changeChequeBalance(targetuser.id,transamount,u"trans from BNB48Assistant",Koge48.BNB48BOT)
        update.message.reply_markdown("向{}发放{} 永久{}".format(getusermd(targetuser),transamount,getkoge48md()),disable_web_page_preview=True)
    elif "/unban" in things[0] and not targetuser is None:
        unban(update.message.chat_id,targetuser.id)
    elif "/unban" in things[0]:
        unban(long(things[1],long(things[2])))
    elif "/groupid" in things[0]:
        bot.sendMessage(SirIanM,"{}".format(update.message.chat_id))
    elif "/casino" in things[0] and update.message.from_user.id == SirIanM:
        CASINO_CONTINUE = True
        startcasino(bot)
    elif "/nocasino" in things[0] and update.message.from_user.id == SirIanM:
        CASINO_CONTINUE = False
        bot.sendMessage(update.message.chat_id, text="Casino stoped")
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

def auctionTitle(auction,first=False):
    if first:
        return "{} 拍卖 {} \n底价{}\n截止时间{}".format(
            auction['asker'].mention_markdown(),
            auction['title'],
            auction['base'],
            auction['end']
        )
    else:
        return "{} 拍卖 `{}` \n底价{}\n截止时间{}\n当前最高出价 {} By {}".format(
            auction['asker'].mention_markdown(),
            auction['title'],
            auction['base'],
            auction['end'],
            auction['price'],
            auction['bidder'].mention_markdown()
        )
def auctionHandler(bot,update):
    things = update.message.text.split(' ')
    if update.message.chat.type == 'private' and "/auction" in things[0] and len(things) >= 4:
        base = int(things[1])
        fee = max(base*0.03,100)
        asker = update.message.from_user
        if koge48core.getChequeBalance(asker.id) < fee:
            update.message.reply_text("发起拍卖需要一次性收取底价3%作为佣金，最低收费100Koge。您的余额不足")
            return
        else:
            koge48core.changeChequeBalance(asker.id,-fee,"auction fee",Koge48.BNB48BOT)
            koge48core.changeChequeBalance(Koge48.BNB48BOT,fee,"auction fee",asker.id)
        hours = float(things[2])
        seconds = int(hours*3600)
        del things[0]
        del things[0]
        del things[0]
        title = " ".join(things)
        auction = {
            "asker":asker,
            "base":base,
            "end":time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(time.time()+seconds)),
            "title":title,
            "bidder":None,
            "price":base
        }
        message = bot.sendMessage(BNB48PUBLISH,auctionTitle(auction,True),reply_markup=buildAuctionMarkup(base),parse_mode=ParseMode.MARKDOWN)
        global_auctions[message.message_id]=auction
        updater.job_queue.run_once(dealAuction,seconds,context=message.message_id)
        update.message.reply_text("拍卖成功发布 https://t.me/bnb48club_publish/{}".format(message.message_id))
    else:
        update.message.reply_text("命令格式：私聊我 发送 '/auction 底价 持续小时 商品描述'")
    
def botcommandhandler(bot,update):
    things = update.message.text.split(' ')

    '''
    if "/trans" in things[0] and len(things) >=2 and not update.message.reply_to_message is None:
        if float(things[1]) <= 0:
            return
        user = update.message.from_user
        targetuser = update.message.reply_to_message.from_user
        transamount = float(things[1])

        if not koge48core.getBalance(user.id) >= transamount:
            update.message.reply_text('活动Koge余额不足')
            return
        
        koge48core.changeBalance(user.id,-transamount,u"trans to "+targetuser.full_name,targetuser.id)
        latestbalance = koge48core.changeBalance(targetuser.id,transamount,u"trans from "+user.full_name,user.id)
        update.message.reply_markdown("{}向{}转账{} 活动{}".format(getusermd(user),getusermd(targetuser),transamount,getkoge48md()),disable_web_page_preview=True)
    '''
    if "/kogetrans" in things[0] and len(things) >=2 and not update.message.reply_to_message is None:
        if float(things[1]) <= 0:
            return
        user = update.message.from_user
        targetuser = update.message.reply_to_message.from_user
        transamount = float(things[1])

        if not koge48core.getChequeBalance(user.id) >= transamount:
            update.message.reply_text('永久Koge余额不足')
            return

        koge48core.changeChequeBalance(user.id,-transamount,u"trans to "+targetuser.full_name,targetuser.id)
        latestbalance = koge48core.changeChequeBalance(targetuser.id,transamount,u"trans from "+user.full_name,user.id)
        update.message.reply_markdown("{}向{}转账{} 永久{}".format(getusermd(user),getusermd(targetuser),transamount,getkoge48md()),disable_web_page_preview=True)
    elif "/slot" in things[0]:
        update.message.reply_text(text="随机转出三列图标，777赢500倍，77x赢20倍，7xx赢3倍",reply_markup=buildslotmarkup(),quote=False)
    elif "/cheque" in things[0]:
        if update.message.chat.type != 'private':
            return
        if SirIanM != update.message.from_user.id:
            return
        if len(things) != 3:
            update.message.reply_text("命令格式: /cheque 金额 UID")
            return
        user = update.message.from_user
        
        number = float(things[1])
        targetuid = int(things[2])
        if number <= 0:
            update.message.reply_text("金额不合法")
            return

        latest = koge48core.changeChequeBalance(targetuid,number,"signed by SirIanM")
        update.message.reply_markdown("添加成功，目前最新余额{}".format(latest))
    elif "/community" in things[0]:
        markdown = "[BNB48 训练营](https://t.me/bnb48club_cn)"
        markdown += "\n"
        markdown += "[BNB48 Camp](https://t.me/bnb48club_en)"
        markdown += "\n"
        markdown += "[BNB48 公示](https://t.me/bnb48club_publish)"
        markdown += "\n"
        markdown+= "[BNB48 大赌场]("+BNB48CASINOLINK+")"
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
            markdown+= "[BNB48 场外交易](https://t.me/joinchat/GRaQmljsjZVAcaDOKqpAKQ)"
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
            if amount > 100:
                amount = 100
        else:
            amount = 1

        if balance/amount < 0.01:
            update.message.reply_text("单个红包平均应至少为0.01")
            return

        koge48core.changeChequeBalance(user.id,-balance,"send redpacket")
        
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
            bot.sendMessage(user.id,"{}的{}活动余额为{}\n永久余额请使用 /kogebal 命令查看".format(getusermd(targetuser),getkoge48md(),koge48core.getBalance(targetuser.id)),disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
        except:
            update.message.reply_text("为保护隐私，建议私聊机器人查询。{}的{}活动余额为{}\n永久余额请使用 /kogebal 命令查看".format(getusermd(targetuser),getkoge48md(),koge48core.getBalance(targetuser.id)),disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
            pass
        update.message.delete()
    elif "/kogebal" in things[0]:
        user = update.message.from_user

        if update.message.reply_to_message is None:
            targetuser = user
        else:
            targetuser = update.message.reply_to_message.from_user

        try:
            bot.sendMessage(user.id,"{}的{}永久余额为{}\n活动余额请使用 /bal 命令查看".format(getusermd(targetuser),getkoge48md(),koge48core.getChequeBalance(targetuser.id)),disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
        except:
            update.message.reply_text("为保护隐私，建议私聊机器人查询。{}的{}永久余额为{}\n活动余额请使用 /bal 命令查看".format(getusermd(targetuser),getkoge48md(),koge48core.getChequeBalance(targetuser.id)),disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
            pass
        update.message.delete()
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
        ''' 
        elif ("/ban" in things[0] or "/kick" in things[0] ) and "from_user" in  dir(update.message.reply_to_message):
        if update.message.from_user.id != SirIanM:
            return
        try:
            bot.kickChatMember(update.message.chat_id,user_id=targetid)
        except:
            logger.warning("except when kicking")
        if "/kick" in things[0]:
            bot.unbanChatMember(update.message.chat_id,user_id=targetid)
        bot.sendMessage(update.message.chat_id, text=u"[{}](tg://user?id={}) is {}".format(update.message.reply_to_message.from_user.full_name,targetid,things[0]+"ed"), reply_to_message_id=update.message.message_id,parse_mode=ParseMode.MARKDOWN)

    elif ("/promote" in things[0] or "/demote" in things[0]) and not update.message.reply_to_message is None:
        if koge48core.getBalance(update.message.from_user.id) < PRICES['promote']:
            bot.sendMessage(update.message.chat_id, text="管理员晋升/解除需要花费{} Koge48积分,再去赚点儿钱吧".format(PRICES['promote']), reply_to_message_id=update.message.message_id)
            return

        targetuser = update.message.reply_to_message.from_user
        targetid = update.message.reply_to_message.from_user.id

        if "/promote" in things[0]:
            bot.promoteChatMember(update.message.chat_id, targetid,can_delete_messages=False,can_pin_messages=True)
            koge48core.changeBalance(update.message.from_user.id,-PRICES['promote'],'promote {}'.format(targetuser.full_name),targetid)
            bot.sendMessage(update.message.chat_id, text=u"{}晋升为管理员\n{} Koge48积分费用由{}支付".format(update.message.reply_to_message.from_user.full_name,PRICES['promote'],update.message.from_user.full_name), reply_to_message_id=update.message.message_id)
        if "/demote" in things[0]:
            bot.promoteChatMember(update.message.chat_id, targetid, can_change_info=False,can_delete_messages=False, can_invite_users=False, can_restrict_members=False, can_pin_messages=False, can_promote_members=False)
            koge48core.changeBalance(update.message.from_user.id,-PRICES['promote'],'demote {}'.format(targetuser.full_name),targetid)
            bot.sendMessage(update.message.chat_id, text=u"{}被革去管理员职位\n{} Koge48积分费用由{}支付".format(update.message.reply_to_message.from_user.full_name,PRICES['promote'],update.message.from_user.full_name), reply_to_message_id=update.message.message_id)

    ''' 
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
def chequehandler(bot,update):
    if update.message.chat.type != 'private':
        return
    result= koge48core.queryCheque(update.message.text)
    update.message.reply_markdown(result)
def cleanHandler(bot,update):
    if update.message.from_user.id == SirIanM:
        updater.job_queue.stop()
        for job in updater.job_queue.jobs():
            job.schedule_removal()
            if job.name in [ "dealAuction" ]:
                job.run(bot)
            logger.warning("job {} cleared".format(job.name))
        updater.stop()
        updater.is_idle = False
        os.exit()

        for each in global_redpackets:
            koge48core.changeChequeBalance(each._fromuser.id,each.balance(),"redpacket return")       

        CASINO_CONTINUE = False
        CASINO_IS_BETTING = False

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
        mined=koge48core.mine(user.id,update.message.chat_id)
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
                print('TelegramError, could be while send private message to admins')
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
            koge48core.changeChequeBalance(newUser.id,Koge48.MINE_MIN_SIZE,"invited",update.message.from_user.id)
            koge48core.changeChequeBalance(update.message.from_user.id,Koge48.MINE_MIN_SIZE,"inviting",newUser.id)
            koge48core.changeChequeBalance(Koge48.BNB48BOT,-2*Koge48.MINE_MIN_SIZE,"inviting",newUser.id)
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
            "nocasino",
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
            "kogechanges",
            "start",
            "send",
            #"slot",
            "join",
        ],
        pmcommandhandler)#处理私聊机器人发送的命令
    )

    dp.add_handler(CommandHandler(["auction"],auctionHandler)) 
    dp.add_handler(CommandHandler(
        [
            "trans",
            "kogetrans",
            "bal",
            "kogebal",
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
            "postweibo"
        ],
        botcommandhandler))# '''处理其他命令'''
    dp.add_handler(CommandHandler( [ "clean" ], cleanHandler))

    # log all errors
    dp.add_error_handler(error)


    #Start the schedule
    job_airdrop = j.run_repeating(airdropportal,interval=7200,first=5)
    #drop each 10 minutes,first time 5 minutes later, to avoid too frequent airdrop when debuging
    '''
    newthread = Thread(target = schedule_thread)
    newthread.start()
    '''

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



def airdropportal(bot,job):
    try:
        file=open("_data/bnb48cn.list","r")
        bnb48cnlist = json.load(file)
        file.close()
    except:
        logger.warning("loading bnb48cn.list exception")
        bnb48cnlist = []
    try:
        file=open("_data/bnb48.list","r")
        bnb48list = json.load(file)
        file.close()
    except:
        logger.warning("loading bnb48.list exception")
        bnb48list = []
    for eachuid in bnb48cnlist:
        try:
            checkThresholds(BNB48CN,eachuid)
        except Exception as e:
            print(e)
            print(eachuid)
            pass
    for eachuid in bnb48list:
        try:
            checkThresholds(BNB48,eachuid)
        except Exception as e:
            print(e)
            print(eachuid)
            pass

    koge48core.KogeDecrease()
    koge48core.BNBAirDrop()
    return
if __name__ == '__main__':
    
    main()

