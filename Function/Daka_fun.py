import base64
import json
import os
import random
import smtplib
import threading
import time
import urllib
import urllib.request
from email.mime.text import MIMEText
from urllib.parse import quote
import requests
import urllib3
import shutil


class clockinThread(threading.Thread):

    def __init__(self, username, pwd, data3, location, userEmailName,
                 EMAIL_ENABLE, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_SERVER,
                 EMAIL_PORT):
        threading.Thread.__init__(self)
        self.username = username
        self.pwd = pwd
        self.data3 = data3
        self.location = location
        self.userEmailName = userEmailName
        self.EMAIL_ENABLE = EMAIL_ENABLE
        self.EMAIL_USERNAME = EMAIL_USERNAME
        self.EMAIL_PASSWORD = EMAIL_PASSWORD
        self.EMAIL_SERVER = EMAIL_SERVER
        self.EMAIL_PORT = EMAIL_PORT
        self.clockinIns = clockin()

    def run(self):
        self.clockinIns.daka(self.username, self.pwd, self.data3,
                             self.location, self.userEmailName,
                             self.EMAIL_ENABLE, self.EMAIL_USERNAME,
                             self.EMAIL_PASSWORD, self.EMAIL_SERVER,
                             self.EMAIL_PORT)


class handler():
    def __init__(self):
        # 递归创建目录，exist_ok为 True 时，创建目录的时候如果已经存在就不报错
        os.makedirs('./local/', exist_ok=True)
        os.makedirs('./temp/', exist_ok=True)
        self.getInfo(debug=False)
        self.userList, self.rawList, self.EMAIL_ENABLE, self.EMAIL_USERNAME, self.EMAIL_PASSWORD, self.EMAIL_SERVER, self.EMAIL_PORT, self.EMAIL_REC_LIST = self.form_builder()
        for user in self.userList:
            flagFileName = './temp/' + user[0] + 'Flag'
            with open(flagFileName, 'w', encoding='utf-8') as fp:
                fp.write('255')

    def clockinHandler(self):
        uid = 0

        for user in self.userList:
            self.createThread(user[0], user[1], self.rawList[uid], user[3]['location_address'], user[2],
                              self.EMAIL_ENABLE, self.EMAIL_USERNAME, self.EMAIL_PASSWORD, self.EMAIL_SERVER,
                              self.EMAIL_PORT)
            uid += 1
        print('打卡程序已启动 账号总数量为 ' + str(len(self.userList)))
        while (True):
            finNum = 0
            for user in self.userList:
                flagFileName = './temp/' + user[0] + 'Flag'
                with open(flagFileName, 'r', encoding='utf-8') as fp:
                    if (fp.read() != '255'):
                        finNum += 1
            if (finNum == len(self.userList)):
                break
        resultString = ''
        succNum = 0
        for user in self.userList:
            flagFileName = './temp/' + user[0] + 'Flag'
            with open(flagFileName, 'rb') as fp:
                tmpStr = fp.read().decode('utf-8')
            if (tmpStr == '0'):
                tmpResultStr = (user[0] + '打卡成功\n')
                succNum += 1
            if (tmpStr == '1'):
                tmpResultStr = (user[0] + '已经打过卡\n')
                succNum += 1
            if (tmpStr == '2'):
                tmpResultStr = (user[0] + '打卡失败,登录成功,表单提交失败\n')
            if (tmpStr == '3'):
                tmpResultStr = (user[0] + '打卡失败,登录失败\n')
            resultString = resultString + tmpResultStr
        print("成功个数：" + str(succNum) + " 总个数：" + str(
            len(self.userList)))
        # 利用stmp发送邮件
        if self.EMAIL_ENABLE:
            try:
                tmpNum = 0
                self.EMAIL_REC_LIST.append(self.EMAIL_USERNAME)
                abstract = '疫情通打卡结果:' + str(succNum) + \
                    '/' + str(len(self.userList))
                for eList in self.EMAIL_REC_LIST:
                    message = MIMEText(resultString, 'plain', 'utf-8')
                    message['Subject'] = abstract
                    message['FROM'] = self.EMAIL_USERNAME
                    message['To'] = eList
                    server = smtplib.SMTP(self.EMAIL_SERVER)
                    server.connect(self.EMAIL_SERVER, self.EMAIL_PORT)
                    server.login(self.EMAIL_USERNAME, self.EMAIL_PASSWORD)
                    server.sendmail(self.EMAIL_USERNAME, [
                                    eList], message.as_string())
                    tmpNum += 1
                print("管理员邮件发送成功")
            except:
                print("管理员邮件发送失败")

        filelist = []
        rootdir = "./temp"
        filelist = os.listdir(rootdir)
        for f in filelist:
            filepath = os.path.join(rootdir, f)
            if os.path.isfile(filepath):
                os.remove(filepath)

    def createThread(self, username, pwd, data3, location, userEmailName, EMAIL_ENABLE, EMAIL_USERNAME, EMAIL_PASSWORD,
                     EMAIL_SERVER, EMAIL_PORT):
        thd = clockinThread(username, pwd, data3, location, userEmailName, EMAIL_ENABLE, EMAIL_USERNAME, EMAIL_PASSWORD,
                            EMAIL_SERVER, EMAIL_PORT)
        thd.start()

    def getInfo(self, debug):
        with open('./local/config.json', 'r', encoding='utf-8') as fp:
            form = json.load(fp=fp)
        mode = form['userInfoMode']
        if (mode == 'local'):
            with open('./local/userInfo.json', 'rb') as fp:
                if (debug):
                    print('localMode:' +
                          fp.read().decode('utf-8').replace(b'\r\n', b'\n'))
                else:
                    with open('./temp/userInfo.json', 'wb') as fp2:
                        fp2.write(fp.read().replace(b'\r\n', b'\n'))

    def form_builder(self):
        rawList = []
        with open('./DontChange/schoolStaticInfo.json', 'r', encoding='utf-8') as fp:
            form = json.load(fp=fp)
        prefixDataObj = form.pop('prefixData')
        suffix_data = form.pop('suffix_data')
        suffix_raw = quote(suffix_data)
        with open('./temp/userInfo.json', 'r', encoding='utf-8') as fp:
            form = json.load(fp=fp)
        userList = form.pop('user')
        with open('./local/config.json', 'r', encoding='utf-8') as fp:
            form = json.load(fp=fp)
        EMAIL_ENABLE = form.pop('EMAIL_ENABLE')
        EMAIL_USERNAME = form.pop('EMAIL_USERNAME')
        EMAIL_PASSWORD = form.pop('EMAIL_PASSWORD')
        EMAIL_SERVER = form.pop('EMAIL_SERVER')
        EMAIL_PORT = form.pop('EMAIL_PORT')
        EMAIL_REC_LIST = form.pop('EMAIL_REC_LIST')

        for it in userList:
            tmp = it[3]
            tmp.update(prefixDataObj)
            prefix_data = json.dumps(tmp, ensure_ascii=False)
            prefix_raw = 'data=' + quote(prefix_data)
            RAW = prefix_raw + suffix_raw
            rawList.append(RAW)
        return userList, rawList, EMAIL_ENABLE, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_SERVER, EMAIL_PORT, EMAIL_REC_LIST


