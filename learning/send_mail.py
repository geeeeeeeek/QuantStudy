import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL


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