from flask import Blueprint, render_template, redirect, url_for
from markupsafe import escape

customer = Blueprint('customer', __name__)

## functions

def img_indexing(room_num, img_amount:int):
    idx = {}
    for i in range(img_amount):
        idx[i] = ''.join([str(room_num), '_', str(i+2), '.jpg'])
    return idx

pricing = {'2 beds':['NT4,100', 'NT2,000', 'NT2,300', 'NT4,100'], 
           '3 beds':['NT4,500', 'NT2,800', 'NT3,300', 'NT4,500'], 
           '4 beds':['NT6,300', 'NT3,100', 'NT3,800', 'NT6,300']}

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
def room_each(room_num):

    if room_num == 301: 

        img_amount = 5
        photo_index = img_indexing(room_num, img_amount)

        return render_template('rooms_each.html', title = '杉行街', 
                                                  header = '杉行街（四人房）', 
                                                  imgs = photo_index, 
                                                  add = 1, 
                                                  pricing = pricing['4 beds'])
    elif room_num == 302: 

        img_amount = 2
        photo_index = img_indexing(room_num, img_amount)

        return render_template('rooms_each.html', title = '君子巷', 
                                                  header = '君子巷（雙人房）', 
                                                  imgs = photo_index, 
                                                  add = 0, 
                                                  pricing = pricing['2 beds'])    
    elif room_num == 303: 

        img_amount = 2
        photo_index = img_indexing(room_num, img_amount)

        return render_template('rooms_each.html', title = '後車巷', 
                                                  header = '後車巷（雙人房）', 
                                                  imgs = photo_index, 
                                                  add = 1, 
                                                  pricing = pricing['2 beds'])    
    elif room_num == 501: 

        img_amount = 3
        photo_index = img_indexing(room_num, img_amount)

        return render_template('rooms_each.html', title = '桂花巷', 
                                                  header = '桂花巷（雙人房）', 
                                                  imgs = photo_index, 
                                                  add = 0, 
                                                  pricing = pricing['2 beds'])
    elif room_num == 502: 

        img_amount = 4
        photo_index = img_indexing(room_num, img_amount)

        return render_template('rooms_each.html', title = '九曲巷', 
                                                  header = '九曲巷（三人房）', 
                                                  imgs = photo_index, 
                                                  add = 1, 
                                                  pricing = pricing['3 beds'])
    else: 
        return 'PAGE NOT FOUND. ROOM NUMBER IS NOT VALID. '



## reservation

@customer.route('/reservation', methods = ['GET', 'POST'])
def reservation():

    return render_template('reservation.html')

