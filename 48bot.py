# -*- coding: utf-8 -*-
import requests
import os
import sys
import math
import re
import logging
import json
from datetime import datetime
import time
import codecs
import random
import configparser
import operator
from threading import Thread
import threading
from telegram import *
from bnb48locales import * #getLocaleString,BNB48_LOCALES
#KeyboardButton, ParseMode, ReplyKeyboardMarkup
from telegram.ext import *
from telegram.ext.dispatcher import run_async
# import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from selectBot import selectBot
from jsonfile import *
from botsapi import bots
from koge48 import Koge48
from redpacket import RedPacket
from election import Election
#from sendweibo import init_weibo, send_pic


#reload(sys)  
#sys.setdefaultencoding('utf8')

def getLang(user):
    if (not user.language_code is None) and "zh" in user.language_code:
        return "CN"
    else:
        return "EN"
def getAdminsInThisGroup(groupid):
    try:
        admins = updater.bot.get_chat_administrators(groupid)
    except:
        admins = []
    RESULTS=[]
    for admin in admins:
        RESULTS.append(admin.user.id)
    return RESULTS

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.WARNING)
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logger = logging.getLogger(__name__)


KOGEMULTIPLIER = 100000000
BLACKLIST= set()
PRICES={"promote":50000,"restrict":500,"unrestrict":1000,"query":10}

FLUSHWORDS = loadJson("_data/flushwords.json",{})["words"]
SPAMWORDS=loadJson("_data/blacklist_names.json",{})["words"]
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
    
ESCROWLIST = loadJson("_data/escrowlist.json",{})

SirIanM=420909210

BNB48PLATINUMCN=-1001136778297
BNB48PLATINUMEN=-1001314822059
EARLYBIRD=-4801
BNB48PUBLISH=-1001180859399
BNB48TEST =-1001395548149
BNB48CN= -1001345282090
BNB48EN= -1001377752898
BNB48C2C = -1001491897749
BNB48MEDIA=-1001180438510
BinanceCN=-1001136071376
BNB48C2CLINK="https://t.me/joinchat/GRaQmljsjZVAcaDOKqpAKQ"
#BNB48PUBLISH=SirIanM
BINANCE_ANNI = 1531526400

ENTRANCE_THRESHOLDS={BNB48PLATINUMCN:1000,BNB48PLATINUMEN:1000}
KICK_THRESHOLDS={BNB48PLATINUMCN:400,BNB48PLATINUMEN:400}
SAY_THRESHOLDS={BNB48PLATINUMCN:800,BNB48PLATINUMEN:400}
KICKINSUFFICIENT = {BNB48PLATINUMCN:True}
SAYINSUFFICIENT = {BNB48PLATINUMCN:False}

kogeconfig = configparser.ConfigParser()
kogeconfig.read("conf/koge48.conf")
koge48core = Koge48(
  kogeconfig.get("mysql","host"),
  kogeconfig.get("mysql","user"),
  kogeconfig.get("mysql","passwd"),
  kogeconfig.get("mysql","database")
)


global_redpackets = {}
USERPROPERTIES = {
    #"BinanceEmail":"^[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+([:,：]\d+){0,1}$",
    #"BinanceUID":"^\d{8}$",
    #"BinanceBNBMemo":"^\d{9}$",
    #"ETH":"^(0x)[0-9A-Fa-f]{40}$",
    #"BNB":"^(bnb1)[0-9a-z]{38}([:,：]\d+){0,1}$",
    "BNB":"^(bnb1)[0-9a-z]{38}$",
    #"EOS":"^[1-5a-z\.]{1,12}$"
}

#weiboclient = init_weibo('BNB48Club')

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

def getCommunityContent(activeuser=None,groupid=None):
    '''
    top10 = koge48core.getGroupMiningStatus()
    powtotal = 0
    for each in top10:
        powtotal += each[1]

    #markdown+= "[BNB48 GFW](https://t.me/joinchat/GRaQmkzYU3oJUphCcG4Y7Q)"
    #markdown += "\n"
    markdown = "[Koge Channel](https://t.me/bnb48club_publish)"
    #if not activeuser is None and str(activeuser.id) in Koge48.BNB48LIST:
        #markdown += "\n"
        #markdown+= "[BNB48 内部通知](https://t.me/joinchat/AAAAAFVOsQwKs4ev-pO2vg)"
        #markdown += "\n"
        #markdown+= "[BNB48 媒体宣传](https://t.me/joinchat/GRaQmkZcD-7Y4q83Nmyj4Q)"
        #markdown += "\n"
        #markdown+= "[BNB48 技术开发](https://t.me/joinchat/GRaQmlISUPSpHFwVblxvxQ)"
        #markdown += "\n"
        #markdown+= "[BNB48 内部测试](https://t.me/joinchat/GRaQmlMuX_XdVSQgpxFT_g)"
        #markdown += "\n"
        #markdown+= "[孵化器](https://t.me/joinchat/GRaQmlWXCEJIJN3niyUUhg)"
        #markdown += "\n"
        #markdown+= "[移民交流](https://t.me/joinchat/GRaQmlAedWPaQFjyfoTDYg)"
        #markdown += "\n"
        #markdown+= "[离岸公司](https://t.me/joinchat/GRaQmlcgwROYjcmMbAu7NQ)"

    markdown += "\n-----------------"
    markdown +="\n*Last 24H {} Blocks*:".format(powtotal)

    tempwhitelist = []#Koge48.MININGWHITELIST.copy()

    for each in top10:
        try:
            fullname = Koge48.MININGWHITELIST[each[0]]['title']
            link = 'https://t.me/{}'.format(Koge48.MININGWHITELIST[each[0]]['username'])
            markdown+="\n{}% [{}]({})".format(round(100.0*each[1]/powtotal,2),fullname,link)
            tempwhitelist.pop(each[0])
        except Exception as e:
            print(e)
            pass

    for each in tempwhitelist:
        fullname = Koge48.MININGWHITELIST[each]['title']
        link = 'https://t.me/{}'.format(Koge48.MININGWHITELIST[each]['username'])
        markdown+="\n0% [{}]({})".format(fullname,link)

    if not groupid is None:
        markdown += "\n"
        markdown += getMiningDetail(groupid)

    return markdown
    '''
    return ""

