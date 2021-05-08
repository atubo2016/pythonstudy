# -*- coding: utf-8 -*-
import _thread
import os
import smtplib
import subprocess
import sys
import pymysql
import time
import csv
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from email.mime.text import MIMEText
from email.utils import formataddr
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from common import holiday
from stock.stockcommon import stocksqlcommon


# 修改履历： v1.1 排除双休日 和 节假日
# 修改履历： v1.2 追加查找连板 和 连涨股票 功能
# 修改履历： v1.3 节假日函数抽共通
# 修改履历： v1.4 新股票导入股票基本表，同时更新股票名称
# 修改履历： v1.5 当日批处理失败重跑，删除已经生成的股票数据文件
# 修改履历： v1.6 处理过程中有错误的话，发邮件通知
# 修改履历： v1.7 规则1_连涨2天同时当日成交额放量3倍
# 修改履历： v1.8 按照交易策略1 购买股票，每股1手
# 修改履历： v1.8 根据购入履历更新股票持仓
# 修改履历： v1.9 SQL共通化
# 修改履历： v2.0 增加均线价格计算
# 修改履历： v2.1 更新持仓收益
# 修改履历： v2.2 关闭chromedriver.exe 和 chrome.exe 进程
# 为线程定义一个函数
def searchstocklist(startnum, tonum, lastpage):
    print('-----------------将要爬取 第{0} 到 第{1} 页股票信息--------'.format(startnum, tonum))
    # noinspection PyBroadException
    try:
        today1 = time.strftime("%Y%m%d", time.localtime())
        # today = '20210316'

        stocklistfile1 = 'D:\\database\\myfund\\stocklist_' + today1 + '_' + str(startnum).zfill(4) + '.csv'
        # print(stocklistfile1)
        # 修改履历： v1.5 当日批处理失败重跑，删除已经生成的股票数据文件 start
        # 文件存在的话，就先删除
        if os.path.exists(stocklistfile1):
            os.remove(stocklistfile1)
        # 修改履历： v1.5 当日批处理失败重跑，删除已经生成的股票数据文件 end

        data1 = []
        title1 = ['股票代码', '股票名称', '日期', '最新价', '涨跌幅', '成交额']
        data1.append(title1)

        url1 = 'http://quote.eastmoney.com/center/gridlist.html#hs_a_board'
        print(url1)
        chrome_options1 = Options()
        chrome_options1.add_argument('--headless')
        driver1 = webdriver.Chrome(options=chrome_options)
        driver1.get(url1)
        time.sleep(2)

        for i in range(startnum, tonum + 1):
            # noinspection PyBroadException
            try:

                print('----------------- 跳转到 {0} 页 -----------------'.format(str(i)))
                if i != 1:
                    # 取得翻页div
                    pagediv1 = driver1.find_element_by_xpath('//*[@id="main-table_paginate"]')
                    # 取得页码输入框
                    pagenoinput = pagediv1.find_elements_by_tag_name('input')
                    # 输入页码
                    pagenoinput[0].clear()
                    pagenoinput[0].send_keys(str(i))
                    # 取得GO按钮
                    gobutton = (pagediv1.find_elements_by_tag_name('a'))[-1]
                    # 点击GO按钮
                    ActionChains(driver1).click(gobutton).perform()
                    time.sleep(2)
                print('当前正在爬取第 ' + str(i) + ' 页股票')

                for x in range(1, 21):
                    # noinspection PyBroadException
                    try:
                        row = driver1.find_element_by_xpath('//*[@id="table_wrapper-table"]/tbody/tr[' + str(x) + ']')
                        columns = row.find_elements_by_tag_name('td')

                        # 股票代码
                        # 股票名称
                        # 最新价
                        # 涨跌幅
                        temp = [columns[1].text, columns[2].text, time.strftime("%Y-%m-%d", time.localtime()),
                                columns[4].text, columns[5].text.replace("%", "")]
                        # 成交额
                        dailyturnover = columns[8].text
                        if dailyturnover != dailyturnover.replace("亿", ""):
                            dailyturnoverfloat = str(int(float(dailyturnover.replace("亿", "")) * 100000000))
                        elif dailyturnover != dailyturnover.replace("万", ""):
                            dailyturnoverfloat = str(int(float(dailyturnover.replace("万", "")) * 10000))
                        else:
                            dailyturnoverfloat = dailyturnover

                        temp.append(dailyturnoverfloat)

                        data1.append(temp)
                    except:
                        # 最后一页 不满20条 的时候不出错误信息
                        # noinspection PyShadowingNames
                        if tonum != lastpage:
                            fo = open('D:\\database\\myfund\\pythonerror_stock_'
                                      + str(startnum).zfill(4) + '.txt', 'a+')
                            fo.write(today1 + " 第 " + str(i) + " 页 第 " + str(x) + " 股票爬取失败！！！\r\n")
                            fo.close()
                        continue  # 爬取失败，则继续下一条股票爬取
            except:
                # noinspection PyShadowingNames
                fo = open('D:\\database\\myfund\\pythonerror_stock_' + str(startnum).zfill(4) + '.txt', 'a+')
                fo.write(today1 + " 第 " + str(i) + " 页 股票爬取失败！！！\r\n")
                fo.close()
                continue  # 爬取失败，则继续下一条股票爬取

        with open(stocklistfile1, 'a+', newline='') as csvfile1:
            writer1 = csv.writer(csvfile1)
            for row1 in data1:
                writer1.writerow(row1)

        fo = open('D:\\database\\myfund\\resultstock.txt', 'a+')
        fo.write("OK")
        fo.close()
    except:
        fo = open('D:\\database\\myfund\\resultstock.txt', 'a+')
        fo.write("OK")
        fo.close()


