# -*- coding: utf-8 -*-
import os
import sys
import time
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from common import holiday
from common.mailcommon import sendmail
from common.properties import fund_log_file


# 修改履历： v1.0 从 searchfundlist6_thread_db_v2.7 拆出 数据下载 数据分析 错误修正 三个模块
# 修改履历： v1.1 天天基金网失败不再重新取得，同时判断 和讯网 有没有错误
if holiday.is_holiday():
    sys.exit(0)

todayYmd = time.strftime("%Y%m%d", time.localtime())
todayY_m_d = time.strftime("%Y-%m-%d", time.localtime())
logfp = open(fund_log_file, 'a+')
logfp.writelines(todayYmd + "开始检查基金信息下载情况！！！" + "\r\n")
logfp.close()

mimetext = ""
err_csv_list = []

# 单个爬取日志（天天基金网）
filter_file_name_fund = "pythonerror_"
filter_file_error = todayYmd + ""

# 修改履历： v1.1 天天基金网失败不再重新取得，同时判断 和讯网 有没有错误 start
# for filename in os.listdir("D:\\database\\myfund"):
#     if filter_file_name_fund in filename:
#         fp = os.path.join("D:\\database\\myfund", filename)
#         if os.path.isfile(fp):
#             with open(fp) as f:
#                 for line in f:
#                     if filter_file_error in line:
#                         err_csv_stratno_list.append(filename[12:filename.rfind('.')])
#                         break
#
# if len(err_csv_stratno_list) != 0:
#     seconds = round(time.mktime(time.strptime(todayYmd + "230008", "%Y%m%d%H%M%S")) - time.time())
#     if seconds > 0:
#         print("sleep " + str(seconds) + " seconds!")
#         time.sleep(seconds)
#
#     for start_no in err_csv_stratno_list:
#         reload_result = searchfundlist(int(start_no), int(start_no) + 999)
#         if reload_result != "all error":
#             cmd = fund_load_data_infile_cmd.format("datalist_" + todayYmd + "_" + start_no + ".csv", todayY_m_d)
#
#             logfp = open(fund_log_file, 'a+')
#             logfp.writelines(cmd)
#             logfp.writelines("\r\n")
#
#             cmd_res = {}
#             res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
#             stdoutlines = res.stdout.readlines()
#             stderrlines = res.stderr.readlines()
#
#             for line in stdoutlines:
#                 logfp.writelines(line.decode('utf-8'))
#             for line in stderrlines:
#                 logfp.writelines(line.decode('utf-8'))
#
#             logfp.close()
#
#         if reload_result != "all success":
#             mimetext = "datalist_" + todayYmd + "_" + start_no + ".csv" + " 二次爬取处理再次出错！！！\r\n" + mimetext
#             logfp = open(fund_err_flg_file, 'a+')
#             logfp.writelines(todayYmd + " reload error" + "\r\n")
#             logfp.close()

# 和讯错误日志文件
filter_file_name_fund_hexun = "pythonerror_hexun_"

for filename in os.listdir("D:\\database\\myfund"):
    if filter_file_name_fund_hexun in filename:
        fp = os.path.join("D:\\database\\myfund", filename)
        if os.path.isfile(fp):
            with open(fp) as f:
                for line in f:
                    if filter_file_error in line:
                        err_csv_list.append(filename)
                        break
    elif filter_file_name_fund in filename:
        fp = os.path.join("D:\\database\\myfund", filename)
        if os.path.isfile(fp):
            with open(fp) as f:
                for line in f:
                    if filter_file_error in line:
                        err_csv_list.append(filename)
                        break

if len(err_csv_list) != 0:
    for filename in err_csv_list:
        mimetext = filename + " 爬取处理出错！！！\r\n" + mimetext

# 修改履历： v1.1 天天基金网失败不再重新取得，同时判断 和讯网 有没有错误 end

key1 = "##################基金爬取结果 " + todayYmd + "##################"
error1 = False
key2 = "ERROR "
error2 = False

# 整个批处理的日志
fo1 = open(fund_log_file, 'r')

for line in fo1.readlines():
    if key1 in line:
        error1 = True

    if error1:
        if key2 in line:
            error2 = True

    if error1 and error2:
        mimetext = "基金数据批量导入出错了！！！\r\n" + mimetext
        break

fo1.close()

# 发邮件
if mimetext != "":
    sendmail(mimetext, todayY_m_d)
    logfp = open(fund_log_file, 'a+')
    logfp.writelines(todayYmd + "基金信息下载出错！！！" + "\r\n")
    logfp.writelines(mimetext + "\r\n")
    logfp.close()
else:
    logfp = open(fund_log_file, 'a+')
    logfp.writelines(todayYmd + "基金信息下载正常！！！" + "\r\n")
    logfp.close()
