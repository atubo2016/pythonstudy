# -*- coding: utf-8 -*-
import os
import sys
import time
import pymysql
from dateutil.relativedelta import relativedelta
from datetime import datetime
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from common import holiday
from common.mailcommon import sendmail
from common.properties import fund_log_file


# 修改履历： v1.0 从 searchfundlist6_thread_db_v2.7 拆出 数据下载 数据分析 错误修正 三个模块
# 修改履历： v1.1 合并和讯网基金信息到天天网基金表
# 修改履历： v1.2 修改 涨幅前50基金统计SQL 基金名变更，导致 数据重复 的问题
if holiday.is_holiday():
    sys.exit(0)

todayYmd = time.strftime("%Y%m%d", time.localtime())
todayY_m_d = time.strftime("%Y-%m-%d", time.localtime())

# 打开数据库连接
db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='myfund', charset='utf8')
# 使用cursor方法创建一个游标
cursor = db.cursor()

# 修改履历： v1.1 合并和讯网基金信息到天天网基金表 start
sql = "insert into fundhistory( " \
      "     fundcode " \
      "    ,fundname " \
      "    ,businessday " \
      "    ,netassetvalue " \
      "    ,accumulatedtotolnetvalue " \
      "    ,dailygrowthrate " \
      "    ,weekgrowthrate " \
      "    ,monthgrowthrate " \
      "    ,threemonthgrowthrate " \
      "    ,halfyeargrowthrate " \
      "    ,downloaddate " \
      ") " \
      "select " \
      "    fh.fundcode " \
      "    ,fh.fundname  " \
      "    ,fh.businessday " \
      "    ,fh.netassetvalue  " \
      "    ,fh.accumulatedtotolnetvalue  " \
      "    ,fh.dailygrowthrate " \
      "    ,fh.weekgrowthrate " \
      "    ,fh.monthgrowthrate " \
      "    ,fh.threemonthgrowthrate " \
      "    ,fh.halfyeargrowthrate " \
      "    ,fh.downloaddate " \
      "from " \
      "    fundhistory_hexun fh " \
      "where " \
      "    fh.businessday = '{0}' " \
      "    and not exists ( " \
      "    select " \
      "        * " \
      "    from " \
      "        fundhistory f " \
      "    where " \
      "        fh.fundcode = f.fundcode " \
      "        and fh.businessday = f.businessday) ".format(todayY_m_d)

fo1 = open(fund_log_file, 'a+')
fo1.writelines("SQL = " + sql + "\r\n")
cursor.execute(sql)
db.commit()

fo1.writelines("合并和讯网基金信息到天天网基金表 完毕！！！" + "\r\n")
fo1.close()

# 修改履历： v1.1 合并和讯网基金信息到天天网基金表 end

# ################ 查找基金履历表的新基金信息，并导入基金基本表 ##################
sql = "insert " \
      "into " \
      "fund(fundcode, " \
      "fundname, " \
      "updatedate) " \
      "select " \
      "b.fundcode, " \
      "b.fundname, " \
      "now() " \
      "from " \
      "( " \
      "select " \
      "h.fundcode as fundcode , " \
      "max(h.businessday) as maxdate " \
      "from " \
      "( " \
      "select " \
      "      fundcode, " \
      "     businessday " \
      "from " \
      "      fundhistory a " \
      "where " \
      "     not exists ( " \
      "     select " \
      "         * " \
      "     from " \
      "         fund b " \
      "     where " \
      "         a.fundcode = b.fundcode)) h " \
      "group by " \
      " h.fundcode) a, " \
      "fundhistory b " \
      "where " \
      "b.fundcode = a.fundcode " \
      "and b.businessday = a.maxdate "

fo1 = open(fund_log_file, 'a+')
fo1.writelines("SQL = " + sql + "\r\n")
cursor.execute(sql)
db.commit()

fo1.writelines("查找基金履历表的新基金信息，并导入基金基本表 完毕！！！" + "\r\n")
fo1.close()

# 每天更新 前一天（因为当天取得的数据可能不全）和当天 的 top20
# 删除数据
yestoday = datetime.strftime(datetime.strptime(todayY_m_d, "%Y-%m-%d") - relativedelta(days=1), "%Y-%m-%d")
sql = " delete from funddailytop20 where businessday = '{0}' or businessday = '{1}' ".format(yestoday, todayY_m_d)
cursor.execute(sql)

# 插入数据
sql = "insert into funddailytop20 (ranking,fundcode,fundname,businessday,dailygrowthrate,top20count) " \
      "select " \
      "    a.rowno, " \
      "    a.fundcode , " \
      "    a.fundname , " \
      "    a.businessday , " \
      "    a.dailygrowthrate, " \
      "    case when b.top20count is null then 1 else b.top20count + 1 end " \
      "from " \
      "    (select " \
      "         @rownum := @rownum  + 1 as rowno, " \
      "         f.fundcode as fundcode , " \
      "         f.fundname as fundname , " \
      "         f.businessday as businessday , " \
      "         f.dailygrowthrate as dailygrowthrate " \
      "    from " \
      "         fundhistory f, " \
      "         (select @rownum := 0) rowtbl " \
      "    where " \
      "         f.businessday = '{0}' " \
      "         and f.dailygrowthrate is not null " \
      "    order by " \
      "         f.dailygrowthrate desc " \
      "    limit 0,20) a " \
      "left outer join " \
      "    (select " \
      "         fundcode, " \
      "         count(1) as top20count " \
      "     from " \
      "         funddailytop20 " \
      "     where " \
      "         businessday > date_sub(curdate(), interval 1 month) " \
      "     group by fundcode) b " \
      "on " \
      "    a.fundcode = b.fundcode"

