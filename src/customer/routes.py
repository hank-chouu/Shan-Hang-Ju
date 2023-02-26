from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from datetime import datetime, timezone, timedelta
import pandas as pd
from sqlalchemy import func

from src.extensions.models import db, Rooms, Booking, Admin
from src.extensions.logger import allLogger, abort_msg
from src.extensions.email import mail, create_msg

## functions, variables and objects

customer = Blueprint('customer', __name__)

def img_indexing(room_num, img_amount:int):
    idx = {}
    for i in range(img_amount):
        idx[i] = ''.join([str(room_num), '_', str(i+2), '.jpg'])
    return idx

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
        

tz = timezone(timedelta(hours=+8))

pricing = {'2 beds':['NT4,100', 'NT2,000', 'NT2,300', 'NT4,100'], 
           '3 beds':['NT4,500', 'NT2,800', 'NT3,300', 'NT4,500'], 
           '4 beds':['NT6,300', 'NT3,100', 'NT3,800', 'NT6,300']}

names = {'301':'杉行街（四人房）', '302':'君子巷（雙人房）', '303':'後車巷（雙人房）',
         '501':'桂花巷（雙人房）', '502':'九曲巷（三人房）'}



## routes

@customer.route('/home', methods = ['GET'])
def home():
    return render_template('home.html')

@customer.route('', methods = ['GET'])
def entrance():
    return redirect(url_for('customer.home'))

@customer.route('/location', methods = ['GET'])
def location():
    return render_template('location.html')

## rooms

@customer.route('/rooms', methods = ['GET'])
def rooms_all():

    return render_template('rooms_all.html')

@customer.route('/rooms/<int:room_num>', methods = ['GET'])
def rooms_each(room_num):
    try:

        if room_num == 301: 

            img_amount = 5
            photo_index = img_indexing(room_num, img_amount)

            return render_template('rooms_each.html', title = names[str(room_num)][0:3], 
                                                    header = names[str(room_num)], 
                                                    imgs = photo_index, 
                                                    add = 1, 
                                                    pricing = pricing['4 beds'])
        elif room_num == 302: 

            img_amount = 2
            photo_index = img_indexing(room_num, img_amount)

            return render_template('rooms_each.html', title = names[str(room_num)][0:3], 
                                                    header = names[str(room_num)], 
                                                    imgs = photo_index, 
                                                    add = 0, 
                                                    pricing = pricing['2 beds'])    
        elif room_num == 303: 

            img_amount = 2
            photo_index = img_indexing(room_num, img_amount)

            return render_template('rooms_each.html', title = names[str(room_num)][0:3], 
                                                    header = names[str(room_num)][0:3], 
                                                    imgs = photo_index, 
                                                    add = 1, 
                                                    pricing = pricing['2 beds'])    
        elif room_num == 501: 

            img_amount = 3
            photo_index = img_indexing(room_num, img_amount)

            return render_template('rooms_each.html', title = names[str(room_num)][0:3], 
                                                    header = names[str(room_num)], 
                                                    imgs = photo_index, 
                                                    add = 0, 
                                                    pricing = pricing['2 beds'])
        elif room_num == 502: 

            img_amount = 4
            photo_index = img_indexing(room_num, img_amount)

            return render_template('rooms_each.html', title = names[str(room_num)][0:3], 
                                                    header = names[str(room_num)], 
                                                    imgs = photo_index, 
                                                    add = 1, 
                                                    pricing = pricing['3 beds'])
        else: 
            return render_template('404.html')
        
    except Exception as e:
        allLogger.error(str(e))
        abort_msg(e)

## reservation

