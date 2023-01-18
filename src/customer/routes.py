from flask import Blueprint, render_template

customer = Blueprint('customer', __name__)


@customer.route('', methods = ['GET'])
def home():

    return render_template('home.html')

@customer.route('/reservation', methods = ['GET', 'POST'])
def reservation():

    return render_template('reservation.html')