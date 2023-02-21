from flask_mail import Mail, Message
import os

# initialize mail object

mail = Mail()

# generate mail for confirmation

def msg_body(info):

    text_msg = """
    <p>訂單編號：{}<br>訂購房型：{}<br>入住日期：{}<br>退房日期：{}<p>
    <p>您這次訂單款項一共 NT{} 元，<br>請在三日內將訂金 NT{} 元匯至管家帳戶，<br>並透過臉書粉專或來電告知，<br>再請於入住時繳清餘款共 NT{} 元。<p>
    <p>匯款銀行：鹿港信用合作社 （165）<br>銀行帳號：00019152248820<br>匯款戶名：黃淑汝<p>
    <p>謝謝您！期待與您在鹿港相見！<br>以下為我們的連絡資訊：<br>電話：04-7756852<br>地址：彰化縣鹿港鎮杉行街77號<br>臉書：<a href='https://www.facebook.com/shanhanju'>杉行居/ SHAN HANG JU</a><p>
    <p>杉行居 敬上<p>
    """.format(info['order_id'],
               info['room'], 
               info['check_in'], 
               info['check_out'], 
               "{:,}".format(info['total']), 
               "{:,}".format(info['deposit']), 
               "{:,}".format(info['final']))


    return text_msg

def create_msg(recipient, info):

    msg_title = '您在杉行居民宿的預訂已完成！'
    msg_sender = os.getenv('MAIL_USERNAME')
    msg_recipients = [recipient]

    body = msg_body(info)

    msg = Message(msg_title,
                  sender=msg_sender,
                  recipients=msg_recipients)
    msg.html = body

    return msg
