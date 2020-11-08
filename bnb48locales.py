# -*- coding: utf-8 -*-
def getLocaleString(key,lang):
    if key in BNB48_LOCALES[lang]:
        return BNB48_LOCALES[lang][key]
    elif key in BNB48_LOCALES["CN"]:
        return BNB48_LOCALES["CN"][key]
    else:
        return "NOT DEFINED"
def isLocaleString(key,text):
    for eachlang in BNB48_LOCALES:
        if BNB48_LOCALES[eachlang][key] == text:
            return True
    return False

BNB48_LOCALES={
    "CN":{
        "KOGEINTRODUCTION":"Koge 是BNB48俱乐部的DAO治理Token。\n\n机器人可以使用的命令:\n\n`/dashboard` - 查看此菜单\n`/myid` - 查询自己的Telegram UID\n`/transfer <金额> <他人UID> [memo]` - 进行转账。仅支持私聊机器人时使用\n`/escrow <金额>` - 向他人发起担保转账，必须回复(引用)对方消息才生效",
        "BINDINTRODUCTION":"直接输入格式正确的内容即可更新资料",
        "MININGINTRODUCTION":"在Koge机器人入驻并开通了功能的Telegram公开群中聊天,有几率获得Koge奖励。即*聊天挖矿*。\n\n聊天挖矿出矿的概率服从以聊天消息间隔为变量的泊松分布,距离上条消息发出的时间越长则本条消息挖出矿的概率越大。\n\n群与群之间出矿独立，您可以查看社区排名,选择热度较低的群发言以更高效地挖矿。\n\n每次出矿的金额大小服从一定范围内的平均分布。\n\n如果需要在您的Telegram公开群引入聊天挖矿,请先将本机器人加入您的群,然后联系[BNB48](https://t.me/bnb48club_cn)了解费用与优惠。",
        "JOININTRODUCTION":"持有铂金徽章方可进入铂金会。您可以通过质押{} Koge获得一枚铂金徽章，您当前余额为{} Koge。\n 点击 /mintplatinum 开始质押。",
        "PLATINUMWELCOME":"欢迎您~尊贵的铂金徽章持有人。您有{} Koge 质押在铂金徽章中。\n点击 /meltplatinum 可以取回质押，同时铂金徽章也会失效。\n点击下方链接进入铂金会私享社群：",
        "PLATINUMFAREWELL":"您已销毁铂金徽章，返还Koge记录可以通过 /changes 命令查看",
        "MENU_KOGE":"Koge简介",
        "MENU_BALANCE":"余额🏦",
        "MENU_CHANGES":"收支",
        "MENU_BIND":"登记空投地址",
        "MENU_SLOT":"🎰水果机",
        "MENU_AIRDROP":"空投",
        "MENU_MINING":"聊天挖矿💬",
        "MENU_COMMUNITY":"社区",
        "MENU_JOIN":"铂金会",
        "MENU_RICH":"富豪榜💲",
        "MENU_CASINO":"娱乐场🎰",
        "MENU_C2C":"交易🤝",
        "MENU_LOTTERY":"回购乐透",
        "MENU_ADDROBOT":"添加机器人",
        "MENU_SENDRANK":"转发",
        "MENU_LANG":"EN ⚙️",
        "FILLHINT":"请输入新的地址。如果有memo/id，请在地址后面输入一个冒号分隔然后写上：",
        "ASSOCIATION":"可绑定地址"

    },
    "EN":{
        "KOGEINTRODUCTION":"Koge is the governance token of BNB48 Club DAO.\n\nCommands: \n\n`/dashboard` - Show this menu.\n`/myid` - Find out your Telegram UID.\n`/transfer <Amount of Koge> <Target User UID> [memo]` - transfer Koge to someone else. Only works in this private chat\n`/escrow <Amount of Koge>` - escrowed transfer to the sender of the message you replied",
        "BINDINTRODUCTION":"Input corresponding content to associate.",
        "MININGINTRODUCTION":"Gossip Mining, refers to the process of chat in Telegram groups while one acquires KOGE airdrop randomly.\n\n Probability of finding a new BLOCK subjects to Poission distribution, which means, the longer time between your message and the last message in this group, the high possibility you are going to find a new BLOCK. \n\nMining pricesses of different groups are independent. In another word, chat in groups with fewer members is more likely to bring you some KOGE. You can view `Community Rank` to make your smart choice.\n\n KOGE in each block differs in a small range. \n\n If you would like to introduce Gossip Mining in your group, simply introduce this bot and contact [BNB48](https://t.me/bnb48club_en) to consult on price and discount.",
        "JOININTRODUCTION":"You need a Platinum badge to enter. You can mint one by staking {} Koge, your balance is {} Koge. \nClick /mintplatinum to mint.",
        "INSUFFICIENTBALANCE":"Insufficient balance",
        "PLATINUMWELCOME":"Welcome~ Honorable Platinum badge holder. \nYou have {} Koge staked on the badge.\nYou can click /meltplatinum to melt your badge and get your Koge back.\nClick following link to join Platinum Group(s):",
        "PLATINUMFAREWELL":"You've melted your platinum badge, check your unstaked Koge via /changes",
        "MENU_KOGE":"Koge",
        "MENU_BALANCE":"Balance 🏦",
        "MENU_CHANGES":"Statement",
        "MENU_BIND":"Signup Airdrop",
        "MENU_SLOT":"🎰Slots",
        "MENU_AIRDROP":"Airdrops",
        "MENU_MINING":"Gossip Mining 💬",
        "MENU_COMMUNITY":"Communities",
        "MENU_JOIN":"Platinum",
        "MENU_RICH":"Forbes 💲",
        "MENU_CASINO":"Casino 🎰",
        "MENU_C2C":"Trade 🤝",
        "MENU_LOTTERY":"Buying-Back Lottery",
        "MENU_ADDROBOT":"Add Bot",
        "MENU_SENDRANK":"Forward",
        "MENU_LANG":"中文 ⚙️",
        "FILLHINT":"Please input new address, if you need to provide a memo/id, attach at the end with a ':'",
        "ASSOCIATION":"Associated addresses"
    }
}
