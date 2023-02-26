from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user
import bcrypt
from datetime import datetime, timezone, timedelta

from src.extensions.models import db, Admin, User, Booking, Rooms
from src.extensions.logger import allLogger, abort_msg
from src.customer.routes import names

admin = Blueprint('admin', __name__)

tz = timezone(timedelta(hours=+8))

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)

    return d

def int_to_yes_no_dict_item(row_dict, keys:list):
    for key in keys:
        if row_dict[key] == 0:
            row_dict[key] = '否'
        else:
            row_dict[key] = '是'

def is_legal_password(password):
    # define a legal pw
    # 1. contains 1 uppercase letter and 1 lowercase letter
    # 2. contains 1 digit
    # 3. at least have length of 8

    if len(password) < 8:
        return False

    check_1 = False
    check_2 = False
    check_3 = False
    for char in password:
        if char.isupper():
            check_1 = True
        if char.islower():
            check_2 = True
        if char.isdigit():
            check_3 = True

    if check_1 and check_2 and check_3:
        return True
    else:
        return False 


# routes


@admin.route('/login', methods = ['GET', 'POST'])
def login():

    try:

        if request.method == 'POST':

            # login process
            admin_info = db.session.query(Admin).filter_by(id = 1).first()
            username = admin_info.username
            hashed_pw = admin_info.pw

            username_correct = False
            pw_correct = False

            input_username = request.form.get('username')
            input_pw = request.form.get('pw')
            input_pw_bytes = input_pw.encode('utf-8')

            if input_username == '' or input_pw == '':
                flash('輸入有誤，請重新輸入', category='error')
                return render_template('login.html')
            
            if username == input_username:
                username_correct = True
            else:
                flash('用戶名輸入有誤，請重新輸入', category='error')
                return render_template('login.html')
            if bcrypt.checkpw(input_pw_bytes, hashed_pw.encode('utf-8')):
                pw_correct = True
            else:
                flash('密碼輸入有誤，請重新輸入', category='error')
                return render_template('login.html')
            if username_correct and pw_correct:
                user = User()
                user.id = 'admin'
                login_user(user, remember=True)
                flash('登入成功', category='success')
                allLogger.info('Admin logged in successfully.')
                return redirect(url_for('admin.bookings'))
            
        return render_template('login.html')
    
    except Exception as e:
        allLogger.error(str(e))
        abort_msg(e)



@admin.route('/bookings', methods = ['GET', 'POST'])
# @login_required
def bookings():

    # future addition:
    # show all
    # find certain row from some date

    try:
        today = datetime.now(tz) - timedelta(days=1) 
        query = db.session.query(Booking).filter(
            Booking.check_in >= today, 
            Booking.check_out >= today, 
            Booking.deleted == 0
        ).order_by(Booking.check_in, Booking.check_out).all()
        data = {}
        for row in query:
            data[row.id] = row2dict(row)
            data[row.id]['check_in'] = (data[row.id]['check_in'] + timedelta(hours=+8)).strftime('%Y-%m-%d')
            data[row.id]['check_out'] = (data[row.id]['check_out'] + timedelta(hours=+8)).strftime('%Y-%m-%d')
            int_to_yes_no_dict_item(data[row.id], ['add_bed', 'parking', 'breakfast'])

        return render_template('bookings.html', data = data)
    
    except Exception as e:
        allLogger.error(str(e))
        abort_msg(e)