fo1 = open(fund_log_file, 'a+')

fo1.writelines("SQL = " + sql.format(yestoday) + "\r\n")
cursor.execute(sql.format(yestoday))

fo1.writelines("SQL = " + sql.format(todayY_m_d) + "\r\n")
cursor.execute(sql.format(todayY_m_d))
db.commit()

fo1.writelines("每日涨幅前20基金统计 完毕！！！" + "\r\n")
fo1.close()

sql = " delete from fundfromsomedaytop20 where updatedate = '{0}'".format(todayY_m_d)
cursor.execute(sql)

sql = "insert into fundfromsomedaytop20( " \
      "fundcode, " \
      "fundname, " \
      "fromprice, " \
      "fromday, " \
      "toprice, " \
      "today, " \
      "changevalue, " \
      "changerate, " \
      "updatedate) " \
      "select " \
      "c.tocode, " \
      "c.toname, " \
      "e.fromprice, " \
      "e.fromday, " \
      "c.toprice, " \
      "c.today, " \
      "c.toprice - e.fromprice, " \
      "(( c.toprice - e.fromprice )/ e.fromprice * 100) as changerate, " \
      "'{1}' " \
      "from " \
      "( " \
      "select " \
      "g.fundcode as fromcode, " \
      "g.fundname as fromname, " \
      "g.businessday as fromday, " \
      "g.netassetvalue as fromprice " \
      "from " \
      "fundhistory g, " \
      "( " \
      "select " \
      "d.fundcode as fundcode, " \
      "max(d.businessday) as fromdate " \
      "from " \
      "fundhistory d " \
      "where " \
      "d.businessday < '{0}' " \
      "group by " \
      "d.fundcode " \
      " ) f " \
      "where " \
      "g.fundcode = f.fundcode " \
      "and g.businessday = f.fromdate ) e, " \
      "( " \
      "select " \
      "a.fundcode as tocode, " \
      "a.fundname as toname, " \
      "a.businessday as today, " \
      "a.netassetvalue as toprice " \
      "from " \
      "fundhistory a, " \
      "( " \
      "select " \
      "h.fundcode, " \
      "max(h.businessday) as maxdate " \
      "from " \
      "fundhistory h " \
      "group by " \
      "h.fundcode ) b " \
      "where " \
      "a.fundcode = b.fundcode " \
      "and a.businessday = b.maxdate ) c " \
      "where " \
      "e.fromcode = c.tocode " \
      "and e.fromprice is not null " \
      "order by changerate desc " \
      "limit 0,50 " \

fo1 = open(fund_log_file, 'a+')
fo1.writelines("SQL = " + sql.format("2021-03-24", todayY_m_d) + "\r\n")
fo1.writelines("2021-03-23 以来 涨幅前50 基金统计 完毕！！！" + "\r\n")
fo1.close()

cursor.execute(sql.format("2021-03-24", todayY_m_d))
db.commit()

mimetext = ""
sql = "select " \
      "fundcode as '基金代码', " \
      "fundname as '基金简称', " \
      "concat(CONVERT(ROUND(dailygrowthrate,1),CHAR) , '%') as '涨跌幅', " \
      "top20count as 'top20出现次数' " \
      "from funddailytop20 " \
      "where businessday = '{0}' " \
      "order by ranking asc " \

mimetext = mimetext + todayY_m_d + " 涨幅前20基金 如下：\r\n"
cursor.execute(sql.format(todayY_m_d))
myresult = cursor.fetchall()
for x in myresult:
    mimetext = mimetext + str(x) + "\r\n"

mimetext = mimetext + "\r\n"
fo1 = open(fund_log_file, 'a+')
fo1.writelines("SQL = " + sql.format(todayY_m_d) + "\r\n")
fo1.close()

mimetext = mimetext + "2021-03-23 以来 涨幅前50基金 如下：\r\n"
sql = "select " \
      "fundcode as '基金代码', " \
      "fundname as '基金简称', " \
      "concat(CONVERT(ROUND(changerate,1),CHAR) , '%') as '涨跌幅' " \
      "from fundfromsomedaytop20 " \
      "where updatedate = '{0}' " \
      "order by changerate desc " \

cursor.execute(sql.format(todayY_m_d))
myresult = cursor.fetchall()
for x in myresult:
    mimetext = mimetext + str(x) + "\r\n"

fo1 = open(fund_log_file, 'a+')
fo1.writelines("SQL = " + sql.format(todayY_m_d) + "\r\n")
fo1.close()

# 发邮件
sendmail(mimetext, todayY_m_d)

fo1 = open(fund_log_file, 'a+')
fo1.writelines("基金数据分析完毕！！！" + "\r\n")
fo1.close()
