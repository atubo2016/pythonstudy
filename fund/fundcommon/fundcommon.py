import os
import time
import csv
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from common.properties import fund_thread_result_file, fund_thread_csv_file, fund_thread_err_file, \
    fund_thread_csv_file_hexun, fund_thread_err_file_hexun, fund_thread_result_file_hexun


# 下载指定区间的基金到CSV文件（和讯网）
def searchfundlist_hexun(startnum, tonum):
    print('-----------------将要爬取 第{0} 到 第{1} 个基金信息--------'.format(startnum, tonum))
    returnvalue = "all success"
    # try 整个函数防止 任意一个失败，导致OK没有写入result文件，程序无法结束
    today1 = time.strftime("%Y%m%d", time.localtime())
    # noinspection PyBroadException
    try:
        # today = '20210316'
        url1 = 'http://jingzhi.funds.hexun.com/jz/kaifang.htm'
        print(url1)

        fundlistfile1 = fund_thread_csv_file_hexun.format(today1 + '_' + str(startnum).zfill(4))
        print(fundlistfile1)
        # 文件存在的话，就先删除
        if os.path.exists(fundlistfile1):
            os.remove(fundlistfile1)

        chrome_options1 = Options()
        chrome_options1.add_argument('--headless')
        driver1 = webdriver.Chrome(options=chrome_options1)
        driver1.get(url1)
        time.sleep(20)

        tr = driver1.find_element_by_xpath('//*[@id="filterTable"]/table/thead/tr[1]')
        ths = tr.find_elements_by_tag_name('th')
        businessday = ths[4].text

        # 点击页面上的【不分页】按钮
        element1 = driver1.find_element_by_xpath('//input[@class="checkpage" and @type="checkbox"]')
        ActionChains(driver1).click(element1).perform()
        time.sleep(30)

        data1 = []
        title1 = ['基金代码', '基金简称', '日期', '单位净值', '累计净值', '日增长率', '近1周', '近1月', '近3月', '近6月']
        data1.append(title1)

        for i in range(startnum, tonum + 1):
            # noinspection PyBroadException
            try:
                print('当前正在爬取第 ' + str(i) + ' 条基金')
                row = driver1.find_element_by_xpath('//*[@id="filterTable"]/table/tbody/tr[' + str(i) + ']')
                columns = row.find_elements_by_tag_name('td')
                # 基金代码
                # 基金简称
                # 日期
                # 单位净值
                # 累计净值
                # 日增长率
                # 近1周
                # 近1月
                # 近3月
                # 近6月
                temp = [columns[2].text, columns[3].text.replace("（吧）", ""), businessday, columns[4].text,
                        columns[5].text, columns[8].text.replace("%", ""), "--", "--", "--", "--"]

                data1.append(temp)
            except:
                # noinspection PyShadowingNames
                fo = open(fund_thread_err_file_hexun.format(str(startnum).zfill(4)), 'a+')
                fo.write(today1 + "第 " + str(i) + " 条基金爬取失败！！！\r\n")
                fo.close()
                returnvalue = "some error"
                continue  # 爬取失败，则继续下一条基金爬取

            if i % 100 == 0:
                with open(fundlistfile1, 'a+', newline='') as csvfile1:
                    writer1 = csv.writer(csvfile1)
                    for row1 in data1:
                        writer1.writerow(row1)
                data1 = []
        with open(fundlistfile1, 'a+', newline='') as csvfile1:
            writer1 = csv.writer(csvfile1)
            for row1 in data1:
                writer1.writerow(row1)

        fo = open(fund_thread_result_file_hexun, 'a+')
        fo.write("OK")
        fo.close()
    except:
        fo = open(fund_thread_err_file_hexun.format(str(startnum).zfill(4)), 'a+')
        fo.write(today1 + " 第" + str(startnum) + " 条 开始的1000条基金全部爬取失败！！！\r\n")
        fo.close()
        fo = open(fund_thread_result_file_hexun, 'a+')
        fo.write("OK")
        fo.close()
        returnvalue = "all error"

    return returnvalue


