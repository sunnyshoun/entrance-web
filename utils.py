import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from locals import *

app_host = 'http://localhost:5000'
if 'DYNO' in os.environ:
    app_host = herokuapp_domain

def send_email(subject, embody, attachments=[], recipient=recipient_email):
    # flaskemail of google account
    sender = sender_email
    password = sender_password
    # email
    content = MIMEMultipart()
    content['subject'] = subject
    content['from'] = sender
    content['to'] = recipient
    # content.attach(MIMEText('主機時間'))
    content.attach(MIMEText(embody, 'html'))

    with smtplib.SMTP(host='smtp.gmail.com', port='587') as smtp:
        try:
            # 驗證 SMTP 伺服器
            smtp.ehlo()
            # 建立加密傳輸
            smtp.starttls()
            smtp.login(sender, password)
            # 附加 pdf 檔
            for pdf in attachments:
                try:
                    with open(pdf, "rb") as fho:
                        the_pdf = MIMEApplication(fho.read(), _subtype="pdf")
                    the_pdf.add_header('Content-Disposition', 'attachment', filename=str(pdf))
                    content.attach(the_pdf)
                except:
                    print(f"No such file '{pdf}'")
                    pass
            smtp.send_message(content)
        except Exception as e:
            pass

def get_now():
    import pytz
    from datetime import datetime
    taipei = pytz.timezone('Asia/Taipei')
    now = datetime.now(taipei)
    return now

def get_datetime():
    now = get_now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_nowid():
    now = get_now()
    return now.strftime("%y%m%d%H%M")

def terminal_log(msg):
    aline = '-'*40
    print(f"{aline}\n{msg}\n{aline}")

def get_sha2(stext, opt):
    import hashlib
    sha2 = '256'
    if opt == 2:
        sha2 = '384'
    elif opt == 3:
        sha2 = '512'
    return eval(f"hashlib.sha{sha2}(stext.encode('utf8')).hexdigest()")


if __name__ == '__main__':
    print('datetime:', get_datetime())
    print('nowid:', get_nowid())
    while True:
        print('a. Get SHA-2 Hash')
        print('b. Test Gmail')
        print('q. Quit')
        op = input('> ').lower()
        if op == 'q':
            break
        elif op == 'a':
            while True:
                stext = input('Input a text to get SHA-2 hash (q. Quit): ')
                if stext.lower() in ('q', 'quit'):
                    break
                else:
                    opt = input('1.SHA-256  2.SHA-384  3.SHA-512: ')[0]
                    if opt in '123':
                        print(get_sha2(stext, int(opt)))
                        print()
        elif op == 'b':
            while True:
                embody = input('Input email body (q. Quit): ')
                if embody.lower() in ('q', 'quit'):
                    break
                else:
                    # 輸入要傳送的 pdf 檔案
                    fi = 1
                    attachments = []
                    while True:
                        # 必須設定可以存取到 pdf 的路徑
                        file_pdf = input(f'#{fi} pdf to attach (empty to end): ')
                        if file_pdf.strip() == '':
                            break
                        attachments.append(file_pdf)
                        fi += 1
                    subject = f'Email Test ({get_now()})'
                    send_email(subject, embody, attachments)
        print()
    