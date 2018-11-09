# 安装步骤
1. 需要 `python 2.7`环境，安装`pip`模块。
1. 克隆本repository。
1. 进入repo目录，运行 `pip install -r requirements.txt` 安装依赖包。

# CommunityBot
社区机器人，用于同一机器人协调管理多个群的情形。
## 配置文件
配置文件示例参见 `conf/watchdog.conf.example`
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
## 启动机器人
`python community.py [config file]`
运行日志输出到stderr，请根据需要重定向
## 功能手册
1. 当机器人检查到有新用户加入正确配置了puzzle的群(机器人需在该群内且拥有读消息权限)时，会自动禁言该用户(需拥有ban权限)并提醒用户(需拥有发消息权限)通过机器人进行入群测试。用户完成测试后解禁，一段时间不通过则自动踢出。
2. send /supervise to add current group(without puzzle).
