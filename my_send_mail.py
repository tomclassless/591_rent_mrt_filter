from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib


def sendmail(message: str):
    content = MIMEMultipart()  # 建立MIMEMultipart物件
    content["subject"] = "有新租屋資訊出現在591"  # 郵件標題
    content["from"] = "tomclassless86@gmail.com"  # 寄件者
    content["to"] = "tomclassless86@gmail.com"  # 收件者
    content.attach(MIMEText(message))  # 郵件內容

    with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("tomclassless86@gmail.com", "fbzqhpvjbreqvlwt")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)


if __name__ == '__main__':
    sendmail('測試成功')
