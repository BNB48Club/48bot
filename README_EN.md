
There are two bots in this repository, `48bot` and `community bot`, to be splitted.
The latter one is designed to be an open source multi-group administrative bot.

# Installation
1. `python 2.7` required, as well as `pip` module.
1. clone this repository
1. `pip install -r requirements.txt` to fullfill dependencies.



# Community Bot
## Config File
You can find a config template here: [`conf/watchdog.conf.example`](./conf/watchdog.conf.example)
Following are description for each section in config file
### [bot]
`
token = 111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
name = @usernameofyourbot
`

token should be the token of bot you got from @botfather
name should be the username of your token, don't miss `@`

### [groups]
`
-1000000000001 = anotherpuzzle.json
-1000000000001 = nopuzzle
`
If Groups doesn't have puzzle file, the following commands will use the group's name as default.

puzzle file must use json as extension

puzzle file format example: `_data/11111111111111.json.example`

format `groupid = puzzle file path`

If puzzle file path is a relative path, then the current directory is the working directory where the bot started.

Have to use UTF-8 encoding to save it
### [confadmins]
The user who has the rights to change config. Format: `userid = Remark`
### [dataadmins]
The user who has the rights to change data. Format: `userid = Remark`
### [blackfiletypes]
The users who send the following type of files will be banned automatically,

Format: `.filetype = Remark`
### [scamkeys]
The keywords that scammers possibly use,

Format: `Keywords  = Remark`
## How to run it
After set the conf file,

Please make sure the current user has the WRITE rights to the folder \_data

Run the following command

`python community.py [config file]`

Run the log output to stderr, possibly need redirect
## Quick Manual
1. When the Community Bot detects a new user join in the group(which has correctly configured the puzzle file, and the bot has READ rights in this group). The bot will temporary ban the new user (needs BAN rights), and ask the new user to take a quiz (needs Send Message rights). The bot will allow the user to join in after he/she complete the quiz successfully. Otherwise it will ban the user if he/she has not finished the quiz in a certain time period.

1. /supervise dataadmin could reply to a user in the group(which has the Bot), and if this user is not in the 'groups' config, this user will be added to the 'groups' config.
1. /dataadmin confadmin could reply to a user in the group(which has the Bot), and this user will become dataadmin.
1. /start watchdog function, user PM the Bot in order to take a quiz.
1. /replybanall dataadmin or confadmin could use this command to ban the user(that has been replied) in ALL groups that under this admin's jurisdiction. And add this user to black list.
1. `/fwdbanall` dataadmin or confadmin could use this command to ban the forwarded user in ALL groups that under this admin's jurisdiction. And add this user to black list.
1. `/idbanall <userid>` dataadmin or confadmin could use this command to ban the userid in ALL groups that under this admin's jurisdiction. And add this userid to black list.
1. `/reload` confadmin could PM the Bot to use this command to reload config files(and config the data files in the config files).
1. `/points` Check your self points in the current group.
1. `/rank` dataadmin check the top 10 ranking.
1. `/clearpoints` confadmin clear all points in the current group.
1. `/clean` confadmin clear the hidden tasks, and after that please stop the Bot immediately.
1. `/punish` group admin, confadmin or dataadmin could clear user's points to punish the user.




# 48Bot
48Bot is a manager program to manage BNB48 club group[@bnb48_bot](https://t.me/bnb48_bot)
## Quick Manual
- start - (PM)Joining BNB48 Club。If the user has enough Koge balance the Bot will show the link to join the group.
- cheque - (PM) Send cheque `/cheque Amount`
- changes - (PM) Check the 10 most recently balance changes
- bind - (PM) Binding the Koge airdrop
- mybinding - (PM) Check my binding and Koge airdrop
- bal - Check the Koge balance. Reply otheres with this command can check other user's balance 
- trans - transfer Koge to others. Have to reply someone to use this command. `/trans Amount`
- auction - Start auction(PM/Charge) `/auction StartingPrice Duration Description`
- hongbao - send hongbao(Red envelope) `/hongbao [Amount] [Quantity] [Wishes]` Default amount is 10，Default quantity is 1，Default wishes is "恭喜发财" (Kung Hei Fat Choy)
- redpacket - send Red envelope `/redpacket [Amount] [Quantity] [Wishes]` The same default value as above
- groupstats - (Admin) Check the current group mining stats.
- casino - (Admin/PM) Open the casino.
- nocasino - (Admin/PM) Close the casino after this round.
- restrict - (Admin/PM) Ban user from posting messages.
- unrestrict - (Admin/PM) Unban.
- promote - (Charge) Promote the user to be the group admin. Have to repy this user to use this command.
- demote - (Charge) Demote the group admin to be a normal user. Have to reply this user to use this command .
- clean Super admin clear the hidden tasks, and after that please stop the Bot immediately.