@admin.route('/bookings/<int:id>', methods = ['GET', 'POST'])
# @login_required
def detailed_booking(id):
    
    try:

        if request.method == 'POST':
            if request.form.get('deposit_paid') == 'paid':
                db.session.query(Booking).\
                    filter(Booking.id == id).\
                    update({'deposit_paid': 1})
                db.session.commit()
                allLogger.info(''.join(['Order #', str(id), ' has changed deposit\'s status to \'paid\'.']))
            elif request.form.get('deposit_unpaid') == 'unpaid':
                db.session.query(Booking).\
                    filter(Booking.id == id).\
                    update({'deposit_paid': 0})
                db.session.commit()
                allLogger.info(''.join(['Order #', str(id), ' has changed deposit\'s status to \'unpaid\'.']))

            elif request.form.get('final_paid') == 'paid':
                db.session.query(Booking).\
                    filter(Booking.id == id).\
                    update({'final_paid': 1})
                db.session.commit()
                allLogger.info(''.join(['Order #', str(id), ' has changed final\'s status to \'paid\'.']))

            elif request.form.get('final_unpaid') == 'unpaid':
                db.session.query(Booking).\
                    filter(Booking.id == id).\
                    update({'final_paid': 0})
                db.session.commit()
                allLogger.info(''.join(['Order #', str(id), ' has changed final\'s status to \'unpaid\'.']))

            elif request.form.get('delete') == 'delete':
                db.session.query(Booking).\
                    filter(Booking.id == id).\
                    update({'deleted': 1})
                db.session.commit()
                flash('成功刪除訂單編號 #' + str(id), category='success')
                allLogger.info(''.join(['Order #', str(id), ' has changed order\'s status to \'deleted\'.']))
                return redirect(url_for('admin.bookings'))

        query = db.session.query(Booking).filter(Booking.id == id).first()
        data = row2dict(query)
        data['room'] = names[data['room_num']][:3]
        data['check_in'] = (data['check_in'] + timedelta(hours=+8)).strftime('%Y-%m-%d')
        data['check_out'] = (data['check_out'] + timedelta(hours=+8)).strftime('%Y-%m-%d')
        
        if data['special_needs'] == '':
            data['special_needs'] = '無' 
        int_to_yes_no_dict_item(data, ['add_bed', 'parking', 'breakfast'])  

        return render_template('booking_detail.html', data = data)
    
    except Exception as e:
        allLogger.error(str(e))
        abort_msg(e)


@admin.route('/settings', methods=['GET', 'POST'])
# @login_required
def settings():

    try:
        admin_info = db.session.query(Admin).filter_by(id = 1).first()
        invite_code = admin_info.invite_code

        if request.method == 'POST':

            if request.form.get('submit_invite') == 'submit':

                if request.form.get('invite') == '':
                    flash('輸入有誤，請再試一次', category='error')
                    return render_template('settings.html', invite_code = invite_code)


                new_invite_code = request.form.get('invite')
                db.session.query(Admin).\
                    filter(Admin.id == 1).\
                    update({'invite_code': new_invite_code})
                db.session.commit()
                invite_code = new_invite_code
                allLogger.info('Invite code has changed into \'' + new_invite_code + '\'.')
                flash('成功修改管家邀請碼')

            elif request.form.get('submit_pw') == 'submit':

                if request.form.get('old_pw') == '' or request.form.get('new_pw') == '' or request.form.get('new_pw_confirm') == '':
                    flash('輸入有誤，請再試一次', category='error')
                    return render_template('settings.html', invite_code = invite_code)

                old_pw = admin_info.pw.encode('utf-8')
                old_pw_input = request.form.get('old_pw').encode('utf-8')
                
                if not bcrypt.checkpw(old_pw_input, old_pw):                    
                    flash('舊密碼輸入有誤，請再試一次', category='error')
                    return render_template('settings.html', invite_code = invite_code)
                
                new_pw = request.form.get('new_pw')
                new_pw_confirm = request.form.get('new_pw_confirm')

                if not is_legal_password(new_pw):
                    flash('新密碼不是有效的密碼，請再試一次', category='error')
                    return render_template('settings.html', invite_code = invite_code)
                
                if new_pw != new_pw_confirm:
                    flash('新密碼前後輸入不一致，請再試一次', category='error')
                    return render_template('settings.html', invite_code = invite_code)
                
                new_pw = new_pw.encode('utf-8')
                hashed_pw = bcrypt.hashpw(new_pw, bcrypt.gensalt(10))
                hashed_pw = hashed_pw.decode('utf-8')

                db.session.query(Admin).\
                    filter(Admin.id == 1).\
                    update({'pw': hashed_pw})
                db.session.commit()
                allLogger.info('Admin\'s password has changed.')
                flash('成功修改管理員密碼')

        return render_template('settings.html', invite_code = invite_code)
    except Exception as e:
        allLogger.error(str(e))
        abort_msg(e)


@admin.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('customer.home'))

@admin.route('/rooms', methods=['GET'])
@login_required
def admin_rooms():

    try:

        today = datetime.now(tz) + timedelta(days=-1)
        query = db.session.query(Rooms).\
            filter(Rooms.date >= today).\
            order_by(Rooms.serial).all()
        
        data = {}        
        for row in query:
            date = row.date
            date = (date + timedelta(hours=8)).strftime('%Y-%m-%d')
            data[date] = row2dict(row)

        return render_template('rooms_admin.html', data = data)

    except Exception as e:
        allLogger.error(str(e))
        abort_msg(e)



