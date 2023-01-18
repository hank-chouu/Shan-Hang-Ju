from flask import Blueprint, render_template, redirect, url_for

customer = Blueprint('customer', __name__)


@customer.route('/home', methods = ['GET'])
def home():

    return render_template('home.html')

@customer.route('', methods = ['GET'])
def entrance():

    return redirect(url_for('customer.home'))

@customer.route('/reservation', methods = ['GET', 'POST'])
def reservation():

    return render_template('reservation.html')

@customer.route('/rooms', methods = ['GET'])
def rooms_type():

    return render_template('rooms_view.html')