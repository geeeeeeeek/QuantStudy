import time

import schedule
from tigeropen.common.consts import (Language, )
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.tiger_open_config import TigerOpenClientConfig
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL


def get_client_config():
    client_config = TigerOpenClientConfig()
    client_config.private_key = read_private_key('E:\\software\\rsa_key')
    client_config.tiger_id = '20150279'
    client_config.account = '20190425155943480'
    client_config.language = Language.en_US
    return client_config


client_config = get_client_config()

quote_client = QuoteClient(client_config)


def is_consecutive_up(closes, days=3):
    # closes: 收盘价列表，比如 [110, 112, 113, 115, 120]
    for i in range(len(closes) - days + 1):
        window = closes[i:i + days]
        # 判断是否递增
        if all(window[j] < window[j + 1] for j in range(len(window) - 1)):
            return True
    return False


def check_rise_three_days():
    symbols = ['AAPL', 'TSLA', 'GOOG']  # 股票代码列表

    for symbol in symbols:
        bars = quote_client.get_bars([symbol], period='day', limit=3)
        # print(bars)
        closes = bars['close'].tolist()
        result = is_consecutive_up(closes, days=3)
        print(f"{symbol}: 连涨3天 ===> {result}")
        if result:
            send_email("产生了交易信号", ['285126081@qq.com'], f"{symbol}出现了3天连涨",
                       sender_pass="your code")


def send_email(
        subject,
        receivers,
        content,
        smtp_server='smtp.qq.com',
        port=465,
        sender_email='285126081@qq.com',
        sender_pass='your_password_or_app_code'
):
    """
    发送邮件的通用方法
    subject: 邮件主题
    receivers: 收件人邮箱（字符串或字符串列表）
    content: 邮件正文（支持html）
    smtp_server: SMTP服务器地址（如smtp.qq.com, smtp.163.com, smtp.gmail.com）
    port: SMTP端口（SSL一般用465）
    sender_email: 发件人邮箱账号
    sender_pass: 邮箱授权码或密码
    """
    if isinstance(receivers, str):
        receivers = [receivers]

    print('send email to =>', ', '.join(receivers))

    msg = MIMEMultipart()
    msg["Subject"] = Header(subject, 'utf-8')
    msg["From"] = sender_email
    msg["To"] = ', '.join(receivers)
    msg.attach(MIMEText(content, 'html', 'utf-8'))

    try:
        smtp = SMTP_SSL(smtp_server, port)
        smtp.set_debuglevel(0)
        smtp.ehlo(smtp_server)
        smtp.login(sender_email, sender_pass)
        smtp.sendmail(sender_email, receivers, msg.as_string())
        smtp.quit()
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print("邮件发送失败, 错误信息:", e)


# 每天固定时间
# schedule.every().day.at("10:00").do(monitor_stocks)

# 或 每隔10秒
schedule.every(10).seconds.do(check_rise_three_days)

print("定时监控启动！")
while True:
    schedule.run_pending()
    time.sleep(5)
