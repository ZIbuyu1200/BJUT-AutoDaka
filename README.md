# 北京工业大学/北工大疫情通/企业微信每日打卡脚本/python

# 请遵守学校相关防疫要求，本人仅做代码和技术的分享，如若出事概不负责

# **本项目借鉴自[大佬 1](https://github.com/HTY-DBY/BJUT-Auto-Daka)和[大佬 2](https://github.com/tsosunchia/bjut_autosignin/)**

## 1. 更新

### 1.1. 2022 年 3 月 16 日

更新了打卡的内容(config.json)，即增加了身体状况和自检体温等

### 1.2. 2022 年 3 月 10 日

[北工大学工系统出现验证码返回空白的故障](https://hty.ink/1802/ "北工大学工系统出现验证码返回空白的故障")，于是修改代码，使正确的账号和密码在运行时不再需要验证码

注意，请在废弃的 ip 地址下(如挂 VPN 等切换 ip 或使用手机热点)测试并确定您的账号和密码是否正确，否则在以上 bug 修复前不要轻易挂载本代码至服务器上

### 1.3. 2022 年 3 月 28 日

由于北京工业大学打卡系统转移至使用原生企业微信打卡系统，而不依赖于学工系统哦本身，因此本项目已失效

## 2. 快速使用

### 2.1. 必须的

#### 2.1.1. 下载源码

文件夹 DontChange，如同名字一样，不要动里面的设定

文件夹 local，里面是关于后文您所需填入的相关设定，详见后文

Main.py 是定时调用 Daka_fun.py 的方法；Daka_fun.py 是真正的打卡方法；requirements.txt，如果您略懂 python，这是告诉新服务器/电脑，你必须需要安装除却 python 原始提供的包后的额外包，如果您实在不会使用这个文件导入，请打开 cmd，输入

```
pip install requests
pip install json_tools
pip install json
pip install smtplib
pip install urllib
pip install requests
pip install urllib3
```

如果您的 python 还缺少了什么包，请自行参照错误提示打开 cmd，进行输入

```
pip install requests 您缺少的包名
```

#### 2.1.2. 登录信息和打卡信息

打开`local/userInfo.json`，格式介绍如下：

```json
{
  "user": [
    //字典user，保留字段不要修改
    [
      //列表里依次存储每个人的信息
      "12345678", //学号
      "password", //学工系统密码
      "example@example.com", //接收结果的邮箱，可以不改则不发
      {
        //下方为表单内容需要手动修改
        "c16": "在校且住宿",
        "c17": "在京",
        "c18": "低风险地区",
        "c15": "无情况",
        "c8": "正常",
        "c9": "正常",
        "location_address": "北京工业大学"
      }
    ], //注意不要多逗号或者少逗号
    [
      "12345678",
      "password",
      "example@example.com",
      {
        "c16": "在校且住宿",
        "c17": "在京",
        "c18": "低风险地区",
        "c15": "无情况",
        "c8": "正常",
        "c9": "正常",
        "location_address": "北京工业大学"
      }
    ]
  ]
}
```

修改您所需填入的信息即可

学工系统的域名为[http://xgxt.bjut.edu.cn](http://xgxt.bjut.edu.cn)，账号即学号，忘记密码的同学可以找辅导员重置或尝试如下可能的初始密码：

- 123456
- 身份证后 7 到 2，或 6 到 1
- cjxb00000L@
- 完整日期+Bjut，如 20220225Bjut

### 2.2. 不必须的

#### 2.2.1. 验证码识别

登录[2captcha](https://2captcha.com/)(可能需要科学上网)，注册登录后，充值，阿里云最低要求为支付 3 美元

2captcha 的识别价格为 1$ 识别 1000 次，识别准确率在 80%左右

在[您的 2captcha 首页](https://2captcha.com/enterpage)找到您的 API key，复制备用

打开`local/config.json`，格式介绍如下：

```json
"EMAIL_REC_LIST": ["example@example.com"],//管理员邮箱，用于接收打卡结果，可以不改
  "userInfoMode": "local",
  "EMAIL_ENABLE": false,//是否开启邮件提醒
  "EMAIL_USERNAME": "example@example.com",//邮件发送者的账号
  "EMAIL_PASSWORD": "password",//邮件发送者的密码
  "EMAIL_SERVER": "example.com",//SMTP服务器地址
  "EMAIL_PORT": 25,//SMTP服务器端口
  "isCaptchaReqResSeparate": true,
  "captchaSendRequestHost": "http://2captcha.com",
  "captchaSendRequestPath": "/in.php",
  "captchaSendRequestOKName": "status",
  "captchaSendRequestOKCode": 1,
  "captchaSendRequestTaskIDName": "request",
  "captchaSendRequestCaptchaName": "captcha",
  "captchaSendRespondBodyContentName": "body",
  "captchaSendRequestHead": {
    "enctype": "multipart/form-data",
    "accept-charset": "UTF-8"
  },
  "captchaSendRequestBody": {
    "method": "base64",
    "key": "API key",//API key
    "min_len": "4",
    "max_len": "4",
    "json": "1"
  },
  "captchaGetRequestOKName": "status",
  "captchaGetRequestOKCode": 1,
  "captchaGetRequestHost": "http://2captcha.com",
  "captchaGetRequestPath": "/res.php",
  "captchaGetRespondTaskIDName": "id",
  "captchaGetRespondBodyContentName": "request",
  "captchaGetRequestHead": {
    "enctype": "multipart/form-data",
    "accept-charset": "UTF-8"
  },
  "captchaGetRespondBody": {
    "key": "API key",//API key
    "action": "get",
    "json": "1"
  }
```

**注意，没注释的地方别动！！！**

在注释为`API key`处，填入刚刚复制的 API key，注意，钱包没钱则无法识别验证码，程序会报错，因此必须先充值 3 美元

**注意，API key 要填两个地方**

#### 2.2.2. 邮箱提醒

如果您需要获得打卡后的邮箱提醒，修改`local/userInfo.json`中的邮箱设置，本项目采用 smtp 发送邮件，不知道什么是 smtp 的请自行百度，通常默认发送端口为 25，如果您设置了 ssh 则一般为 625，或者参照您的邮箱中的帮助文档

#### 2.2.3. 打卡时间

如果您采取`Main.py`运行程序，本项目默认 0 点 1 分打卡，如果您想在其他时间打卡，请自行依照相关注释修改`Main.py`中的代码

## 3. 开始运行

### 3.1. 方法一

在服务器上设置定时运行 `Daka.py`，注意一定要设置定时运行，具体百度

### 3.2. 方法二

在服务器上设置运行 `Main.py`，具体百度

## 4. 开源声明

本项目采用`MIT License`
