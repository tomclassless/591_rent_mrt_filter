import datetime
import time

from main import check_591
from my_send_mail import sendmail

if __name__ == '__main__':
    while True:
        try:
            check_591(mail=True)
            time.sleep(60 * 20)
        except Exception as e:
            print(e)
            sendmail(f'591 crawler failed at {str(datetime.datetime.now())}')
            time.sleep(60)
