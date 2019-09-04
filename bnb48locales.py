# -*- coding: utf-8 -*-
def getLocaleString(key,lang):
    if key in BNB48_LOCALES[lang]:
        return BNB48_LOCALES[lang][key]
    elif key in BNB48_LOCALES["CN"]:
        return BNB48_LOCALES["CN"][key]
    else:
        return "NOT DEFINED"

BNB48_LOCALES={
    "CN":{
        "KOGEINTRODUCTION":"Koge是BNB48俱乐部管理/发行的Token。\n\n向俱乐部[捐赠](http://bnb48club.mikecrm.com/c3iNLGn)BNB,会按比例得到Koge。\n\nBNB48还通过空投*活动*Koge作为在币安交易所长期持有BNB者的鼓励。持有BNB每天可以获得等量的(包含现货与杠杆余额)活动Koge空投,同时活动Koge会以每天10%的速度自然衰减。\n\nKoge目前通过Telegram Bot进行中心化管理,可以使用如下命令进行操作：\n/escrow - 担保交易,回复使用。参数：金额。\n/trans - Koge转账,回复使用。参数：金额。\n/hongbao - 红包。参数：金额 个数 [祝福语]\n\n注意 _活动Koge不能通过机器人进行转账等任何形式的操作。_\n\n适当的时候Koge会在币安链发行token,进行链上映射。链上映射时,活动Koge也将进行1:1映射,映射后不再区分活动与否。",
        "APIINTRODUCTION":"为了确认空投数量,我们需要您提供币安账户的API(只读)。按照 `apikey#apisecret` 的格式输入api密钥即可进行绑定/更新\n\n您当前绑定的币安APIkey(secret隐藏):\n*{}*\n\n末次快照BNB余额:\n*{}*\n\n请注意:_BNB48俱乐部与币安交易所无隶属关系,持仓快照是根据币安交易所公开的API接口获取信息。俱乐部尽力保证程序按照设计运行并对服务器做出力所能及的安全防护,然而我们无法做出100%的安全承诺。在极端情况下,您提交的API信息有可能被盗,我们无力对这种极端情况带来的后果负责。请自行做好必要的安全措施,例如对绑定的API设置只读权限。_\n\n您承诺是在充分了解上述风险之后决定继续绑定币安账户API。",
        "MININGINTRODUCTION":"在Koge机器人入驻并开通了聊天挖矿功能的Telegram公开群中聊天,有几率获得Koge奖励。即聊天挖矿。\n\n聊天挖矿出矿的概率服从以聊天消息间隔为变量的泊松分布,距离上条消息发出的时间越长则本条消息挖出矿的概率越大。\n\n核心群成员享有聊天挖矿双倍出矿概率\n\n换言之,越少其他人聊天,则越容易出矿。您可以查看社区排名,选择热度较低的群发言以更高效地挖矿。\n\n每次出矿的金额大小服从一定范围内的平均分布。\n\n通过聊天挖矿送出的Koge由BNB48 Club®️运营资金支付。\n\n如果需要在您的Telegram公开群引入聊天挖矿,请先将本机器人加入您的群,然后联系[BNB48](https://t.me/bnb48club_cn)开通。",
        "JOININTRODUCTION":"持仓Koge大于等于{}可自助加入核心群",
        "MENU_KOGE":"什么是Koge❓",
        "MENU_BALANCE":"账户余额🏦",
        "MENU_CHANGES":"收支明细",
        "MENU_API":"绑定API",
        "MENU_AIRDROP":"空投记录",
        "MENU_MINING":"聊天挖矿💬",
        "MENU_COMMUNITY":"社区热度",
        "MENU_JOIN":"加入核心群",
        "MENU_RICH":"富豪榜💲",
        "MENU_CASINO":"娱乐场🎰",
        "MENU_C2C":"场外交易🤝",
        "MENU_ADDROBOT":"添加机器人到...",
        "MENU_SENDRANK":"转发社区热度排名到...",
        "MENU_LANG":"EN ⚙️"
    },
    "EN":{
        "KOGEINTRODUCTION":"Koge is issued/managed by BNB48 Club. \n\nBy [donating](http://bnb48club.mikecrm.com/c3iNLGn) to BNB48 Club, you get Koge correspondingly.\n\nAlso, by holding BNB in binance.com, you will be eligible to claim *floating* Koge from BNB48 at a rate of 1:1 each day. Notice that *floating* Koge decreases at 10% everyday.\n\nKoge is now managed by this very Telegram Bot, you can operate your Koge through following commands: \n/escrow - escrow payment,reply to use,`<Number of Koge>`\n/trans - Koge transfer. Reply to use,`<Number of Koge>`\n/redpacket - lucky draw,`<Number of Koge> <Number of shares> [Title, optional]`\n\n_You can't operate *floating* Koge through above commands_\n\nKoge will be mapped to on-chain token in the future, the converting rate will be fixed at 1:1 no matter *floating* or not.",
        "APIINTRODUCTION":"Only through API can we safely retrieve your hodl information. `apikey#apisecret` , if you decide to do so, input following syntax on the left.\nThis APIkey(API secret hidden) is currently binded to your account:\n*{}*\n\nBNB Balance in last snapshot:\n*{}*\nNotice that _BNB48 Club is in no way affiliated with Binance. Hodl snapshot is retrieved through public engpoint published by Binance. We will try to store/handle your API carefully but we can not guarantee anything. In the worst condition, leaking of tradable API may cause a loss of fund. Please make sure you only submit read-only API info_\nBefore submitting anything, you promise you understand the risk above and still decide to submit API info.",
        "MININGINTRODUCTION":"Gossip Mining, refers to the process of chat in Telegram groups while one acquires KOGE airdrop randomly.\n\n Probability of finding a new BLOCK subjects to Poission distribution, which means, the longer time between your message and the last message in this group, the high possibility you are going to find a new BLOCK. \n\n _Member of Elite group has a doubled power of mining._\n\nIn another word, chat in groups with fewer members is more likely to bring you some KOGE. You can view `Community Rank` to find out Gossip Mining power rank.\n\n KOGE in each block differs in a small range. \n\n Gossip Mining is funded by BNB48 Club®, no extra minting occurs.\n\n If you would like to introduce Gossip Mining in your group, simply add KOGE bot as a member and contact [BNB48](https://t.me/bnb48club_en) to activate.",
        "JOININTRODUCTION":"You need a balance of {} Koge to join",
        "MENU_KOGE":"What is Koge❓",
        "MENU_BALANCE":"Account Balance 🏦",
        "MENU_CHANGES":"Statement",
        "MENU_API":"Bind Binance API",
        "MENU_AIRDROP":"Airdrop Record",
        "MENU_MINING":"Gossip Mining 💬",
        "MENU_COMMUNITY":"Community Rank",
        "MENU_JOIN":"Join Elite Group",
        "MENU_RICH":"Koge Forbes 💲",
        "MENU_CASINO":"Casino 🎰",
        "MENU_C2C":"OTC trade 🤝",
        "MENU_ADDROBOT":"Add Bot",
        "MENU_SENDRANK":"Publish Community Rank",
        "MENU_LANG":"中文 ⚙️"
    }
}