def callbackhandler(bot,update):
    message_id = update.callback_query.message.message_id
    activeuser = update.callback_query.from_user
    userInfo(activeuser.id,"FULLNAME",activeuser.full_name)
    logger.warning("{} callback, content: {}".format(activeuser.full_name,update.callback_query.data))
    if update.callback_query.data.startswith("MENU#"):
        thedatas = update.callback_query.data.split('#')
        lang = thedatas[2]
        if "BALANCE" == thedatas[1]:
            response = "{} {} {}".format(getusermd(activeuser),getkoge48md(),format(koge48core.getChequeBalance(activeuser.id)/KOGEMULTIPLIER,','))
            try:
                update.callback_query.message.edit_text(response,disable_web_page_preview=True,reply_markup=builddashboardmarkup(lang),parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                logger.warning(e)
        elif "CHANGES" == thedatas[1]:
            response = "{}:\n".format(activeuser.full_name)
            kogechanges=koge48core.getChequeRecentChanges(activeuser.id)
            for each in kogechanges:
                response += "  {} ago,`{}`,{}\n".format(each['before'],each['number']/KOGEMULTIPLIER,each['memo'])
            update.callback_query.message.edit_text(response,disable_web_page_preview=True,reply_markup=builddashboardmarkup(lang),parse_mode=ParseMode.MARKDOWN)
        elif "BIND" == thedatas[1]:
            #bindstatus = koge48core.getAirDropStatus(activeuser.id)
            #response = getLocaleString("BINDINTRODUCTION",lang).format(bindstatus['api'][0],bindstatus['bnb'][1])
            response = getLocaleString("BINDINTRODUCTION",lang)

            for each in USERPROPERTIES:
                response += "\n*{}*:".format(each)
                value = userInfo(update.effective_user.id,each)
                logger.warning(value)
                if not value is None:
                    response += "\n"
                    response += value
            update.callback_query.message.edit_text(response,disable_web_page_preview=True,reply_markup=builddashboardmarkup(lang),parse_mode=ParseMode.MARKDOWN)
        elif "MINING" == thedatas[1]:
            response = getLocaleString("MININGINTRODUCTION",lang)
            update.callback_query.message.edit_text(response,disable_web_page_preview=True,reply_markup=builddashboardmarkup(lang),parse_mode=ParseMode.MARKDOWN)
        elif "KOGE" == thedatas[1]:
            try:
                update.callback_query.message.edit_text(getLocaleString("KOGEINTRODUCTION",lang),disable_web_page_preview=True,reply_markup=builddashboardmarkup(lang),parse_mode=ParseMode.MARKDOWN)
            except:
                pass
        elif "JOIN" == thedatas[1]:
            response=""
            if koge48core.getTotalBalance(activeuser.id)/KOGEMULTIPLIER >= ENTRANCE_THRESHOLDS[BNB48PLATINUMEN]:
                response += "[BNB48 Platinum]({})\n".format(bot.exportChatInviteLink(BNB48PLATINUMEN))
            if koge48core.getTotalBalance(activeuser.id)/KOGEMULTIPLIER >= ENTRANCE_THRESHOLDS[BNB48PLATINUMCN]:
                response += "[BNB48 铂金会]({})\n".format(bot.exportChatInviteLink(BNB48PLATINUMCN))
            response += "[BNB48 Club®️ En](https://t.me/bnb48club_en)\n"
            response += "[BNB48 Club®️ 中文](https://t.me/bnb48club_cn)\n"
            #response =getLocaleString("JOININTRODUCTION",lang).format(ENTRANCE_THRESHOLDS[BNB48])
            update.callback_query.message.edit_text(response,disable_web_page_preview=True,reply_markup=builddashboardmarkup(lang),parse_mode=ParseMode.MARKDOWN)
            bot.sendMessage(update.effective_user.id,response,disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
            update.callback_query.answer()
        elif "RICH" == thedatas[1]:
            top10 = koge48core.getTop(20)
            text="On-Telegram Supply:{}\n---\nKoge Forbes:\n\n".format(format(koge48core.getTotalFrozen()/KOGEMULTIPLIER,','))
            for each in top10:
                text+="[{}](tg://user?id={})\t{}\n".format(getFullname(each[0]),each[0],each[1]/KOGEMULTIPLIER)
            update.callback_query.message.edit_text(text,disable_web_page_preview=True,reply_markup=builddashboardmarkup(lang),parse_mode=ParseMode.MARKDOWN)
        elif "COMMUNITY" == thedatas[1]:
            markdown=getCommunityContent(activeuser)
            update.callback_query.message.edit_text(markdown,disable_web_page_preview=True,reply_markup=builddashboardmarkup(lang),parse_mode=ParseMode.MARKDOWN)
        elif "LANG" == thedatas[1]:

            if "CN" == thedatas[2]:
                newlang = "EN"
            else:
                newlang = "CN"
            update.callback_query.message.edit_text(getLocaleString("KOGEINTRODUCTION",newlang),disable_web_page_preview=True,reply_markup=builddashboardmarkup(newlang),parse_mode=ParseMode.MARKDOWN)
        else:
            update.callback_query.answer()

    elif update.callback_query.data.startswith("ELECTION#"):
        thedatas = update.callback_query.data.split('#')
        election_id = thedatas[1]
        election_action = thedatas[2]
        election = Election(election_id)
        if "NOMI" == election_action:
            if election.selfNomi(update.effective_user.id):
                votees = election.getVotees()
                update.effective_message.edit_text(getElectionTitle(votees),reply_markup=buildelection(votees,election.getId()),parse_mode="Markdown")
        elif "END" == election_action and update.effective_user.id == SirIanM:
            update.effective_message.edit_reply_markup()
        else:
            if election.toggleVote(update.effective_user.id,election_action):
                votees = election.getVotees()
                update.effective_message.edit_text(getElectionTitle(votees),reply_markup=buildelection(votees,election.getId()),parse_mode="Markdown")

        update.callback_query.answer()
    elif update.callback_query.data.startswith("FILLING#"):
        thedatas = update.callback_query.data.split('#')
        lang = getLang(update.effective_user)
        #logger.warning("chat action")
        #bot.sendChatAction(update.effective_user.id,"Waiting for {}...".format(thedatas[1]))
        userInfo(update.effective_user.id,"FILLING",update.effective_message.message_id)
        update.effective_message.edit_reply_markup(reply_markup=buildfilling(update.effective_user.id,thedatas[1]))
        update.callback_query.answer(getLocaleString("FILLHINT",lang))
    elif update.callback_query.data.startswith("FILL#"):
        thedatas = update.callback_query.data.split('#')
        redpacketid = thedatas[1]
        prop = thedatas[2]
        currentstat = thedatas[3]
        export = loadJson("_data/redpacket{}.json".format(redpacketid),{})
        if prop == export["prop"]:
            update.callback_query.answer()
            return
        export["prop"]=prop
        saveJson("_data/redpacket{}.json".format(redpacketid),export)
        update.effective_message.edit_text(genDistList(export),reply_markup=buildfillselection(export),parse_mode=ParseMode.MARKDOWN)
    elif update.callback_query.data.startswith("escrow#"):
        thedatas = update.callback_query.data.split('#')
        escrow_id = str(update.callback_query.message.chat_id)+str(update.callback_query.message.message_id)
        if thedatas[1] == "confirm":
            if activeuser.id != float(thedatas[2]):
                update.callback_query.answer("Only the sender/只有发起者才能确认",show_alert=True)
                return
            if ESCROWLIST[escrow_id]=="start":
                ESCROWLIST[escrow_id]="confirm"
                saveJson("_data/escrowlist.json",ESCROWLIST)
                koge48core.transferChequeBalance(Koge48.BNB48BOT,int(thedatas[3]),float(thedatas[4]),"escrow confirm, from {} to {}".format(thedatas[2],thedatas[3]))
                try:
                    bot.sendMessage(int(thedatas[3]),"{} just approved the escrow transfer of {} Koge to you".format(getusermd(activeuser),thedatas[4]),parse_mode=ParseMode.MARKDOWN)
                except:
                    pass
            update.callback_query.answer("{} just approved".format(activeuser.full_name),show_alert=True)
            update.callback_query.message.edit_reply_markup(reply_markup=buildtextmarkup('Approved'))

        elif thedatas[1] == "cancel":
            if activeuser.id != float(thedatas[3]):
                update.callback_query.answer("Only the receiver/只有接受者才能取消",show_alert=True)
                return
            if ESCROWLIST[escrow_id]=="start":
                ESCROWLIST[escrow_id]="cancel"
                saveJson("_data/escrowlist.json",ESCROWLIST)
                koge48core.transferChequeBalance(Koge48.BNB48BOT,int(thedatas[2]),float(thedatas[4]),"escrow cancel, from {} to {}".format(thedatas[2],thedatas[3]))
                try:
                    bot.sendMessage(int(thedatas[2]),"Your escrowed transfer to {} of {} Koge was just aborted by peer".format(getusermd(activeuser),thedatas[4]),parse_mode=ParseMode.MARKDOWN)
                except Exception as e:
                    logger.warning(e)
                    pass
            update.callback_query.message.edit_reply_markup(reply_markup=buildtextmarkup('Aborted'))
            update.callback_query.answer("{} Aborted".format(activeuser.full_name),show_alert=True)
            
    elif update.callback_query.data.startswith("HONGBAO#"):
        thedatas = update.callback_query.data.split('#')
        redpacket_id = thedatas[1]
        if not redpacket_id in global_redpackets:
            delayMessageDelete(update.callback_query.message)
            return
        redpacket = global_redpackets[redpacket_id]
        thisdraw = redpacket.draw(activeuser)
        if thisdraw > 0:
            if "KOGE" == redpacket.currency():
                koge48core.transferChequeBalance(Koge48.BNB48BOT,activeuser.id,thisdraw,"collect redpacket from {}".format(redpacket._fromuser.full_name))
            update.callback_query.answer("{} {}".format(thisdraw,redpacket.currency()),show_alert=True)
        elif 0 == thisdraw:
            update.callback_query.answer("每人只能领取一次/One person, One share",show_alert=True)
        else:
            update.callback_query.answer("红包发完了/Out of share",show_alert=True)

        if 0 != thisdraw and not redpacket.needUpdate():
            redpacket.needUpdate(True)
            delayUpdateRedpacket(redpacket_id)
    else:
        update.callback_query.answer()

def delayMessageDelete(message,delay=10):
    thread = Thread(target = actualMessageDelete, args=[message,delay])
    thread.start()
def actualMessageDelete(message,delay):
    time.sleep(delay)
    try:
        message.delete()
    except Exception as e:
        print(e)
def delayUpdateRedpacket(redpacket_id):
    thread = Thread(target = actualUpdateRedpacket, args=[redpacket_id])
    thread.start()
def actualUpdateRedpacket(redpacket_id):
    time.sleep(1)
    redpacket = global_redpackets[redpacket_id]
    if redpacket.left() < 1:
        thismarkup = None
    else:
        thismarkup = buildredpacketmarkup(redpacket_id)
    try:
        updater.bot.edit_message_caption(chat_id=redpacket.groupId(),message_id=redpacket.messageId(),caption=redpacket.getLog(),reply_markup=thismarkup,parse_mode="Markdown")
        if "KOGE" != redpacket.currency():
            export = redpacket.export()
            saveJson("_data/redpacket{}.json".format(export["id"]),export)
    except Exception as e:
        print(e)
        pass
    redpacket.needUpdate(False)

def delayAnswer(query,content=None):
    thread = Thread(target = actualAnswer, args=[query,content])
    thread.start()
def actualAnswer(query,content=None):
    time.sleep(0.1)
    if content is None:
        query.answer()
    else:
        query.answer(text=content)

def buildelection(votees,eid):
    res=[]
    curline=[]
    for eachid in votees:
        curline.append(InlineKeyboardButton("🗳"+userInfo(eachid,"FULLNAME"),callback_data="ELECTION#{}#{}".format(eid,eachid)))
        if len(curline) >=4 :
            res.append(curline)
            curline=[]
    if len(curline) > 0:
        res.append(curline)
    res.append([InlineKeyboardButton("我要参选",callback_data="ELECTION#{}#NOMI".format(eid))])
    res.append([InlineKeyboardButton("结束",callback_data="ELECTION#{}#END".format(eid))])
    return InlineKeyboardMarkup(res)
def buildfilling(uid,editing=None):
    res = []
    for each in USERPROPERTIES:
        if editing == each:
            res.append([InlineKeyboardButton(each+"    ✍️",callback_data="FILLING#{}".format(each))])
        else:
            info = userInfo(uid,each)
            if info is None:
                info = ""
            res.append([InlineKeyboardButton(each+"    "+info,callback_data="FILLING#{}".format(each))])
    return  InlineKeyboardMarkup(res)

def buildfillselection(export):
    res = []
    for each in USERPROPERTIES:
        if each ==  export['prop']:
            flag = "✅"
            command = "CHECKED"
        else:
            flag = "🔘"
            command = "UNCHECKED"
        res.append([InlineKeyboardButton(each+flag,callback_data="FILL#{}#{}#{}".format(export["id"],each,command))])
    return  InlineKeyboardMarkup(res)

def buildkeyboard(lang="CN"):
    return ReplyKeyboardMarkup(
        [
            [
                getLocaleString("MENU_BALANCE",lang),
                getLocaleString("MENU_CHANGES",lang),
            ],
            [
                getLocaleString("MENU_RICH",lang),
                getLocaleString("MENU_COMMUNITY",lang),
            ],
            [
                getLocaleString("MENU_C2C",lang),
                getLocaleString("MENU_JOIN",lang),
            ],
            [
                getLocaleString("MENU_KOGE",lang),
                getLocaleString("MENU_MINING",lang),
            ],
            [
                getLocaleString("MENU_LANG",lang)
            ]
        ],
        resize_keyboard = True
    )
def builddashboardmarkup(lang="CN"):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(getLocaleString("MENU_KOGE",lang),callback_data="MENU#KOGE#"+lang),
                #InlineKeyboardButton(getLocaleString("MENU_MINING",lang),callback_data="MENU#MINING#"+lang),
                #InlineKeyboardButton(getLocaleString("MENU_COMMUNITY",lang),callback_data="MENU#COMMUNITY#"+lang),
            ],
            [
                InlineKeyboardButton(getLocaleString("MENU_BALANCE",lang),callback_data="MENU#BALANCE#"+lang),
                InlineKeyboardButton(getLocaleString("MENU_CHANGES",lang),callback_data="MENU#CHANGES#"+lang),
                #InlineKeyboardButton(getLocaleString("MENU_RICH",lang),callback_data="MENU#RICH#"+lang),
            ],
            [
                InlineKeyboardButton(getLocaleString("MENU_C2C",lang),url=BNB48C2CLINK),
            ],
            [
                InlineKeyboardButton(getLocaleString("MENU_JOIN",lang),callback_data="MENU#JOIN#"+lang),
                #InlineKeyboardButton(getLocaleString("MENU_BIND",lang),callback_data="MENU#BIND#"+lang),
                InlineKeyboardButton(getLocaleString("MENU_LANG",lang),callback_data="MENU#LANG#"+lang),
            ],
        ]
    )
    '''
            [
                #InlineKeyboardButton(getLocaleString("MENU_ADDROBOT",lang),url="https://telegram.me/bnb48_bot?startgroup=join"),
            ],
        [
        ],
    '''