# 修改履历： v1.3 节假日函数抽共通 start
# # 修改履历： v1.1 排除双休日 和 节假日
# # 休：工作日 变 节假日 （干脆把节日全部计入，不分周末了。反正都是休息日）
# holidays_exception = [
#     '20210405',  # 清明节,周一
#     '20210501',  # 劳动节,周六
#     '20210502',  # 劳动节,周日
#     '20210503',  # 劳动节,周一
#     '20210504',  # 劳动节,周二
#     '20210505',  # 劳动节,周三
#     '20210612',  # 端午节,周六
#     '20210613',  # 端午节,周日
#     '20210614',  # 端午节,周一
#     '20210919',  # 中秋节,周日
#     '20210920',  # 中秋节,周一
#     '20210921',  # 中秋节,周二
#     '20211001',  # 国庆节,周五
#     '20211002',  # 国庆节,周六
#     '20211003',  # 国庆节,周日
#     '20211004',  # 国庆节,周一
#     '20211005',  # 国庆节,周二
#     '20211006',  # 国庆节,周三
#     '20211007',  # 国庆节,周四
# ]
#
# # 班：周末 变 工作日
# workdays_exception = [
#     '88888888',  # 这种情况下股市也不开，不用定义
# ]
#
#
# def is_workday(day=None):
#     """
#         Args:
#             day: 日期, 默认为今日
#
#         Returns:
#             True: 上班
#             False: 放假
#     """
#     # 如果不传入参数则为今天
#     today2 = datetime.today()
#     # logger.info(today)
#     day = day or today2
#
#     week_day = datetime.weekday(day) + 1  # 今天星期几(星期一 = 1，周日 = 7)
#     is_work_day_in_week = week_day in range(1, 6)  # 这周是不是非周末，正常工作日, 不考虑调假
#     day_str = f'{day.year}{str(day.month).zfill(2)}{str(day.day).zfill(2)}'
#
#     if day_str in workdays_exception:  # 班：周末 变 上班日
#         return True
#     elif day_str in holidays_exception:  # 休：工作日 变 节假日
#         return False
#     elif is_work_day_in_week:  # 周末
#         return True
#     else:
#         return False
#
#
# def is_holiday(day=None):
#     # 如果不传入参数则为今天
#     today3 = datetime.today()
#     day = day or today3
#     if is_workday(day):
#         return False
#     else:
#         return True
# # 修改履历： v1.1 排除双休日 和 节假日
# 修改履历： v1.3 节假日函数抽共通 end

# ################### 股票数据抓取 主程序 ######################
# 修改履历： v1.1 排除双休日 和 节假日
# 修改履历： v1.3 节假日函数抽共通 start
# if is_holiday():
if holiday.is_holiday():
    sys.exit(0)
# 修改履历： v1.3 节假日函数抽共通 end
# 修改履历： v1.1 排除双休日 和 节假日

# 移除result.txt
if os.path.exists('D:\\database\\myfund\\resultstock.txt'):
    os.remove('D:\\database\\myfund\\resultstock.txt')

today = time.strftime("%Y%m%d", time.localtime())
today2 = time.strftime("%Y-%m-%d", time.localtime())

fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
fo1.writelines("################## 股票爬取结果 " + today + "##################\r\n")

url = 'http://quote.eastmoney.com/center/gridlist.html#hs_a_board'
print(url)
fo1.writelines("东方财富网URL: " + url + "\r\n")

chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

print('-----------------连接东方财富网-----------------')
fo1.writelines("-----------------连接东方财富网-----------------" + "\r\n")
time.sleep(3)

pagediv = driver.find_element_by_xpath('//*[@id="main-table_paginate"]')
pagelinkspans = pagediv.find_elements_by_tag_name('span')
alinks = pagelinkspans[0].find_elements_by_tag_name('a')
# 取得最后一页 的 页码
maxpage = alinks[-1].text

# 修改履历： v2.2 关闭chromedriver.exe 和 chrome.exe 进程 start
os.system('taskkill /im chromedriver.exe /F')
os.system('taskkill /im chrome.exe /F')
# 修改履历： v2.2 关闭chromedriver.exe 和 chrome.exe 进程 end

print('-----------------将要爬取 {0} 页股票信息--------'.format(maxpage))
fo1.writelines("-----------------将要爬取 {0} 页股票信息--------".format(maxpage) + "\r\n")
fo1.close()