# 下载指定区间的基金到CSV文件（天天基金网）
def searchfundlist(startnum, tonum):
    print('-----------------将要爬取 第{0} 到 第{1} 个基金信息--------'.format(startnum, tonum))
    returnvalue = "all success"
    # try 整个函数防止 任意一个失败，导致OK没有写入result文件，程序无法结束
    today1 = time.strftime("%Y%m%d", time.localtime())
    # noinspection PyBroadException
    try:
        # today = '20210316'
        url1 = 'http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;s6yzf;pn50;ddesc;qsd' \
               + today1 + ';qed' + today1 + \
               ';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
        print(url1)

        fundlistfile1 = fund_thread_csv_file.format(today1 + '_' + str(startnum).zfill(4))
        print(fundlistfile1)
        # 文件存在的话，就先删除
        if os.path.exists(fundlistfile1):
            os.remove(fundlistfile1)

        chrome_options1 = Options()
        chrome_options1.add_argument('--headless')
        driver1 = webdriver.Chrome(options=chrome_options1)
        driver1.get(url1)
        time.sleep(20)
        # 点击页面上的【不分页】按钮
        element1 = driver1.find_element_by_xpath('//*[@id="showall"]')
        ActionChains(driver1).click(element1).perform()
        time.sleep(30)

        data1 = []
        title1 = ['基金代码', '基金简称', '日期', '单位净值', '累计净值', '日增长率', '近1周', '近1月', '近3月', '近6月']
        # title1.append('序号')
        # title1.append('近1年')
        # title1.append('近2年')
        # title1.append('近3年')
        # title1.append('今年来')
        # title1.append('成立来')
        # title1.append('手续费')
        data1.append(title1)
        # start100 = datetime.datetime.now()
        # startall = datetime.datetime.now()
        for i in range(startnum, tonum + 1):
            # noinspection PyBroadException
            try:
                print('当前正在爬取第 ' + str(i) + ' 条基金')
                # start1 = time.time()
                # startfindnode = time.time()
                row = driver1.find_element_by_xpath('//*[@id="dbtable"]/tbody/tr[' + str(i) + ']')
                # endfindtr = time.time()
                # print('-----------------1条 查找TR {0} 秒！！！-----------------'.format(endfindtr - startfindnode))

                columns = row.find_elements_by_tag_name('td')
                # endfindtd = time.time()
                # print('-----------------1条 查找TD {0} 秒！！！-----------------'.format(endfindtd - endfindtr))

                temp = [columns[2].text, columns[3].text]
                # temp.append(columns[1].text)
                # 基金代码
                # 基金简称
                # 日期
                businessday = columns[4].text
                if businessday == '---':
                    temp.append(time.strftime("%Y-%m-%d", time.localtime()))
                else:
                    thisyear = time.strftime("%Y-", time.localtime())
                    businessday = thisyear + businessday
                    today2 = datetime.today().date()

                    if datetime.strptime(businessday, "%Y-%m-%d").date() > today2:
                        # 修复 跨年 日期不正 的bug
                        # print(datetime.strftime(datetime.strptime(businessday, "%Y-%m-%d")
                        #                         - relativedelta(years=1), "%Y-%m-%d"))
                        temp.append(datetime.strftime(datetime.strptime(businessday, "%Y-%m-%d")
                                                      - relativedelta(years=1), "%Y-%m-%d"))
                    else:
                        temp.append(businessday)

                # 单位净值
                temp.append(columns[5].text)
                # 累计净值
                temp.append(columns[6].text)
                # 日增长率
                temp.append(columns[7].text.replace("%", ""))
                # 近1周
                temp.append(columns[8].text.replace("%", ""))
                # 近1月
                temp.append(columns[9].text.replace("%", ""))
                # 近3月
                temp.append(columns[10].text.replace("%", ""))
                # 近6月
                temp.append(columns[11].text.replace("%", ""))
                # temp.append(columns[12].text)
                # temp.append(columns[13].text)
                # temp.append(columns[14].text)
                # temp.append(columns[15].text)
                # temp.append(columns[16].text)
                # temp.append(columns[18].text)
                data1.append(temp)
                # endsetdata = time.time()
                # print('-----------------1条 编辑数据 {0} 秒！！！-----------------'.format(endsetdata - endfindtd))
            except:
                # noinspection PyShadowingNames
                fo = open(fund_thread_err_file.format(str(startnum).zfill(4)), 'a+')
                fo.write(today1 + "第 " + str(i) + " 条基金爬取失败！！！\r\n")
                fo.close()
                returnvalue = "some error"
                continue  # 爬取失败，则继续下一条基金爬取

            if i % 100 == 0:
                # startfile = time.time()
                with open(fundlistfile1, 'a+', newline='') as csvfile1:
                    writer1 = csv.writer(csvfile1)
                    for row1 in data1:
                        writer1.writerow(row1)
                # print('-----------------第 {0} 条基金下载完成！！！-----------------'.format(i))
                # endfile = time.time()
                # print('-----------------写文件 {0} 秒！！！-----------------'.format(endfile - startfile))
                # end100 = datetime.datetime.now()
                # print('-----------------100条 {0} 秒！！！-----------------'.format((end100 - start100).seconds))
                # start100 = datetime.datetime.now()
                data1 = []
        # 最后100条 不管 有没有 一百条，不管有没有出错，都要写一次 文件。防止最后一条出错被 continue 掉
        # elif i == tonum:
        with open(fundlistfile1, 'a+', newline='') as csvfile1:
            writer1 = csv.writer(csvfile1)
            for row1 in data1:
                writer1.writerow(row1)
                # print('-----------------第 {0} 条(全部)基金下载完成！！！-----------------'.format(i))
                # endall = datetime.datetime.now()
            # end1 = time.time()
            # print('-----------------1条 {0} 秒！！！-----------------'.format(end1 - start1))
        # print('-----------------总共 {0} 秒！！！-----------------'.format((endall - startall).seconds))
        fo = open(fund_thread_result_file, 'a+')
        fo.write("OK")
        fo.close()
    except:
        fo = open(fund_thread_err_file.format(str(startnum).zfill(4)), 'a+')
        fo.write(today1 + " 第" + str(startnum) + " 条 开始的1000条基金全部爬取失败！！！\r\n")
        fo.close()
        fo = open(fund_thread_result_file, 'a+')
        fo.write("OK")
        fo.close()
        returnvalue = "all error"

    return returnvalue
