from flask import Blueprint, render_template, redirect, url_for

customer = Blueprint('customer', __name__)


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
def rooms_type():

    return render_template('rooms_view.html')

@customer.route('/rooms/301', methods = ['GET'])
def room301():

    return render_template('room301.html')


@customer.route('/rooms/302', methods = ['GET'])
def room302():

    return render_template('room302.html')

@customer.route('/rooms/501', methods = ['GET'])
def room501():

    return render_template('room501.html')

@customer.route('/rooms/502', methods = ['GET'])
def room502():

    return render_template('room502.html')

## reservation

@customer.route('/reservation', methods = ['GET', 'POST'])
def reservation():

    return render_template('reservation.html')

