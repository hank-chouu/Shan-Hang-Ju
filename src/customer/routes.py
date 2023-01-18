from flask import Blueprint, render_template

customer = Blueprint('customer', __name__)

@customer.route('/reservation', methods = ['GET', 'POST'])
def reservation():

    return render_template('reservation.html')