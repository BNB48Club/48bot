# 安装步骤
1. 需要 `python 2.7`环境，安装`pip`模块。
1. 克隆本repository。
1. 进入repo目录，运行 `pip install -r requirements.txt` 安装依赖包。
# 48Bot
48Bot是用于BNB48俱乐部的管家机器人[@bnb48_bot](https://t.me/bnb48_bot)的管理程序
## 功能手册
auction - (私聊) /auction 底价 持续小时 商品描述

start - (私聊)加入BNB48 Club

join - (私聊)加入BNB48 Club

bal - 查余额

trans - 转账

cheque - (私聊)发支票。 /cheque 金额

hongbao - 发红包。 /hongbao [金额 个数 祝福语]

redpacket - 发红包。 /redpacket [金额 个数 祝福语]

changes - (私聊)查看最近十条余额

bind - (私聊)绑定BNB空投Koge

mybinding - (私聊)查看绑定与空投

mining - (管理)查看本群挖矿统计

restrict - (管理/收费)禁言

unrestrict - (管理/收费)解禁

promote - (收费)提升为本群管理员

demote - (收费)剥夺本群管理员

rich - (收费)查看Koge流通量、富豪榜

roller - (收费)查看Koge赌场豪客榜

clean - 大Boss清空隐藏任务，之后请立即停止机器人运行
# CommunityBot
社区机器人，用于同一机器人协调管理多个群的情形。
## 配置文件
配置文件示例参见 `conf/watchdog.conf.example`
必须使用UTF-8编码保存
### [bot]
`
token = 111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
name = @usernameofyourbot
`

token用于接入telegram bot
name 用于提醒消息中显示，建议填写bot的username

### [groups]
`
-1000000000001 = anotherpuzzle.json
-1000000000001 = nopuzzle
`
群组可以没有puzzle文件，此时后面的内容默认按群组名处理

puzzle文件必须以json为后缀名

puzzle文件格式参考`_data/11111111111111.json.example`

格式为 `groupid = puzzle文件路径`

其中puzzle文件路径若使用相对路径，current directory为启动机器人时的working directory

必须使用UTF-8编码保存
### [confadmins]
有在线更改conf权限的用户，格式为 `userid = 备注内容`
### [dataadmins]
有在线更改data权限的用户，格式为 `userid = 备注内容`
### [blackfiletypes]
发送这些后缀名文件的用户会被自动封禁

格式为`.filetype = 备注`
### [scamkeys]
骗子可能使用的关键字

格式为`关键字  = 备注`
## 运行方式
配置完毕conf文件

确认当前用户对\_data目录有写权限

运行下述命令

`python community.py [config file]`

运行日志输出到stderr，请根据需要重定向
## 功能手册
1. 当机器人检查到有新用户加入正确配置了puzzle的群(机器人需在该群内且拥有读消息权限)时，会自动禁言该用户(需拥有ban权限)并提醒用户(需拥有发消息权限)通过机器人进行入群测试。用户完成测试后解禁，一段时间不通过则自动踢出。
1. /supervise dataadmin在机器人加入的群中发送该命令，如果该群并未在groups中配置，机器人会将该群写入groups配置。
1. /dataadmin confadmin在机器人加入的群中回复别人的消息，被回复者会被配置为dataadmin。
1. /start watchdog功能中，用户私聊机器人发送该命令进行入群测试。
1. /replybanall dataadmin或者confadmin使用该命令，在所有管辖群中封禁被回复者，并加入黑名单。
1. `/fwdbanall` dataadmin或者confadmin使用该命令，在所有管辖群中封禁被回复消息的转发来源者，并加入黑名单。
1. `/idbanall <userid>` dataadmin或者confadmin使用该命令，在所有管辖群中封禁该userid，并加入黑名单。
1. `/reload` confadmin私聊机器人使用该命令，重新载入配置文件(以及配置文件中指定的数据文件)
1. `/points` 查看自己在本群的社区积分
1. `/top [N]` data管理员查看本群积分排名前N名单
1. `/above [N]` data管理员查看本群积分大于N的名单
1. `/rank N` data管理员查看本群积分排名第N名 如果总数不足N则返回最后一名
1. `/clearpoints` confadmin管理员清空本群所有积分
1. `/clean` confadmin 清空隐藏任务，之后请立即停止机器人运行
1. `/mute /ban` 群管理员或confadmin或dataadmin惩罚本群成员，清零积分
1. `/activity` confadmin在本群使用，开启聊天挖积分
1. `/deactivity` confadmin在本群使用，关闭聊天挖积分
1. `/codebonus 口令` dataadmin或confadmin在本群使用，新增一个口令红包口令，每天重置，聊天挖积分关闭时口令红包不生效
1. `/decodebonus 口令` 同上，只是变成删除口令红包口令