# 创建线程
strflg = ""
csvfilelist = []
# noinspection PyBroadException
try:
    for j in range(0, int(maxpage) // 60 + 1):
        strflg = strflg + "OK"
        csvfilelist.append('D:/database/myfund/stocklist_' + today + '_' + str(1 + j * 60).zfill(4) + '.csv')
        if j != int(maxpage) // 60:
            _thread.start_new_thread(searchstocklist, (1 + j * 60, (j + 1) * 60, int(maxpage),))
        else:
            _thread.start_new_thread(searchstocklist, (1 + j * 60, int(maxpage), int(maxpage),))
        time.sleep(120)
except:
    print("Error: 无法启动线程")
    fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
    fo1.writelines("Error: 无法启动线程" + "\r\n")
    fo1.close()

print("预想文件内容：" + strflg)

while 1:
    time.sleep(8)
    str1 = ""
    if os.path.exists('D:\\database\\myfund\\resultstock.txt'):
        fo2 = open('D:\\database\\myfund\\resultstock.txt', "r")
        str1 = fo2.read()
        print("实际文件内容：" + str1)
        fo2.close()

    if str1 == strflg:
        print("所有线程文件写入完毕！！！")
        fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
        fo1.writelines("所有线程文件写入完毕！！！" + "\r\n")
        fo1.close()
        break

# 移除resultstock.txt
if os.path.exists('D:\\database\\myfund\\resultstock.txt'):
    os.remove('D:\\database\\myfund\\resultstock.txt')

# 修改履历： v2.2 关闭chromedriver.exe 和 chrome.exe 进程 start
os.system('taskkill /im chromedriver.exe /F')
os.system('taskkill /im chrome.exe /F')
# 修改履历： v2.2 关闭chromedriver.exe 和 chrome.exe 进程 end

fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')

# Load data infile
for filename in csvfilelist:
    cmd = "mysql -uroot -p123456 myfund --local-infile -e" \
          " \"load data local infile '" + filename + "' " \
          "REPLACE into table stockhistory " \
          "CHARACTER SET gbk " \
          "FIELDS TERMINATED BY ',' " \
          "ENCLOSED BY '''' " \
          "LINES TERMINATED BY '\\r\\n' " \
          "IGNORE 1 LINES " \
          "(stockcode,stockname,businessday,@price,@changepercent,@dailyturnover) " \
          "SET " \
          "price = CASE WHEN @price<>'-' THEN @price END," \
          "changepercent = CASE WHEN @changepercent<>'-' THEN @changepercent END," \
          "dailyturnover = CASE WHEN @dailyturnover<>'-' THEN @dailyturnover END," \
          "downloaddate = now();\""

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

fo1.writelines("今日股票数据写入完毕！！！" + "\r\n")
fo1.close()

# 打开数据库连接
db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='myfund', charset='utf8')
# 使用cursor方法创建一个游标
cursor = db.cursor()

# 修改履历： v1.4 新股票导入股票基本表，同时更新股票名称 start
sql = "insert " \
      "    into " \
      "    stock(stockcode, " \
      "    stockname, " \
      "    updatedate) " \
      "select " \
      "    b.stockcode, " \
      "    b.stockname, " \
      "    now() " \
      "from " \
      "    ( " \
      "    select " \
      "        h.stockcode as stockcode , " \
      "        max(h.businessday) as maxdate " \
      "    from " \
      "        ( " \
      "        select " \
      "            stockcode, " \
      "            businessday " \
      "        from " \
      "            stockhistory a " \
      "        where " \
      "            not exists ( " \
      "            select " \
      "                * " \
      "            from " \
      "                stock b " \
      "            where " \
      "                a.stockcode = b.stockcode)) h " \
      "    group by " \
      "        h.stockcode) a, " \
      "    stockhistory b " \
      "where " \
      "    b.stockcode = a.stockcode " \
      "    and b.businessday = a.maxdate "

fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
fo1.writelines("SQL = " + sql + "\r\n")
fo1.writelines("新股票导入股票基本表" + "\r\n")
cursor.execute(sql)
db.commit()

sql = "with d as ( "
sql = sql + stocksqlcommon.sql_lateststock
sql = sql + " )  " \
      "update " \
      "    stock c " \
      "set " \
      "    c.stockname =( " \
      "    select " \
      "        d.stockname " \
      "    from " \
      "        d " \
      "    where " \
      "        c.stockcode = d.stockcode " \
      "        and c.stockname <> d.stockname) " \
      "where " \
      "    exists ( " \
      "    select " \
      "        1 " \
      "    from " \
      "        d " \
      "    where " \
      "        c.stockcode = d.stockcode " \
      "        and c.stockname <> d.stockname) "

fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
fo1.writelines("SQL = " + sql + "\r\n")
fo1.writelines("更新股票名称" + "\r\n")
cursor.execute(sql)
db.commit()
# 修改履历： v1.4 新股票导入股票基本表，同时更新股票名称 end

# ################ 以下开始分析 ##################
# 修改履历： v2.0 增加均线价格计算 start
sql = " delete from stockavghistory where businessday = '{0}' ".format(today2)
cursor.execute(sql)