def buildredpacketmarkup(redpacket_id):
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('💰',callback_data="HONGBAO#{}".format(redpacket_id))]
        ]
    )

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

def testHandler(bot,update):
    update.message.reply_text(bot.exportChatInviteLink(update.message.chat_id))
def pmcommandhandler(bot,update):
    if update.message.chat.type != 'private':
        delayMessageDelete(update.message.reply_text('Talk to me in private'))
        delayMessageDelete(update.message,0)
        return

    things = update.message.text.split(' ')
    if "/transfer" == things[0]:
        if len(things)<3 or float(things[1]) <= 0 or int(things[2]) <= 0:
            update.message.reply_markdown("`/transfer <amount> <target uid> [memo]`")
            return
        sourceuserid = update.effective_user.id
        targetuserid = int(things[2])
        transamount = int(float(things[1])*KOGEMULTIPLIER)
        if len(things) > 3:
            del things[0]
            del things[0]
            del things[0]
            memo = " ".join(things)
        else:
            memo = ""

        try:
            koge48core.transferChequeBalance(sourceuserid,targetuserid,transamount,"{} send to {}, memo: {}".format(sourceuserid,targetuserid,memo))
        except:
            delayMessageDelete(update.message,0)
            return

        update.message.reply_markdown("Sent {} {}Koge,memo: {}".format(getusermd(targetuserid),transamount/KOGEMULTIPLIER,memo),disable_web_page_preview=True)
        try:
            bot.sendMessage(targetuserid,"{} Send you {} Koge,memo: {}".format(getusermd(sourceuserid),transamount/KOGEMULTIPLIER,memo),parse_mode=ParseMode.MARKDOWN)
        except:
            pass
    elif "/myid" in things[0]:
        update.message.reply_text(update.effective_user.id)
    elif "/start" in things[0]:
        #if 'private' == update.message.chat.type:
        lang=getLang(update.message.from_user)
        if len(things) > 1 and things[1].startswith("fill"):
            redpacketid = things[1][4:]
            export = loadJson("_data/redpacket{}.json".format(redpacketid),{})
            if "sender" in export and export["sender"] == update.effective_user.id:
                update.message.reply_markdown(genDistList(export),reply_markup=buildfillselection(export))
                if str(update.effective_user.id) in export['map']:
                    response = "[{}]{}\n{} {}\n\n".format(export['title'],userInfo(export['sender'],"FULLNAME"),export['map'][str(update.effective_user.id)][1],export["currency"])
            else:
                response = getLocaleString("ASSOCIATION",lang)
                update.message.reply_markdown(response,disable_web_page_preview=True,reply_markup=buildfilling(update.effective_user.id,update.effective_message.message_id))
        elif len(things) > 1 and things[1].startswith("myid"):
            update.message.reply_text("Your UID is {}".format(update.effective_user.id))
        else:
            update.message.reply_markdown(getLocaleString("KOGEINTRODUCTION",lang),reply_markup=builddashboardmarkup(lang))
    elif "/dashboard" in things[0]:
        lang=getLang(update.message.from_user)
        update.message.reply_markdown(getLocaleString("KOGEINTRODUCTION",lang),reply_markup=builddashboardmarkup(lang))
    elif "/key" in things[0]:
        lang=getLang(update.message.from_user)
        update.message.reply_markdown(getLocaleString("KOGEINTRODUCTION",lang),reply_markup=buildkeyboard(lang))

