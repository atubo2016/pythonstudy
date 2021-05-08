# -*- coding: utf-8 -*-
import os
import sys
import _thread
import smtplib
import subprocess
import time
import csv
from email.mime.text import MIMEText
from email.utils import formataddr
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from common import holiday

# 修改履历： v1.0 初版做成
# 修改履历： v1.1 关闭chromedriver.exe 和 chrome.exe 进程
todayYmd = time.strftime("%Y%m%d", time.localtime())
todayY_m_d = time.strftime("%Y-%m-%d", time.localtime())
# 主进程日志文件
logfile = "D:/database/myfund/loadindustrylog.txt"
# 线程执行完毕标识文件（处理过程中出现，处理完毕后删除） 有几个线程，文件内容就有几个OK
resultlogfile = "D:/database/myfund/resultindustry.txt"
# 重要指数，行业信息 CSV文件名
industrylistfile = "D:/database/myfund/plateindexlist_" + todayYmd + '.csv'
# 线程出错日志
industryerrorlogfile = 'D:/database/myfund/pythonerror_industry.txt'


# 为线程定义一个函数
def searchplateindexlist():
    print('-----------------将要爬取 沪深重要指数 信息--------')
    global industrylistfile, resultlogfile, industryerrorlogfile, todayYmd, todayY_m_d, logfile
    url1 = 'http://quote.eastmoney.com/center/hszs.html'

    fo = open(logfile, 'a+')
    fo.writelines("板块指数取得开始！！！" + "\r\n")
    fo.close()

    # noinspection PyBroadException
    try:
        # 文件存在的话，就先删除
        if os.path.exists(industrylistfile):
            os.remove(industrylistfile)

        data1 = []
        title1 = ['代码', '名称', '日期', '指数', '涨跌值', '涨跌幅', '成交量', '成交额', '最高', '最低']
        data1.append(title1)

        chrome_options1 = Options()
        chrome_options1.add_argument('--headless')
        driver1 = webdriver.Chrome(options=chrome_options1)
        driver1.get(url1)
        time.sleep(2)

        # 取得指数列表长度
        hszs_table = driver1.find_element_by_xpath('//*[@id="hszs_hszyzs_simple-table"]/tbody')
        rows = hszs_table.find_elements_by_tag_name('tr')
        rownum = len(rows)

        for x in range(1, rownum + 1):
            # noinspection PyBroadException
            try:
                row = driver1.find_element_by_xpath('//*[@id="hszs_hszyzs_simple-table"]/tbody/tr[' + str(x) + ']')
                columns = row.find_elements_by_tag_name('td')

                temp = [columns[1].text, columns[2].text, todayY_m_d,
                        columns[3].text, columns[4].text, columns[5].text.replace("%", ""), ]

                # 成交量
                dailyturnoveramount = columns[6].text
                if dailyturnoveramount != dailyturnoveramount.replace("亿", ""):
                    dailyturnoverfloat = str(int(float(dailyturnoveramount.replace("亿", "")) * 100000000))
                elif dailyturnoveramount != dailyturnoveramount.replace("万", ""):
                    dailyturnoverfloat = str(int(float(dailyturnoveramount.replace("万", "")) * 10000))
                else:
                    dailyturnoverfloat = dailyturnoveramount

                temp.append(dailyturnoverfloat)

                # 成交额
                dailyturnover = columns[7].text
                if dailyturnover != dailyturnover.replace("亿", ""):
                    dailyturnoverfloat = str(int(float(dailyturnover.replace("亿", "")) * 100000000))
                elif dailyturnover != dailyturnover.replace("万", ""):
                    dailyturnoverfloat = str(int(float(dailyturnover.replace("万", "")) * 10000))
                else:
                    dailyturnoverfloat = dailyturnover

                temp.append(dailyturnoverfloat)

                # 最高
                temp.append(columns[10].text)
                # 最低
                temp.append(columns[11].text)

                data1.append(temp)

            except:
                fo = open(industryerrorlogfile, 'a+')
                fo.write(todayYmd + " 第 " + str(x) + " 指数爬取失败！！！\r\n")
                fo.close()
                continue  # 爬取失败，则继续下一条指数爬取

        with open(industrylistfile, 'a+', newline='') as csvfile1:
            writer1 = csv.writer(csvfile1)
            for row1 in data1:
                writer1.writerow(row1)

    except:
        fo = open(industryerrorlogfile, 'a+')
        fo.write(todayYmd + " " + url1 + " 指数网页打开失败！！！\r\n")
        fo.close()

    fo = open(resultlogfile, 'a+')
    fo.write("OK")
    fo.close()
    fo = open(logfile, 'a+')
    fo.writelines("板块指数取得结束！！！" + "\r\n")
    fo.close()


# ################### 股票数据抓取 主程序 ######################
if holiday.is_holiday():
    sys.exit(0)

# 移除result.txt
if os.path.exists(resultlogfile):
    os.remove(resultlogfile)

