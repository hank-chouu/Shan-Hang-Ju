from flask import Blueprint, render_template, redirect, url_for, request, flash
from datetime import datetime, timezone, timedelta
from markupsafe import escape
# import pytz
import pandas as pd


from src.extensions.models import db, Rooms, allLogger



## functions, variables and objects

customer = Blueprint('customer', __name__)

def img_indexing(room_num, img_amount:int):
    idx = {}
    for i in range(img_amount):
        idx[i] = ''.join([str(room_num), '_', str(i+2), '.jpg'])
    return idx

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
        return 'PAGE NOT FOUND. ROOM NUMBER IS NOT VALID. '



## reservation

@customer.route('/reservation', methods = ['GET', 'POST'])
def reservation():

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

            return redirect(url_for('customer.form', room_num = room_num, 
                                                     check_in = check_in, 
                                                     check_out = check_out, 
                                                     total = total))

                        
    return render_template('reservation.html', result = False)


@customer.route('/form?room_num=<string:room_num>&check_in=<string:check_in>&check_out=<string:check_out>&total=<int:total>', methods=['GET', 'POST'])
def form(room_num, check_in, check_out, total):

    # send parameters to form
    info = {}
    info['room_num'] = room_num
    info['name'] = names[room_num]
    info['check_in'] = check_in
    info['check_out'] = check_out
    info['total'] = total

    info['deposit'] = round(total * 0.3 / 100) * 100
    info['final'] = total - info['deposit']

    return render_template('form.html', info=info)


@customer.route('/add', methods=["GET"])
def add_row():

    today_date = '2023/01/22'
    today_date = datetime.strptime(today_date, '%Y/%m/%d').replace(tzinfo=tz)

    for i in range(10):

        row = Rooms(today_date, 1, 1, 1, 1, 1)
        db.session.add(row)
        today_date = today_date + timedelta(days=1)
    db.session.commit()
    # check_in = '2023/01/24'
    # check_out = '2023/01/25'
    # check_in = datetime.strptime(check_in, '%Y/%m/%d').replace(tzinfo=tz)
    # check_out = datetime.strptime(check_out, '%Y/%m/%d').replace(tzinfo=tz)

    # # print(today_date)
    # query = db.session.query(Rooms).filter(
    #     Rooms.date >= check_in, 
    #     Rooms.date < check_out
    # ).all()
    # for row in query:
    #     print(row.date.replace(tzinfo=tz))
    # db.session.commit()


    return 'OK'