sql = "insert into stockavghistory ( " \
      "    stockcode " \
      "    ,businessday " \
      "    ,avg5 " \
      "    ,avg10 " \
      "    ,avg20 " \
      "    ,avg30 " \
      "    ,avg60 " \
      "    ,avg120 " \
      "    ,avg240 " \
      "    ,avg480 " \
      "    ,avgfromstart  " \
      "    ,updatedate) " \
      "with pricegroup as ( " \
      "    select " \
      "        a.stockcode as stockcode, " \
      "        a.businessday as businessday, " \
      "        a.price as price, " \
      "        if(@stockcode = a.stockcode, " \
      "        @rownum := @rownum + 1, " \
      "        @rownum := 1 ) as rownum, " \
      "        (@stockcode := a.stockcode) as stockcodetmp " \
      "    from " \
      "        stockhistory a, " \
      "        (select @rownum := 0,@stockcode := NULL) b   " \
      "    where  " \
      "        a.changepercent is not null " \
      "    order by " \
      "        stockcode asc, " \
      "        businessday desc " \
      "), " \
      "pricemaxno as ( " \
      "    select stockcode,count(1) as maxno from stockhistory group by stockcode  " \
      ") " \
      "select  " \
      "    pricemaxno.stockcode " \
      "    ,DATE_FORMAT(NOW(),'%Y-%m-%d')   " \
      "    ,avg5.price_avg5 " \
      "    ,avg10.price_avg10 " \
      "    ,avg20.price_avg20 " \
      "    ,avg30.price_avg30 " \
      "    ,avg60.price_avg60 " \
      "    ,avg120.price_avg120 " \
      "    ,avg240.price_avg240 " \
      "    ,avg480.price_avg480 " \
      "    ,avgfromstart.price_avgfromstart " \
      "    ,now() " \
      "from  " \
      "    pricemaxno " \
      "left outer join " \
      "    ( " \
      "    select pricegroup.stockcode as stockcode , avg(pricegroup.price) as price_avg5 " \
      "    from  " \
      "        pricegroup " \
      "    where pricegroup.rownum < 6 " \
      "    group by pricegroup.stockcode " \
      "    ) avg5 " \
      "ON  " \
      "    pricemaxno.stockcode = avg5.stockcode " \
      "    and pricemaxno.maxno > 5 " \
      "left outer join " \
      "    ( " \
      "    select pricegroup.stockcode as stockcode , avg(pricegroup.price) as price_avg10 " \
      "    from              " \
      "        pricegroup " \
      "    where pricegroup.rownum < 11 " \
      "    group by pricegroup.stockcode " \
      "    ) avg10 " \
      "ON  " \
      "    pricemaxno.stockcode = avg10.stockcode " \
      "    and pricemaxno.maxno > 10 " \
      "left outer join " \
      "    ( " \
      "    select pricegroup.stockcode as stockcode, avg(pricegroup.price) as price_avg20 " \
      "    from              " \
      "        pricegroup " \
      "    where pricegroup.rownum < 21 " \
      "    group by pricegroup.stockcode " \
      "    ) avg20 " \
      "ON  " \
      "    pricemaxno.stockcode = avg20.stockcode " \
      "    and pricemaxno.maxno > 20 " \
      "left outer join " \
      "    ( " \
      "    select pricegroup.stockcode as stockcode, avg(pricegroup.price) as price_avg30 " \
      "    from              " \
      "        pricegroup " \
      "    where pricegroup.rownum < 31 " \
      "    group by pricegroup.stockcode " \
      "    ) avg30 " \
      "ON  " \
      "    pricemaxno.stockcode = avg30.stockcode " \
      "    and pricemaxno.maxno > 30 " \
      "left outer join " \
      "    ( " \
      "    select pricegroup.stockcode as stockcode, avg(pricegroup.price) as price_avg60 " \
      "    from              " \
      "        pricegroup " \
      "    where pricegroup.rownum < 61 " \
      "    group by pricegroup.stockcode " \
      "    ) avg60 " \
      "ON  " \
      "    pricemaxno.stockcode = avg60.stockcode " \
      "    and pricemaxno.maxno > 60 " \
      "left outer join " \
      "    ( " \
      "    select pricegroup.stockcode as stockcode, avg(pricegroup.price) as price_avg120 " \
      "    from              " \
      "        pricegroup " \
      "    where pricegroup.rownum < 121 " \
      "    group by pricegroup.stockcode " \
      "    ) avg120 " \
      "ON  " \
      "    pricemaxno.stockcode = avg120.stockcode " \
      "    and pricemaxno.maxno > 120 " \
      "left outer join " \
      "    ( " \
      "    select pricegroup.stockcode as stockcode, avg(pricegroup.price) as price_avg240 " \
      "    from              " \
      "        pricegroup " \
      "    where pricegroup.rownum < 241 " \
      "    group by pricegroup.stockcode " \
      "    ) avg240 " \
      "ON  " \
      "    pricemaxno.stockcode = avg240.stockcode " \
      "    and pricemaxno.maxno > 240 " \
      "left outer join " \
      "    ( " \
      "    select pricegroup.stockcode as stockcode, avg(pricegroup.price) as price_avg480 " \
      "    from              " \
      "        pricegroup " \
      "    where pricegroup.rownum < 481 " \
      "    group by pricegroup.stockcode " \
      "    ) avg480 " \
      "ON  " \
      "    pricemaxno.stockcode = avg480.stockcode " \
      "    and pricemaxno.maxno > 480 " \
      "left outer join " \
      "    ( " \
      "    select pricegroup.stockcode as stockcode, avg(pricegroup.price) as price_avgfromstart " \
      "    from              " \
      "        pricegroup " \
      "    group by pricegroup.stockcode " \
      "    ) avgfromstart " \
      "ON  " \
      "    pricemaxno.stockcode = avgfromstart.stockcode "

fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
fo1.writelines("SQL = " + sql + "\r\n")
fo1.writelines("计算均线价格" + "\r\n")
fo1.close()
cursor.execute(sql)
db.commit()

# 修改履历： v2.0 增加均线价格计算 end

# 修改履历： v1.2 追加查找连板 和 连涨股票 功能 start
mimetext = ""
mimetext = mimetext + today + " 4连涨以上股票 如下：\r\n"
sql = "select " \
      "d.stockcode as stockcode, e.stockname as stockname, concat(d.ranking - 1, '连涨') " \
      "from ( " \
      "    select c.stockcode as stockcode, min(c.rownum) as ranking " \
      "    from  " \
      "    ( " \
      "        select " \
      "            a.stockcode as stockcode, " \
      "            a.businessday as businessday, " \
      "            a.changepercent as changepercent, " \
      "            if(@stockcode = a.stockcode, " \
      "            @rownum := @rownum + 1, " \
      "            @rownum := 1 ) as rownum, " \
      "            (@stockcode := a.stockcode) as stockcodetmp " \
      "        from " \
      "            stockhistory a, " \
      "            (select @rownum := 0,@stockcode := NULL) b " \
      "        where  " \
      "            a.changepercent is not null " \
      "        order by " \
      "            stockcode asc, " \
      "            businessday desc " \
      "    ) c " \
      "    where  " \
      "        c.changepercent < 0  " \
      "    group by  " \
      "        c.stockcode  " \
      "    order by  " \
      "        ranking desc  " \
      ") d, stock e " \
      "where  " \
      "    d.stockcode = e.stockcode  " \
      "    and ranking > 4 "

cursor.execute(sql)
myresult = cursor.fetchall()
for y in myresult:
    mimetext = mimetext + str(y) + "\r\n"
mimetext = mimetext + "\r\n"

fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
fo1.writelines("SQL = " + sql + "\r\n")
fo1.writelines("查找4连涨以上股票" + "\r\n")
fo1.close()

mimetext = mimetext + today + " 2连板以上股票 如下：\r\n"

sql = "select " \
      "d.stockcode as stockcode, e.stockname as stockname, concat(d.ranking - 1, '连板') " \
      "from ( " \
      "    select c.stockcode as stockcode, min(c.rownum) as ranking " \
      "    from  " \
      "    ( " \
      "        select " \
      "            a.stockcode as stockcode, " \
      "            a.businessday as businessday, " \
      "            a.changepercent as changepercent, " \
      "            if(@stockcode = a.stockcode, " \
      "            @rownum := @rownum + 1, " \
      "            @rownum := 1 ) as rownum, " \
      "            (@stockcode := a.stockcode) as stockcodetmp " \
      "        from " \
      "            stockhistory a, " \
      "            (select @rownum := 0,@stockcode := NULL) b " \
      "        where  " \
      "            a.changepercent is not null " \
      "        order by " \
      "            stockcode asc, " \
      "            businessday desc " \
      "    ) c " \
      "    where  " \
      "        c.changepercent < 9.6 " \
      "    group by  " \
      "        c.stockcode  " \
      "    order by  " \
      "        ranking desc  " \
      ") d, stock e " \
      "where  " \
      "    d.stockcode = e.stockcode  " \
      "    and ranking > 2 "

cursor.execute(sql)
myresult = cursor.fetchall()
for y in myresult:
    mimetext = mimetext + str(y) + "\r\n"

fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
fo1.writelines("SQL = " + sql + "\r\n")
fo1.writelines("查找2连板以上股票" + "\r\n")
fo1.close()

# 修改履历： v1.7 规则1_连涨2天同时当日成交额放量3倍 start
mimetext = mimetext + "\r\n"
mimetext = mimetext + today + " 规则1_连涨2天同时当日成交额放量3倍 如下：\r\n"