fo1 = open(logfile, 'a+')
startlogcontent = "################## 板块指数/行业指数 爬取结果 " + todayYmd + "##################"
fo1.writelines(startlogcontent + "\r\n")
fo1.close()

# 创建线程
strflg = ""
csvfilelist = []
# noinspection PyBroadException
try:
    strflg = strflg + "OK"
    csvfilelist.append(industrylistfile)
    _thread.start_new_thread(searchplateindexlist, (), )

except:
    print("Error: 无法启动线程")
    fo1 = open(logfile, 'a+')
    fo1.writelines("Error: 无法启动线程" + "\r\n")
    fo1.close()

print("预想文件内容：" + strflg)

while 1:
    time.sleep(8)
    str1 = ""
    if os.path.exists(resultlogfile):
        fo2 = open(resultlogfile, "r")
        str1 = fo2.read()
        print("实际文件内容：" + str1)
        fo2.close()

    if str1 == strflg:
        print("所有线程文件写入完毕！！！")
        fo1 = open(logfile, 'a+')
        fo1.writelines("所有线程文件写入完毕！！！" + "\r\n")
        fo1.close()
        break

# 移除resultstock.txt
if os.path.exists(resultlogfile):
    os.remove(resultlogfile)

# 修改履历： v1.1 关闭chromedriver.exe 和 chrome.exe 进程 start
os.system('taskkill /im chromedriver.exe /F')
os.system('taskkill /im chrome.exe /F')
# 修改履历： v1.1 关闭chromedriver.exe 和 chrome.exe 进程 end

fo1 = open(logfile, 'a+')

# Load data infile
for filename in csvfilelist:
    cmd = "mysql -uroot -p123456 myfund --local-infile -e" \
          " \"load data local infile '" + filename + "' " \
          "REPLACE into table plateindexhistory " \
          "CHARACTER SET gbk " \
          "FIELDS TERMINATED BY ',' " \
          "ENCLOSED BY '''' " \
          "LINES TERMINATED BY '\\r\\n' " \
          "IGNORE 1 LINES " \
          "(plateindexcode,plateindexname,businessday,indexvalue," \
          "changevalue,changepercent,dailyturnovernum,dailyturnover,indexvaluedailymax,indexvaluedailymin) " \
          "SET " \
          "updatedate = now();\""

    fo1.writelines(cmd)
    fo1.writelines("\r\n")

    cmd_res = {}
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    stdoutlines = res.stdout.readlines()
    stderrlines = res.stderr.readlines()

    for line in stdoutlines:
        fo1.writelines(line.decode('utf-8'))
    for line in stderrlines:
        fo1.writelines(line.decode('utf-8'))

fo1.writelines("今日板块数据写入完毕！！！" + "\r\n")
fo1.close()

mimetext = ""

# 整个批处理的日志
fo1 = open(logfile, 'r')

key1 = startlogcontent
error1 = False
key2 = "ERROR "
error2 = False

for line in fo1.readlines():
    if key1 in line:
        error1 = True

    if error1:
        if key2 in line:
            error2 = True

    if error1 and error2:
        mimetext = "板块行业批量导入出错了！！！\r\n" + mimetext
        break

fo1.close()

# 行业指数线程错误日志
if os.path.exists(industryerrorlogfile):
    fo1 = open(industryerrorlogfile, 'r')
    for line in fo1.readlines():
        if todayYmd + " " in line:
            # print(filename + " 爬取处理出错了！！！")
            mimetext = " pythonerror_industry.txt 板块行业爬取处理出错了！！！\r\n" + mimetext
            break
    fo1.close()

if mimetext == "":
    mimetext = "板块行业信息下载成功！！！"
print(mimetext)

try:
    my_sender = '8248585@qq.com'  # 发件人邮箱账号
    my_pass = 'djjrbacdtxaabjjh'  # 发件人邮箱密码
    my_user = '8248585@qq.com'  # 收件人邮箱账号，我这边发送给自己

    msg = MIMEText(mimetext, 'plain', 'utf-8')
    # noinspection PyTypeChecker
    msg['From'] = formataddr(["minnanzi", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    # noinspection PyTypeChecker
    msg['To'] = formataddr(["minnanzi", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg['Subject'] = '板块行业信息 ' + todayYmd  # 邮件的主题，也可以说是标题

    server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器（SSL），端口是465
    server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
    server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
    server.quit()  # 关闭连接

    fo1 = open(logfile, 'a+')
    fo1.writelines("邮件发送完毕！！！！！！" + "\r\n")
    fo1.close()

except Exception as e:
    # print('邮件发送失败！！！！！！' + str(e))
    fo1 = open(logfile, 'a+')
    fo1.writelines("邮件发送失败！！！！！！" + "\r\n")
    fo1.writelines(str(e))
    fo1.writelines("\r\n")
    fo1.close()

fo1 = open(logfile, 'a+')
fo1.writelines("全部处理结束！！！" + "\r\n")
fo1.close()