def genDistList(export):
    res = "Address,Amount\n"
    for eachid in export["map"]:
        res += "["
        info = userInfo(eachid,export['prop'])
        if info is None:
            info = "___"
        res += info
        res += ","
        res += str(export["map"][eachid][1])
        '''
        res += ","
        res += export["currency"]
        '''
        res += "](tg://user?id={})".format(eachid)
        res += "\n"
    return res
def getAssociation(uid):
    mid = userInfo(uid,"FILLING")
    if not mid is None:
        updater.bot.edit_message_reply_markup(chat_id=uid,message_id=mid,reply_markup=buildfilling(uid))
        clearUserInfo(uid,"FILLING")

    response = ""
    for each in USERPROPERTIES:
        response += "\n*{}*:\n".format(each)
        value = userInfo(uid,each)
        if not value is None:
            response += value
        else:
            response += ""
    return response

def groupadminhandler(bot,update):
    chatid = update.message.chat_id
    user = update.message.from_user
    admins = bot.get_chat_administrators(chatid)
    if not bot.getChatMember(chatid,user.id) in admins:
        delayMessageDelete(update.message.reply_text("Admin Only"))
        return

def getFullname(uid):
    name = userInfo(uid,"FULLNAME")
    if name is None:
        return uid
    else:
        return name
