from flask import Blueprint, render_template
# from flask_login import 

admin = Blueprint('admin', __name__)

@admin.route('/login', methods = ['GET', 'POST'])
def login():

    return render_template('login.html')
