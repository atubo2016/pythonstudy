# -*- coding: utf-8 -*-
import _thread
import os
import subprocess
import sys
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from common import holiday
from common.properties import fund_thread_result_file, fund_log_file, fund_thread_csv_file
from fund.fundcommon.fundcommon import searchfundlist
from fund.fundcommon.fundsqlcommon import fund_load_data_infile_cmd


# 修改履历： v1.0 从 searchfundlist6_thread_db_v2.7 拆出 数据下载 数据分析 错误修正 三个模块
# 修改履历： v1.1 关闭chromedriver.exe 和 chrome.exe 进程
if holiday.is_holiday():
    sys.exit(0)
# 移除result.txt
if os.path.exists(fund_thread_result_file):
    os.remove(fund_thread_result_file)

today = time.strftime("%Y%m%d", time.localtime())

fo1 = open(fund_log_file, 'a+')
fo1.writelines("##################基金爬取结果 " + today + "##################\r\n")

url = 'http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;s6yzf;pn50;ddesc;qsd' \
      + today + ';qed' + today + \
      ';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
print(url)
fo1.writelines("天天基金网URL: " + url + "\r\n")

chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

fo1.writelines("-----------------连接天天基金网-----------------" + "\r\n")
time.sleep(3)
# 点击页面上的【不分页】按钮
element = driver.find_element_by_xpath('//*[@id="showall"]')
ActionChains(driver).click(element).perform()
time.sleep(30)

dbtable = driver.find_element_by_xpath('//*[@id="dbtable"]')
rows = dbtable.find_elements_by_tag_name('tr')
# 去掉title行
foundnum = len(rows) - 1

# 修改履历： v1.1 关闭chromedriver.exe 和 chrome.exe 进程 start
os.system('taskkill /im chromedriver.exe /F')
os.system('taskkill /im chrome.exe /F')
# 修改履历： v1.1 关闭chromedriver.exe 和 chrome.exe 进程 end

fo1.writelines("-----------------将要爬取{0}个基金信息--------".format(foundnum - 1) + "\r\n")
fo1.close()

# 创建线程
strflg = ""
csvfilelist = []
# noinspection PyBroadException
try:
    for j in range(0, foundnum // 1000 + 1):
        strflg = strflg + "OK"
        # 循环内创建文件名，否则会造成 跨日爬取数据时，导入文件名和爬取文件名不一致
        csvfilelist.append(fund_thread_csv_file.format(time.strftime("%Y%m%d", time.localtime())
                           + '_' + str(1 + j * 1000).zfill(4)))
        if j != foundnum // 1000:
            _thread.start_new_thread(searchfundlist, (1 + j * 1000, (j + 1) * 1000,))
        else:
            _thread.start_new_thread(searchfundlist, (1 + j * 1000, foundnum,))
        time.sleep(120)
except:
    # print("Error: 无法启动线程")
    fo1 = open(fund_log_file, 'a+')
    fo1.writelines("Error: 无法启动线程" + "\r\n")
    fo1.close()

while 1:
    time.sleep(8)
    str1 = ""
    if os.path.exists(fund_thread_result_file):
        fo2 = open(fund_thread_result_file, "r")
        str1 = fo2.read()
        fo2.close()

    if str1 == strflg:
        fo1 = open(fund_log_file, 'a+')
        fo1.writelines("所有线程文件写入完毕！！！" + "\r\n")
        fo1.close()
        break

# 移除result.txt
if os.path.exists(fund_thread_result_file):
    os.remove(fund_thread_result_file)

# 修改履历： v1.1 关闭chromedriver.exe 和 chrome.exe 进程 start
os.system('taskkill /im chromedriver.exe /F')
os.system('taskkill /im chrome.exe /F')
# 修改履历： v1.1 关闭chromedriver.exe 和 chrome.exe 进程 end

fo1 = open(fund_log_file, 'a+')

today3 = time.strftime("%Y-%m-%d", time.localtime())
# Load data infile
for filename in csvfilelist:
    cmd = fund_load_data_infile_cmd.format(filename, today3)
    # cmd = "mysql -uroot -p123456 myfund --local-infile -e" \
    #       " \"load data local infile '" + filename + "' " \
    #       "REPLACE into table fundhistory " \
    #       "CHARACTER SET gbk " \
    #       "FIELDS TERMINATED BY ',' " \
    #       "ENCLOSED BY '''' " \
    #       "LINES TERMINATED BY '\\r\\n' " \
    #       "IGNORE 1 LINES " \
    #       "(fundcode,fundname,@businessday,@netassetvalue,@accumulatedtotolnetvalue," \
    #       "@dailygrowthrate,@weekgrowthrate,@monthgrowthrate,@threemonthgrowthrate,@halfyeargrowthrate) " \
    #       "SET " \
    #       "businessday = CASE WHEN @businessday<>'---' THEN @businessday ELSE '" + today3 + "' END," \
    #       "netassetvalue = CASE WHEN @netassetvalue<>'---' THEN @netassetvalue END," \
    #      "accumulatedtotolnetvalue = CASE WHEN @accumulatedtotolnetvalue<>'---' THEN @accumulatedtotolnetvalue END," \
    #       "dailygrowthrate = CASE WHEN @dailygrowthrate<>'---' THEN @dailygrowthrate END," \
    #       "weekgrowthrate = CASE WHEN @weekgrowthrate<>'---' THEN @weekgrowthrate END," \
    #       "monthgrowthrate = CASE WHEN @monthgrowthrate<>'---' THEN @monthgrowthrate END," \
    #       "threemonthgrowthrate = CASE WHEN @threemonthgrowthrate<>'---' THEN @threemonthgrowthrate END," \
    #       "halfyeargrowthrate = CASE WHEN @halfyeargrowthrate<>'---' THEN @halfyeargrowthrate END, " \
    #       "downloaddate = now();\""

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

fo1.writelines("基金数据导入完毕！！！" + "\r\n")
print("基金数据导入完毕！！！")
fo1.close()