# 修改履历： v1.9 SQL共通化 start
# sql = "with rise2day as ( " \
#       "    select d.stockcode as stockcode " \
#       "    from ( " \
#       "        select c.stockcode as stockcode, min(c.rownum) as ranking " \
#       "        from  " \
#       "        ( " \
#       "            select " \
#       "                a.stockcode as stockcode, " \
#       "                a.businessday as businessday, " \
#       "                a.changepercent as changepercent, " \
#       "                if(@stockcode = a.stockcode, " \
#       "                @rownum := @rownum + 1, " \
#       "                @rownum := 1 ) as rownum, " \
#       "                (@stockcode := a.stockcode) as stockcodetmp " \
#       "            from " \
#       "                stockhistory a, " \
#       "                (select @rownum := 0,@stockcode := NULL) b " \
#       "            where  " \
#       "                a.changepercent is not null " \
#       "            order by " \
#       "                stockcode asc, " \
#       "                businessday desc " \
#       "        ) c " \
#       "        where  " \
#       "            c.changepercent < 0  " \
#       "        group by  " \
#       "            c.stockcode  " \
#       "        order by  " \
#       "            ranking asc  " \
#       "    ) d " \
#       "    where  " \
#       "        ranking = 3 " \
#       ")  " \
#       "select  " \
#       "    after2day.stockcode " \
#       "    ,stock.stockname " \
#       "    ,concat(ROUND(after2day.avg2day_after/before2day.avg2day_before,1), '倍') as increasement " \
#       "from  " \
#       "( " \
#       "    select " \
#       "        c.stockcode as stockcode " \
#       "        ,avg(c.dailyturnover) as avg2day_after " \
#       "    from " \
#       "        ( " \
#       "        select " \
#       "            a.stockcode as stockcode " \
#       "            ,a.businessday as businessday " \
#       "            ,a.changepercent as changepercent " \
#       "            ,a.dailyturnover as dailyturnover  " \
#       "            ,if(@stockcode = a.stockcode, " \
#       "                @rownum := @rownum + 1, " \
#       "                @rownum := 1 ) as rownum " \
#       "            ,(@stockcode := a.stockcode) as stockcodetmp " \
#       "        from " \
#       "            stockhistory a, " \
#       "            (select @rownum := 0,@stockcode := NULL) b " \
#       "        where  " \
#       "            a.changepercent is not null " \
#       "        order by " \
#       "            stockcode asc, " \
#       "            businessday desc " \
#       "        ) c " \
#       "        ,rise2day " \
#       "    where " \
#       "        c.rownum <= 2 " \
#       "        and c.stockcode = rise2day.stockcode " \
#       "    group by  " \
#       "        c.stockcode " \
#       ") after2day, " \
#       "( " \
#       "    select " \
#       "        c.stockcode as stockcode " \
#       "        ,avg(c.dailyturnover) as avg2day_before " \
#       "    from " \
#       "        ( " \
#       "        select " \
#       "            a.stockcode as stockcode " \
#       "            ,a.businessday as businessday " \
#       "            ,a.changepercent as changepercent " \
#       "            ,a.dailyturnover as dailyturnover " \
#       "            ,if(@stockcode = a.stockcode, " \
#       "                @rownum := @rownum + 1, " \
#       "                @rownum := 1 ) as rownum " \
#       "            ,(@stockcode := a.stockcode) as stockcodetmp " \
#       "        from " \
#       "            stockhistory a, " \
#       "            (select @rownum := 0,@stockcode := NULL) b " \
#       "        where  " \
#       "            a.changepercent is not null " \
#       "        order by " \
#       "            stockcode asc, " \
#       "            businessday desc " \
#       "        ) c " \
#       "        , rise2day " \
#       "    where " \
#       "        c.rownum > 2 " \
#       "        and c.stockcode = rise2day.stockcode " \
#       "    group by  " \
#       "        c.stockcode " \
#       ") before2day " \
#       ", stock " \
#       "where  " \
#       "  after2day.stockcode = before2day.stockcode " \
#       "  and after2day.avg2day_after/before2day.avg2day_before > 3 " \
#       "  and after2day.stockcode = stock.stockcode  " \
#       "order by " \
#       "  after2day.avg2day_after/before2day.avg2day_before desc  "

sql = "with rise2day as ( "
sql = sql + stocksqlcommon.sql_rise2day
sql = sql + ")  " \
      "select  " \
      "    after2day.stockcode " \
      "    ,stock.stockname " \
      "    ,concat(ROUND(after2day.avg2day_after/before2day.avg2day_before,1), '倍') as increasement " \
      "from  " \
      "( "
sql = sql + stocksqlcommon.sql_after2day
sql = sql + ") after2day, " \
      "( "
sql = sql + stocksqlcommon.sql_before2day
sql = sql + ") before2day " \
      ", stock " \
      "where  " \
      "  after2day.stockcode = before2day.stockcode " \
      "  and after2day.avg2day_after/before2day.avg2day_before > 3 " \
      "  and after2day.stockcode = stock.stockcode  " \
      "order by " \
      "  after2day.avg2day_after/before2day.avg2day_before desc  "
# 修改履历： v1.9 SQL共通化 end

cursor.execute(sql)
myresult = cursor.fetchall()
for y in myresult:
    mimetext = mimetext + str(y) + "\r\n"

fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
fo1.writelines("SQL = " + sql + "\r\n")
fo1.writelines("查找连涨2天同时当日成交额放量3倍以上股票" + "\r\n")
fo1.close()
# 修改履历： v1.7 规则1_连涨2天同时当日成交额放量3倍 end

# 修改履历： v1.6 处理过程中有错误的话，发邮件通知 start
# 整个批处理的日志
fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'r')

key1 = "################## 股票爬取结果 " + today + "##################"
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
        mimetext = "股票数据批量导入出错了！！！\r\n" + mimetext
        break

fo1.close()

# 单个爬取日志
filter_file_name = "pythonerror_stock_"
filter_file_error = today + " "

for filename in os.listdir("D:\\database\\myfund"):
    if filter_file_name in filename:
        fp = os.path.join("D:\\database\\myfund", filename)
        if os.path.isfile(fp):
            with open(fp) as f:
                for line in f:
                    if filter_file_error in line:
                        # print(filename + " 爬取处理出错了！！！")
                        mimetext = filename + " 爬取处理出错了！！！\r\n" + mimetext
                        break