@customer.route('/reservation', methods = ['GET', 'POST'])
def reservation():
        
    try:
        if request.method == 'POST':
            if request.form.get('search') == 'search':
                check_in = request.form.get('check_in_date')
                check_out = request.form.get('check_out_date')
                room_type = request.form.get('room_type')

                if check_in != '' and check_out != '':

                    check_in_dt = datetime.strptime(check_in, '%Y/%m/%d').replace(tzinfo=tz)
                    check_out_dt = datetime.strptime(check_out, '%Y/%m/%d').replace(tzinfo=tz)

                    # filter by date
                    
                    query = db.session.query(Rooms).filter(
                            Rooms.date >= check_in_dt, 
                            Rooms.date < check_out_dt
                    ).all()

                    # check if rooms are available

                    available_rooms = []
                    total_days = (check_out_dt.date() - check_in_dt.date()).days
                    
                    if room_type == '2':
                        room_302, room_303, room_501 = 0, 0, 0
                        for rooms in query:
                            room_302 += rooms.room_302
                            room_303 += rooms.room_303
                            room_501 += rooms.room_501                
                        if room_302 == total_days:
                            available_rooms.append('302')
                        if room_501 == total_days:
                            available_rooms.append('501')
                        if room_303 == total_days:
                            available_rooms.append('303')
                        

                    elif room_type == '3':
                        room_502 = 0
                        for rooms in query:
                            room_502 += rooms.room_502
                        if room_502 == total_days:
                            available_rooms.append('502')

                    elif room_type == '4':
                        room_301 = 0
                        for rooms in query:
                            room_301 += rooms.room_301
                        if room_301 == total_days:
                            available_rooms.append('301')

                    # generate available room info
                    if len(query) == 0:
                        allLogger.warn('Room database has ran out of records.')
                        flash('資料庫內部異常，無法查詢', category='error')
                        return render_template('reservation.html', result = False)
                    elif len(available_rooms) == 0:
                        is_available = False
                        info = [check_in.replace('/', '-'), check_out.replace('/', '-')]
                    elif len(available_rooms) != 0:
                        is_available = True

                        # prepare price table
                        date_pricing = pd.read_csv('src/files/date_pricing.csv')
                        date_pricing['date_dt'] = pd.to_datetime(date_pricing['date'], format='%Y/%m/%d')
                        date_pricing['date_dt'] = date_pricing['date_dt'].dt.tz_localize('UTC').dt.tz_convert('Asia/Taipei')
                        date_pricing = date_pricing[(date_pricing.date_dt >= pd.Timestamp(check_in_dt)) & (date_pricing.date_dt < pd.Timestamp(check_out_dt))]

                        info = {}
                        for room in available_rooms:
                            room_detail = {}
                            room_detail['img'] = room + '_1.jpg'
                            room_detail['name'] = names[room]
                            room_detail['dates'] = [check_in.replace('/', '-'), check_out.replace('/', '-'), len(date_pricing)]
                            room_detail['amount'] = date_pricing[room].sum()
                            info[room] = room_detail


                    return render_template('reservation.html', result = True, 
                                                            available = is_available, 
                                                            info = info)

            elif request.form.get('booking') == 'booking':

                # below parameter are sent by hidden inputs
                # basically won't mess up
                room_num = request.form.get('room_num')
                check_in = request.form.get('check_in_booking')
                check_out = request.form.get('check_out_booking')
                total = int(request.form.get('amount'))

                session['access_to_form'] = ''.join([room_num, check_in, check_out])

                return redirect(url_for('customer.form', room_num = room_num, 
                                                        check_in = check_in, 
                                                        check_out = check_out, 
                                                        total = total))
                                        
        return render_template('reservation.html', result = False)
    
    except Exception as e:
        allLogger.error(str(e))
        abort_msg(e)

# form

