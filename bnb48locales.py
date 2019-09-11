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
        "KOGEINTRODUCTION":"Koge不只是一个Telegram支付系统。\n\n命令列表\n`/escrow <金额>` - 担保支付,在交易群内使用。\n`/trans <金额>` - 回复他人进行转账\n`/hongbao <金额> <个数> [祝福语]` - 发红包。",
        "BINDINTRODUCTION":"直接输入对应内容即可绑定/更新, API信息的格式为`apikey#apisecret`\n\n*APIkey*:\n{}\n*末次快照BNB余额*:\n{}",
        "MININGINTRODUCTION":"在Koge机器人入驻并开通了功能的Telegram公开群中聊天,有几率获得Koge奖励。即*聊天挖矿*。\n\n聊天挖矿出矿的概率服从以聊天消息间隔为变量的泊松分布,距离上条消息发出的时间越长则本条消息挖出矿的概率越大。\n\n群与群之间出矿独立，您可以查看社区排名,选择热度较低的群发言以更高效地挖矿。\n\n每次出矿的金额大小服从一定范围内的平均分布。\n\n如果需要在您的Telegram公开群引入聊天挖矿,请先将本机器人加入您的群,然后联系[BNB48](https://t.me/bnb48club_cn)了解费用与优惠。",
        "JOININTRODUCTION":"持仓Koge大于等于{}可自助加入核心群",
        "MENU_KOGE":"Koge简介",
        "MENU_BALANCE":"账户余额🏦",
        "MENU_CHANGES":"收支明细",
        "MENU_BIND":"绑定账户",
        "MENU_AIRDROP":"空投记录",
        "MENU_MINING":"聊天挖矿💬",
        "MENU_COMMUNITY":"社区排名",
        "MENU_JOIN":"加入核心群",
        "MENU_RICH":"富豪榜💲",
        "MENU_CASINO":"娱乐场🎰",
        "MENU_C2C":"场外交易🤝",
        "MENU_ADDROBOT":"添加机器人",
        "MENU_SENDRANK":"转发",
        "MENU_LANG":"EN ⚙️",
        "FILLHINT":"请输入新的地址。如果有memo/id，请在地址后面输入一个冒号分隔然后写上：",
        "ASSOCIATION":"可绑定地址"

    },
    "EN":{
        "KOGEINTRODUCTION":"Koge is not only a Telegram payment system.\n\nCommands: \n`/escrow <Number of Koge>` - escrow payment,reply to sombody in OTC group to start an escrow.\n`/trans <Number of Koge>` - reply to transfer.\n`/redpacket  <Number of Koge> <Number of shares> [Title(optional)]` - send a redpacket.",
        "BINDINTRODUCTION":"Input corresponding content to associate.\nSyntax for api: `apikey#apisecret`\n\n*APIkey*:\n{}\n*BNB Balance*:\n{}",
        "MININGINTRODUCTION":"Gossip Mining, refers to the process of chat in Telegram groups while one acquires KOGE airdrop randomly.\n\n Probability of finding a new BLOCK subjects to Poission distribution, which means, the longer time between your message and the last message in this group, the high possibility you are going to find a new BLOCK. \n\nMining pricesses of different groups are independent. In another word, chat in groups with fewer members is more likely to bring you some KOGE. You can view `Community Rank` to make your smart choice.\n\n KOGE in each block differs in a small range. \n\n If you would like to introduce Gossip Mining in your group, simply introduce this bot and contact [BNB48](https://t.me/bnb48club_en) to consult on price and discount.",
        "JOININTRODUCTION":"You need a balance of {} Koge to join",
        "MENU_KOGE":"About Koge",
        "MENU_BALANCE":"Balance 🏦",
        "MENU_CHANGES":"Statement",
        "MENU_BIND":"Associating",
        "MENU_AIRDROP":"Airdrops",
        "MENU_MINING":"Gossip Mining 💬",
        "MENU_COMMUNITY":"Communities",
        "MENU_JOIN":"Join Elite Group",
        "MENU_RICH":"Koge Forbes 💲",
        "MENU_CASINO":"Casino 🎰",
        "MENU_C2C":"OTC trade 🤝",
        "MENU_ADDROBOT":"Add Bot",
        "MENU_SENDRANK":"Forward",
        "MENU_LANG":"中文 ⚙️",
        "FILLHINT":"Please input new address, if you need to provide a memo/id, attach at the end with a ':'",
        "ASSOCIATION":"Associated addresses"
    }
}