# 修改履历： v1.6 处理过程中有错误的话，发邮件通知 end

# 修改履历： v1.8 按照交易策略1 购买股票，每股1手 start
# 修改履历： v1.9 SQL共通化 start
# sql = "insert into " \
#       "stockdealhistory( " \
#       "        stockcode " \
#       "        ,dealpolicy " \
#       "        ,dealdate " \
#       "        ,dealprice " \
#       "        ,dealtype " \
#       "        ,dealamount " \
#       "        ,updatedate) " \
#       "with rise2day as ( " \
#       "    select d.stockcode as stockcode " \
#       "    from ( " \
#       "        select c.stockcode as stockcode, min(c.rownum) as ranking " \
#       "        from  " \
#       "        ( " \
#       "            select " \
#       "                a.stockcode as stockcode, " \
#       "                a.businessday as businessday, " \
#       "                a.changepercent as changepercent, " \
#       "                if(@stockcode = a.stockcode, " \
#       "                @rownum := @rownum + 1, " \
#       "                @rownum := 1 ) as rownum, " \
#       "                (@stockcode := a.stockcode) as stockcodetmp " \
#       "            from " \
#       "                stockhistory a, " \
#       "                (select @rownum := 0,@stockcode := NULL) b  " \
#       "            where  " \
#       "                a.changepercent is not null " \
#       "            order by " \
#       "                stockcode asc, " \
#       "                businessday desc " \
#       "        ) c " \
#       "        where " \
#       "            c.changepercent < 0 " \
#       "        group by " \
#       "            c.stockcode  " \
#       "        order by  " \
#       "            ranking asc  " \
#       "    ) d " \
#       "    where  " \
#       "        ranking = 3 " \
#       ")  " \
#       "select " \
#       "    after2day.stockcode " \
#       "    ,1  " \
#       "    ,'{0}' " \
#       "    ,stockhistory.price " \
#       "    ,'1' " \
#       "    ,100 " \
#       "    ,now() " \
#       "from  " \
#       "( " \
#       "    select " \
#       "        c.stockcode as stockcode " \
#       "        ,avg(c.dailyturnover) as avg2day_after  " \
#       "    from " \
#       "        ( " \
#       "        select " \
#       "            a.stockcode as stockcode " \
#       "            ,a.businessday as businessday " \
#       "            ,a.changepercent as changepercent " \
#       "            ,a.dailyturnover as dailyturnover " \
#       "            ,if(@stockcode = a.stockcode, " \
#       "                @rownum := @rownum + 1, " \
#       "                @rownum := 1 ) as rownum " \
#       "            ,(@stockcode := a.stockcode) as stockcodetmp " \
#       "        from " \
#       "            stockhistory a, " \
#       "            (select @rownum := 0,@stockcode := NULL) b  " \
#       "        where  " \
#       "            a.changepercent is not null " \
#       "        order by " \
#       "            stockcode asc, " \
#       "            businessday desc " \
#       "        ) c " \
#       "        ,rise2day " \
#       "    where " \
#       "        c.rownum <= 2  " \
#       "        and c.stockcode = rise2day.stockcode " \
#       "    group by  " \
#       "        c.stockcode " \
#       ") after2day, " \
#       "( " \
#       "    select " \
#       "        c.stockcode as stockcode " \
#       "        ,avg(c.dailyturnover) as avg2day_before  " \
#       "    from " \
#       "        ( " \
#       "        select " \
#       "            a.stockcode as stockcode " \
#       "            ,a.businessday as businessday " \
#       "            ,a.changepercent as changepercent " \
#       "            ,a.dailyturnover as dailyturnover " \
#       "            ,if(@stockcode = a.stockcode, " \
#       "                @rownum := @rownum + 1, " \
#       "                @rownum := 1 ) as rownum " \
#       "            ,(@stockcode := a.stockcode) as stockcodetmp " \
#       "        from " \
#       "            stockhistory a, " \
#       "            (select @rownum := 0,@stockcode := NULL) b  " \
#       "        where  " \
#       "            a.changepercent is not null " \
#       "        order by " \
#       "            stockcode asc, " \
#       "            businessday desc " \
#       "        ) c " \
#       "        , rise2day " \
#       "    where " \
#       "        c.rownum > 2  " \
#       "        and c.stockcode = rise2day.stockcode " \
#       "    group by  " \
#       "        c.stockcode " \
#       ") before2day " \
#       ", stock " \
#       ", stockhistory  " \
#       "where  " \
#       "    after2day.stockcode not in " \
#       "    (select stockcode from stockdealhistory where dealpolicy = 1 and dealtype = '1') " \
#       "    and after2day.stockcode = before2day.stockcode " \
#       "    and after2day.stockcode = stockhistory.stockcode " \
#       "    and stockhistory.businessday = '{1}' " \
#       "    and after2day.avg2day_after/before2day.avg2day_before > 3   " \
#       "    and after2day.stockcode = stock.stockcode  "
sql = "insert into " \
      "stockdealhistory( " \
      "        stockcode " \
      "        ,dealpolicy " \
      "        ,dealdate " \
      "        ,dealprice " \
      "        ,dealtype " \
      "        ,dealamount " \
      "        ,updatedate) " \
      "with rise2day as ( "