class clockin():
    def __init__(self):
        self.retry = 0
        self.isIn = False
        self.readConfig()

    def readConfig(self):
        with open('./DontChange/schoolStaticInfo.json', 'r', encoding='utf-8') as fp:
            self.staticForm = json.load(fp=fp)

        with open('./local/config.json', 'r', encoding='utf-8') as fp:
            self.configForm = json.load(fp=fp)

    def getJSessionID(self, header):

        r1 = requests.get(url=self.staticForm['xgxtURL'], headers=header)
        # print('初始化JSessionID状态码：', r1.status_code)
        setcookie = r1.headers['Set-Cookie']
        # print(setcookie)
        # print('初始化JSessionIDcookie：', setcookie)
        self.strJSID = setcookie[:setcookie.index(';')]
        self.token = setcookie[setcookie.index(
            ',') + 8:setcookie.index('; Expires')]

    def login(self, username, password):
        while self.retry < 5 and (not self.isIn):
            self.getJSessionID(self.staticForm['captchaHeader'])
            self.captchaImgPath = './temp/' + \
                str(random.randint(100000, 999999)) + 'img.JFIF'
            try:
                self.retry += 1
                self.Jcookie = {'Cookie': self.strJSID}
                self.staticForm['captchaHeader'].update(self.Jcookie)
                self.staticForm['checkCaptchaRequiredHeader'].update(
                    self.Jcookie)
                chkCaptchaNeededRequest = requests.get(url=self.staticForm['checkCaptchaRequiredURL'],
                                                       headers=self.staticForm['checkCaptchaRequiredHeader'])
                print(username, '是否需要验证码请求结果：', chkCaptchaNeededRequest.status_code,
                      chkCaptchaNeededRequest.content.decode('utf-8'))
                if (chkCaptchaNeededRequest.content.decode('utf-8') == "false"):
                    self.captchaNeeded = False
                if (self.captchaNeeded):
                    CaptchaRequest = requests.get(url=self.staticForm['captchaURL'],
                                                  headers=self.staticForm['captchaHeader'])
                    print('\n验证码获取状态码：', CaptchaRequest.status_code)
                    with open(self.captchaImgPath, 'wb') as f:
                        f.write(CaptchaRequest.content)
                    captchaStat = self.captchaApi()
                    if (captchaStat != 0):
                        continue
                else:
                    self.captcha = ''
                user = base64.b64encode(
                    username.encode('utf-8')).decode('utf-8')
                pwd = base64.b64encode(
                    password.encode('utf-8')).decode('utf-8')
                loginData = {
                    'username': user,
                    'password': pwd,
                    'verification': self.captcha,
                    'token': self.token
                }
                self.staticForm['loginHeader'].update(self.Jcookie)
                loginPost = requests.post(url=self.staticForm['loginURL'], headers=self.staticForm['loginHeader'],
                                          data=loginData)
                # print('\n登录Post状态码：', loginPost.status_code)
                # print('loginPostheaders：', loginPost.headers)
                checkLogin = requests.get(
                    url=self.staticForm['checkLoginURL'], headers=self.staticForm['loginHeader'])
                if checkLogin.content.decode() == 'true':
                    print(username + '登陆成功')
                    self.isIn = True
                else:
                    print(checkLogin.content.decode())
                    print(username + '登陆失败')
                    self.isIn = False
            except:
                continue

    def daka(self, username, password, data3, location, userEmailName, EMAIL_ENABLE, EMAIL_USERNAME, EMAIL_PASSWORD,
             EMAIL_SERVER, EMAIL_PORT):
        self.login(username, password)
        flagFileName = './temp/' + username + 'Flag'
        if (self.isIn == True):
            self.staticForm['clockinHeader']['Cookie'] = 'menuVisible=1; username=' + \
                username + '; ' + self.strJSID
            clockinPost = requests.post(url=self.staticForm['clockinURL'], headers=self.staticForm['clockinHeader'],
                                        data=data3)
            # print(data3)
            # print('\n打卡post状态码：', clockinPost.status_code)
            if clockinPost.text == 'success':
                returnMsg = '成功打卡'
                print(username + returnMsg + '  ' +
                      str(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime())))
                with open(flagFileName, 'w', encoding='utf-8') as fp:
                    fp.write('0')
            else:
                if clockinPost.text == 'Applied today':
                    returnMsg = '今天已经打过卡'
                    print(username + ' ' + returnMsg + ' ' +
                          str(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime())))
                    with open(flagFileName, 'w', encoding='utf-8') as fp:
                        fp.write('1')
                else:
                    returnMsg = '打卡失败:登录成功,表单提交失败,请联系管理员'
                    print(username + returnMsg + '   ' +
                          str(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime())))
                    with open(flagFileName, 'w', encoding='utf-8') as fp:
                        fp.write('2')
        else:
            returnMsg = '打卡失败:登录失败,请联系管理员'
            print(username + returnMsg + '   ' +
                  str(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime())))
            with open(flagFileName, 'w', encoding='utf-8') as fp:
                fp.write('3')
        if EMAIL_ENABLE:
            try:
                body = str(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime())) + '\n' + 'username：%s' % (
                    username) + '\n打卡地点：' + location
                message = MIMEText(body, 'plain', 'utf-8')
                message['Subject'] = '疫情通打卡结果:' + returnMsg
                message['FROM'] = EMAIL_USERNAME
                message['To'] = userEmailName
                server = smtplib.SMTP(EMAIL_SERVER)
                server.connect(EMAIL_SERVER, EMAIL_PORT)
                server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USERNAME, [
                                userEmailName], message.as_string())
                print('个人提醒邮件发送成功')
            except:
                print('个人提醒邮件发送失败')

    def captchaApi(self):
        url = self.configForm['captchaSendRequestHost'] + \
            self.configForm['captchaSendRequestPath']
        url2 = self.configForm['captchaGetRequestHost'] + \
            self.configForm['captchaGetRequestPath']
        retryApiLimitRequest = 0
        while (True):
            retryApiLimitRequest += 1
            if retryApiLimitRequest > 50:
                return 1

            with open(self.captchaImgPath, 'rb') as f:
                contents = base64.b64encode(f.read())
            bodys = self.configForm['captchaSendRequestBody']
            bodys[self.configForm['captchaSendRespondBodyContentName']] = contents
            post_data = urllib.parse.urlencode(bodys).encode('utf-8')
            request = urllib.request.Request(url, post_data)
            for RHead in self.configForm['captchaSendRequestHead']:
                request.add_header(
                    RHead, self.configForm['captchaSendRequestHead'][RHead])
            response = urllib.request.urlopen(request)
            content = response.read()
            if content:
                returnDict = json.loads(content)
                if returnDict[self.configForm['captchaSendRequestOKName']] == self.configForm[
                        'captchaSendRequestOKCode']:
                    if (self.configForm['isCaptchaReqResSeparate']):
                        taskID = returnDict[self.configForm['captchaSendRequestTaskIDName']]
                        # print("\ntaskId:" + taskID)
                        break
                    else:
                        self.captcha = returnDict[self.configForm['captchaSendRequestCaptchaName']]
                        return 0
                else:
                    time.sleep(0.5)
        retryApiLimitRespond = 0
        while (self.configForm['isCaptchaReqResSeparate']):
            retryApiLimitRespond += 1
            if retryApiLimitRespond > 50:
                return 1
            bodys = self.configForm['captchaGetRespondBody']
            bodys[self.configForm['captchaGetRespondTaskIDName']] = taskID
            post_data = urllib.parse.urlencode(bodys).encode('utf-8')
            request = urllib.request.Request(url2, post_data)
            for RHead in self.configForm['captchaGetRequestHead']:
                request.add_header(
                    RHead, self.configForm['captchaGetRequestHead'][RHead])
            response = urllib.request.urlopen(request)
            content = response.read()
            content = content.decode('utf-8')
            # print(content)
            if content:
                returnDict = json.loads(content)
                if returnDict[self.configForm['captchaGetRequestOKName']] == self.configForm['captchaGetRequestOKCode']:
                    self.captcha = returnDict[self.configForm['captchaGetRespondBodyContentName']]
                    # print(self.captcha)
                    print('验证码获取成功')
                    return 0
                else:
                    time.sleep(0.5)


def daka_fun():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    app = handler()
    app.clockinHandler()
    shutil.rmtree('./temp')


if __name__ == '__main__':
    daka_fun()
