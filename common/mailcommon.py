import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.utils import formataddr
curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curPath)
from properties import fund_log_file


# 下载指定区间的基金到CSV文件
def sendmail(mimetext, maildate):
    try:
        my_sender = '8248585@qq.com'  # 发件人邮箱账号
        my_pass = 'djjrbacdtxaabjjh'  # 发件人邮箱密码
        my_user = '8248585@qq.com'  # 收件人邮箱账号，我这边发送给自己

        msg = MIMEText(mimetext, 'plain', 'utf-8')
        # noinspection PyTypeChecker
        msg['From'] = formataddr(["minnanzi", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        # noinspection PyTypeChecker
        msg['To'] = formataddr(["minnanzi", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = '基金信息 ' + maildate  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器（SSL），端口是465
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接

        fo1 = open(fund_log_file, 'a+')
        fo1.writelines("邮件发送完毕！！！！！！" + "\r\n")
        fo1.close()

    except Exception as e:
        # print('邮件发送失败！！！！！！' + str(e))
        fo1 = open(fund_log_file, 'a+')
        fo1.writelines("邮件发送失败！！！！！！" + "\r\n")
        fo1.writelines(str(e))
        fo1.writelines("\r\n")
        fo1.close()