sql = sql + stocksqlcommon.sql_rise2day
sql = sql + ")  " \
      "select " \
      "    after2day.stockcode " \
      "    ,1  " \
      "    ,'{0}' " \
      "    ,stockhistory.price " \
      "    ,'1' " \
      "    ,100 " \
      "    ,now() " \
      "from  " \
      "( "
sql = sql + stocksqlcommon.sql_after2day
sql = sql + ") after2day, " \
      "( "
sql = sql + stocksqlcommon.sql_before2day
sql = sql + ") before2day " \
      ", stock " \
      ", stockhistory  " \
      "where  " \
      "    after2day.stockcode not in " \
      "    (select stockcode from stockdealhistory where dealpolicy = 1 and dealtype = '1') " \
      "    and after2day.stockcode = before2day.stockcode " \
      "    and after2day.stockcode = stockhistory.stockcode " \
      "    and stockhistory.businessday = '{1}' " \
      "    and after2day.avg2day_after/before2day.avg2day_before > 3   " \
      "    and after2day.stockcode = stock.stockcode  "
# 注意这里是 买过的 就不买了 after2day.stockcode not in
# 修改履历： v1.9 SQL共通化 end

fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
fo1.writelines("SQL = " + sql.format(today2, today2) + "\r\n")
fo1.writelines("按照交易策略1 购买股票，每股1手" + "\r\n")
fo1.close()

cursor.execute(sql.format(today2, today2))
db.commit()
# 修改履历： v1.8 按照交易策略1 购买股票，每股1手 end

# 修改履历： v1.8 根据购入履历更新股票持仓 start
# 每天重新计算持仓
sql = " delete from stockholdings "
cursor.execute(sql)

sql = "insert into stockholdings ( " \
      "    stockcode " \
      "    ,dealpolicy " \
      "    ,holdingprice " \
      "    ,holdingamount " \
      "    ,updatedate) " \
      "select  " \
      "    b.stockcode " \
      "    ,b.dealpolicy " \
      "    ,case when sum(b.dealamount) = 0 then 0 else sum(b.dealprice * b.dealamount)/sum(b.dealamount) end " \
      "    ,sum(b.dealamount) " \
      "    ,now() " \
      "from ( " \
      "    select  " \
      "        a.stockcode as stockcode " \
      "        ,a.dealpolicy as dealpolicy  " \
      "        ,a.dealtype as dealtype  " \
      "        ,a.dealprice as dealprice  " \
      "        ,case when a.dealtype = '2' then 0 - sum(a.dealamount) else sum(a.dealamount) end as dealamount  " \
      "    from  " \
      "    stockdealhistory a " \
      "    group by  " \
      "    a.stockcode ,a.dealpolicy ,a.dealtype ,a.dealprice  " \
      ") b " \
      "group by  " \
      "b.stockcode,b.dealpolicy "

fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
fo1.writelines("SQL = " + sql + "\r\n")
fo1.writelines("根据购入履历更新股票持仓" + "\r\n")
fo1.close()

cursor.execute(sql)
db.commit()
# 修改履历： v1.8 根据购入履历更新股票持仓 end

# 修改履历： v2.1 更新持仓收益 start
sql = "with d as ( "
sql = sql + stocksqlcommon.sql_lateststock
sql = sql + " )  " \
      "update " \
      "    stockholdings c " \
      "set " \
      "    c.increasement =( " \
      "    select " \
      "        d.price / c.holdingprice " \
      "    from " \
      "        d " \
      "    where " \
      "        c.stockcode = d.stockcode) " \

fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
fo1.writelines("SQL = " + sql + "\r\n")
fo1.writelines("更新持仓收益" + "\r\n")
fo1.close()

cursor.execute(sql)
db.commit()
# 修改履历： v2.1 更新持仓收益 end

try:
    my_sender = '8248585@qq.com'  # 发件人邮箱账号
    my_pass = 'djjrbacdtxaabjjh'  # 发件人邮箱密码
    my_user = '8248585@qq.com'  # 收件人邮箱账号，我这边发送给自己

    msg = MIMEText(mimetext, 'plain', 'utf-8')
    # noinspection PyTypeChecker
    msg['From'] = formataddr(["minnanzi", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    # noinspection PyTypeChecker
    msg['To'] = formataddr(["minnanzi", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg['Subject'] = '股票信息 ' + today  # 邮件的主题，也可以说是标题

    server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器（SSL），端口是465
    server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
    server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
    server.quit()  # 关闭连接

    fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
    fo1.writelines("邮件发送完毕！！！！！！" + "\r\n")
    fo1.close()

except Exception as e:
    # print('邮件发送失败！！！！！！' + str(e))
    fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
    fo1.writelines("邮件发送失败！！！！！！" + "\r\n")
    fo1.writelines(str(e))
    fo1.writelines("\r\n")
    fo1.close()
# 修改履历： v1.2 追加查找连板 和 连涨股票 功能 end

fo1 = open('D:\\database\\myfund\\loadstocklog.txt', 'a+')
fo1.writelines("全部处理结束！！！" + "\r\n")
fo1.close()