def getusermd(user,link=True):
    if hasattr(user, 'id'):
        res="[{}]".format(user.full_name)
        if link:
            res += "(tg://user?id={})".format(user.id)
        return res
    else:
        userid = int(user)
        res = "[{}]".format(getFullname(userid))
        if link:
            res += "(tg://user?id={})".format(userid)
        return res
    #return "`{}`".format(user.full_name)
def getkoge48md():
    return "[Koge](https://t.me/bnb48_bot)"

def getElectionTitle(votees):
    md = "每人可投7票，选出9个理事席位。得票情况:\n"
    for eachid in votees:
        md += "[{}](tg://user?id={})\n▫️{}票\n".format(userInfo(eachid,"FULLNAME"),eachid,len(votees[eachid]))
    return md
def siriancommandhandler(bot,update):
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
        kick(int(things[1],int(things[2])))
    elif "/rich" in things[0]:
        top10 = koge48core.getTop(100)
        text="On-Telegram Supply:{}\n---\nKoge Forbes:\n\n".format(format(koge48core.getTotalFrozen()/KOGEMULTIPLIER,','))
        for each in top10:
            text+="[{}](tg://user?id={})\t{}\n".format(getFullname(each[0]),each[0],each[1]/KOGEMULTIPLIER)
        update.message.reply_markdown(text,disable_web_page_preview=True)
    elif "/findgroup" in things[0]:
        update.message.reply_markdown("[{}]({})".format(things[1],bot.exportChatInviteLink(int(things[1]))))
    elif "/ban" in things[0] and not targetuser is None:
        ban(update.message.chat_id,targetuser.id)
    elif "/ban" in things[0]:
        ban(int(things[1],int(things[2])))
    elif "/cheque" in things[0]:
        if len(things) != 2:
            update.message.reply_text("回复他人消息: /cheque 金额")
            return
        number = float(things[1])
        latest = koge48core.signCheque(targetuser.id,number,"signed by SirIanM")
        update.message.reply_markdown("添加成功,目前最新余额{}".format(latest))

    elif "/reimburse" in things[0]:
        if len(things)<4 or float(things[1]) <= 0 or int(things[2]) <= 0:
            update.message.reply_markdown("`/reimburse <amount> <target uid> <memo>`")
            return
        sourceuserid = Koge48.BNB48BOT
        targetuserid = int(things[2])
        transamount = int(float(things[1])*KOGEMULTIPLIER)
        del things[0]
        del things[0]
        del things[0]
        memo = " ".join(things)
        try:
            koge48core.transferChequeBalance(sourceuserid,targetuserid,transamount,"reimburse to {}, memo: {}".format(targetuserid,memo))
        except:
            delayMessageDelete(update.message,0)
            return
        update.message.reply_markdown("Reimburse {} {}Koge,memo: {}".format(getusermd(targetuserid),transamount/KOGEMULTIPLIER,memo),disable_web_page_preview=True)
        try:
            bot.sendMessage(targetuserid,"Received reimbursement {} Koge,memo: {}".format(transamount/KOGEMULTIPLIER,memo),parse_mode=ParseMode.MARKDOWN)
        except:
            pass

    elif "/unban" in things[0] and not targetuser is None:
        unban(update.message.chat_id,targetuser.id)
    elif "/unban" in things[0]:
        unban(int(things[1],int(things[2])))
    elif "/groupid" in things[0]:
        bot.sendMessage(SirIanM,"{}".format(update.message.chat_id))
    elif "/burn" in things[0]:
        number = float(things[1])
        #koge48core.burn(Koge48.LOTTERY,number)
        update.message.reply_markdown("销毁成功")
    elif "/election" in things[0]:
        election = Election()
        votees = election.getVotees()
        update.message.reply_markdown(getElectionTitle(votees),reply_markup=buildelection(votees,election.getId()),quote=False)
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
            bot.sendMessage(update.message.chat_id, text="增加\""+thekeyword+"\"为刷屏关键词", reply_to_message_id=update.message.message_id)
        else:
            if not thekeyword in FLUSHWORDS:
                return
            FLUSHWORDS.remove(thekeyword)
            bot.sendMessage(update.message.chat_id, text="不再将\""+thekeyword+"\"作为刷屏关键词", reply_to_message_id=update.message.message_id)

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
            bot.sendMessage(update.message.chat_id, text="增加\""+thekeyword+"\"为垃圾账号关键词", reply_to_message_id=update.message.message_id)
        else:
            if not thekeyword in SPAMWORDS:
                return
            SPAMWORDS.remove(thekeyword)
            bot.sendMessage(update.message.chat_id, text="不再将\""+thekeyword+"\"作为垃圾账号关键词", reply_to_message_id=update.message.message_id)

        file = codecs.open("_data/blacklist_name.json","w","utf-8")
        file.write(json.dumps({"words":SPAMWORDS}))
        file.flush()
        file.close()
        logger.warning("blacklist_name updated")

