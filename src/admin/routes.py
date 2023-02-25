from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, UserMixin
import bcrypt
from datetime import datetime, timezone, timedelta

from src.extensions.models import db, Admin, User, Booking
from src.extensions.logger import allLogger, abort_msg

admin = Blueprint('admin', __name__)

tz = timezone(timedelta(hours=+8))


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
                login_user(user)
                flash('登入成功', category='success')
                allLogger.info('Admin logged in successfully.')
                return redirect(url_for('admin.bookings'))
            
        return render_template('login.html')
    
    except Exception as e:
        allLogger.error(str(e))
        abort_msg(e)



@admin.route('/bookings', methods = ['GET', 'POST'])
@login_required
def bookings():

    try:

        today = datetime.now(tz) - timedelta(days=1)
        

        data = db.session.query(Booking).filter(
            Booking.check_in >= today, 
            Booking.check_out >= today
        ).all()

        return render_template('bookings.html', data = data)
    
    except Exception as e:
        allLogger.error(str(e))
        abort_msg(e)