@customer.route('/form?room_num=<string:room_num>&check_in=<string:check_in>&check_out=<string:check_out>&total=<int:total>', methods=['GET', 'POST'])
def form(room_num, check_in, check_out, total):

    try:
        if 'access_to_form' not in session.keys():
            return render_template('404.html')
        elif session['access_to_form'] != ''.join([room_num, check_in, check_out]):
            flash('頁面已失效！請重新查詢', category='error')
            return redirect(url_for('customer.reservation'))
        
        # get invite code

        admin_info = db.session.query(Admin).filter_by(id = 1).first()
        invite_code = admin_info.invite_code

        # send parameters to form
        info = {}
        info['room_num'] = room_num
        info['name'] = names[room_num]
        info['check_in'] = check_in
        info['check_out'] = check_out
        info['total'] = total

        deposit = round(total * 0.3 / 100) * 100
        final = total - deposit

        info['deposit'] = deposit
        info['final'] = final

        check_in_dt = datetime.strptime(check_in, '%Y-%m-%d').replace(tzinfo=tz)
        check_out_dt = datetime.strptime(check_out, '%Y-%m-%d').replace(tzinfo=tz)
        total_days = (check_out_dt.date() - check_in_dt.date()).days
        info['total_days'] = total_days

        if request.method == 'POST':

            name = request.form.get('name')
            gender = request.form.get('gender')
            phone = request.form.get('phone')
            email = request.form.get('email')

            arrival = request.form.get('arrival_time')
            parking = 0
            if request.form.get('parking') == 'yes':
                parking = 1
            breakfast = 0
            if request.form.get('breakfast') == 'yes':
                breakfast = 1
            add_bed = 0
            if request.form.get('add_bed'):
                add_bed = 1
                total += 500 * total_days
                deposit += 150 * total_days
                final += 350 * total_days
            invite_code_form = request.form.get('invite')
            special_needs = request.form.get('special_needs')

            # check
            # invite code and valid phone number
            if '' in [name, phone, email, invite_code_form]:
                flash('資料未填齊全', category='error')
                return render_template('form.html', info=info)
            elif len(phone) != 10:
                flash('電話號碼格式有誤，請輸入您的手機號碼共 10 碼', category='error')
                return render_template('form.html', info=info)
            elif invite_code_form != invite_code:
                flash('邀請碼錯誤，請向管家索取正確的邀請碼', category='error')
                return render_template('form.html', info=info)

            # find the room, change status
            ## to check if the room is still available

            query = db.session.query(Rooms).filter(
                            Rooms.date >= check_in_dt, 
                            Rooms.date < check_out_dt)            
            status_list = [getattr(row, "room_" + room_num) for row in query.all()]
            # if still available, then room's value = 1
            if sum(status_list) != total_days :
                flash('您所選擇的房型在此日期已無法選購，請重新下訂', category='error')
                return redirect(url_for('customer.reservtion'))

            ## change room status
            current_date_dt = check_in_dt
            while (current_date_dt < check_out_dt):
                db.session.query(Rooms).\
                    filter(Rooms.date == current_date_dt).\
                    update({'room_'+ room_num: 0})
                current_date_dt += timedelta(days = 1)
            db.session.commit()         

            # add new booking record

            created_at = datetime.now(tz)

            client_info = [name, gender, phone, email]
            booking_info = [room_num, check_in_dt, check_out_dt, add_bed, arrival, parking, breakfast, special_needs, created_at]
            amounts = [total, deposit, final]

            max_id = db.session.query(func.max(Booking.id)).scalar()

            if max_id is None:
                new_id = 1
            else:
                new_id = max_id + 1
            new_booking_record = Booking(new_id, client_info, booking_info, amounts)
            db.session.add(new_booking_record)
            db.session.commit()
            allLogger.info(''.join(['Booking record created. Order ID: ', str(new_id), '. Client: ', name, '.']))
            allLogger.info(''.join(['Order ID ', str(new_id), ': room ', room_num, ' is booked from ', check_in, ' to ', check_out, '.']))


            # sending confirmation mail

            mail_info = {}
            mail_info['order_id'] = new_id
            mail_info['room'] = names[room_num]
            mail_info['check_in'] = check_in
            mail_info['check_out'] = check_out
            mail_info['total'] = total
            mail_info['deposit'] = deposit
            mail_info['final'] = final

            msg = create_msg(email, mail_info)
            mail.send(msg)

            session['access_to_confirm'] = new_id
            session['access_to_form'] = False

            # succeed and completed
            # redirect to complete page
            return redirect(url_for('customer.confirmed', order_id = new_id))

        return render_template('form.html', info=info)
    
    except Exception as e:
        allLogger.error(str(e))
        abort_msg(e)

# redirect to confirmation after successful reservation

@customer.route('/confirmed?order_id=<int:order_id>', methods = ['GET'])
def confirmed(order_id):
        
    try:

        if 'access_to_confirm' not in session.keys():
            return render_template('404.html')
        elif session['access_to_confirm'] != order_id:
            return render_template('404.html')
        order = db.session.query(Booking).filter(Booking.id == order_id).first()
        order = row2dict(order)
        order['room'] = names[order['room_num']]
        order['check_in'] = (order['check_in'] + timedelta(hours=+8)).strftime('%Y-%m-%d')
        order['check_out'] = (order['check_out'] + timedelta(hours=+8)).strftime('%Y-%m-%d')
        int_to_yes_no_dict_item(order, ['add_bed', 'parking', 'breakfast'])
        if order['special_needs'] == '':
            order['special_needs'] = '無'

        return render_template('confirmation.html', order = order)
    
    except Exception as e:
        allLogger.error(str(e))
        abort_msg(e)

        


### testing routes ###
@customer.route('/manual-addition', methods=["GET"])
def by_me():

    # add rows

    start_date = '2023/02/01'
    start_date = datetime.strptime(start_date, '%Y/%m/%d').replace(tzinfo=tz)

    for i in range(180):
        row = Rooms(start_date, 1, 1, 1, 1, 1)
        db.session.add(row)
        start_date = start_date + timedelta(days=1)
    db.session.commit()

    # updates

    # check_in = '2023-01-29'
    # check_out = '2023-01-30'
    # room_num = '302'
    # check_in_dt = datetime.strptime(check_in, '%Y-%m-%d').replace(tzinfo=tz)
    # check_out_dt = datetime.strptime(check_out, '%Y-%m-%d').replace(tzinfo=tz)
    # current_date_dt = check_in_dt
    # while (current_date_dt < check_out_dt):
    #     db.session.query(Rooms).\
    #         filter(Rooms.date == current_date_dt).\
    #         update({'room_'+ room_num: 1})
    #     current_date_dt += timedelta(days = 1)

    # drop all

    # db.drop_all()

    return 'OK'




@customer.route('/update')
def uppdate():



    return 'Update'


@customer.route('/drop-all')
def drop():


    db.drop_all()
    

    return 'drop all'