def inlinequeryHandler(bot,update):
    if "community" == update.inline_query.query:
        update.inline_query.answer(
            results=[
                        InlineQueryResultArticle(
                            id=update.inline_query.id+"community",
                            cache_time=60,
                            title="24小时社区热度排行",
                            input_message_content=InputTextMessageContent(message_text=getCommunityContent(),disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
                        )
            ],
            is_personal=False
        )
    return
def choseninlineresultHandler(bot,update):
    return
def botcommandhandler(bot,update):
    things = update.message.text.split(' ')
    logger.warning(things)
    if "/trans" in things[0]:
        if update.message.reply_to_message is None or len(things) < 2 or float(things[1]) <= 0:
            delayMessageDelete(update.message,0)
            return
        if len(things)>2:
            memo=things[2]
        else:
            memo=""
        user = update.effective_user
        targetuser = update.message.reply_to_message.from_user
        if user.id == targetuser.id:
            delayMessageDelete(update.message,0)
            return
        transamount = int(float(things[1])*KOGEMULTIPLIER)
        try:
            koge48core.transferChequeBalance(user.id,targetuser.id,transamount,"{} send to {}, memo:{}".format(user.id,targetuser.id,memo))
        except:
            delayMessageDelete(update.message,0)
            return
        try:
            bot.sendMessage(targetuser.id,"{} 💸 {} Koge,memo: {}".format(getusermd(user),transamount/KOGEMULTIPLIER,memo),parse_mode=ParseMode.MARKDOWN)
        except:
            pass
        update.message.reply_markdown("{} 💸 {} {} Koge,memo: {}".format(getusermd(user),getusermd(targetuser),transamount/KOGEMULTIPLIER,memo),disable_web_page_preview=True)
    elif "/escrow" in things[0] and len(things) >=2 and not update.message.reply_to_message is None:
        if float(things[1]) <= 0:
            return
        '''
        if update.message.chat_id != BNB48C2C:
            delayMessageDelete(update.message.reply_markdown("[BNB48 C2C]({})".format(BNB48C2CLINK)))
            return
        '''
        user = update.message.from_user
        targetuser = update.message.reply_to_message.from_user

        if targetuser.id == Koge48.BNB48BOT or targetuser.id == user.id:
            return
        transamount = int(float(things[1])*KOGEMULTIPLIER)

        try:
            koge48core.transferChequeBalance(user.id,Koge48.BNB48BOT,transamount,"escrow start, from {} to {}".format(user.id,targetuser.id))
        except:
            delayMessageDelete(update.message)
            return

        message = update.message.reply_markdown("{} --escrowed--> {}\n{} Koge\nClick ✅to approve or click ❌ to abort".format(getusermd(user),getusermd(targetuser),transamount),disable_web_page_preview=True,reply_markup=buildescrowmarkup(user.id,targetuser.id,transamount))
        ESCROWLIST[str(message.chat_id) + str(message.message_id)]="start"
        saveJson("_data/escrowlist.json",ESCROWLIST)
            
    elif "/mining" in things[0]:
        content = getCommunityContent(groupid=update.effective_chat.id)
        delayMessageDelete(update.message,0)
        delayMessageDelete(update.message.reply_markdown(content,disable_web_page_preview=True,quote=False))
    elif "/donate" in things[0] or "/juankuan" in things[0]:
        try:
            try:
                donatevalue = float(things[1])
            except:
                donatevalue = 100

            koge48core.transferChequeBalance(update.effective_user.id,Koge48.BNB48BOT,donatevalue,"donation")
            update.message.reply_text("🙏 {} Koge".format(donatevalue))
        except:
            delayMessageDelete(update.message)
    elif "/posttg" in things[0]:
        if update.message.chat_id != BNB48MEDIA:
            photoid = update.message.reply_to_message.photo[-1].file_id
            update.message.reply_text(photoid)
            return
        for group in [BNB48PLATINUM,BNB48PUBLISH]:
            #bot.forwardMessage(group,update.message.chat_id,update.message.reply_to_message.message_id)
            photoid = update.message.reply_to_message.photo[-1].file_id
            bot.sendPhoto(group,photoid)
        update.message.reply_text("已转发")
    elif "/hongbao" in things[0] or "/rain" in things[0]:
        if update.message.chat.type == 'private':
            delayMessageDelete(update.message.reply_text("send in a group"))
            return
        user = update.message.from_user
        
        currency = "KOGE"

        if len(things) >1 and not is_number(things[1]):
            currency = things[1]
            del things[1]

        if "KOGE" != currency and not user.id in getAdminsInThisGroup(update.message.chat_id):
            delayMessageDelete(update.message)
            return

        if len(things) >1 and is_number(things[1]):
            balance = float(things[1])
        elif "KOGE" == currency:
            balance = 100
        else:
            delayMessageDelete(update.message,1)
            return

        if balance <= 0:
            delayMessageDelete(update.message,1)
            return


        if len(things) > 2 and is_number(things[2]):
            amount = int(things[2])
            if amount < 1:
                amount = 1
        else:
            amount = 10

        if "KOGE" == currency and amount > 40:
            amount = 40
            '''
            try:
                delayMessageDelete(update.message.reply_text("MAX 40"))
            except:
                pass
            delayMessageDelete(update.message)
            return
            '''

        if "KOGE" == currency and balance/amount < RedPacket.SINGLE_AVG:
            delayMessageDelete(update.message)
            return

        if "KOGE" == currency:
            try:
                koge48core.transferChequeBalance(user.id,Koge48.BNB48BOT,balance,"send koge rain")
            except:
                delayMessageDelete(update.message,0)
                return
        
        if len(things) > 3:
            del things[0]
            del things[0]
            del things[0]
            title = " ".join(things)
        else:
            title = "Who's lucky ?"

        redpacket = RedPacket(update.message.from_user,balance,amount,title,currency)
        redpacket_id = str(int(time.time()))
        redpacket.groupId(update.message.chat_id)
        redpacket.id(redpacket_id)
        #message = bot.sendPhoto(update.message.chat_id,photo=open("redpacket.png","rb"),caption=redpacket.getLog(),reply_markup=buildredpacketmarkup())
        message = bot.sendPhoto(update.message.chat_id,photo="AgADBQADOqkxG6cCyVY36YVebnCyl_14-TIABAEAAwIAA3gAA5dPAgABFgQ",caption=redpacket.getLog(),reply_markup=buildredpacketmarkup(redpacket_id),parse_mode="Markdown")
        redpacket.messageId(message.message_id)
        global_redpackets[redpacket_id]=redpacket

        if not message.chat.username is None:
            #bot.sendMessage(BNB48,"https://t.me/{}/{}".format(message.chat.username,message.message_id))
            bot.sendMessage(BNB48PLATINUMCN,"有人发红包 👉 [{}](https://t.me/{}/{})".format(message.chat.title,message.chat.username,message.message_id),disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
            '''
            if message.chat_id != BNB48CN:
                bot.sendMessage(BNB48CN,"有人发红包 👉 [{}](https://t.me/{}/{})".format(message.chat.title,message.chat.username,message.message_id),disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
            if message.chat_id != BNB48EN:
                bot.sendMessage(BNB48EN,"Someone releases a luckydraw 👉 [{}](https://t.me/{}/{})".format(message.chat.title,message.chat.username,message.message_id),disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
            '''
        delayMessageDelete(update.message,0)

    elif "/querybal" in things[0]:
        update.message.reply_text("{}".format(koge48core.getChequeBalance(int(things[1]))/KOGEMULTIPLIER))
    elif "/bal" in things[0]:
        user = update.message.from_user
        if update.message.reply_to_message is None:
            targetuser = user
        else:
            targetuser = update.message.reply_to_message.from_user

        response = "{}的{}余额为{}".format(getusermd(targetuser),getkoge48md(),koge48core.getChequeBalance(targetuser.id)/KOGEMULTIPLIER)
        try:
            bot.sendMessage(user.id,response,disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
        except:
            update.message.reply_markdown("为保护隐私,建议私聊机器人查询。\n"+response,disable_web_page_preview=True)
        delayMessageDelete(update.message)
    elif "/changes" in things[0]:
        
        user = update.message.from_user
        if update.message.reply_to_message is None:
            targetuser = user
        else:
            targetuser = update.message.reply_to_message.from_user

        response = "{}最近的Koge变动记录:\n".format(targetuser.full_name)
        kogechanges=koge48core.getChequeRecentChanges(targetuser.id)
        for each in kogechanges:
            response += "        {}前,`{}`,{}\n".format(each['before'],each['number']/KOGEMULTIPLIER,each['memo'])

        try:
            bot.sendMessage(user.id,response,disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
        except:
            update.message.reply_markdown("为保护隐私,建议私聊机器人查询。\n"+response,disable_web_page_preview=True)

        delayMessageDelete(update.message)

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
    return
def listMiningGroup(message):
    thegroup = message.chat_id
    if message.chat.username is None:
        message.reply_text("Gossip Mining Only in Public Groups")
    '''
    if not str(thegroup) in Koge48.MININGWHITELIST:
        Koge48.MININGWHITELIST[str(thegroup)]={"id":thegroup,"title":update.message.chat.title,"username":update.message.chat.username}
        message.reply_text("Mining Enabled")
    '''

def cleanHandler(bot,update):
    logger.warning("clean triggered")
    if update.message.from_user.id == SirIanM:
        logger.warning("stop job...")
        updater.job_queue.stop()
        logger.warning("done")
        for job in updater.job_queue.jobs():
            job.schedule_removal()
            logger.warning("job {} cleared".format(job.name))
        logger.warning("All job cleared")

        for each in global_redpackets:
            balance = global_redpackets[each].balance()
            if balance <=0:
                continue
            global_redpackets[each].clear()
            if "KOGE" == global_redpackets[each].currency():
                koge48core.transferChequeBalance(Koge48.BNB48BOT,global_redpackets[each]._fromuser.id,balance,"redpacket return")
            delayUpdateRedpacket(each)

        logger.warning("All redpackets cleared")

        saveJson("_data/userinfomap.json",USERINFOMAP)
        update.message.reply_text('cleaned')
        updater.stop()
        updater.is_idle = False
        sys.exit()
def bnbhandler(bot,update):
    if update.message.chat_id != update.message.from_user.id:
        return
    '''
    if not userInfo(update.effective_user.id,"BNB") is None:
        update.message.reply_text("⛔️");
        return
    '''
    userInfo(update.effective_user.id,"BNB",update.message.text)
    markdown=getAssociation((update.effective_user.id))
    if not markdown is None:
        update.message.reply_markdown(markdown)
def eoshandler(bot,update):
    if update.message.chat_id != update.message.from_user.id:
        return
    update.message.reply_text("ETH: {}".format(update.message.text))
def ethhandler(bot,update):
    if update.message.chat_id != update.message.from_user.id:
        return
    userInfo(update.effective_user.id,"ETH",update.message.text)
    markdown=getAssociation((update.effective_user.id))
    if not markdown is None:
        update.message.reply_markdown(markdown)
def binanceuidhandler(bot,update):
    if update.message.chat_id != update.message.from_user.id:
        return
    userInfo(update.effective_user.id,"BinanceUID",update.message.text)
def binancebnbmemohandler(bot,update):
    if update.message.chat_id != update.message.from_user.id:
        return
    userInfo(update.effective_user.id,"BinanceBNBMemo",update.message.text)
    update.message.reply_text("BinanceBNBMemo: {}".format(update.message.text))
def binanceemailhandler(bot,update):
    if update.message.chat_id != update.message.from_user.id:
        return
    userInfo(update.effective_user.id,"BinanceEmail",update.message.text)
    markdown=getAssociation((update.effective_user.id))
    if not markdown is None:
        update.message.reply_markdown(markdown)

def apihandler(bot,update):
    if update.message.chat_id != update.message.from_user.id:
        return
    message_text = update.message.text
    api = message_text.split("#")
    koge48core.setApiKey(update.message.from_user.id,api[0],api[1])
    update.message.reply_text("apikey绑定完成,注意绑定过程不会验证api的有效性")
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

def privateTextHandler(bot,update):
    return
def botmessagehandler(bot, update):
    #checkThresholds(update.message.chat_id,update.message.from_user.id)

    userInfo(update.message.from_user.id,"FULLNAME",update.message.from_user.full_name)
    message_text = update.message.text
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
                logger.warning(update.message.from_user.full_name+" restricted because of " + update.message.text);
                return
        user = update.message.from_user
        if minable(update):
            mined=koge48core.mine(user.id,update.message.chat_id)
        else:
            mined = False

        if mined:
            logger.warning("{} {} 在 {} @{} {} 出矿 {}".format(user.full_name,user.id,update.message.chat.title,update.message.chat.username,update.message.chat_id,mined))
            delayMessageDelete(update.message.reply_markdown("{} 💰 {} {}".format(getusermd(user,False),mined,getkoge48md()),disable_web_page_preview=True,quote=False))

def minable(update):
    return False
    '''
    user = update.message.from_user
    if user.id in Koge48.MININGBLACKLIST:
        return False
    if not str(update.message.chat_id) in Koge48.MININGWHITELIST:
        return False
    if len(update.message.text) < 5:
        return False
    if update.message.chat.username is None:
        return False
    
    return True
    '''

def onleft(bot,update):
    for SPAMWORD in SPAMWORDS:
        if SPAMWORD in update.message.left_chat_member.full_name:
            delayMessageDelete(update.message)

def welcome(bot, update):
    userInfo(update.message.from_user.id,"FULLNAME",update.message.from_user.full_name)
    checkThresholds(update.message.chat_id,update.message.from_user.id)
    if update.message.chat_id == BNB48PLATINUMCN or  update.message.chat_id == BNB48PLATINUMEN:
        bot.exportChatInviteLink(update.message.chat_id)
    #筛选垃圾消息
    isSpam = False
    '''
    for newUser in update.message.new_chat_members:
        if  update.message.chat_id == BNB48CN and update.message.from_user.id != newUser.id and not newUser.is_bot and koge48core.getChequeBalance(newUser.id) == 0:
            koge48core.transferChequeBalance(Koge48.BNB48BOT,newUser.id,Koge48.MINE_MIN_SIZE,"invited")
            koge48core.transferChequeBalance(Koge48.BNB48BOT,update.message.from_user.id,Koge48.MINE_MIN_SIZE,"inviting")
            update.message.reply_text("{}邀请{},两人各挖到{}Koge".format(update.message.from_user.full_name,newUser.full_name,Koge48.MINE_MIN_SIZE))
        #if update.message.chat_id == BNB48CN and (newUser.username is None or len(newUser.username == 0) and newUser.get_profile_photos().total_count == 0:
        #    update.message.reply_text("Hi",quote=False,)
        for SPAMWORD in SPAMWORDS:
            if SPAMWORD in newUser.full_name:
                isSpam = True
                break;
    '''

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
                #updater.bot.sendMessage(userid,"Koge持仓{}不足{},被移除出群。".format(balance,KICK_THRESHOLDS[chatid]),disable_web_page_preview=True)
                updater.bot.sendMessage(chatid,"{}持仓{},不足{},移除出群。".format(getFullname(userid),balance,KICK_THRESHOLDS[chatid]),disable_web_page_preview=True)
                logger.warning("{}Koge持仓{}不足{},被移除出群。".format(userid,balance,KICK_THRESHOLDS[chatid]))
                return True
            except:
                pass
            return
        if SAYINSUFFICIENT[chatid] and balance < SAY_THRESHOLDS[chatid]:
            try:
                updater.bot.sendMessage(userid,"Koge持仓不足{},此消息将持续出现。不足{}将被移除出群。".format(SAY_THRESHOLDS[chatid],KICK_THRESHOLDS[chatid]),disable_web_page_preview=True)
            except:
                pass
        

def ban(chatid,userid):
    updater.bot.kickChatMember(chatid,userid)
def unban(chatid,userid):
    updater.bot.unbanChatMember(chatid,userid)
def kick(chatid,userid):
    if BNB48PLATINUMCN == chatid:
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
updater = Updater(token=mytoken, request_kwargs={'read_timeout': 60, 'connect_timeout': 60})
j = updater.job_queue



def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    #dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.photo & Filters.private, callback=photoHandler))#'''处理私发的图片'''
    dp.add_handler(CallbackQueryHandler(callbackhandler))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))#'''处理新成员加入'''
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, onleft))#'''处理成员离开'''
    dp.add_handler(MessageHandler(Filters.group & Filters.text & (~Filters.status_update),botmessagehandler))# '''处理大群中的直接消息'''
    dp.add_handler(RegexHandler("^\w{64}\s*#\s*\w{64}$",apihandler))
    #dp.add_handler(RegexHandler(USERPROPERTIES["ETH"],ethhandler))
    #dp.add_handler(RegexHandler(USERPROPERTIES["EOS"],eoshandler))
    dp.add_handler(RegexHandler(USERPROPERTIES["BNB"],bnbhandler))
    #dp.add_handler(RegexHandler(USERPROPERTIES["BinanceEmail"],binanceemailhandler))
    #dp.add_handler(RegexHandler(USERPROPERTIES["BinanceUID"],binanceuidhandler))
    #dp.add_handler(RegexHandler(USERPROPERTIES["BinanceBNBMemo"],binancebnbmemohandler))


    dp.add_handler(CommandHandler(
        [
        ],
        groupadminhandler)#只对管理员账号做出响应的响应
    )
    #dp.add_handler(CommandHandler(["kogefaucettestnet"],kogefaucetHandler))
    #dp.add_handler(CommandHandler(["bnbfaucettestnet"],bnbfaucetHandler))
    dp.add_handler(CommandHandler(
        [
            "spam",
            "despam",
            "flush",
            "deflush",
            "kick",
            "findgroup",
            "ban",
            "unban",
            "groupid",
            "reimburse",
            "exclude",
            "list",
            "delist",
            "cheque",
            "rich",
            #"burn",
            "election"
        ],
        siriancommandhandler)#
    )
    dp.add_handler(CommandHandler(
        [
            "start",
            "dashboard",
            #"key",
            "myid",
            "transfer",
        ],
        pmcommandhandler)#处理仅私聊有效的命令
    )

    dp.add_handler(CommandHandler( [ "clean" ], cleanHandler))

    dp.add_handler(CommandHandler(
        [
            #"trans",
            "escrow",
            "bal",
            "querybal",
            "changes",
            #"promote",
            #"demote",
            #"restrict",
            #"unrestrict",
            #"hongbao",
            #"rain",
            #"burn",
            #"mining",
            #"donate",
            #"juankuan",
            #"community",
            #"posttg",
        ],
        botcommandhandler))# '''处理其他命令'''

    dp.add_handler(CommandHandler( [ "test" ], testHandler))
    dp.add_handler(InlineQueryHandler(inlinequeryHandler))
    dp.add_handler(ChosenInlineResultHandler(choseninlineresultHandler))
    dp.add_handler(MessageHandler(Filters.text and Filters.private, callback=privateTextHandler))#'''处理私聊文字'''
    # log all errors
    dp.add_error_handler(error)
    #Start the schedule
    logger.warning("will start periodical in 0 seconds")
    job_airdrop = j.run_repeating(periodical,interval=3600,first=0)

    '''
        gap = 86400- time.time()%86400
        logger.warning("will start community broadcast in %s seconds",gap)
        job_airdrop = j.run_repeating(broadcastCommunity,interval=86400,first=gap)
    '''


    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()




def getMiningDetail(groupid):
    content=""
    top10 = koge48core.getMiningStatus(groupid)
    if len(top10) > 0:
        content += "👇👇👇👇👇👇👇👇👇👇"
        for each in top10:
            content += "\n{} Koge [{}](tg://user?id={})".format(round(each[1],2),userInfo(each[0],"FULLNAME"),each[0])
    return content

def broadcastCommunity(bot,job):
    content = getCommunityContent()
    for eachgroupid in []: #Koge48.MININGWHITELIST:
        try:
            thiscontent = content
            thiscontent += "\n"
            groupdetail = getMiningDetail(eachgroupid)
            if groupdetail == "":
                continue
            thiscontent += groupdetail
            bot.sendMessage(int(eachgroupid),thiscontent,disable_web_page_preview=True,parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(e)

def periodical(bot,job):
    #Koge48.refresh()
    '''
    for eachuid in Koge48.BNB48LIST:
        try:
            if checkThresholds(BNB48,eachuid):
                bnb48list.remove(eachuid)
        
        except Exception as e:
            print(e)
            print(eachuid)
            pass
    '''

    saveJson("_data/userinfomap.json",USERINFOMAP)
    return
if __name__ == '__main__':
    
    main()

