from flask_mail import Mail, Message
import os

# initialize mail object

mail = Mail()

# generate mail for confirmation

def msg_body(info):
    text_msg = '訂購房型：{}\n入住日期：{}\n退房日期：{}\n\n您這次訂單款項一共 NT{} 元，\n請在三日內將訂金 NT{} 元轉至管家帳戶，\n並於入住時繳清餘款共 NT{} 元\n\n'.format(
        info['room'], info['check_in'], info['check_out'], info['total'], info['deposit'], info['final']
    )

    text_msg = text_msg + '銀行代碼：\n帳號：\n\n謝謝您！期待與您在鹿港相見！\n\n杉行居 敬上'

    return text_msg

def create_msg(recipient, info):

    msg_title = '您在杉行居民宿的預訂已完成！'
    msg_sender = os.getenv('MAIL_USERNAME')
    msg_recipients = [recipient]

    body = msg_body(info)

    msg = Message(msg_title,
                  sender=msg_sender,
                  recipients=msg_recipients)
    msg.body = body

    return msg
